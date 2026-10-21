"""
invoice_zip.py  --  Zip handoff for the monthly-invoice skill.
==============================================================
The caching bridge between Windows and the sandbox serves brand-new filenames
correctly but can serve STALE/TRUNCATED data for paths it has already cached
(i.e. files edited in place outside the sandbox). A zip is a single fresh blob,
so it always transfers whole. Use it as the boundary whenever invoices have
been edited on the Windows side.

Two modes
---------
  pack    Zip a folder of PDFs into one archive (what you drop in for the
          sandbox to process). Each PDF is integrity-checked first.

  unpack  Extract an archive into a folder, verifying every member lands
          intact (ends in %%EOF and parses). Corrupt members are reported
          and the exit code is non-zero.

Usage
-----
    python invoice_zip.py pack   --src "<...>/Working files/New" --zip "<...>/new.zip"
    python invoice_zip.py unpack --zip "<...>/new.zip" --dst "<...>/Working files/New"

Requires invoice_io.py on the same path.
"""
import argparse, os, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import invoice_io as iio  # noqa: E402


def pack(src, zpath):
    pdfs = [f for f in sorted(os.listdir(src)) if f.lower().endswith('.pdf')]
    if not pdfs:
        sys.exit(f"No PDFs found in {src}")
    bad = []
    for f in pdfs:
        p = os.path.join(src, f)
        if not iio.is_pdf_intact(p):
            bad.append(f)
    if bad:
        print("Refusing to pack -- these files are not intact on disk:")
        for f in bad:
            print("   ", f)
        print("Re-save/re-copy them first (they may be half-written).")
        sys.exit(2)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in pdfs:
            z.write(os.path.join(src, f), f)
    # verify the archive we just wrote
    with zipfile.ZipFile(zpath) as z:
        broken = z.testzip()
        if broken is not None:
            sys.exit(f"Archive verify failed on member: {broken}")
        n = len([m for m in z.namelist() if m.lower().endswith('.pdf')])
    print(f"Packed {n} PDFs -> {zpath}")


def unpack(zpath, dst):
    os.makedirs(dst, exist_ok=True)
    with zipfile.ZipFile(zpath) as z:
        broken = z.testzip()
        if broken is not None:
            sys.exit(f"Archive is corrupt (member: {broken}). Re-create the zip.")
        members = [m for m in z.namelist() if m.lower().endswith('.pdf')]
        ok = bad = 0
        for m in members:
            data = z.read(m)
            out = os.path.join(dst, os.path.basename(m))
            # write with verify-after-write (atomic + retry)
            iio.safe_write_bytes(data, out, require_eof=True)
            if iio.is_pdf_intact(out):
                print(f"OK    {os.path.basename(m)}")
                ok += 1
            else:
                print(f"BAD   {os.path.basename(m)}  (failed integrity gate after extract)")
                bad += 1
    print(f"\nExtracted {ok} intact, {bad} bad -> {dst}")
    if bad:
        sys.exit(3)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='mode', required=True)
    p = sub.add_parser('pack');   p.add_argument('--src', required=True); p.add_argument('--zip', required=True, dest='zip')
    u = sub.add_parser('unpack'); u.add_argument('--zip', required=True, dest='zip'); u.add_argument('--dst', required=True)
    args = ap.parse_args()
    if args.mode == 'pack':
        pack(args.src, args.zip)
    else:
        unpack(args.zip, args.dst)


if __name__ == '__main__':
    main()
