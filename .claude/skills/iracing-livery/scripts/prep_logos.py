#!/usr/bin/env python3
"""Clean and audit logo files before they go on a car.

Usage:
  python prep_logos.py LOGO_OR_DIR [LOGO_OR_DIR ...] --out logos_clean [--knockout auto|white|black|none]

For each image (PNG/JPG/WEBP/...; files with the wrong extension are detected by content):
  * removes a solid background connected to the border when there is no real transparency
    (--knockout auto: only if the border is one flat colour; inner holes such as an eye stay)
  * trims empty margins
  * writes <name>.png (cleaned), <name>_white.png and <name>_black.png (mono versions for dark/light panels)
  * reports size, real format, main colours and whether it is big enough

Writes logos.json and logos_sheet.png (contact sheet on a checkerboard) to --out.
A logo should be at least as many pixels as it will be on the paint (e.g. 400px wide for a
400px door logo); upscaling more than ~1.5x looks soft in the sim.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent))
from livery_lib import label_font, write_json  # noqa: E402

EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tga", ".tif", ".tiff"}


def knockout(im: Image.Image, mode: str):
    a = np.array(im.getchannel("A"))
    if a.min() < 250 and mode == "auto":
        return im, "has transparency"
    rgb = np.array(im.convert("RGB")).astype(np.int16)
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    ref = np.median(border, axis=0)
    if mode == "white":
        ref = np.array([255, 255, 255])
    elif mode == "black":
        ref = np.array([0, 0, 0])
    elif mode == "none":
        return im, "left as is"
    spread = np.abs(border - ref).max(axis=1)
    if mode == "auto" and (spread > 24).mean() > 0.1:
        return im, "opaque, busy border — NOT knocked out (pass --knockout white/black if needed)"
    diff = np.abs(rgb - ref).max(axis=2)
    bgish = diff < 28
    lab, _ = ndi.label(bgish)
    edge_ids = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge_ids))
    soft = np.clip((diff - 10) / 30, 0, 1)  # anti-aliased edge
    alpha = np.where(bg, 0, 255).astype(np.float32)
    near = ndi.binary_dilation(bg, iterations=2) & ~bg
    alpha[near] = (soft[near] * 255)
    out = im.copy()
    out.putalpha(Image.fromarray(alpha.astype(np.uint8)))
    return out, f"background {tuple(int(v) for v in ref)} knocked out"


def main_colours(im: Image.Image, k=5):
    a = np.array(im.getchannel("A")) > 127
    if not a.any():
        return []
    px = np.array(im.convert("RGB"))[a]
    q = (px // 32) * 32 + 16
    keys, counts = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(-counts)[:k]
    tot = counts.sum()
    return [{"hex": "#%02x%02x%02x" % tuple(int(v) for v in keys[i]), "share": round(float(counts[i] / tot), 2)} for i in order]


def mono(im: Image.Image, col):
    m = Image.new("RGBA", im.size, col + (255,))
    m.putalpha(im.getchannel("A"))
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--knockout", default="auto", choices=["auto", "white", "black", "none"])
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    files = []
    for p in map(Path, args.inputs):
        files += sorted(f for f in p.iterdir() if f.suffix.lower() in EXTS) if p.is_dir() else [p]
    results, tiles = [], []
    for f in files:
        try:
            im = Image.open(f)
            real = im.format
            im.load()
        except Exception as e:  # noqa: BLE001
            print(f"  SKIP {f.name}: {e}")
            continue
        im = im.convert("RGBA")
        cleaned, note = knockout(im, args.knockout)
        bb = cleaned.getchannel("A").getbbox()
        if bb is None:
            print(f"  SKIP {f.name}: empty after knockout")
            continue
        cleaned = cleaned.crop(bb)
        stem = f.stem.replace(" ", "_")
        cleaned.save(out / f"{stem}.png")
        mono(cleaned, (255, 255, 255)).save(out / f"{stem}_white.png")
        mono(cleaned, (0, 0, 0)).save(out / f"{stem}_black.png")
        cols = main_colours(cleaned)
        warn = []
        if real and f.suffix.lower().lstrip(".") not in (real.lower(), "jpg" if real == "JPEG" else ""):
            warn.append(f"extension says {f.suffix} but it is really {real}")
        if max(cleaned.size) < 400:
            warn.append(f"small ({cleaned.width}x{cleaned.height}) — fine for small stickers only")
        if real == "JPEG":
            warn.append("JPEG — check edges for compression fringing")
        r = {"source": str(f), "clean": f"{stem}.png", "format": real, "size": list(cleaned.size),
             "note": note, "colours": cols, "mono_hint": bool(cols and cols[0]["share"] > 0.85), "warnings": warn}
        results.append(r)
        tiles.append((cleaned, stem, r))
        print(f"  {f.name}: {real} {cleaned.width}x{cleaned.height}; {note}; colours {[c['hex'] for c in cols[:3]]}"
              + ("".join(f"\n      WARN: {w}" for w in warn)))
    write_json(out / "logos.json", results)

    if tiles:
        T = 280
        cols_n = 4
        rows = (len(tiles) + cols_n - 1) // cols_n
        sheet = Image.new("RGB", (cols_n * T, rows * (T + 40)), (40, 40, 40))
        f = label_font(14)
        for i, (im, stem, r) in enumerate(tiles):
            x, y = (i % cols_n) * T, (i // cols_n) * (T + 40)
            chk = Image.new("RGB", (T - 10, T - 10))
            dd = ImageDraw.Draw(chk)
            for yy in range(0, T, 20):
                for xx in range(0, T, 20):
                    dd.rectangle([xx, yy, xx + 19, yy + 19], fill=(200, 200, 200) if (xx + yy) // 20 % 2 else (150, 150, 150))
            t = im.copy()
            t.thumbnail((T - 30, T - 30))
            chk.paste(t, ((chk.width - t.width) // 2, (chk.height - t.height) // 2), t)
            sheet.paste(chk, (x + 5, y + 5))
            ImageDraw.Draw(sheet).text((x + 6, y + T), f"{stem[:26]}\n{r['size'][0]}x{r['size'][1]} {r['format']}",
                                       fill=(255, 220, 120) if r["warnings"] else (255, 255, 255), font=f)
        sheet.save(out / "logos_sheet.png")
    print(f"\n{len(results)} logos -> {out} (see logos_sheet.png and logos.json)")


if __name__ == "__main__":
    main()
