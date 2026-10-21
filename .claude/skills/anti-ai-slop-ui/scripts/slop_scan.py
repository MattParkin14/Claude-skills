#!/usr/bin/env python3
"""
slop_scan.py - static scanner for code-detectable AI-slop UI tells.

Usage:
    python3 slop_scan.py <file-or-folder> [more paths...] [--json] [--strict]

Scans HTML/CSS/JS/JSX/TS/TSX/Vue/Svelte/Astro/MDX files for patterns from the
69-tell list (IDs match references/the-69-tells.md). Hits are prompts to check,
not verdicts: a real brand colour or a user-requested style can be a justified
exception. The scanner cannot see layout, spacing rhythm, alignment, overflow or
image quality, so always finish with a manual review.

Score = number of distinct HIGH + MEDIUM tells found. LOW hits are "possible,
verify by eye". INFO hits are stack fingerprints that only matter in combination.
    0-1  clean     |  2-3  mild, fix before shipping  |  4+  heavy, rework tokens/structure

--strict exits with code 1 when the verdict is heavy (useful in CI).
"""

import json
import os
import re
import sys
from collections import defaultdict

EXTS = {".html", ".htm", ".css", ".scss", ".sass", ".less", ".js", ".jsx", ".ts",
        ".tsx", ".vue", ".svelte", ".astro", ".mdx"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", ".svelte-kit",
             ".output", "coverage", "vendor", "__pycache__", ".turbo", ".vercel"}

I = re.IGNORECASE
PURPLE_HEX = r"#(?:6366f1|4f46e5|4338ca|818cf8|8b5cf6|7c3aed|6d28d9|a78bfa|a855f7|9333ea|c084fc)\b"
CREAM_HEX = (r"#(?:faf8f5|f5f1ea|fdfbf7|faf7f2|f7f3ed|fbf8f3|f5f0e8|f8f5f0|fffbf5|f9f6f1|"
             r"f4efe6|faf9f6|f5f5f0|fdf8f0|f6f1e9)\b")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u27BF\u2B50\u2B55]")

# Each rule: id, name, severity, patterns, min_count (per whole scan), flags
RULES = [
    (1, "Indigo/violet/purple as accent", "high",
     [r"\b(?:bg|text|border|ring|fill|stroke|from|via|to|decoration|outline|accent|shadow)-(?:indigo|violet|purple)-\d{2,3}\b",
      PURPLE_HEX], 1, I),
    (2, "Purple-to-blue/pink gradient", "high",
     [r"from-(?:indigo|violet|purple|fuchsia)-\d{2,3}[^\"'`\n]{0,80}?(?:via|to)-(?:blue|cyan|sky|pink|fuchsia|indigo|violet|purple|rose)-\d{2,3}",
      r"linear-gradient\([^)\n]{0,120}(?:" + PURPLE_HEX[1:-2] + r"|purple|violet)[^)\n]{0,120}(?:#(?:3b82f6|2563eb|06b6d4|0ea5e9|ec4899|db2777)|blue|cyan|pink)"],
     1, I),
    (3, "Gradient text (bg-clip-text / background-clip: text)", "high",
     [r"\bbg-clip-text\b", r"background-clip:\s*text", r"-webkit-text-fill-color:\s*transparent"], 1, I),
    (5, "Many gradients (5+)", "medium",
     [r"bg-gradient-to-|bg-linear-to-|bg-linear-\d|linear-gradient\(|conic-gradient\("], 5, I),
    (6, "Coloured glow / coloured shadow", "high",
     [r"shadow-\[0_0_\d+px", r"\bshadow-(?:indigo|violet|purple|blue|cyan|pink|fuchsia|sky|emerald|teal)-\d{2,3}",
      r"box-shadow:\s*0(?:px)?\s+0(?:px)?\s+\d{2,}px", r"drop-shadow-\[0_0_"], 1, I),
    (8, "Cream/beige page background", "medium",
     [CREAM_HEX, r"\bbg-(?:stone|amber|orange)-50\b"], 1, I),
    (9, "Neon text colours (check if on dark)", "low",
     [r"\btext-(?:cyan|lime|fuchsia)-(?:300|400)\b"], 2, I),
    (12, "Inter font", "medium",
     [r"['\"]Inter['\"]", r"family=Inter\b", r"\bInter\s*\(", r"font-family:[^;\n]*\bInter\b"], 1, 0),
    (13, "Geist font", "medium",
     [r"\bGeist(?:_Mono|Mono|_Sans|Sans)?\b", r"geist/font"], 1, 0),
    (14, "Autopilot 'distinctive' font", "medium",
     [r"Space[ +_]Grotesk|Instrument[ +_]Serif|Fraunces|Playfair[ +_]Display|DM[ +_]Sans|Plus[ +_]Jakarta|Manrope"], 1, 0),
    (15, "Italic accent inside a headline", "low",
     [r"<h[12][^>]{0,200}>[^<]{0,120}<(?:em|i)\b", r"<h[12][^>]{0,200}>[^<]{0,120}<span[^>]{0,120}\bitalic\b"], 1, I),
    (17, "Very large H1 size (check it doesn't fill the screen)", "low",
     [r"\btext-(?:7xl|8xl|9xl)\b", r"text-\[(?:7[2-9]|[89]\d|1\d\d)px\]",
      r"font-size:\s*(?:(?:7[2-9]|[89]\d|1\d\d)px|[5-9](?:\.\d+)?rem)"], 1, I),
    (18, "Crushed letter-spacing", "medium",
     [r"\btracking-tighter\b", r"letter-spacing:\s*-0\.(?:0[6-9]|[1-9])\d*em", r"tracking-\[-0\.(?:0[6-9]|[1-9])"], 1, I),
    (20, "All-caps tracked micro-labels (3+)", "medium",
     [r"\buppercase\b[^\"'`\n]{0,80}\btracking-(?:wide|wider|widest|\[)", r"\btracking-(?:wider|widest)\b[^\"'`\n]{0,80}\buppercase\b",
      r"text-transform:\s*uppercase"], 3, I),
    (28, "Stat banner numbers (verify they are real and sourced)", "medium",
     [r"\b\d{1,3}(?:[.,]\d)?\s?[kKmM]\+", r"\b99\.9+%", r"\b\d{1,3},\d{3}\+"], 1, 0),
    (29, "Decorative 01/02/03 numbering", "medium",
     [r">\s*0[1-6]\s*<", r"['\"`]0[1-6]['\"`]", r">\s*0[1-6]\s*[./]"], 2, 0),
    (30, "Huge uniform section padding", "low",
     [r"\bpy-(?:24|28|32|36|40|48)\b"], 4, 0),
    (33, "Arbitrary spacing values (no scale)", "low",
     [r"\b(?:p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr|gap)-\[\d+(?:\.\d+)?(?:px|rem)\]"], 3, 0),
    (36, "Coloured accent stripe on card edge", "high",
     [r"\bborder-[lt]-(?:4|8|\[\d+px\])\b[^\"'`\n]{0,80}\bborder-(?:indigo|violet|purple|blue|emerald|green|amber|orange|pink|cyan|teal|primary|brand)",
      r"\bborder-(?:indigo|violet|purple|blue|emerald|green|amber|orange|pink|cyan|teal|primary|brand)[-\w]*[^\"'`\n]{0,80}\bborder-[lt]-(?:4|8|\[\d+px\])\b",
      r"border-left:\s*[3-8]px\s+solid"], 1, I),
    (37, "Large radius everywhere (5+ rounded-2xl/3xl)", "medium",
     [r"\brounded-(?:2xl|3xl)\b"], 5, 0),
    (38, "Pill buttons (check they aren't the only shape)", "low",
     [r"<(?:button|Button|a)\b[^>]{0,300}\brounded-full\b"], 3, 0),
    (39, "Blob-level radius on cards", "low",
     [r"rounded-\[(?:3[2-9]|4\d)px\]", r"border-radius:\s*(?:3[2-9]|4\d)px"], 1, 0),
    (40, "Border + large shadow on the same element", "low",
     [r"\bborder\b[^\"'`\n]{0,80}\bshadow-(?:lg|xl|2xl)\b", r"\bshadow-(?:lg|xl|2xl)\b[^\"'`\n]{0,80}\bborder\b(?!-)"], 2, 0),
    (41, "Untouched shadcn Card classes", "high",
     [r"rounded-(?:lg|xl) border bg-card", r"bg-card text-card-foreground"], 1, 0),
    (42, "Decorative grid-line background", "medium",
     [r"\bbg-grid", r"bg-\[linear-gradient\(to_right", r"linear-gradient\(\s*(?:to right|90deg)[^)\n]{0,80}\b1px\b"], 1, I),
    (43, "Repeating stripe texture", "medium",
     [r"repeating-linear-gradient"], 1, I),
    (45, "Eyebrow pill above headline", "high",
     [r"rounded-full[^>]{0,300}>\s*(?:<[^>]{1,200}>\s*){0,3}[^<]{0,6}(?:New|NEW|Beta|BETA|Introducing|Announcing|Now (?:in|available|live)|Just launched|v\d)"], 1, 0),
    (46, "Dot-prefixed all-caps eyebrow", "low",
     [r"(?:\u2022|&bull;|\u00b7)\s*[A-Z][A-Z ]{3,}"], 1, 0),
    (47, "Gradient CTA button", "high",
     [r"<(?:button|Button|a|Link)\b[^>]{0,300}\bbg-(?:gradient|linear)-"], 1, 0),
    (48, "Gradient-initial avatars", "low",
     [r"\brounded-full\b[^\"'`\n]{0,80}\bbg-(?:gradient|linear)-", r"\bbg-(?:gradient|linear)-[^\"'`\n]{0,120}\brounded-full\b"], 2, 0),
    (49, "Lucide icons (stack fingerprint)", "info",
     [r"lucide-(?:react|vue|vue-next|svelte|static|angular)\b|unpkg\.com/lucide|lucide\.createIcons"], 1, I),
    (50, "Icon in tinted rounded tile", "low",
     [r"\b(?:h|w|size)-(?:10|11|12|14)\b[^\"'`\n]{0,80}\brounded-(?:lg|xl|2xl|full)\b[^\"'`\n]{0,80}\bbg-[a-z]+(?:-\d{2,3})?/(?:5|10|15|20)\b",
      r"\bbg-[a-z]+(?:-\d{2,3})?/(?:5|10|15|20)\b[^\"'`\n]{0,80}\b(?:h|w|size)-(?:10|11|12|14)\b[^\"'`\n]{0,80}\brounded-(?:lg|xl|2xl|full)\b"], 2, 0),
    (53, "Sparkles as the 'AI' signifier", "high",
     [r"\bSparkles\b", "\u2728"], 1, 0),
    (60, "Near-opaque overlay on image", "low",
     [r"\bbg-black/(?:8\d|9\d)\b", r"rgba\(0,\s*0,\s*0,\s*0?\.(?:8|9)\d*\)"], 1, 0),
    (61, "Fade-in animations everywhere (4+)", "medium",
     [r"animate-fade|fadeIn|fade-in|fadeUp|fade-up|fadeInUp", r"initial=\{\{\s*opacity:\s*0"], 4, I),
    (62, "Scroll-triggered reveals on many sections (3+)", "medium",
     [r"whileInView|data-aos|useInView|IntersectionObserver|ScrollTrigger"], 3, 0),
    (63, "Hover-scale / lift on cards", "high",
     [r"hover:scale-1[01]\d\b", r"whileHover=\{\{\s*scale", r"hover:-translate-y-"], 2, 0),
    (64, "Bounce / elastic easing", "low",
     [r"\banimate-bounce\b", r"cubic-bezier\(\s*0?\.\d+\s*,\s*1\.[2-9]", r"bounce:\s*0?\.[3-9]"], 1, I),
    (65, "Decorative pulses / pings / marquees / blinking", "medium",
     [r"\banimate-(?:pulse|ping)\b", r"marquee", r"@keyframes\s+blink", r"animate-scroll"], 1, I),
    (67, "Big blur blobs / aurora glow", "medium",
     [r"\bblur-(?:2xl|3xl|\[\d{2,3}px\])\b", r"filter:\s*blur\(\s*(?:[4-9]\d|\d{3})px\)"], 1, 0),
    (68, "Cliche hero/marketing copy", "medium",
     [r"\btransform your\b", r"\bsupercharge", r"\bunlock the (?:power|potential|future)", r"\bbuild the future\b",
      r"\bthe future of\b", r"\brevolutioni[sz]e", r"\bseamless(?:ly)?\b", r"\beffortless(?:ly)?\b",
      r"\bnext[- ]gen(?:eration)?\b", r"\bgame[- ]chang", r"\b10x your\b", r"\belevate your\b",
      r"\bempower(?:s|ing)? (?:your|teams|you)\b", r"\ball-in-one platform\b", r"\bcutting[- ]edge\b",
      r"\blike never before\b", r"\breimagin(?:e|ed|ing)\b", r"\bharness the power\b",
      r"\bto the next level\b", r"\bat the speed of thought\b"], 1, I),
]

DARK_BG = re.compile(r"\bbg-(?:black|zinc-9[05]0|slate-9[05]0|neutral-9[05]0|gray-9[05]0|stone-950)\b|"
                     r"#(?:0a0a0a|09090b|020617|030712|0c0a09|111111|0b0b0f)\b", I)
GREY_TEXT = re.compile(r"\btext-(?:gray|zinc|slate|neutral|stone)-(?:400|500)\b")
SERIF_TASTE = re.compile(r"Instrument[ +_]Serif|Fraunces|Playfair[ +_]Display", I)
GREEN_ACCENT = re.compile(r"\b(?:bg|text|border|from|to)-(?:emerald|green|lime|teal)-(?:6|7|8|9)00\b|"
                          r"#(?:2f4f3a|3a5a40|4a6741|556b2f|1f3d2b|2d4a3e|5b7553|6b8f71|87a878|3f5e4b)\b", I)
IMG = re.compile(r"<img\b|<Image\b|<picture\b|<video\b|background-image:\s*url\(|bg-\[url\(", I)
H1 = re.compile(r"<h1\b", I)
EM_DASH = "\u2014"
FAKE_NAME = re.compile(r"\b[A-Z][a-z]{2,} [A-Z]\.(?=\s*(?:,|<|\u2014|-|\n|\"|'|\)))")

SEV_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}


def iter_files(paths):
    for p in paths:
        if os.path.isfile(p):
            if os.path.splitext(p)[1].lower() in EXTS:
                yield p
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
                for f in files:
                    if os.path.splitext(f)[1].lower() in EXTS:
                        yield os.path.join(root, f)


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def snippet(s, n=70):
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "\u2026"


def scan(paths):
    compiled = [(rid, name, sev, [re.compile(p, fl) for p in pats], minc)
                for rid, name, sev, pats, minc, fl in RULES]
    hits = defaultdict(list)          # rid -> [(file, line, text)]
    agg = defaultdict(bool)
    files = list(iter_files(paths))
    em_dash_total = 0
    imageless_pages = []
    fake_names = []

    for f in files:
        try:
            text = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for rid, name, sev, pats, minc in compiled:
            for rx in pats:
                for m in rx.finditer(text):
                    hits[rid].append((f, line_of(text, m.start()), snippet(m.group(0))))
        # emoji (52)
        for m in EMOJI.finditer(text):
            if m.group(0) == "\u2728":
                continue  # counted under 53
            hits[52].append((f, line_of(text, m.start()), m.group(0)))
        # aggregates
        if DARK_BG.search(text):
            agg["dark"] = True
        if GREY_TEXT.search(text):
            agg["grey"] = True
        if SERIF_TASTE.search(text):
            agg["serif"] = True
        if GREEN_ACCENT.search(text):
            agg["green"] = True
        if re.search(CREAM_HEX, text, I) or re.search(r"\bbg-(?:stone|amber)-50\b", text):
            agg["cream"] = True
        em_dash_total += text.count(EM_DASH)
        if H1.search(text) and not IMG.search(text):
            imageless_pages.append((f, line_of(text, H1.search(text).start()), "h1 with no img/video"))
        for m in FAKE_NAME.finditer(text):
            fake_names.append((f, line_of(text, m.start()), m.group(0)))

    findings = []
    for rid, name, sev, pats, minc in compiled:
        h = hits.get(rid, [])
        if len(h) >= minc:
            findings.append({"id": rid, "name": name, "severity": sev, "count": len(h), "examples": h[:3]})
    if len(hits.get(52, [])) >= 2:
        findings.append({"id": 52, "name": "Emoji used in UI (icons/bullets?)", "severity": "high",
                         "count": len(hits[52]), "examples": hits[52][:3]})
    if agg["dark"] and agg["grey"]:
        findings.append({"id": 66, "name": "Dark background + grey-400/500 body text (also check #11 contrast)",
                         "severity": "medium", "count": 1, "examples": []})
    if agg["cream"] and agg["serif"] and agg["green"]:
        findings.append({"id": 7, "name": "Cream + serif + green combo (the 2026 'tasteful' default)",
                         "severity": "high", "count": 1, "examples": []})
    if imageless_pages:
        findings.append({"id": 56, "name": "Page(s) with a headline but no real images/video", "severity": "medium",
                         "count": len(imageless_pages), "examples": imageless_pages[:3]})
    if em_dash_total >= 6:
        findings.append({"id": 69, "name": f"Em-dashes in copy ({em_dash_total})", "severity": "medium",
                         "count": em_dash_total, "examples": []})
    if len(fake_names) >= 2:
        findings.append({"id": 69, "name": "Initial-style testimonial names (verify they are real)",
                         "severity": "high", "count": len(fake_names), "examples": fake_names[:3]})

    findings.sort(key=lambda x: (SEV_ORDER[x["severity"]], x["id"]))
    scored_ids = {x["id"] for x in findings if x["severity"] in ("high", "medium")}
    score = len(scored_ids)
    verdict = "CLEAN" if score <= 1 else ("MILD: fix before shipping" if score <= 3
                                          else "HEAVY: rework tokens/structure, don't patch")
    return {"files_scanned": len(files), "score": score, "verdict": verdict, "findings": findings}


EYE_ONLY = "10, 16, 19, 21-27, 31, 32, 34, 35, 44, 51, 54, 55, 57-59"


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    as_json = "--json" in argv
    strict = "--strict" in argv
    if not args:
        print(__doc__)
        return 2
    res = scan(args)
    if as_json:
        print(json.dumps(res, indent=2))
    else:
        print(f"AI-slop scan: {res['files_scanned']} file(s)")
        print(f"Score: {res['score']} distinct high/medium tells  ->  {res['verdict']}\n")
        if not res["findings"]:
            print("No code-detectable tells found.")
        cur = None
        for f in res["findings"]:
            if f["severity"] != cur:
                cur = f["severity"]
                label = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW (possible, verify by eye)",
                         "info": "INFO (stack fingerprint, matters in combination)"}[cur]
                print(label)
            print(f"  [{f['id']}] {f['name']}  x{f['count']}")
            for (fp, ln, tx) in f["examples"]:
                print(f"       {os.path.relpath(fp)}:{ln}  {tx}")
        print(f"\nNot checkable by script, review by eye: tells {EYE_ONLY}.")
        print("Details and fixes: references/the-69-tells.md")
    if strict and res["score"] >= 4:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
