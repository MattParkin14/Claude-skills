#!/usr/bin/env python3
"""Install a build into the iRacing paint folder, backing up whatever is there first.

Usage:
  python install_paint.py BUILD_DIR --paint-dir PAINT_DIR --car CAR_FOLDER --customer-id ID [--force] [--dry-run]
  python install_paint.py --restore [STAMP] --paint-dir PAINT_DIR --car CAR_FOLDER --customer-id ID
  python install_paint.py --list-backups --paint-dir PAINT_DIR --car CAR_FOLDER

What it does on install:
  1. refuses a build whose report.json has errors (unless --force)
  2. moves the existing car_<id>.tga, car_spec_<id>.tga/.mip, car_num_<id>.tga, car_decal_<id>.tga into
     <iRacing>/paint_backups/<car>/<timestamp>/  (outside the paint folder, so Trading Paints won't touch it)
  3. copies the build's car_*.tga files in
  4. leaves no stale car_spec_<id>.mip behind, so the sim rebuilds the spec map from the new TGA
Then in iRacing: open the car (test drive or Paint Shop) and press Ctrl+R to reload paints.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

MANAGED = ["car_{id}.tga", "car_spec_{id}.tga", "car_spec_{id}.mip", "car_num_{id}.tga", "car_decal_{id}.tga"]


def backup_root(paint_dir: Path, car: str) -> Path:
    return paint_dir.parent / "paint_backups" / car


def snapshots(broot: Path):
    def key(p):
        parts = p.name.split("-")
        return (parts[0], parts[1] if len(parts) > 1 else "", int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1)
    return sorted((p for p in broot.glob("*") if p.is_dir()), key=key) if broot.exists() else []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("build", nargs="?")
    ap.add_argument("--paint-dir", required=True)
    ap.add_argument("--car", required=True, help="car folder name inside paint/, e.g. 'mx5 mx52016'")
    ap.add_argument("--customer-id")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--create", action="store_true", help="create the car folder if missing")
    ap.add_argument("--restore", nargs="?", const="latest")
    ap.add_argument("--list-backups", action="store_true")
    args = ap.parse_args()

    paint = Path(args.paint_dir)
    car_dir = paint / args.car
    broot = backup_root(paint, args.car)

    if args.list_backups:
        for b in snapshots(broot):
            print(f"  {b.name}: {', '.join(sorted(p.name for p in b.iterdir()))}")
        return
    if not args.customer_id or not args.customer_id.isdigit():
        sys.exit("--customer-id (numeric) is required")
    cid = args.customer_id
    names = [n.format(id=cid) for n in MANAGED]

    if not car_dir.is_dir():
        if args.create and not args.dry_run:
            car_dir.mkdir(parents=True)
        elif not args.create:
            sys.exit(f"{car_dir} does not exist. Drive the car once in iRacing (that creates the folder) or pass --create.")

    def backup_existing():
        present = [car_dir / n for n in names if (car_dir / n).exists()]
        if not present:
            print("  nothing to back up")
            return None
        stamp = time.strftime("%Y%m%d-%H%M%S")
        dest = broot / stamp
        n = 2
        while dest.exists():  # never merge into an existing snapshot
            dest = broot / f"{stamp}-{n}"
            n += 1
        print(f"  backing up {len(present)} file(s) -> {dest}")
        if not args.dry_run:
            dest.mkdir(parents=True, exist_ok=True)
            for p in present:
                shutil.move(str(p), str(dest / p.name))
        return dest

    if args.restore:
        snaps = snapshots(broot)
        if not snaps:
            sys.exit(f"no backups in {broot}")
        snap = snaps[-1] if args.restore == "latest" else broot / args.restore
        if not snap.is_dir():
            sys.exit(f"backup {snap} not found; use --list-backups")
        print(f"restoring {snap.name} into {car_dir}")
        backup_existing()
        for p in snap.iterdir():
            print(f"  {p.name}")
            if not args.dry_run:
                shutil.copy2(p, car_dir / p.name)
        print("done. In iRacing press Ctrl+R to reload paints.")
        return

    if not args.build:
        sys.exit("give a BUILD_DIR (e.g. builds/v03) or --restore")
    build = Path(args.build)
    rep = build / "report.json"
    if rep.exists():
        r = json.loads(rep.read_text())
        if r.get("errors") and not args.force:
            sys.exit(f"{build.name} has {r['errors']} placement error(s) — fix them or pass --force")
        if r.get("customer_id") and str(r["customer_id"]) != cid:
            sys.exit(f"build was made for customer ID {r['customer_id']}, not {cid}. Rebuild with the right ID.")
    files = sorted(build.glob(f"car*_{cid}.tga"))
    if not files:
        sys.exit(f"no car*_{cid}.tga files in {build}")
    print(f"installing {build.name} -> {car_dir}")
    backup_existing()
    for f in files:
        print(f"  copy {f.name}")
        if not args.dry_run:
            shutil.copy2(f, car_dir / f.name)
    mip = car_dir / f"car_spec_{cid}.mip"
    if mip.exists() and not args.dry_run:
        mip.unlink()
    print("\ndone. Now in iRacing: open this car in a test drive (or the Paint Shop) and press Ctrl+R.")
    print("Screenshots to send back: front 3/4 L+R, rear 3/4 L+R, both profiles, top, plus close-ups of anything wrong.")
    print(f"Undo with: install_paint.py --restore --paint-dir \"{paint}\" --car \"{args.car}\" --customer-id {cid}")


if __name__ == "__main__":
    main()
