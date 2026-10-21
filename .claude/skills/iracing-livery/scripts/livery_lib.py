"""Shared helpers for the iracing-livery scripts (colours, finishes, fonts, masks, TGA output)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None

# ---------------------------------------------------------------------------
# Spec-map finishes.  Channels: R = metallic, G = roughness, B = clearcoat.
# Clearcoat (blue): 0 = no clearcoat; 16 = shiniest clear; 255 = dullest clear.
# Values marked TP come from Trading Paints' published "spec map starter" recipes.
# ---------------------------------------------------------------------------
FINISHES: dict[str, tuple[int, int, int]] = {
    "gloss": (0, 60, 16),            # clear-coated solid paint
    "gloss_noclear": (0, 30, 0),     # glossy, no clearcoat layer
    "satin": (0, 110, 0),
    "matte": (0, 175, 0),
    "flat": (0, 230, 0),             # rubber / primer / flat black
    "sticker": (0, 105, 0),          # satin vinyl so decals read as stickers
    "metallic": (255, 85, 0),        # TP "March Metallic"
    "metallic_deep": (255, 64, 18),  # TP "Shiny Side Up"
    "metallic_soft": (217, 115, 0),  # TP "Twilight Shimmer"
    "brushed": (255, 128, 64),       # TP "Brushed Alloy"
    "patina": (229, 178, 0),         # TP "Arizona Patina"
    "pearl": (255, 26, 217),         # TP "Freshly Waxed"
    "matte_metal": (28, 131, 0),     # TP "The Mattedor" (velvety matte)
    "chrome": (255, 15, 0),          # needs near-white albedo
    "carbon_gloss": (0, 45, 16),
    "carbon_matte": (0, 150, 0),
}

NAMED_COLOURS = {
    "white": (255, 255, 255), "black": (0, 0, 0), "red": (220, 20, 30),
    "blue": (20, 70, 200), "green": (20, 160, 60), "yellow": (255, 210, 0),
    "orange": (255, 120, 0), "grey": (128, 128, 128), "gray": (128, 128, 128),
}


def parse_colour(c) -> tuple[int, int, int]:
    if isinstance(c, (list, tuple)) and len(c) >= 3:
        return int(c[0]), int(c[1]), int(c[2])
    if not isinstance(c, str):
        raise ValueError(f"bad colour: {c!r}")
    s = c.strip().lower()
    if s in NAMED_COLOURS:
        return NAMED_COLOURS[s]
    if s.startswith("#"):
        s = s[1:]
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"bad colour: {c!r}")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def resolve_finish(f, default="keep"):
    """Return dict(rgb=(r,g,b) or None for keep, jitter=int) from a finish spec."""
    if f is None:
        f = default
    jitter = 0
    if isinstance(f, dict):
        jitter = int(f.get("roughness_jitter", 0))
        if "preset" in f:
            r, g, b = FINISHES[f["preset"]]
        else:
            r, g, b = 0, 110, 0
        r = int(f.get("metallic", r)); g = int(f.get("roughness", g)); b = int(f.get("clearcoat", b))
        return {"rgb": (r, g, b), "jitter": jitter}
    if isinstance(f, (list, tuple)):
        return {"rgb": tuple(int(v) for v in f[:3]), "jitter": 0}
    if f == "keep":
        return {"rgb": None, "jitter": 0}
    if f not in FINISHES:
        raise ValueError(f"unknown finish '{f}'. Known: {', '.join(FINISHES)} (or [r,g,b], or 'keep')")
    return {"rgb": FINISHES[f], "jitter": 0}


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_CANDIDATES = [
    "arialbd.ttf", "Arial Bold.ttf", "ariblk.ttf", "seguibl.ttf", "segoeuib.ttf",
    "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


def load_font(name: str | None, size: int) -> ImageFont.FreeTypeFont:
    tried = []
    names = [name] if name else []
    names += FONT_CANDIDATES
    win_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    for n in names:
        if not n:
            continue
        for cand in (n, str(win_fonts / n)):
            try:
                return ImageFont.truetype(cand, size)
            except OSError:
                tried.append(cand)
    raise SystemExit(f"No usable TrueType font found (tried {tried[:6]}...). Pass a .ttf path with \"font\".")


def label_font(size: int = 18):
    try:
        return load_font(None, size)
    except SystemExit:
        return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

def load_mask(path, size=None) -> np.ndarray:
    """Load an L/RGBA image as a boolean mask (white or opaque = True)."""
    im = Image.open(path)
    if size and im.size != size:
        im = im.resize(size, Image.NEAREST)
    if im.mode in ("RGBA", "LA"):
        a = np.array(im.getchannel("A"))
        if a.min() < 250:
            return a > 127
    return np.array(im.convert("L")) > 127


def save_tga(img: Image.Image, path, rle=True):
    """Save as a TGA iRacing can read: 24-bit RGB (or 32-bit if RGBA), RLE-compressed."""
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    img.save(path, format="TGA", compression="tga_rle" if rle else None)


def to_view(img: Image.Image, width=1024) -> Image.Image:
    if img.width <= width:
        return img.copy()
    h = round(img.height * width / img.width)
    return img.resize((width, h), Image.LANCZOS)


def draw_grid(img: Image.Image, full_size: int, step: int = 256, colour=(0, 200, 255, 140)):
    """Draw a coordinate grid labelled in full-resolution template pixels."""
    d = ImageDraw.Draw(img, "RGBA")
    sc = img.width / full_size
    f = label_font(max(10, int(14 * img.width / 1024)))
    for v in range(0, full_size + 1, step):
        p = round(v * sc)
        d.line([(p, 0), (p, img.height)], fill=colour, width=1)
        d.line([(0, p), (img.width, p)], fill=colour, width=1)
        if v < full_size:
            d.text((p + 2, 1), str(v), fill=(255, 255, 255, 230), font=f, stroke_width=2, stroke_fill=(0, 0, 0, 230))
            if v:
                d.text((2, p + 1), str(v), fill=(255, 255, 255, 230), font=f, stroke_width=2, stroke_fill=(0, 0, 0, 230))
    return img


def rel_luminance(rgb) -> float:
    c = np.asarray(rgb, dtype=np.float64) / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])


def contrast_ratio(a, b) -> float:
    la, lb = rel_luminance(a), rel_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)
