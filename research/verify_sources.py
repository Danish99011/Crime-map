#!/usr/bin/env python3
"""Link-check every URL in the source catalogue, from an unblocked network.

Phase 1 research was carried out in a sandbox whose egress policy blocked
almost every host that matters (*.gov.in, *.nic.in, data.police.uk, OSM
mirrors, archive.org). Agents could find sources but could not open them, so
most catalogue entries are marked CITED rather than VERIFIED_*.

This script closes that gap. Run it anywhere with ordinary internet access —
it needs only the Python standard library:

    python3 research/verify_sources.py                 # check everything
    python3 research/verify_sources.py --domain ncrb-national
    python3 research/verify_sources.py --patch         # write results back

It records, per URL: HTTP status, final URL after redirects, content type,
size, and the <title> of HTML pages. That last field is the important one — a
200 response proves a server answered, not that it answered with the dataset
we wanted. A portal that quietly redirects every unknown path to its homepage
will return 200 for a URL that no longer exists, so compare the title against
the entry's `evidence` before believing it.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"
REPORT_JSON = ROOT / "url_check.json"
REPORT_MD = ROOT / "URL_CHECK.md"

UA = "IndiaCrimeMap-LinkCheck/1.0 (+research; contact: repo owner)"
TITLE_RE = re.compile(rb"<title[^>]*>(.*?)</title>", re.I | re.S)

# One request at a time per host, with a gap between them. This is
# reconnaissance against public-sector servers, several of which are frail.
_host_locks: dict[str, threading.Lock] = defaultdict(threading.Lock)
_host_last: dict[str, float] = defaultdict(float)


def _ssl_context() -> ssl.SSLContext:
    """Trust the system CAs, plus a proxy CA bundle if we are behind one.

    Sandboxes that re-terminate TLS (including the one this research was done
    in) hand every connection a certificate signed by their own CA. Without
    this, every host would come back as a TLS failure and the report would say
    the whole of Indian government is offline.
    """
    context = ssl.create_default_context()
    for candidate in (os.environ.get("SSL_CERT_FILE"),
                      os.environ.get("REQUESTS_CA_BUNDLE"),
                      "/root/.ccr/ca-bundle.crt"):
        if candidate and Path(candidate).is_file():
            try:
                context.load_verify_locations(candidate)
            except (OSError, ssl.SSLError):
                continue
            break
    return context


def fetch(url: str, timeout: float, delay: float) -> dict:
    host = urlsplit(url).netloc
    result = {"url": url, "host": host, "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    with _host_locks[host]:
        gap = delay - (time.monotonic() - _host_last[host])
        if gap > 0:
            time.sleep(gap)
        _host_last[host] = time.monotonic()

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": UA,
                "Accept": "*/*",
                "Accept-Encoding": "gzip",
                "Accept-Language": "en-IN,en;q=0.9",
            },
        )
        # Many Indian government sites still serve outdated or misconfigured
        # TLS. Record that fact rather than silently skipping the host.
        context = _ssl_context()
        try:
            with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
                body = response.read(262144)
                if response.headers.get("Content-Encoding") == "gzip":
                    try:
                        body = gzip.decompress(body)
                    except (OSError, EOFError):
                        pass
                result.update(
                    status=response.status,
                    final_url=response.url.split("?", 1)[0],  # never keep signed/tokened query strings
                    content_type=(response.headers.get("Content-Type") or "").split(";")[0].strip(),
                    content_length=response.headers.get("Content-Length"),
                    redirected=response.url.rstrip("/") != url.rstrip("/"),
                )
                match = TITLE_RE.search(body)
                if match:
                    title = match.group(1).decode("utf-8", "replace")
                    result["title"] = re.sub(r"\s+", " ", title).strip()[:200]
        except urllib.error.HTTPError as exc:
            result.update(status=exc.code, error=f"HTTP {exc.code} {exc.reason}")
        except urllib.error.URLError as exc:
            reason = exc.reason
            kind = "tls" if isinstance(reason, ssl.SSLError) else "network"
            result.update(status=None, error=f"{kind}: {reason}")
        except Exception as exc:  # timeouts, malformed URLs, decoding failures
            result.update(status=None, error=f"{type(exc).__name__}: {exc}")

    return result


def collect_urls(domain_filter: str | None) -> list[tuple[str, str, str, str]]:
    """Return (domain, entry_id, url_key, url) for every URL in the catalogue."""
    found = []
    for path in sorted(SOURCES.glob("*.jsonl")):
        if domain_filter and path.stem != domain_filter:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            urls = entry.get("urls")
            if not isinstance(urls, dict):
                continue
            for key, url in urls.items():
                if isinstance(url, str) and url.startswith(("http://", "https://")):
                    found.append((path.stem, entry.get("id", "?"), key, url))
    return found


def verdict(result: dict) -> str:
    status = result.get("status")
    if status is None:
        return "UNREACHABLE"
    if status == 200:
        return "REDIRECTED" if result.get("redirected") else "OK"
    if status in (401, 403):
        return "FORBIDDEN"
    if status == 404:
        return "DEAD"
    if 300 <= status < 400:
        return "REDIRECTED"
    return "ERROR"


def write_report(rows: list[dict]) -> None:
    REPORT_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    buckets = defaultdict(list)
    for row in rows:
        buckets[row["verdict"]].append(row)

    order = ["OK", "REDIRECTED", "FORBIDDEN", "DEAD", "ERROR", "UNREACHABLE"]
    lines = [
        "# URL Check",
        "",
        "Generated by `research/verify_sources.py` — do not edit by hand.",
        "",
        f"Checked **{len(rows)} URLs** across **{len({r['domain'] for r in rows})} domains** "
        f"on {time.strftime('%Y-%m-%d', time.gmtime())}.",
        "",
        "| verdict | count | meaning |",
        "|---|---|---|",
    ]
    meanings = {
        "OK": "server returned the page at the requested URL",
        "REDIRECTED": "server answered, but sent us somewhere else — check the title",
        "FORBIDDEN": "exists but refuses anonymous access (login, geo-block, WAF)",
        "DEAD": "404 — the URL in the catalogue is wrong or the page is gone",
        "ERROR": "other HTTP error, often a server fault rather than a bad URL",
        "UNREACHABLE": "DNS, TLS or timeout failure — record it, do not assume it is gone",
    }
    for key in order:
        if buckets[key]:
            lines.append(f"| {key} | {len(buckets[key])} | {meanings[key]} |")

    for key in order:
        if not buckets[key]:
            continue
        lines += ["", f"## {key}", "", "| domain | entry | url | title / error |", "|---|---|---|---|"]
        for row in sorted(buckets[key], key=lambda r: (r["domain"], r["entry_id"])):
            detail = row.get("title") or row.get("error") or ""
            detail = detail.replace("|", "\\|")[:120]
            url = row["url"].replace("|", "%7C")
            lines.append(f"| {row['domain']} | `{row['entry_id']}` | {url} | {detail} |")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def patch_jsonl(rows: list[dict]) -> int:
    """Write the check result back onto each entry as a `url_check` field."""
    by_entry = defaultdict(dict)
    for row in rows:
        by_entry[(row["domain"], row["entry_id"])][row["url_key"]] = {
            "verdict": row["verdict"],
            "status": row.get("status"),
            "title": row.get("title"),
            "error": row.get("error"),
            "checked_at": row.get("checked_at"),
        }

    patched = 0
    for path in sorted(SOURCES.glob("*.jsonl")):
        out = []
        changed = False
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                out.append(line)
                continue
            try:
                entry = json.loads(stripped)
            except json.JSONDecodeError:
                out.append(line)
                continue
            check = by_entry.get((path.stem, entry.get("id")))
            if check:
                entry["url_check"] = check
                changed = True
                patched += 1
            out.append(json.dumps(entry, ensure_ascii=False))
        if changed:
            path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return patched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--domain", help="check only one domain, e.g. ncrb-national")
    parser.add_argument("--workers", type=int, default=8, help="parallel requests across hosts (default 8)")
    parser.add_argument("--delay", type=float, default=1.5, help="seconds between requests to the same host")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--patch", action="store_true", help="write results back into the source jsonl files")
    parser.add_argument("--skip-host", action="append", default=[], metavar="HOST",
                        help="do not touch this host; repeatable. Use it when another "
                             "job already owns that host, so the two do not make "
                             "concurrent requests to one public-sector server.")
    args = parser.parse_args()

    targets = collect_urls(args.domain)
    if args.skip_host:
        skip = {h.lower() for h in args.skip_host}
        kept = [t for t in targets
                if not any(urlsplit(t[3]).netloc.lower().endswith(h) for h in skip)]
        print(f"Skipping {len(targets) - len(kept)} URLs on {', '.join(sorted(skip))} "
              f"(another job owns those hosts)")
        targets = kept
    if not targets:
        print("No URLs found. Have the research agents written research/sources/*.jsonl yet?", file=sys.stderr)
        return 1

    print(f"Checking {len(targets)} URLs across {len({urlsplit(u).netloc for _, _, _, u in targets})} hosts...")
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(fetch, url, args.timeout, args.delay): (domain, entry_id, key, url)
            for domain, entry_id, key, url in targets
        }
        for done, future in enumerate(as_completed(futures), 1):
            domain, entry_id, key, url = futures[future]
            result = future.result()
            result.update(domain=domain, entry_id=entry_id, url_key=key)
            result["verdict"] = verdict(result)
            rows.append(result)
            print(f"  [{done}/{len(targets)}] {result['verdict']:12s} {url}", flush=True)

    write_report(rows)
    counts = defaultdict(int)
    for row in rows:
        counts[row["verdict"]] += 1
    print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"Wrote {REPORT_JSON.name} and {REPORT_MD.name}")

    if args.patch:
        print(f"Patched url_check onto {patch_jsonl(rows)} entries")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
