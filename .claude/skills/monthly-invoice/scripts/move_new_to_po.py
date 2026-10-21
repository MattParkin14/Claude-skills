"""
Monthly Invoice Step 2 (HARDENED) -- move_new_to_po.py
======================================================
Run AFTER the user has created PO numbers and typed them into the stamped
annotations of the PDFs in Working files/New.

For each PDF it finds a PO number (annotation stamps first, then document text,
then filename), appends _<PO> to the name, and moves it to Working files/PO.
Files with no PO are left in New and reported.

What's different from the original
----------------------------------
This version is defensive against the Windows<->sandbox caching bridge that can
serve stale / truncated copies of externally-edited files:

  * Reads PDFs with pikepdf (recovers broken trailers) via invoice_io.
  * INTEGRITY GATE: every file is checked (ends in %%EOF and parses) before it
    is trusted. A file that fails is reported and skipped, never moved blindly.
  * Does NOT trust os.listdir alone. It builds a filename manifest and, if the
    listing looks suspiciously empty, retries; you can also pass --manifest.
  * Moves with os.replace (rename) + retry, never cp/mv (whose same-inode
    check the bridge breaks).

Usage
-----
    python move_new_to_po.py --base "<...>/Working files"
    python move_new_to_po.py --base "<...>/Working files" --manifest names.txt

Requires invoice_io.py on the same path (PYTHONPATH or same folder).
"""
import argparse, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import invoice_io as iio  # noqa: E402

PO_PATTERNS = [
    r'\bPO[:\s\-]*([0-9]{5,})\b',
    r'Purchase\s+Order\s*(?:No\.?|Number|#)?\s*[:\-]?\s*((?:PO)?[0-9]{5,})',
    r'\bP\.?O\.?\s*(?:No\.?|Number|#)\s*[:\-]?\s*((?:PO)?[0-9]{5,})',
]


def find_po(strings):
    for s in strings:
        if not s:
            continue
        for pat in PO_PATTERNS:
            m = re.search(pat, s, re.IGNORECASE)
            if m:
                v = m.group(1)
                return v if v.upper().startswith('PO') else 'PO' + v
    return None


def body_text(path):
    """Best-effort body text (only used as a fallback for PO detection)."""
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n".join(p.extract_text() or '' for p in pdf.pages[:2])
    except Exception:
        return ''


def list_new_pdfs(new_dir, manifest=None):
    """Return PDF filenames in New/. Guards against stale-empty listings."""
    if manifest:
        with open(manifest, encoding='utf-8') as fh:
            names = [ln.strip() for ln in fh if ln.strip().lower().endswith('.pdf')]
        return names
    names = []
    for _ in range(4):
        names = sorted(f for f in os.listdir(new_dir) if f.lower().endswith('.pdf'))
        if names:
            break
        time.sleep(0.7)  # listing may be a stale-empty cache; give it a beat
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True, help='Path to Working files/ folder')
    ap.add_argument('--manifest', help='Optional text file: one New/ PDF name per line')
    args = ap.parse_args()

    NEW = os.path.join(args.base, 'New')
    PO = os.path.join(args.base, 'PO')
    if not os.path.isdir(NEW):
        sys.exit(f"No 'New' folder at {NEW} -- run the main processing first.")
    os.makedirs(PO, exist_ok=True)

    names = list_new_pdfs(NEW, args.manifest)
    if not names:
        sys.exit("No PDFs found in New/. If you know they're there, the folder "
                 "listing may be stale -- pass --manifest with the filenames.")

    moved = left = corrupt = 0
    for fname in names:
        src = os.path.join(NEW, fname)
        if not os.path.exists(src):
            print(f"MISS   {fname}  (listed but not readable -- stale cache?)")
            corrupt += 1
            continue

        # INTEGRITY GATE -- never process a truncated/half-synced file
        if not iio.is_pdf_intact(src):
            print(f"CORRUPT {fname}  (no %%EOF / won't parse -- re-copy this file, "
                  f"ideally via the zip handoff)")
            corrupt += 1
            continue

        # Stage locally, then read from the clean local copy
        try:
            local = iio.stage_local(src)
            texts = iio.annotation_texts(local)
        except iio.IntegrityError as e:
            print(f"CORRUPT {fname}  ({e})")
            corrupt += 1
            continue

        po = find_po(texts + [body_text(local), fname])
        if not po:
            print(f"LEFT   {fname}  (no PO number found)")
            left += 1
            continue

        stem, ext = os.path.splitext(fname)
        new_name = fname if po.lower() in fname.lower() else f"{stem}_{po}{ext}"
        dst = os.path.join(PO, new_name)
        if os.path.exists(dst):
            i, s2, e2 = 2, *os.path.splitext(new_name)
            while os.path.exists(os.path.join(PO, f"{s2}({i}){e2}")):
                i += 1
            dst = os.path.join(PO, f"{s2}({i}){e2}")

        try:
            iio.safe_move(src, dst)
            # confirm the file that landed is intact
            if not iio.is_pdf_intact(dst):
                raise iio.IntegrityError("moved file failed integrity gate")
            print(f"MOVED  {fname}  ->  PO/{os.path.basename(dst)}")
            moved += 1
        except iio.IntegrityError as e:
            print(f"FAIL   {fname}: {e}")
            left += 1

    print(f"\n{moved} moved to PO, {left} left in New, {corrupt} corrupt/unreadable")
    if corrupt:
        print("Corrupt files were NOT moved. Re-deliver them (zip handoff "
              "recommended) and re-run.")


if __name__ == '__main__':
    main()
