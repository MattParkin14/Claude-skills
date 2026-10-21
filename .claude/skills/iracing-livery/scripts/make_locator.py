#!/usr/bin/env python3
"""Make a one-off "locator" paint: a labelled coordinate grid painted onto the car.

Install it, orbit the car in iRacing, take screenshots, and every visible cell label tells you
exactly which template coordinates land where on the real car. Text that reads backwards means
that panel is mirrored in the template; rotated text shows the panel's orientation; cells that
never appear in any screenshot are hidden (under wings, inside arches, behind mirrors).

Usage:
  python make_locator.py INSPECT_DIR OUT_DIR --customer-id 123456 [--cell 128]

Writes car_<id>.tga, car_spec_<id>.tga (plain satin) and locator_key.png (1024px key).
Cell names: column letter A, B, C... left to right, row number 01, 02... top to bottom.
Cell C07 covers x = 2*cell .. 3*cell, y = 6*cell .. 7*cell.
"""
from __future__ import annotations

import argparse
import colorsys
import string
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent))
from livery_lib import FINISHES, draw_grid, label_font, load_font, save_tga, to_view  # noqa: E402


def cell_name(cx, cy):
    letters = string.ascii_uppercase
    col = letters[cx] if cx < 26 else letters[cx // 26 - 1] + letters[cx % 26]
    return f"{col}{cy + 1:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inspect_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--customer-id", required=True)
    ap.add_argument("--cell", type=int, default=128, help="cell size in template px (128 = 16x16 on a 2048 paint)")
    args = ap.parse_args()

    insp, out = Path(args.inspect_dir), Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    labels = np.array(Image.open(insp / "islands_labels.png")).astype(np.int32)
    S = labels.shape[0]
    c = args.cell
    n = S // c

    img = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(img)
    font = load_font(None, int(c * 0.36))
    small = load_font(None, int(c * 0.16))
    for cy in range(n):
        for cx in range(n):
            h = (cx / n) % 1.0
            light = 0.62 if (cx + cy) % 2 == 0 else 0.42
            r, g, b = colorsys.hls_to_rgb(h, light, 0.85)
            col = (int(r * 255), int(g * 255), int(b * 255))
            x0, y0 = cx * c, cy * c
            d.rectangle([x0, y0, x0 + c - 1, y0 + c - 1], fill=col)
            name = cell_name(cx, cy)
            d.text((x0 + c / 2, y0 + c * 0.42), name, font=font, anchor="mm", fill="white", stroke_width=3, stroke_fill="black")
            # an asymmetric "F" marker plus arrow: shows rotation and mirroring at a glance
            d.text((x0 + 6, y0 + c - 6), "F", font=small, anchor="ld", fill="black", stroke_width=1, stroke_fill="white")
            ax, ay, s = x0 + c * 0.32, y0 + c * 0.86, c * 0.07
            d.polygon([(ax, ay - s), (ax + 3 * s, ay), (ax, ay + s)], fill="black", outline="white")
    # thick panel outlines and big island numbers
    arr = np.array(img)
    edges = (labels != ndi.grey_erosion(labels, size=(9, 9))) & (labels > 0)
    arr[edges] = (0, 0, 0)
    img = Image.fromarray(arr)
    d = ImageDraw.Draw(img)
    big = load_font(None, int(c * 0.8))
    for i, sl in enumerate(ndi.find_objects(labels), start=1):
        if sl is None:
            continue
        ys, xs = np.nonzero(labels[sl] == i)
        cx, cy = sl[1].start + xs.mean(), sl[0].start + ys.mean()
        d.text((cx, cy), f"#{i}", font=big, anchor="mm", fill="white", stroke_width=6, stroke_fill="black")

    cid = args.customer_id
    save_tga(img, out / f"car_{cid}.tga")
    save_tga(Image.new("RGB", (S, S), FINISHES["satin"]), out / f"car_spec_{cid}.tga")
    key = to_view(img)
    draw_grid(key, S, step=c * 2, colour=(255, 255, 255, 90))
    key.save(out / "locator_key.png")
    (out / "report.json").write_text('{"errors": 0, "warnings": 0, "locator": true}')
    print(f"locator paint -> {out} ({n}x{n} cells of {c}px). Install it with install_paint.py, then screenshot:")
    print("  front 3/4 both sides, rear 3/4 both sides, both side profiles, top-down, nose and tail close-ups.")


if __name__ == "__main__":
    main()
