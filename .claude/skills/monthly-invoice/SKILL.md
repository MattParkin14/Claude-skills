---
name: monthly-invoice
description: >
  Process monthly IT invoices for Tasti: stamp PDFs with draggable annotations
  (budget code, description, and signature), update the it_budget.csv with
  correct billing months, and produce Ext_PO.csv, New_PO.csv, and Other.csv
  reports. Use this skill whenever the user says anything like "process this
  month's invoices", "stamp the invoices", "run the invoice processing",
  "do the monthly invoices", or "invoices are ready to process". Also use it
  if the user asks to re-run stamping, regenerate the CSV reports, or update
  the budget CSV with new months. Trigger even if the user phrases it casually
  like "the invoices are in" or "can you do the invoices again".
---

# Monthly Invoice Processing

This skill processes IT invoices for Tasti Products Ltd each month. Here is the full workflow.

## Folder layout (always the same)

```
Z:\Claude\Invoicing\
  Working files\        ← drop new PDFs here before running
    New\                ← output: stamped, matched to budget, no PO
    PO\                 ← output: had a PO (filename gets _<PO> appended)
    Other\              ← output: signature only, review manually
  it_budget.csv         ← budget reference (updated in-place)
  signature.png         ← approval signature stamped on every PDF
  Ext_PO.csv            ← output: invoices with existing PO numbers
  New_PO.csv            ← output: invoices matched + stamped
  Other.csv             ← output: invoices that couldn't be matched
```

## Before you start

1. Confirm with the user that all new invoices are in `Working files\`.
2. Check that `signature.png` exists in the Invoicing folder.
3. Check that `it_budget.csv` is present and up to date.

If any are missing, ask the user to add them before proceeding.

## Step 1 — Discover the Linux mount path

The bash shell uses a different path from Windows. Run this to find the mount:

```bash
ls /sessions/*/mnt/ 2>/dev/null | head -5
# The Invoicing folder will be at something like:
# /sessions/beautiful-wonderful-rubin/mnt/Invoicing/
```

Set variables (adjust session name as needed):
```bash
MNT="/sessions/<session-name>/mnt"
BASE="$MNT/Invoicing/Working files"
SIG="$MNT/Invoicing/signature.png"
CSV="$MNT/Invoicing/it_budget.csv"
OUT="$MNT/Invoicing"
SCRIPTS="<skill_dir>/scripts"
```

To find your skill directory path:
```bash
find /sessions -name "stamp_annot.py" 2>/dev/null
```

## Step 2 — Install dependencies (first time or if missing)

```bash
pip install pypdf pdfplumber pillow pikepdf --break-system-packages -q
```

## Step 3 — Stamp the PDFs

```bash
python "$SCRIPTS/stamp_annot.py" \
  --base "$BASE" \
  --sig  "$SIG" \
  --csv  "$CSV"
```

This will:
- Strip any previous overlay AND any previous FreeText/Stamp annotations from each PDF (safe to re-run)
- Match each invoice to `it_budget.csv` by vendor name and keywords
- Add a draggable blue-text FreeText annotation (no border or background box) with the budget Vendor name (only for invoices without a PO)
- Add a draggable blue-text FreeText annotation (no border or background box) with the budget Code
- Add a draggable blue-text FreeText annotation (no border or background box) with the budget Text description
- Vendor, Code, and Text are stacked one below the other in that order; lines may shift horizontally relative to each other so the group fits into header whitespace
- Add a draggable Stamp annotation with the signature at its original resolution and a transparent background (alpha derived from luminance if the PNG has none)
- All stamps are placed only in empty space — never over text, images, logos, or graphics (vector objects and images count as occupied)
- Entire table regions (detected via pdfplumber find_tables) count as occupied — stamps never go inside a table, even in empty cells
- Stamps are never placed within 2 cm of the top edge or 3 cm of the side edges; central positions are preferred
- The signature is displayed at ~16.5 pt high (half natural size)
- If a PO number is already present in the invoice, stamp that instead of the budget code/text

The script prints `OK` or `FAIL` for each file. Note any failures for the user.

## Step 4 — Update CSV and generate reports

```bash
python "$SCRIPTS/update_csv_reports.py" \
  --base "$BASE" \
  --csv  "$CSV" \
  --out  "$OUT"
```

This will:
- Scan each PDF for its billing month (e.g. "Apr26")
- Replace any `???26` placeholders in `it_budget.csv` Text column with the real month
- Sort the processed PDFs into three subfolders of `Working files\`:
  - `New\`   — matched to budget and stamped with code + text, no PO
  - `PO\`    — a PO number was found (document text or filename); `_<PO>` is appended to the filename if not already present
  - `Other\` — only the signature was stamped (no match, no PO)
- Produce `Ext_PO.csv`, `New_PO.csv`, and `Other.csv` (rows correspond to the PO / New / Other folders; File Name shows the final, possibly renamed path)

Note: because PDFs are moved into subfolders, re-running either script requires moving the PDFs back into `Working files\` first.

## Step 5 — (LATER, ON REQUEST) Move New -> PO after the user adds PO numbers

This is a SECOND PASS run days later, when the user says something like
"run the next step", "I've added the POs", "move the new invoices to PO".
By then the user has typed PO numbers into the stamped annotations on the PDFs
in `Working files\New` (normally replacing the code/text stamp, e.g.
"Gans - SQL Database Monitoring..." becomes "PO27008101").

### IMPORTANT — the caching bridge

`Z:` is a healthy local drive, but the Windows<->sandbox bridge can serve STALE
or TRUNCATED copies of files that were edited OUTSIDE the sandbox (which is
exactly what Step 5 files are). Symptoms: PDFs read back missing their final
`%%EOF`, folder listings come back empty, re-writing the same path fails.
Brand-new filenames always transfer correctly, so the fix is a zip handoff plus
an integrity gate. The hardened scripts below handle both.

### Preferred: zip handoff

Ask the user to zip the `New` folder on their PC (right-click -> Send to ->
Compressed folder) and drop the zip in `Working files\`. Then:

```bash
# unpack the delivered zip, verifying every file lands intact
python "$SCRIPTS/invoice_zip.py" unpack --zip "$BASE/new.zip" --dst "$BASE/New"

# move New -> PO with integrity gate + robust reads/moves
python "$SCRIPTS/move_new_to_po.py" --base "$BASE"
```

`invoice_zip.py pack` (run on the user's side, or here) refuses to build a zip
if any PDF is half-written, catching corruption before the handoff.

### Direct run (if files are already in New and read cleanly)

```bash
python "$SCRIPTS/move_new_to_po.py" --base "$BASE"
```

For each PDF in `Working files\New` this will:
- INTEGRITY GATE each file first (must end in `%%EOF` and parse). Files that
  fail are printed as `CORRUPT` and left untouched — never moved blindly. Tell
  the user to re-deliver those via the zip handoff.
- Find the PO number (annotation stamps first via pikepdf, then document text,
  then filename).
- Append `_<PO>` to the file name (skipped if already present).
- Move the file to `Working files\PO` with an atomic rename + retry.

Files with no detectable PO are left in `New` and listed. If the folder listing
comes back empty but you know files are there (stale-cache symptom), pass a
manifest: `--manifest names.txt` (one New/ PDF name per line).

The hardened scripts require `invoice_io.py` and `invoice_zip.py` to sit in the
same `scripts/` folder (they already do in this package).

## Step 6 — Review and report back

After both scripts complete, tell the user:
1. How many PDFs were stamped successfully
2. How many ended up in each category (Ext_PO / New_PO / Other)
3. Any failures or edge cases (e.g. invoices where price shows N/A, or vendor couldn't be matched)
4. Provide clickable links to the three output CSV files

Example report:
```
✓ 27 invoices stamped, 2 failed

Ext_PO:  6 invoices (had existing PO numbers)
New_PO: 19 invoices (matched to budget and stamped)
Other:   2 invoices (couldn't match — review manually)

Review the CSV files:
- Z:\Claude\Invoicing\Ext_PO.csv
- Z:\Claude\Invoicing\New_PO.csv
- Z:\Claude\Invoicing\Other.csv

Issues to check:
- Spark invoice: price shows $21.00 — may need manual update
- INV_018606: unmatched (vendor domain has no spaces) — check manually
```

## Key technical notes (if you need to debug)

**Vendor matching**: Scores each budget row against invoice text. Vendor name in text = 20 pts (also matched with spaces removed, e.g. digitalisland.co.nz), in filename = 15 pts; parenthetical vendor alias (e.g. "FastCom (Unisphere)" matches "Unisphere") = 18 pts; each keyword match = 3 pts; each Reference-line token matching the row Text = 8 pts (the invoice's Reference line is the strongest signal for vendors with multiple services); `[aliases: ...]` tags in the Notes column = 15 pts each. Threshold = 15. Ties at the top score return multiple rows.

**Multi-code splits**: If multiple rows tie and all carry `$1/N` in Notes (e.g. Spark's three codes), the invoice subtotal is split N ways and one line is stamped per code: `$3,122.85 /3 = 1,040.95 - 72210-IT-X - ...`. The CSV reports get one row per code with the split price.

**Vendor stamp**: shows the full Vendors value including parenthetical, e.g. "Dropsuite (Unisphere)".

**Billing months**: date ranges like "From Date: July 1, 2026 ... To Date: September 30, 2026" become "Jul26 to Sep26" and fill `???26 to ???26` placeholders pairwise. Placeholders are only updated in budget rows the invoice actually MATCHED (no vendor-wide guessing). Stamps fill `???26` for display on first run even before the CSV is updated.

**PO detection**: Looks for patterns like "Purchase Order No: 12345", "PO: 27007578", or "_PO27007578" in the filename. If a PO is found, stamps the PO number instead of the budget code/text.

**Month extraction**: Tries date formats like "28 Apr 2026", "30/04/2026", or "Work conducted in April, 2026". The `???26` placeholder in the CSV means the month wasn't known when the budget was created.

**CSV NUL bytes**: The budget CSV sometimes contains NUL bytes from Excel exports. The scripts handle this automatically with `raw.replace(b'\x00', b'')`.

**Coordinate system**: pdfplumber uses y-down (top-left origin); PDF annotations use y-up (bottom-left). The `to_pdf_rect()` function converts between them.

**Re-running safely**: The stamp script strips any previous baked overlay before re-stamping, so it's safe to run multiple times on the same files.

**Annotation type**: All text stamps are PDF FreeText annotations; the signature is a Stamp annotation with a custom appearance stream. Both are draggable and editable in any PDF viewer that supports annotations (e.g. Adobe Acrobat, PDF Expert).

**Caching bridge / integrity (Step 5)**: Files edited outside the sandbox reach
the scripts through a caching layer that can serve stale/truncated data for a
previously-seen path (missing `%%EOF`, empty listings, failed rewrites). Defenses
live in `invoice_io.py`: `is_pdf_intact()` (ends in `%%EOF` AND parses in
pikepdf), `safe_write_bytes()`/`safe_copy()` (verify-after-write + retry),
`safe_move()` (os.replace rename, never cp/mv — the bridge's same-inode quirk
breaks cp/mv), and `stage_local()` (copy to local disk, verified, before
parsing). `invoice_zip.py` provides the fresh-blob handoff that sidesteps the
stale cache entirely. Reads use pikepdf, which recovers slightly-malformed
trailers that make pypdf/pdfplumber throw "stream ended unexpectedly".
