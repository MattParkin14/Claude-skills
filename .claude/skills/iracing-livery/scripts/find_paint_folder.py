#!/usr/bin/env python3
"""Find the iRacing paint folder, list car folders, and guess the user's customer ID.

Usage:
  python find_paint_folder.py [--root "C:/Users/me/Documents/iRacing"] [--car mx5] [--json]

Finds Documents the way Windows does (so OneDrive-redirected Documents are handled), then lists
Documents/iRacing/paint/<car folder>/ sorted by most recently used, with the paint files in each.

Customer ID guess: IDs on helmet_/suit_ files in the root paint folder are strong evidence; IDs that
appear in many car folders are weaker (Trading Paints also downloads other drivers' paints there).
Always confirm the ID with the user — it is shown on their iRacing account/profile page.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys
from pathlib import Path

PAINT_RX = re.compile(r"^(car|car_spec|car_num|car_decal|car_team|car_num_team|car_spec_team|helmet|suit)_(\d+)\.(tga|mip)$", re.I)


def windows_documents():
    try:
        import ctypes
        import uuid
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

        u = uuid.UUID("{FDD39AD0-238F-46AF-ADB4-6C85480369C7}")  # FOLDERID_Documents
        g = GUID(u.time_low, u.time_mid, u.time_hi_version, (ctypes.c_ubyte * 8).from_buffer_copy(u.bytes[8:]))
        p = ctypes.c_wchar_p()
        if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(g), 0, None, ctypes.byref(p)) == 0:
            path = p.value
            ctypes.windll.ole32.CoTaskMemFree(p)
            return Path(path)
    except Exception:  # noqa: BLE001
        pass
    return None


def candidates():
    out = []
    wd = windows_documents()
    if wd:
        out.append(wd / "iRacing")
    home = Path.home()
    up = os.environ.get("USERPROFILE")
    for base in filter(None, [up and Path(up), home]):
        out += [base / "Documents" / "iRacing", base / "OneDrive" / "Documents" / "iRacing"]
        out += [Path(p) / "Documents" / "iRacing" for p in glob.glob(str(base / "OneDrive*"))]
    out += [Path(p) for p in glob.glob("/mnt/c/Users/*/Documents/iRacing")]
    out += [Path(p) for p in glob.glob("/mnt/c/Users/*/OneDrive*/Documents/iRacing")]
    seen, uniq = set(), []
    for c in out:
        k = str(c).lower()
        if k not in seen:
            seen.add(k)
            uniq.append(c)
    return uniq


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="the iRacing documents folder (the one containing 'paint')")
    ap.add_argument("--car", help="only show car folders whose name contains this")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    roots = [Path(args.root)] if args.root else [c for c in candidates() if (c / "paint").is_dir()]
    if not roots:
        tried = "\n  ".join(str(c) for c in candidates())
        print(f"No iRacing paint folder found. Tried:\n  {tried}\n"
              "Drive any car in iRacing once (it creates Documents/iRacing/paint/<car>/), or pass --root.")
        sys.exit(1)
    root = roots[0]
    paint = root / "paint"
    result = {"iracing_dir": str(root), "paint_dir": str(paint), "onedrive": "onedrive" in str(root).lower(),
              "cars": [], "customer_id_candidates": []}

    strong, weak = collections.Counter(), collections.Counter()
    for f in paint.iterdir():
        m = PAINT_RX.match(f.name)
        if f.is_file() and m and m.group(1).lower() in ("helmet", "suit"):
            strong[m.group(2)] += 1
    cars = []
    for d in paint.iterdir():
        if not d.is_dir():
            continue
        if args.car and args.car.lower() not in d.name.lower():
            continue
        files = []
        ids = set()
        for f in d.iterdir():
            m = PAINT_RX.match(f.name)
            if m:
                files.append(f.name)
                ids.add(m.group(2))
        for i in ids:
            weak[i] += 1
        cars.append({"folder": d.name, "path": str(d), "mtime": d.stat().st_mtime, "paint_files": sorted(files)})
    cars.sort(key=lambda c: -c["mtime"])
    result["cars"] = cars
    cand = []
    for cid, n in strong.most_common():
        cand.append({"id": cid, "evidence": f"helmet/suit files in root paint folder ({n})"})
    for cid, n in weak.most_common(5):
        if cid not in strong:
            cand.append({"id": cid, "evidence": f"paint files in {n} car folder(s)"})
    result["customer_id_candidates"] = cand

    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(f"iRacing folder: {root}")
    if result["onedrive"]:
        print("  WARNING: Documents is inside OneDrive. iRacing support says OneDrive backup of this folder causes problems;"
              " if paints fail to load, stop OneDrive backing up Documents.")
    print(f"paint folder:   {paint}\n")
    print("car folders (most recently used first):")
    for c in cars[:40]:
        shown = ", ".join(c["paint_files"][:6]) + (" ..." if len(c["paint_files"]) > 6 else "")
        print(f"  {c['folder']:<32} {shown}")
    if len(cars) > 40:
        print(f"  ... {len(cars) - 40} more (use --car to filter)")
    print("\ncustomer ID candidates (confirm with the user):")
    for c in cand or [{"id": "?", "evidence": "no paint files yet"}]:
        print(f"  {c['id']:<10} {c['evidence']}")


if __name__ == "__main__":
    main()
