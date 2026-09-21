"""Fetch the public source data the Bihar pipeline is built from.

Everything here is a public download with a stated licence. Nothing in this
file touches a government portal directly: both artefacts are community mirrors
of government data, which is what made them reachable at all. Re-verify the
upstream originals before relying on this in production — see
docs/PHASE1-FINDINGS.md section 9.

Not here, and deliberately: GeoNames' Indian postal-code file (mirrored at
github.com/sanand0/pincode). It was tried as a way to centre the map on a
pincode and rejected on measurement: of 89 Mumbai pincodes in it, 82 share one
point (19.0167, 72.85) and the rest fall on two more. Zooming "to a pincode"
with that would place most of the city on top of Fort. A pincode is only
located here from a police station's own published address.

Run:  python3 -m pipeline.download
"""

from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

DOWNLOADS = [
    {
        "filename": "INDIA_POLICE_STATIONS.geojson",
        "url": "https://raw.githubusercontent.com/yashveeeeeeer/india-geodata/"
               "main/data/police/stations/INDIA_POLICE_STATIONS.geojson",
        "about": "16,459 all-India police station points with MHA station codes",
        "licence": "unstated upstream; mirror asserts CC0-1.0",
    },
    {
        "filename": "Bhugoal_BH_Police_Thana_Boundaries.geojsonl.7z",
        "url": "https://github.com/ramSeraph/indian_admin_boundaries/releases/"
               "download/police/Bhugoal_BH_Police_Thana_Boundaries.geojsonl.7z",
        "about": "896 Bihar police thana jurisdiction polygons, from i-Bhugoal",
        "licence": "CC0-1.0; attribute datameet and the original government source",
        "extract": "Bhugoal_BH_Police_Thana_Boundaries.geojsonl",
    },
]


def fetch(url: str, target: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "IndiaCrimeMap/0.1"})
    with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as handle:
        while chunk := response.read(1 << 16):
            handle.write(chunk)


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    for item in DOWNLOADS:
        target = RAW / item["filename"]
        if target.exists():
            print(f"have  {item['filename']} ({target.stat().st_size:,} bytes)")
        else:
            print(f"fetch {item['filename']} — {item['about']}")
            try:
                fetch(item["url"], target)
            except Exception as exc:
                print(f"  FAILED: {exc}", file=sys.stderr)
                print(f"  url: {item['url']}", file=sys.stderr)
                return 1
            print(f"  {target.stat().st_size:,} bytes")

        digest = hashlib.sha256(target.read_bytes()).hexdigest()[:16]
        print(f"      sha256:{digest}  licence: {item['licence']}")

        extract = item.get("extract")
        if extract and not (RAW / extract).exists():
            try:
                import py7zr
            except ImportError:
                print("  py7zr not installed; run: pip install py7zr", file=sys.stderr)
                return 1
            with py7zr.SevenZipFile(target) as archive:
                archive.extractall(path=RAW)
            print(f"      extracted {extract}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
