"""
Monthly Invoice CSV Updater — update_csv_reports.py
====================================================
1. Updates it_budget.csv replacing ??? placeholders with correct billing month
2. Creates Ext_PO.csv  — invoices that already had a PO number in the document
3. Creates New_PO.csv  — invoices stamped with a budget code + text
4. Creates Other.csv   — invoices that couldn't be matched

Usage:
    python update_csv_reports.py --base <working_files_dir> --csv <it_budget.csv> --out <output_dir>
"""
import argparse, csv, re, os, io, pdfplumber
from datetime import datetime

ap = argparse.ArgumentParser()
ap.add_argument('--base', required=True, help='Path to Working files/ folder')
ap.add_argument('--csv',  required=True, help='Path to it_budget.csv')
ap.add_argument('--out',  required=True, help='Output directory for the 3 CSV files')
args = ap.parse_args()
BASE    = args.base.rstrip('/') + '/'
CSV_IN  = args.csv
OUT_DIR = args.out.rstrip('/') + '/'

MONTHS_ABBR = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
MONTHS_FULL = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']

STOPWORDS = {'the','and','for','in','of','to','a','an','is','are','with',
             'charges','yearly26','yearly','annual','year25','year26',
             'support','service','services','monthly','license','licensing'}

def load_budget(path):
    with open(path, 'rb') as f:
        raw = f.read().replace(b'\x00', b'')
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig', errors='replace'))))

def has_po_in_doc(text, filename):
    return bool(re.search(r'\bPO\d{5,}', text))

NARROW_PO_PATTERNS = [
    r'Purchase\s+Order\s+(?:No\.?|Number|#)?\s*[:\-]?\s*([A-Z0-9]{4,20})',
    r'\bP\.?O\.?\s+(?:No\.?|Number|#)\s*[:\-]?\s*([A-Z0-9]{4,20})',
    r'PO\s+No[\.:]\s*([A-Z0-9]{4,20})',
    r'Your\s+Order\s+([A-Z0-9]{4,20})',
    r'\bPO\s*[:\-]\s*([A-Z0-9]{4,20})',
]
def narrow_po(text, filename):
    for pat in NARROW_PO_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            v = m.group(1).strip().rstrip('.')
            if re.search(r'\d', v) and len(v) >= 4:
                return v
    m = re.search(r'[_\-](PO[A-Z0-9]{4,})', filename, re.IGNORECASE)
    return m.group(1) if m else None

def extract_reference(text):
    """The invoice's Reference line is the strongest tagging signal for
    vendors that send several invoices for different services."""
    m = re.search(r'Reference\s*:?\s*\n\s*([^\n]+)', text)
    if not m:
        m = re.search(r'Reference\s*:\s*([^\n]+)', text)
    return m.group(1).strip() if m else ''

def norm_vendor_parts(vendor):
    full = re.sub(r'\s+', ' ', vendor or '').strip()
    base = re.sub(r'\s*\([^)]*\)', '', full).strip()
    parens = [a.strip() for a in re.findall(r'\(([^)]*)\)', full) if a.strip()]
    return full, base, parens

def row_aliases(row):
    """Optional [aliases: a, b] tag in the Notes column adds match keywords
    without changing the stamped text."""
    notes = row.get('Notes') or ''
    m = re.search(r'\[aliases?:\s*([^\]]+)\]', notes, re.I)
    return [a.strip() for a in m.group(1).split(',') if a.strip()] if m else []

def _row_kws(csvtext):
    return [w.lower() for w in re.split(r'[\s\-,+&]+', csvtext)
            if len(w) > 3 and w.lower() not in STOPWORDS and not w.startswith('???')]

def score_row(row, txt, fname, ref_l, txt_nospace):
    vendor  = row.get('Vendors','') or ''
    code    = row.get('Code','').strip()
    csvtext = row.get('Text','').strip()
    if not vendor.strip() or not code: return 0
    full, base, parens = norm_vendor_parts(vendor)
    bl = base.lower()
    score = 0
    if bl and bl in txt:                                   score += 20
    elif bl and bl.replace(' ','') in txt_nospace:         score += 20
    elif bl and bl in fname:                               score += 15
    for al in parens:
        a = al.lower()
        if a and (a in txt or a.replace(' ','') in txt_nospace):
            score += 18; break
    for al in row_aliases(row):
        a = al.lower()
        if a and (a in txt or (ref_l and a in ref_l)):
            score += 15
    kws = _row_kws(csvtext)
    for kw in kws:
        if kw in txt: score += 3
    if ref_l:
        # Reference tokens match the row text directly (no STOPWORDS filter:
        # words like "licensing" are weak in body text but strong in a Reference)
        row_tokens = {w.lower() for w in re.split(r'[\s\-,+&]+', csvtext)
                      if len(w) > 3 and not w.startswith('???')}
        for t in set(re.split(r'[\s\-,+&]+', ref_l)):
            if len(t) > 3 and t in row_tokens:
                score += 8
    return score

def match_budget(text, filename, budget):
    """Returns a LIST of matched budget rows. Usually one; multiple when
    several rows tie at the top score (e.g. Spark's three $1/3 codes).
    Duplicate (Code, Text) rows are collapsed to one."""
    txt, fname  = text.lower(), filename.lower()
    txt_nospace = re.sub(r'\s+', '', txt)
    ref_l       = extract_reference(text).lower()
    scored = [(score_row(r, txt, fname, ref_l, txt_nospace), r) for r in budget]
    best = max((sc for sc, _ in scored), default=0)
    if best < 15: return []
    top, seen = [], set()
    for sc, r in scored:
        if sc != best: continue
        k = (r['Code'].strip(), r['Text'].strip())
        if k in seen: continue
        seen.add(k); top.append(r)
    return top

def extract_invoice_month(text):
    # date ranges first: "From Date: July 1, 2026 ... To Date: September 30, 2026"
    m = re.search(r'From\s+Date:\s*([A-Za-z]+)\s+\d{1,2},?\s*(\d{4})'
                  r'.*?To\s+Date:\s*([A-Za-z]+)\s+\d{1,2},?\s*(\d{4})',
                  text, re.IGNORECASE | re.DOTALL)
    if m:
        m1, y1 = m.group(1)[:3].capitalize(), m.group(2)[-2:]
        m2, y2 = m.group(3)[:3].capitalize(), m.group(4)[-2:]
        if m1 in MONTHS_ABBR and m2 in MONTHS_ABBR:
            return f"{m1}{y1} to {m2}{y2}"
    m = re.search(
        r'\b(\d{1,2})\s*(' + '|'.join(MONTHS_ABBR + MONTHS_FULL) + r')[a-z]*\s*(\d{4})',
        text, re.IGNORECASE)
    if m:
        mon = m.group(2)[:3].capitalize()
        if mon in MONTHS_ABBR:
            return f"{mon}{m.group(3)[-2:]}"
    m = re.search(r'\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})', text)
    if m:
        try:
            mnum, y = int(m.group(2)), m.group(3)
            if 1 <= mnum <= 12:
                return f"{MONTHS_ABBR[mnum-1]}{y[-2:]}"
        except Exception: pass
    m = re.search(
        r'(?:in|for|period)[:\s]+(' + '|'.join(MONTHS_FULL) + r')[,\s]+(\d{4})',
        text, re.IGNORECASE)
    if m:
        mon = m.group(1)[:3].capitalize()
        if mon in MONTHS_ABBR:
            return f"{mon}{m.group(2)[-2:]}"
    return None

def fill_month(text, month):
    """Substitute ???26 placeholders with the real month(s) for DISPLAY,
    so first-run stamps never show '???26'. Handles ranges pairwise."""
    if not month or '???' not in text: return text
    if ' to ' in month:
        out = text
        for p in month.split(' to '):
            new = re.sub(r'\?\?\?(?=\d{2}\b)', p[:3], out, count=1)
            if new == out: break
            out = new
        return out
    return re.sub(r'\?\?\?(?=\d{2}\b)', month[:3], text)

def extract_price(text):
    patterns = [
        r'Subtotal\s+excl\.?\s*GST\s*\$?\s*([0-9,]+\.\d{2})',
        r'Amount\s*\(Excl\.?\s*GST\)\s+([0-9,]+\.?\d*[-]?)',
        r'Subtotal\s*\$?\s*([0-9,]+\.?\d*)',
        r'Sub\s*Total[:\s]+\$?\s*([0-9,]+\.?\d*)',
        r'Net\s+Sale\s+Amount\s*\$?\s*([0-9,]+\.?\d*)',
        r'Monthly\s+Charges\s+excl\.?\s*GST\s*\$?\s*([0-9,]+\.?\d*)',
        r'Total\s+excl?\.?\s*GST[:\s]+\$?\s*([0-9,]+\.?\d*)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw = m.group(1).replace(',','').strip()
            neg = raw.endswith('-'); raw = raw.rstrip('-')
            try:
                val = float(raw)
                return -val if neg else val
            except Exception: pass
    return None

def extract_vendor_name(text, csv_match):
    if csv_match:
        return re.sub(r'\s+', ' ', csv_match.get('Vendors','')).strip()
    for line in text.split('\n'):
        line = line.strip()
        if 4 < len(line) < 60 and not re.search(r'^\d|GST|TAX|Invoice', line, re.I):
            return line
    return 'Unknown'

def process_all(budget):
    results = []
    for fname in sorted(os.listdir(BASE)):
        if not fname.lower().endswith('.pdf'): continue
        src = os.path.join(BASE, fname)
        try:
            with pdfplumber.open(src) as pdf:
                text = "\n".join(p.extract_text() or '' for p in pdf.pages[:2])
        except:
            text = ""
        po_in_doc  = has_po_in_doc(text, fname)
        matches    = match_budget(text, fname, budget)
        csv_match  = matches[0] if matches else None
        month      = extract_invoice_month(text)
        price      = extract_price(text)
        vendor     = extract_vendor_name(text, csv_match)
        po_val     = narrow_po(text, fname)
        if not po_val and po_in_doc:
            m = re.search(r'\bPO\d{5,}', text)
            po_val = m.group(0) if m else None
        if po_val or po_in_doc:
            category = 'Ext_PO'
        elif csv_match:
            category = 'New_PO'
        else:
            category = 'Other'
        n = len(matches)
        split = n > 1 and all(re.search(r'\$1/(\d+)', (r.get('Notes') or '')) for r in matches)
        entries = []
        for r in matches:
            entries.append({
                'code':  r['Code'].strip(),
                'text':  fill_month(r['Text'].strip(), month),
                'price': (price / n) if (split and price is not None) else price,
            })
        if not entries:
            entries = [{'code': '', 'text': '', 'price': price}]
        results.append({
            'fname': fname, 'category': category, 'vendor': vendor,
            'code': csv_match['Code'].strip() if csv_match else '',
            'text': csv_match['Text'].strip() if csv_match else '',
            'price': price, 'month': month, 'po_val': po_val,
            'match_rows': matches, 'entries': entries,
        })
        print(f"  {category:8s}  {fname[:55]}")
        print(f"             month={month}  price={price}  po={po_val}")
    return results

def update_budget_csv(budget_rows, invoice_data):
    """Fill ??? placeholders ONLY in the budget rows each invoice actually
    matched (plus identical twin rows). No vendor-wide guessing."""
    updated = 0
    for inv in invoice_data:
        month = inv.get('month')
        if not month: continue
        for row in inv.get('match_rows', []):
            old_t = row.get('Text','')
            targets = [r for r in budget_rows
                       if r.get('Code','').strip() == row.get('Code','').strip()
                       and r.get('Text','') == old_t]
            for r in targets:
                new_t = fill_month(old_t, month)
                if new_t != old_t:
                    r['Text'] = new_t
                    updated += 1
                    print(f"  CSV: {old_t!r}  ->  {new_t!r}")
    return updated

COLS = ['Vendor', 'Code', 'Text', 'Price (ex GST)', 'File Name']

def write_csv(path, category, invoice_data):
    subset = [inv for inv in invoice_data if inv['category'] == category]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for inv in subset:
            for e in inv['entries']:
                price_str = f"{e['price']:.2f}" if e['price'] is not None else 'N/A'
                w.writerow({
                    'Vendor': inv['vendor'], 'Code': e['code'], 'Text': e['text'],
                    'Price (ex GST)': price_str, 'File Name': inv['fname'],
                })
    print(f"  -> {path}  ({len(subset)} rows)")

def save_budget_csv(path, rows, original_fieldnames):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=original_fieldnames)
        w.writeheader()
        w.writerows(rows)

print("=== Analysing invoices ===")
budget = load_budget(CSV_IN)
with open(CSV_IN, 'rb') as f:
    raw = f.read().replace(b'\x00', b'')
original_fields = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig', errors='replace'))).fieldnames or [])

invoice_data = process_all(budget)

print("\n=== Updating it_budget.csv ===")
n_updated = update_budget_csv(budget, invoice_data)
save_budget_csv(CSV_IN, budget, original_fields)
print(f"  {n_updated} rows updated in it_budget.csv")

print("\n=== Sorting processed PDFs into New / PO / Other ===")
FOLDER_FOR = {'Ext_PO': 'PO', 'New_PO': 'New', 'Other': 'Other'}
for _sub in set(FOLDER_FOR.values()):
    os.makedirs(os.path.join(BASE, _sub), exist_ok=True)
for inv in invoice_data:
    folder = FOLDER_FOR[inv['category']]
    fname  = inv['fname']
    new_name = fname
    # PO files get _<PO> appended to the filename (unless already there)
    if inv['category'] == 'Ext_PO' and inv['po_val']:
        po = inv['po_val']
        if po.lower() not in fname.lower():
            stem, ext = os.path.splitext(fname)
            new_name = f"{stem}_{po}{ext}"
    src = os.path.join(BASE, fname)
    dst = os.path.join(BASE, folder, new_name)
    if os.path.exists(dst):
        stem, ext = os.path.splitext(new_name)
        i = 2
        while os.path.exists(os.path.join(BASE, folder, f"{stem}({i}){ext}")): i += 1
        dst = os.path.join(BASE, folder, f"{stem}({i}){ext}")
    try:
        os.replace(src, dst)
        inv['fname'] = folder + '/' + os.path.basename(dst)
        print(f"  {folder:6s} <- {os.path.basename(dst)}")
    except OSError as e:
        print(f"  !! could not move {fname}: {e}")

print("\n=== Writing 3 CSV report files ===")
write_csv(OUT_DIR + 'Ext_PO.csv',  'Ext_PO',  invoice_data)
write_csv(OUT_DIR + 'New_PO.csv',  'New_PO',  invoice_data)
write_csv(OUT_DIR + 'Other.csv',   'Other',   invoice_data)

cats = {'Ext_PO':0,'New_PO':0,'Other':0}
for inv in invoice_data: cats[inv['category']] += 1
print(f"\nSummary: Ext_PO={cats['Ext_PO']}  New_PO={cats['New_PO']}  Other={cats['Other']}")
