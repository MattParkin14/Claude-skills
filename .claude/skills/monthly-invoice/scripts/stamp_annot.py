"""
Monthly Invoice Stamper — stamp_annot.py
========================================
Adds moveable, editable annotations to each PDF in the Working files folder:
  • FreeText annotation (blue text, no border/box, draggable, editable) for budget Code + Text, or PO number
  • Stamp annotation with the signature image at original resolution with transparency (draggable)

Usage:
    python stamp_annot.py --base <working_files_dir> --sig <signature.png> --csv <it_budget.csv>
"""
import argparse, csv, re, os, io, pdfplumber
from PIL import Image as PILImage
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import FreeText
from pypdf.generic import (
    DictionaryObject, ArrayObject, NameObject, NumberObject, DecodedStreamObject,
)

ap = argparse.ArgumentParser()
ap.add_argument('--base', required=True, help='Path to Working files/ folder')
ap.add_argument('--sig',  required=True, help='Path to signature.png')
ap.add_argument('--csv',  required=True, help='Path to it_budget.csv')
args = ap.parse_args()
BASE  = args.base.rstrip('/') + '/'
SIG   = args.sig
CSV_P = args.csv

def load_budget(path):
    with open(path, 'rb') as f:
        raw = f.read().replace(b'\x00', b'')
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig', errors='replace'))))

STOPWORDS = {'the','and','for','in','of','to','a','an','is','are','with',
             'charges','yearly26','yearly','annual','year25','year26',
             'support','service','services','monthly','license','licensing'}

def extract_po(text, filename):
    patterns = [
        r'Purchase\s+Order\s+(?:No\.?|Number|#)?\s*[:\-]?\s*([A-Z0-9]{4,20})',
        r'\bP\.?O\.?\s+(?:No\.?|Number|#)\s*[:\-]?\s*([A-Z0-9]{4,20})',
        r'PO\s+No[\.:]\s*([A-Z0-9]{4,20})',
        r'Your\s+Order\s+([A-Z0-9]{4,20})',
        r'\bPO\s*[:\-]\s*([A-Z0-9]{4,20})',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            v = m.group(1).strip().rstrip('.')
            if re.search(r'\d', v) and len(v) >= 4:
                return v
    m = re.search(r'[_\-](PO[A-Z0-9]{4,})', filename, re.IGNORECASE)
    return m.group(1) if m else None

MONTHS_ABBR = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
MONTHS_FULL = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']

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

OVERLAY_RE = re.compile(
    rb'\nq\n0\.0 0\.0 [\d.]+ [\d.]+ re\nW\nn\n1 0 0 1 0 0 cm\n.*',
    re.DOTALL
)

def strip_overlay(stream_bytes):
    return OVERLAY_RE.sub(b'', stream_bytes)

def strip_overlays_from_pdf(src):
    reader = PdfReader(src)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i == 0:
            contents = page.get("/Contents")
            if contents is not None:
                obj = contents.get_object() if hasattr(contents, 'get_object') else contents
                if hasattr(obj, 'get_data'):
                    data = obj.get_data()
                    cleaned = strip_overlay(data)
                    if len(cleaned) < len(data):
                        new_obj = DecodedStreamObject.__new__(DecodedStreamObject)
                        new_obj.update({k: v for k, v in obj.items()
                                        if k not in ('/Length', '/Filter')})
                        new_obj.set_data(cleaned)
                        page[NameObject('/Contents')] = writer._add_object(new_obj)
        writer.add_page(page)
    tmp = src + '.clean'
    with open(tmp, 'wb') as f:
        writer.write(f)
    os.replace(tmp, src)

TOP_MARGIN  = 56.7   # 2 cm in points — never stamp closer to the top
SIDE_MARGIN = 85.0   # 3 cm in points — never stamp closer to the sides

def find_zone(words, pw, ph, need_w, need_h, margin=3):
    occ = [(w['x0']-margin, w['top']-margin, w['x1']+margin, w['bottom']+margin)
           for w in words]
    def free(x, y):
        for ox0,oy0,ox1,oy1 in occ:
            if x<ox1 and x+need_w>ox0 and y<oy1 and y+need_h>oy0: return False
        return True
    step = 4
    # Allowed x range respects the side margins; try central spots first
    xs = list(range(int(SIDE_MARGIN), int(pw - SIDE_MARGIN - need_w) + 1, step))
    xs.sort(key=lambda x: abs((x + need_w/2) - pw/2))
    # Scan top-to-bottom (starting below the top margin) over the whole
    # page so stamps land in genuinely empty space, never over text,
    # images, or graphics
    for y in range(int(TOP_MARGIN), int(ph - need_h - 4), step):
        for x in xs:
            if free(x, y): return x, y
    return SIDE_MARGIN, TOP_MARGIN

def find_stacked(words, pw, ph, widths, lh, gap=2, margin=3):
    """Place N stacked lines (top to bottom) on adjacent rows. The widest
    line anchors the search; the other lines may shift horizontally
    relative to it so the group can nestle into header whitespace, exactly
    like a human would place them. Returns [(x, y), ...] per line."""
    occ = [(w['x0']-margin, w['top']-margin, w['x1']+margin, w['bottom']+margin)
           for w in words]
    def free(x, y, need_w):
        for ox0,oy0,ox1,oy1 in occ:
            if x<ox1 and x+need_w>ox0 and y<oy1 and y+lh>oy0: return False
        return True
    step = 4
    n = len(widths)
    anchor = max(range(n), key=lambda i: widths[i])
    aw = widths[anchor]
    axs = list(range(int(SIDE_MARGIN), int(pw - SIDE_MARGIN - aw) + 1, step))
    axs.sort(key=lambda x: abs((x + aw/2) - pw/2))
    xall = [list(range(int(SIDE_MARGIN), int(pw - SIDE_MARGIN - widths[i]) + 1, step))
            for i in range(n)]
    block_h = n*lh + (n-1)*gap
    for y0 in range(int(TOP_MARGIN), int(ph - block_h - 4), step):
        ys = [y0 + i*(lh+gap) for i in range(n)]
        for ax in axs:
            if not free(ax, ys[anchor], aw): continue
            pos = [None]*n; pos[anchor] = ax
            ok = True
            for i in range(n):
                if i == anchor: continue
                for x in sorted(xall[i], key=lambda v: abs(v - ax)):
                    if free(x, ys[i], widths[i]):
                        pos[i] = x; break
                else:
                    ok = False; break
            if ok:
                return list(zip(pos, ys))
    # fallback: independent placement
    res = []; w2 = list(words)
    for i in range(n):
        x, y = find_zone(w2, pw, ph, widths[i], lh); reserve(w2, x, y, widths[i], lh)
        res.append((x, y))
    return res

def reserve(words, x, y, w, h, m=2):
    words.append({'x0':x-m,'top':y-m,'x1':x+w+m,'bottom':y+h+m})

def to_pdf_rect(px_x, px_y, pw_pts, ph_pts, page_h):
    return (px_x, page_h - px_y - ph_pts, px_x + pw_pts, page_h - px_y)

def add_freetext(writer, page_num, rect, text, color='0033CC'):
    ann = FreeText(
        text=text, rect=rect,
        font='Helvetica', bold=True, font_size='9pt',
        font_color=color, border_color=None,
        background_color=None,
    )
    writer.add_annotation(page_number=page_num, annotation=ann)
    # pypdf leaves /DA empty; set it so text renders blue in all viewers
    from pypdf.generic import TextStringObject
    r, g, b = (int(color[i:i+2], 16)/255 for i in (0, 2, 4))
    annots = writer.pages[page_num][NameObject('/Annots')]
    if hasattr(annots, 'get_object'): annots = annots.get_object()
    annots[-1].get_object()[NameObject('/DA')] = TextStringObject(
        f"{r:.3f} {g:.3f} {b:.3f} rg /Helv 9 Tf")

def prep_sig_rgb(sig_path, target_h_pts=38):
    """Embed the signature at its ORIGINAL pixel resolution (no resampling).
    Returns RGB + alpha (SMask) bytes so the background is transparent
    instead of a white box. Display height capped at target_h_pts; smaller
    originals display at natural size (1:1, crisp)."""
    img = PILImage.open(sig_path).convert('RGBA')
    px_w, px_h = img.size
    a = img.split()[3]
    if a.getextrema()[0] == 255:
        # No real transparency in file: derive alpha from luminance
        # (dark ink -> opaque, white paper -> transparent)
        lum = img.convert('L')
        a = lum.point(lambda v: 0 if v >= 245 else min(255, (255 - v) * 2))
    bg = PILImage.new('RGB', (px_w, px_h), 'white')
    bg.paste(img.convert('RGB'), mask=img.split()[3])
    h_pts = float(min(target_h_pts, px_h))
    w_pts = h_pts * px_w / px_h
    return bg.tobytes(), a.tobytes(), px_w, px_h, w_pts, h_pts

def add_image_stamp(writer, page_num, rect, raw_rgb, raw_alpha, px_w, px_h):
    x0, y0, x1, y1 = rect
    w_pts, h_pts = x1 - x0, y1 - y0
    img_obj = DecodedStreamObject.__new__(DecodedStreamObject)
    img_obj.update({
        NameObject('/Type'):             NameObject('/XObject'),
        NameObject('/Subtype'):          NameObject('/Image'),
        NameObject('/Width'):            NumberObject(px_w),
        NameObject('/Height'):           NumberObject(px_h),
        NameObject('/ColorSpace'):       NameObject('/DeviceRGB'),
        NameObject('/BitsPerComponent'): NumberObject(8),
    })
    img_obj.set_data(raw_rgb)
    if raw_alpha is not None:
        smask_obj = DecodedStreamObject.__new__(DecodedStreamObject)
        smask_obj.update({
            NameObject('/Type'):             NameObject('/XObject'),
            NameObject('/Subtype'):          NameObject('/Image'),
            NameObject('/Width'):            NumberObject(px_w),
            NameObject('/Height'):           NumberObject(px_h),
            NameObject('/ColorSpace'):       NameObject('/DeviceGray'),
            NameObject('/BitsPerComponent'): NumberObject(8),
        })
        smask_obj.set_data(raw_alpha)
        img_obj[NameObject('/SMask')] = writer._add_object(smask_obj)
    img_ref = writer._add_object(img_obj)
    ap_stream = f"q {w_pts:.4f} 0 0 {h_pts:.4f} 0 0 cm /Im0 Do Q".encode()
    form_obj = DecodedStreamObject.__new__(DecodedStreamObject)
    form_obj.update({
        NameObject('/Type'):    NameObject('/XObject'),
        NameObject('/Subtype'): NameObject('/Form'),
        NameObject('/BBox'):    ArrayObject([NumberObject(0), NumberObject(0),
                                             NumberObject(w_pts), NumberObject(h_pts)]),
        NameObject('/Resources'): DictionaryObject({
            NameObject('/XObject'): DictionaryObject({NameObject('/Im0'): img_ref})
        }),
    })
    form_obj.set_data(ap_stream)
    form_ref = writer._add_object(form_obj)
    annot = DictionaryObject({
        NameObject('/Type'):    NameObject('/Annot'),
        NameObject('/Subtype'): NameObject('/Stamp'),
        NameObject('/Rect'):    ArrayObject([NumberObject(x0), NumberObject(y0),
                                             NumberObject(x1), NumberObject(y1)]),
        NameObject('/Name'):    NameObject('/Custom'),
        NameObject('/AP'):      DictionaryObject({NameObject('/N'): form_ref}),
        NameObject('/F'):       NumberObject(4),
    })
    annot_ref = writer._add_object(annot)
    page = writer.pages[page_num]
    if NameObject('/Annots') not in page:
        page[NameObject('/Annots')] = ArrayObject()
    annots = page[NameObject('/Annots')]
    if hasattr(annots, 'get_object'):
        annots = annots.get_object()
    annots.append(annot_ref)

def strip_old_annots(writer):
    for page in writer.pages:
        annots = page.get('/Annots')
        if annots is None: continue
        if hasattr(annots, 'get_object'): annots = annots.get_object()
        keep = ArrayObject()
        for ref in annots:
            obj = ref.get_object()
            if obj.get('/Subtype') in ('/FreeText', '/Stamp'):
                continue
            keep.append(ref)
        page[NameObject('/Annots')] = keep

def process(src, budget, sig_rgb, sig_alpha, sig_pw, sig_ph, sig_w_pts, sig_h_pts):
    strip_overlays_from_pdf(src)
    with pdfplumber.open(src) as pdf:
        pg    = pdf.pages[0]
        pw, ph = float(pg.width), float(pg.height)
        words  = pg.extract_words() or []
        # Treat images and vector graphics (logos, header bands, table
        # rules) as occupied so stamps never sit on top of them.
        page_area = pw * ph
        # Entire table regions count as occupied — stamps must never sit
        # inside a table, even in empty cells.
        try:
            for tb in pg.find_tables():
                tx0, ttop, tx1, tbot = tb.bbox
                if (tx1-tx0) * (tbot-ttop) > 0.65 * page_area: continue
                words.append({'x0': max(0, tx0), 'top': max(0, ttop),
                              'x1': min(pw, tx1), 'bottom': min(ph, tbot)})
        except Exception:
            pass
        for obj in (pg.images + pg.rects + pg.lines + pg.curves):
            try:
                x0, top = float(obj['x0']), float(obj['top'])
                x1, bot = float(obj['x1']), float(obj['bottom'])
            except (KeyError, TypeError, ValueError):
                continue
            if x1 <= x0 or bot <= top: continue
            if (x1 - x0) * (bot - top) > 0.5 * page_area:
                continue  # full-page background fill, ignore
            words.append({'x0': max(0, x0), 'top': max(0, top),
                          'x1': min(pw, x1), 'bottom': min(ph, bot)})
    with pdfplumber.open(src) as pdf:
        text = "\n".join(p.extract_text() or '' for p in pdf.pages[:2])
    filename = os.path.basename(src)
    po      = extract_po(text, filename)
    matches = match_budget(text, filename, budget)
    month   = extract_invoice_month(text)
    CW = 5.8; FS = 9; LH = FS + 10
    cur = list(words)
    items = []
    if po:
        txt = f"PO: {po}"
        tw = len(txt)*CW + 14
        x, y = find_zone(cur, pw, ph, tw, LH);  reserve(cur, x, y, tw, LH)
        items.append((x, y, tw, LH, 'text', txt))
    elif matches:
        row0   = matches[0]
        # Vendor stamped with its parenthetical, e.g. "Dropsuite (Unisphere)"
        vendor = re.sub(r'\s+', ' ', row0.get('Vendors','')).strip()
        texts  = [fill_month(r['Text'].strip(), month) for r in matches]
        if len(matches) > 1:
            n = len(matches)
            split = all(re.search(r'\$1/(\d+)', (r.get('Notes') or '')) for r in matches)
            price = extract_price(text) if split else None
            body  = []
            for r, t in zip(matches, texts):
                if split and price:
                    body.append(f"${price:,.2f} /{n} = {price/n:,.2f} - {r['Code'].strip()} - {t}")
                else:
                    body.append(f"{r['Code'].strip()} - {t}")
            lines = [vendor] + body
        else:
            lines = [vendor, row0['Code'].strip(), texts[0]]
        lines  = [t for t in lines if t]
        widths = [len(t)*CW + 14 for t in lines]
        spots  = find_stacked(cur, pw, ph, widths, LH)
        for (x, y), w, t in zip(spots, widths, lines):
            reserve(cur, x, y, w, LH)
            items.append((x, y, w, LH, 'text', t))
    sx, sy = find_zone(cur, pw, ph, sig_w_pts+4, sig_h_pts+4)
    items.append((sx, sy, sig_w_pts, sig_h_pts, 'image', None))
    reader = PdfReader(src)
    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    for i in range(1, len(reader.pages)):
        writer.add_page(reader.pages[i])
    strip_old_annots(writer)
    for x, y, w, h, kind, content in items:
        r = to_pdf_rect(x, y, w, h, ph)
        if kind == 'text':
            add_freetext(writer, 0, r, content)
        else:
            add_image_stamp(writer, 0, r, sig_rgb, sig_alpha, sig_pw, sig_ph)
    tmp = src + '.tmp'
    with open(tmp, 'wb') as f:
        writer.write(f)
    os.replace(tmp, src)
    if po:
        note = f"PO: {po}"
    elif matches:
        note = f"{matches[0]['Code']} | {fill_month(matches[0]['Text'], month)}"
        if len(matches) > 1: note += f"  (+{len(matches)-1} tied rows)"
    else:
        note = "sig only"
    return note

budget   = load_budget(CSV_P)
sig_rgb, sig_alpha, sig_pw, sig_ph, sig_w_pts, sig_h_pts = prep_sig_rgb(SIG, target_h_pts=16.5)
ok = fail = 0
for fname in sorted(os.listdir(BASE)):
    if not fname.lower().endswith('.pdf'): continue
    src = os.path.join(BASE, fname)
    try:
        note = process(src, budget, sig_rgb, sig_alpha, sig_pw, sig_ph, sig_w_pts, sig_h_pts)
        print(f"OK  {fname}\n    {note}")
        ok += 1
    except Exception as e:
        import traceback
        print(f"FAIL  {fname}: {e}")
        traceback.print_exc()
        fail += 1
print(f"\n{'='*55}\n{ok} OK   {fail} FAILED")
