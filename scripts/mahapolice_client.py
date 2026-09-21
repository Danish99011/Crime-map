#!/usr/bin/env python3
"""HTTP client for the Maharashtra Police published-FIR form.

Standard library only, so it runs on any laptop in India with Python 3.9+.
The parser it feeds lives in `pipeline/mahapolice.py`.

The form is ASP.NET WebForms, which means four things a naive scraper gets
wrong, all of them found by probing the live page on 2026-09-20:

1. **The unit list is empty until a session exists.** Requesting
   `PublishedFIRs.aspx` cold returns the page with a single "Select" option and
   no districts. Visiting `index.aspx` first sets the session cookie that makes
   the server populate it. A scraper that skips this sees no units and concludes
   the portal is broken.
2. **Selecting a unit is a server round-trip**, not a client-side filter. The
   police-station list for that unit only exists after posting back with
   `__EVENTTARGET` set to the unit dropdown.
3. **`__VIEWSTATE` and `__EVENTVALIDATION` must be carried forward from the
   most recent response.** Posting a stale pair, or an option value the server
   did not render, returns a generic error page -- which is why the station
   dropdown's "Select" must be posted as an empty string and not as the literal
   "Select" that the unit dropdown uses.
4. **Connections reset.** These servers drop roughly one request in five from
   here. Every request retries with backoff; without that the fetch looks like
   an absence of data rather than a flaky link.

Politeness is not optional and not configurable below a floor: one request at a
time, with a pause between them. This is a public-sector server that citizens
depend on, and degrading it would do more harm than the map does good.
"""

from __future__ import annotations

import gzip
import html
import http.cookiejar
import re
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://citizen.mahapolice.gov.in"
INDEX = BASE + "/Citizen/MH/index.aspx"
FORM = BASE + "/Citizen/MH/PublishedFIRs.aspx"

UA = ("Mozilla/5.0 (compatible; IndiaCrimeMap/0.1; public-interest safety research; "
      "contact via the project repository)")

# Control names, read off the live form rather than guessed.
UNIT = "ctl00$ContentPlaceHolder1$ddlDistrict"
STATION = "ctl00$ContentPlaceHolder1$ddlPoliceStation"
DATE_FROM = "ctl00$ContentPlaceHolder1$txtDateOfRegistrationFrom"
DATE_TO = "ctl00$ContentPlaceHolder1$txtDateOfRegistrationTo"
FIR_NO = "ctl00$ContentPlaceHolder1$txtFirno"
PAGE_SIZE = "ctl00$ContentPlaceHolder1$ucRecordView$ddlPageSize"
PAGE_NUMBER = "ctl00$ContentPlaceHolder1$ucGridRecordView$txtPageNumber"
PAGE_GO = "ctl00$ContentPlaceHolder1$ucGridRecordView$btnPageNumber"
SEARCH = "ctl00$ContentPlaceHolder1$btnSearch"
GRID = "ctl00$ContentPlaceHolder1$gdvDeadBody"

STATE_KEYS = ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION",
              "__VIEWSTATEENCRYPTED")

SELECT_BLOCK = re.compile(r'<select[^>]*name="([^"]+)"[^>]*>(.*?)</select>', re.S | re.I)
OPTION = re.compile(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', re.S | re.I)

# The portal's minimum courteous interval. Not exposed as a flag below this.
MIN_DELAY = 2.0


class PortalError(RuntimeError):
    """The portal answered, but not with a page we can use."""


class MahapoliceClient:
    def __init__(self, delay: float = 3.0, tries: int = 6, timeout: float = 90.0):
        self.delay = max(delay, MIN_DELAY)
        self.tries = tries
        self.timeout = timeout
        self._jar = http.cookiejar.CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self._jar))
        self._last_body = ""
        self.requests_made = 0
        self.retries = 0

    # ---------------------------------------------------------------- transport

    def _request(self, url: str, data: bytes | None = None,
                 referer: str | None = None) -> str:
        headers = {
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-IN,en;q=0.9",
            "Accept-Encoding": "gzip",
        }
        if referer:
            headers["Referer"] = referer
        if data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        last: Exception | None = None
        for attempt in range(self.tries):
            try:
                request = urllib.request.Request(url, data=data, headers=headers)
                with self._opener.open(request, timeout=self.timeout) as response:
                    body = response.read()
                    if response.headers.get("Content-Encoding") == "gzip":
                        body = gzip.decompress(body)
                    self.requests_made += 1
                    self._last_body = body.decode("utf-8", "replace")
                    return self._last_body
            except Exception as exc:                # reset, timeout, TLS, HTTP
                last = exc
                self.retries += 1
                # A connection reset means the server never finished serving
                # this request, so retrying promptly adds no load to it -- the
                # politeness that matters is the delay between *served*
                # requests, which `_pause` keeps. Escalating backoff here was
                # costing minutes per page on a link that drops roughly one
                # request in five, turning a month into a day's work for no
                # benefit to the portal. Later attempts still back off, in
                # case the server itself is the thing struggling.
                reset = isinstance(exc, (ConnectionResetError, TimeoutError)) or \
                    "reset" in str(exc).lower() or "timed out" in str(exc).lower()
                if reset and attempt < 3:
                    time.sleep(1.0)
                else:
                    time.sleep(min(self.delay * (attempt + 1), 30.0))
        raise PortalError(f"{url} failed after {self.tries} attempts: {last}")

    def _pause(self) -> None:
        time.sleep(self.delay)

    # ------------------------------------------------------------------ parsing

    @staticmethod
    def _form_state(page: str) -> dict:
        state = {}
        for key in STATE_KEYS:
            found = re.search(r'name="%s"[^>]*value="([^"]*)"' % key, page)
            if found:
                state[key] = html.unescape(found.group(1))
        if "__VIEWSTATE" not in state:
            raise PortalError(
                "no __VIEWSTATE on this page -- the session has probably "
                "expired or the portal returned its error page")
        return state

    @staticmethod
    def _options(page: str, control: str) -> list[tuple[str, str]]:
        for name, block in SELECT_BLOCK.findall(page):
            if name == control:
                return [(value,
                         re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", label))).strip())
                        for value, label in OPTION.findall(block)]
        return []

    def _placeholder(self, control: str) -> str:
        """The value the form currently gives its "Select" option.

        This is not cosmetic. On the blank form the station dropdown's
        placeholder is the literal "Select"; once a unit has been chosen the
        server re-renders it with an empty value. Posting the wrong one fails
        EventValidation and the portal answers with a generic error page, which
        is indistinguishable from "no crime" unless you are looking for it.
        """
        for value, label in self._options(self._last_body, control):
            if label.strip().lower() == "select":
                return value
        return ""

    @staticmethod
    def _is_error_page(page: str) -> bool:
        return "Error Has Occurred" in page and len(page) < 8000

    # -------------------------------------------------------------------- steps

    def open_form(self) -> list[tuple[str, str]]:
        """Warm a session, open the search form, return its list of units.

        The warm-up is the non-obvious part: without visiting `index.aspx`
        first the unit dropdown comes back empty and every later step fails.
        """
        self._request(INDEX)
        self._pause()
        page = self._request(FORM, referer=INDEX)
        self._pause()
        units = [(v, t) for v, t in self._options(page, UNIT) if v and v != "Select"]
        if not units:
            raise PortalError(
                "the unit dropdown came back empty even after the session "
                "warm-up. Do not treat this as 'no data'; it is a failed fetch.")
        return units

    def reset(self, unit_id: str) -> list[tuple[str, str]]:
        """Return to a clean search form with `unit_id` selected.

        A month must not be started from the state the previous month left
        behind. The client posts the __VIEWSTATE it last received, and after a
        month finishes that is the final page of that month's results grid.
        Re-posting the unit selection from there is not enough to clear it:
        over a 23-month run it produced an exact three-month cycle -- one month
        complete, the next truncated at its second page with 50 rows, the third
        refused outright with "unit was rejected", then clean again because the
        refusal forced a new session. Half the series came back short, and the
        shortfalls were ours, not the portal's.

        So this re-walks the whole entry path: index.aspx for a session, the
        form, then the unit postback. Three requests at the start of a month
        that costs a hundred and sixty, in exchange for each month standing on
        its own.
        """
        self.open_form()
        return self.select_unit(unit_id)

    def select_unit(self, unit_id: str) -> list[tuple[str, str]]:
        """Post back the unit selection; return that unit's police stations."""
        form = self._form_state(self._last_body)
        form.update({
            "__EVENTTARGET": UNIT, "__EVENTARGUMENT": "", "__LASTFOCUS": "",
            UNIT: unit_id, STATION: self._placeholder(STATION),
            DATE_FROM: "", DATE_TO: "", FIR_NO: "", PAGE_SIZE: "0",
            "ctl00$hdnSessionIdleTime": "", "ctl00$hdnUserUniqueId": "",
        })
        page = self._request(FORM, urllib.parse.urlencode(form).encode(), FORM)
        self._pause()
        if self._is_error_page(page):
            raise PortalError(f"unit {unit_id} was rejected by the portal")
        return [(v, t) for v, t in self._options(page, STATION) if v]

    def search(self, unit_id: str, date_from: str, date_to: str,
               page_size: int = 50, station_id: str | None = None) -> str:
        """Run a search. Dates are dd/MM/yyyy, the format the form's mask sets.

        `station_id` defaults to "all stations in the unit". Returns the raw
        results page for `pipeline.mahapolice.parse_grid`.
        """
        if station_id is None:
            station_id = self._placeholder(STATION)
        form = self._form_state(self._last_body)
        form.update({
            "__EVENTTARGET": "", "__EVENTARGUMENT": "", "__LASTFOCUS": "",
            UNIT: unit_id, STATION: station_id,
            "ctl00$ContentPlaceHolder1$meeDateOfRegistrationFrom_ClientState": "",
            "ctl00$ContentPlaceHolder1$meeDateOfRegistrationTo_ClientState": "",
            DATE_FROM: date_from, DATE_TO: date_to, FIR_NO: "",
            PAGE_SIZE: str(page_size), SEARCH: "Search",
            "ctl00$hdnSessionIdleTime": "", "ctl00$hdnUserUniqueId": "",
        })
        page = self._request(FORM, urllib.parse.urlencode(form).encode(), FORM)
        self._pause()
        if self._is_error_page(page):
            raise PortalError(
                f"search for unit {unit_id} {date_from}..{date_to} returned the "
                f"portal's error page. This is a failure, not an empty result.")
        return page

    def goto_grid_page(self, number: int, unit_id: str, date_from: str,
                       date_to: str, page_size: int = 50,
                       station_id: str | None = None) -> str:
        """Move to page `number` using the GridView's own pager postback.

        The grid renders its page links as
        `__doPostBack('ctl00$ContentPlaceHolder1$gdvDeadBody', 'Page$N')`, and
        driving that directly is more reliable than the page-number textbox:
        it is what the page itself does, it needs no other field to be
        re-posted consistently, and it works for pages beyond the ten the
        pager chooses to render.

        The search whose results are being paged must be the most recent
        request on this client, because the posted __VIEWSTATE carries it.
        """
        if station_id is None:
            station_id = self._placeholder(STATION)
        form = self._form_state(self._last_body)
        form.update({
            "__EVENTTARGET": GRID, "__EVENTARGUMENT": f"Page${number}",
            "__LASTFOCUS": "",
            UNIT: unit_id, STATION: station_id,
            DATE_FROM: date_from, DATE_TO: date_to, FIR_NO: "",
            PAGE_SIZE: str(page_size),
            "ctl00$hdnSessionIdleTime": "", "ctl00$hdnUserUniqueId": "",
        })
        page = self._request(FORM, urllib.parse.urlencode(form).encode(), FORM)
        self._pause()
        if self._is_error_page(page):
            raise PortalError(f"paging to {number} returned the portal error page")
        return page

    def goto_page(self, unit_id: str, date_from: str, date_to: str,
                  number: int, page_size: int = 50,
                  station_id: str | None = None) -> str:
        """Move to page `number` of the current result set."""
        if station_id is None:
            station_id = self._placeholder(STATION)
        form = self._form_state(self._last_body)
        form.update({
            "__EVENTTARGET": "", "__EVENTARGUMENT": "", "__LASTFOCUS": "",
            UNIT: unit_id, STATION: station_id,
            DATE_FROM: date_from, DATE_TO: date_to, FIR_NO: "",
            PAGE_SIZE: str(page_size),
            PAGE_NUMBER: str(number), PAGE_GO: "Go",
            "ctl00$hdnSessionIdleTime": "", "ctl00$hdnUserUniqueId": "",
        })
        page = self._request(FORM, urllib.parse.urlencode(form).encode(), FORM)
        self._pause()
        if self._is_error_page(page):
            raise PortalError(f"paging to {number} returned the error page")
        return page
