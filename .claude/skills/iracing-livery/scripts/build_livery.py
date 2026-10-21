#!/usr/bin/env python3
"""Render an iRacing livery + spec map from a livery.json, check every logo's placement, and write proofs.

Usage:
  python build_livery.py path/to/livery.json [--out DIR]

Outputs go to <livery dir>/builds/vNN/ (next free number) unless --out is given:
  car_<id>.tga        24-bit RLE paint (also car_num_<id>.tga when "custom_number": true)
  car_spec_<id>.tga   24-bit RLE spec map (R metallic, G roughness, B clearcoat)
  preview.png         1024px paint
  spec_preview.png    1024px spec map
  proof.png           1024px paint + wireframe + panel outlines + stamp zones + labelled logo boxes
  crops/              1:1 crops of every logo/text element
  report.json         placement checks (errors must be fixed before installing) and design hints
  livery.json         snapshot of the spec that produced this build

The livery.json format is documented in references/livery-json.md.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from livery_lib import (FINISHES, contrast_ratio, die, draw_grid, label_font, load_font,  # noqa: E402
                        load_mask, parse_colour, read_json, rel_luminance, resolve_finish,
                        save_tga, to_view, write_json)

CHECKED_TYPES = {"logo", "text"}


# ---------------------------------------------------------------------------
# context
# ---------------------------------------------------------------------------
class Ctx:
    def __init__(self, spec_path: Path, spec: dict):
        self.base_dir = spec_path.parent
        self.spec = spec
        insp = self.p(spec.get("inspect_dir", "inspect"))
        if not (insp / "mask.png").exists():
            die(f"{insp}/mask.png not found — run inspect_template.py first or set \"inspect_dir\"")
        self.insp = insp
        self.mask = load_mask(insp / "mask.png")
        self.S = self.mask.shape[0]
        sz = (self.S, self.S)
        self.lines = load_mask(insp / "wire_mask.png", sz) if (insp / "wire_mask.png").exists() else np.zeros(sz, bool)
        self.keep = load_mask(insp / "keepout.png", sz) if (insp / "keepout.png").exists() else np.zeros(sz, bool)
        if spec.get("custom_number") and (insp / "stamps.png").exists():
            # number blocks are free to paint on when the number is painted by us
            self.keep = load_mask(insp / "stamps.png", sz)
        lab_p = insp / "islands_labels.png"
        self.labels = np.array(Image.open(lab_p)).astype(np.int32) if lab_p.exists() else ndi.label(self.mask)[0]
        self.dist = ndi.distance_transform_edt(self.labels > 0)
        dens = ndi.uniform_filter(self.lines.astype(np.float32), size=65)
        on = self.labels > 0
        self.dnorm = float(np.percentile(dens[on], 95)) if on.any() and dens[on].max() > 0 else 1.0
        self.density = dens / self.dnorm if self.dnorm else dens
        self.edge_margin = int(spec.get("edge_margin", 24))
        self.extra_keepout = []
        for k in spec.get("keep_out_extra", []):
            m = Image.new("L", sz, 0)
            ImageDraw.Draw(m).polygon([tuple(p) for p in k["polygon"]], fill=255)
            self.extra_keepout.append((k.get("label", "keep-out"), np.array(m) > 0, k["polygon"]))
        self.rng = np.random.default_rng(int(spec.get("seed", 1)))

    def p(self, rel) -> Path:
        q = Path(rel)
        return q if q.is_absolute() else (self.base_dir / q)


# ---------------------------------------------------------------------------
# geometry → masks
# ---------------------------------------------------------------------------

def aa_draw(S, fn):
    """Draw at 2x and downsample for anti-aliased edges."""
    big = Image.new("L", (S * 2, S * 2), 0)
    fn(ImageDraw.Draw(big), 2)
    return np.asarray(big.resize((S, S), Image.BOX), dtype=np.float32) / 255.0


def shape_mask(ctx: Ctx, L: dict) -> np.ndarray:
    S = ctx.S
    kind = L.get("shape", "polygon")
    if kind == "polygon":
        pts = L["points"]
        m = aa_draw(S, lambda d, k: d.polygon([(x * k, y * k) for x, y in pts], fill=255))
    elif kind == "rect":
        x0, y0, x1, y1 = L["rect"]
        r = L.get("radius", 0)
        m = aa_draw(S, lambda d, k: d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=r * k, fill=255))
    elif kind == "ellipse":
        x0, y0, x1, y1 = L["rect"]
        m = aa_draw(S, lambda d, k: d.ellipse([x0 * k, y0 * k, x1 * k, y1 * k], fill=255))
    elif kind == "band":
        pts, w = L["points"], L["width"]

        def _band(d, k):
            d.line([(x * k, y * k) for x, y in pts], fill=255, width=int(w * k), joint="curve")
            if L.get("round_caps", False):
                for x, y in (pts[0], pts[-1]):
                    d.ellipse([(x - w / 2) * k, (y - w / 2) * k, (x + w / 2) * k, (y + w / 2) * k], fill=255)
        m = aa_draw(S, _band)
    elif kind == "island":
        m = np.isin(ctx.labels, L["islands"]).astype(np.float32)
    elif kind == "full":
        m = np.ones((S, S), np.float32)
    elif kind == "mask_file":
        m = load_mask(ctx.p(L["file"]), (S, S)).astype(np.float32)
    else:
        die(f"unknown shape '{kind}' in layer {L.get('label', '?')}")
    if L.get("feather"):
        m = ndi.gaussian_filter(m, sigma=float(L["feather"]) / 2)
    if L.get("invert"):
        m = 1.0 - m
    return m.astype(np.float32)


def clip_mask(ctx: Ctx, L: dict):
    clip = L.get("clip")
    m = None
    if clip == "paintable":
        m = (ctx.labels > 0).astype(np.float32)
    elif isinstance(clip, list):
        m = np.isin(ctx.labels, clip).astype(np.float32)
    if L.get("clip_region"):
        r = L["clip_region"]
        im = Image.new("L", (ctx.S, ctx.S), 0)
        d = ImageDraw.Draw(im)
        if len(r) == 4 and not isinstance(r[0], (list, tuple)):
            d.rectangle([r[0], r[1], r[2] - 1, r[3] - 1], fill=255)
        else:
            d.polygon([tuple(p) for p in r], fill=255)
        rm = (np.asarray(im) > 0).astype(np.float32)
        m = rm if m is None else m * rm
    return m


def window(m, pad=2):
    ys, xs = np.nonzero(m > 1e-3)
    if ys.size == 0:
        return None
    S = m.shape[0]
    return (slice(max(0, ys.min() - pad), min(S, ys.max() + 1 + pad)),
            slice(max(0, xs.min() - pad), min(S, xs.max() + 1 + pad)))


# ---------------------------------------------------------------------------
# fills and patterns  (all return rgb[h,w,3] 0..255, alpha[h,w] 0..1, rough_offset[h,w] or None)
# ---------------------------------------------------------------------------

def grid_xy(sl):
    ys = np.arange(sl[0].start, sl[0].stop, dtype=np.float32)
    xs = np.arange(sl[1].start, sl[1].stop, dtype=np.float32)
    return np.meshgrid(xs, ys)


def solid(col, shape):
    rgb = np.empty(shape + (3,), np.float32)
    rgb[:] = parse_colour(col)
    return rgb


def gradient(g, sl):
    X, Y = grid_xy(sl)
    (fx, fy), (tx, ty) = g["from"], g["to"]
    dx, dy = tx - fx, ty - fy
    t = ((X - fx) * dx + (Y - fy) * dy) / max(dx * dx + dy * dy, 1e-6)
    t = np.clip(t, 0, 1)
    stops = sorted(((float(p), parse_colour(c)) for c, p in g["stops"]), key=lambda s: s[0])
    rgb = np.zeros(t.shape + (3,), np.float32)
    pos = np.array([s[0] for s in stops], np.float32)
    cols = np.array([s[1] for s in stops], np.float32)
    for ch in range(3):
        rgb[..., ch] = np.interp(t, pos, cols[:, ch])
    return rgb


def cells(points, sl, colours, gap_colour, gap_width, jitter, shade, rng, alpha_fill=True):
    X, Y = grid_xy(sl)
    tree = cKDTree(points)
    d, idx = tree.query(np.stack([X.ravel(), Y.ravel()], 1), k=2, workers=-1)
    cell = idx[:, 0].reshape(X.shape)
    n = len(points)
    cols = np.array([parse_colour(c) for c in colours], np.float32) if colours else np.zeros((1, 3), np.float32)
    pick = rng.integers(len(cols), size=n)
    rgb = cols[pick][cell].astype(np.float32)
    if shade:
        mult = rng.uniform(1 - shade, 1 + shade, size=n).astype(np.float32)
        rgb *= mult[cell][..., None]
    alpha = np.ones(X.shape, np.float32) if alpha_fill else np.zeros(X.shape, np.float32)
    if gap_width:
        edge = ((d[:, 1] - d[:, 0]) / 2).reshape(X.shape)
        a = np.clip(gap_width / 2 - edge + 0.5, 0, 1)
        gc = np.array(parse_colour(gap_colour or "#000"), np.float32)
        rgb = rgb * (1 - a[..., None]) + gc * a[..., None]
        if not alpha_fill:
            alpha = a
    rough = None
    if jitter:
        rough = rng.uniform(-jitter, jitter, size=n).astype(np.float32)[cell]
    return np.clip(rgb, 0, 255), alpha, rough


def pattern(p, sl, rng):
    kind = p["kind"]
    h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    x0, y0 = sl[1].start, sl[0].start
    if kind == "shards":
        scale = float(p.get("scale", 140))
        n = max(6, int(h * w / scale ** 2))
        pts = rng.uniform([x0 - scale, y0 - scale], [x0 + w + scale, y0 + h + scale], size=(n, 2))
        return cells(pts, sl, p.get("colours", p.get("colors", ["#222", "#333"])), p.get("gap_colour", p.get("gap_color")),
                     float(p.get("gap_width", 0)), float(p.get("roughness_jitter", 0)), float(p.get("shade", 0.06)), rng)
    if kind == "hex":
        s = float(p.get("size", 40))
        hw, hh = math.sqrt(3) * s, 1.5 * s
        pts = []
        for j in range(int((y0 - 2 * s) // hh), int((y0 + h + 2 * s) // hh) + 1):
            for i in range(int((x0 - 2 * hw) // hw), int((x0 + w + 2 * hw) // hw) + 1):
                pts.append((i * hw + (j % 2) * hw / 2, j * hh))
        filled = bool(p.get("colours") or p.get("colors"))
        return cells(np.array(pts, np.float32), sl, p.get("colours", p.get("colors")), p.get("line_colour", p.get("line_color", "#000")),
                     float(p.get("line_width", 3)), float(p.get("roughness_jitter", 0)), float(p.get("shade", 0)), rng,
                     alpha_fill=filled)
    if kind == "carbon":
        X, Y = grid_xy(sl)
        t = float(p.get("tile", 14))
        c0 = np.array(parse_colour(p.get("dark", "#121212")), np.float32)
        c1 = np.array(parse_colour(p.get("light", "#3a3a3a")), np.float32)
        tx, ty = np.floor(X / t), np.floor(Y / t)
        horiz = ((tx + ty) % 4) < 2
        fx, fy = (X % t) / t, (Y % t) / t
        across = np.where(horiz, fy, fx)
        along = np.where(horiz, fx, fy)
        sheen = np.sin(np.pi * across) * (0.6 + 0.4 * np.sin(np.pi * along))
        k = np.where(horiz, sheen, sheen * 0.75)[..., None]
        return c0 * (1 - k) + c1 * k, np.ones(X.shape, np.float32), None
    if kind == "stripes":
        X, Y = grid_xy(sl)
        a = math.radians(float(p.get("angle", 45)))
        sp, sw = float(p.get("spacing", 40)), float(p.get("width", 12))
        u = (X * math.cos(a) + Y * math.sin(a)) % sp
        dd = np.minimum(np.abs(u - sw / 2), sp - np.abs(u - sw / 2))
        alpha = np.clip(sw / 2 - dd + 0.5, 0, 1).astype(np.float32)
        return solid(p.get("colour", p.get("color", "#fff")), X.shape), alpha, None
    if kind == "halftone":
        X, Y = grid_xy(sl)
        sp = float(p.get("spacing", 24))
        a = math.radians(float(p.get("angle", 45)))
        ca, sa = math.cos(a), math.sin(a)
        U, V = X * ca + Y * sa, -X * sa + Y * ca
        cu, cv = (np.floor(U / sp) + 0.5) * sp, (np.floor(V / sp) + 0.5) * sp
        cx, cy = cu * ca - cv * sa, cu * sa + cv * ca
        (fx, fy), (tx, ty) = p["from"], p["to"]
        dx, dy = tx - fx, ty - fy
        t = np.clip(((cx - fx) * dx + (cy - fy) * dy) / max(dx * dx + dy * dy, 1e-6), 0, 1)
        size = float(p.get("max", 1.0)) * (1 - t) + float(p.get("min", 0.0)) * t
        r = sp * 0.72 * size
        dist = np.hypot(U - cu, V - cv)
        alpha = np.clip(r - dist + 0.5, 0, 1).astype(np.float32)
        return solid(p.get("colour", p.get("color", "#000")), X.shape), alpha, None
    die(f"unknown pattern kind '{kind}' (shards, hex, carbon, stripes, halftone)")


_TEX_CACHE: dict = {}


def texture(ctx: Ctx, t: dict, sl):
    """Tile an image (carbon weave, brushed metal, camo...) in template space, so it runs seamlessly across shapes."""
    key = (str(ctx.p(t["file"])), float(t.get("scale", 1.0)), float(t.get("angle", 0)))
    if key not in _TEX_CACHE:
        im = Image.open(ctx.p(t["file"])).convert("RGB")
        sc = key[1]
        if sc != 1.0:
            im = im.resize((max(2, round(im.width * sc)), max(2, round(im.height * sc))), Image.LANCZOS)
        _TEX_CACHE[key] = np.asarray(im, np.float32)
    tile = _TEX_CACHE[key]
    th, tw = tile.shape[:2]
    X, Y = grid_xy(sl)
    a = np.radians(key[2])
    if a:
        X, Y = X * np.cos(a) + Y * np.sin(a), -X * np.sin(a) + Y * np.cos(a)
    rgb = tile[np.mod(Y.astype(np.int64), th), np.mod(X.astype(np.int64), tw)]
    if t.get("tint"):
        tint = np.array(parse_colour(t["tint"]), np.float32) / 255.0
        rgb = rgb * tint
    rgb = rgb * float(t.get("brightness", 1.0))
    return np.clip(rgb, 0, 255), np.ones(X.shape, np.float32), None


def make_fill(ctx: Ctx, fill, sl):
    shape = (sl[0].stop - sl[0].start, sl[1].stop - sl[1].start)
    if isinstance(fill, (str, list, tuple)):
        return solid(fill, shape), np.ones(shape, np.float32), None
    if isinstance(fill, dict) and "gradient" in fill:
        return gradient(fill["gradient"], sl), np.ones(shape, np.float32), None
    if isinstance(fill, dict) and "pattern" in fill:
        return pattern(fill["pattern"], sl, ctx.rng)
    if isinstance(fill, dict) and "texture" in fill:
        return texture(ctx, fill["texture"], sl)
    die(f"bad fill: {fill!r}")


# ---------------------------------------------------------------------------
# compositing
# ---------------------------------------------------------------------------

def composite(albedo, spec, sl, rgb, a, fin, rough=None):
    """Blend rgb (h,w,3) with alpha a (h,w) into albedo/spec windows."""
    a3 = a[..., None]
    albedo[sl] = albedo[sl] * (1 - a3) + rgb * a3
    if fin["rgb"] is not None:
        f = np.empty(rgb.shape, np.float32)
        f[:] = fin["rgb"]
        if fin.get("jitter") or rough is not None:
            off = rough if rough is not None else ctxless_jitter(a.shape, fin["jitter"])
            f[..., 1] = np.clip(f[..., 1] + off, 0, 255)
        spec[sl] = spec[sl] * (1 - a3) + f * a3


_JIT = np.random.default_rng(99)


def ctxless_jitter(shape, j):
    return _JIT.uniform(-j, j, size=shape).astype(np.float32)


def stroke_mask(m, width, position="outside"):
    inside = m > 0.5
    if position == "outside":
        d = ndi.distance_transform_edt(~inside)
        return np.clip(width + 0.5 - d, 0, 1) * (~inside)
    if position == "inside":
        d = ndi.distance_transform_edt(inside)
        return np.clip(width + 0.5 - d, 0, 1) * inside
    d_out = ndi.distance_transform_edt(~inside)
    d_in = ndi.distance_transform_edt(inside)
    d = np.where(inside, d_in, d_out)
    return np.clip(width / 2 + 0.5 - d, 0, 1)


def do_shape(ctx, L, albedo, spec):
    raw = shape_mask(ctx, L)
    cm = clip_mask(ctx, L)
    m = raw if cm is None else raw * cm
    op = float(L.get("opacity", 1.0))
    fin = resolve_finish(L.get("finish"), "keep")
    sl = window(m)
    if sl is not None and L.get("fill") is not None:
        rgb, pa, rough = make_fill(ctx, L["fill"], sl)
        if L.get("grain"):
            g = ctx.rng.normal(0, float(L["grain"]) * 255, size=pa.shape).astype(np.float32)
            rgb = np.clip(rgb + g[..., None], 0, 255)
        composite(albedo, spec, sl, rgb, m[sl] * pa * op, fin, rough)
    st = L.get("stroke")
    if st:
        # stroke follows the shape's own edge, not the panel edge it was clipped to
        sm = stroke_mask(raw, float(st.get("width", 6)), st.get("position", "outside"))
        if cm is not None:
            sm = sm * cm
        ssl = window(sm)
        if ssl is not None:
            sfin = resolve_finish(st.get("finish"), "keep")
            composite(albedo, spec, ssl, solid(st["colour"] if "colour" in st else st["color"], (ssl[0].stop - ssl[0].start, ssl[1].stop - ssl[1].start)),
                      sm[ssl] * op, sfin)
    return m


def prepare_sprite(ctx, L, src: Image.Image, report_el):
    """Trim, recolour, scale, flip, rotate an RGBA sprite. Returns (rgba Image, upscale factor)."""
    src = src.convert("RGBA")
    bb = src.getchannel("A").getbbox()
    if bb is None:
        die(f"{L.get('label')}: image is fully transparent")
    src = src.crop(bb)
    if L.get("recolour") or L.get("recolor"):
        col = parse_colour(L.get("recolour") or L.get("recolor"))
        solid_im = Image.new("RGBA", src.size, col + (255,))
        solid_im.putalpha(src.getchannel("A"))
        src = solid_im
    if "width" in L:
        tw = float(L["width"]); th = tw * src.height / src.width
    elif "height" in L:
        th = float(L["height"]); tw = th * src.width / src.height
    else:
        tw, th = src.width, src.height
    up = max(tw / src.width, th / src.height)
    src = src.resize((max(1, round(tw)), max(1, round(th))), Image.LANCZOS)
    if L.get("flip_x"):
        src = src.transpose(Image.FLIP_LEFT_RIGHT)
    if L.get("flip_y"):
        src = src.transpose(Image.FLIP_TOP_BOTTOM)
    rot = float(L.get("rotation", 0))
    if rot:
        src = src.rotate(rot, resample=Image.BICUBIC, expand=True)
    return src, up


def text_sprite(L) -> Image.Image:
    text = L["text"]
    probe = load_font(L.get("font"), 200)
    cap = probe.getbbox("H")
    cap_h = max(1, cap[3] - cap[1])
    target = float(L.get("height", 100))
    size = max(4, int(round(200 * target / cap_h)))
    font = load_font(L.get("font"), size)
    spacing = float(L.get("letter_spacing", 0)) * size
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + spacing * max(0, len(text) - 1)
    im = Image.new("RGBA", (int(total + size), int(size * 1.6)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = size / 2
    col = parse_colour(L.get("colour", L.get("color", "#fff")))
    for ch, wch in zip(text, widths):
        d.text((x, size * 0.2), ch, font=font, fill=col + (255,))
        x += wch + spacing
    return im


def do_sprite(ctx, L, albedo, spec, checks, sprite_src):
    label = L.get("label") or L.get("file") or L.get("text") or L["type"]
    el = {"label": label, "type": L["type"], "issues": []}
    sprite, up = prepare_sprite(ctx, L, sprite_src, el)
    a_logo = np.asarray(sprite.getchannel("A"), np.float32) / 255.0
    rgb_logo = np.asarray(sprite.convert("RGB"), np.float32)
    ol = L.get("outline")
    pad = int(math.ceil(float(ol.get("width", 6)))) + 2 if ol else 0
    if pad:
        a_logo = np.pad(a_logo, pad)
        rgb_logo = np.pad(rgb_logo, ((pad, pad), (pad, pad), (0, 0)))
    h, w = a_logo.shape
    cx, cy = L["center"]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    S = ctx.S
    # clip to canvas
    sx0, sy0 = max(0, x0), max(0, y0)
    sx1, sy1 = min(S, x0 + w), min(S, y0 + h)
    off_canvas = 0.0
    total = float((a_logo > 0.5).sum()) or 1.0
    if sx1 <= sx0 or sy1 <= sy0:
        el["issues"].append(("ERROR", "entirely off the canvas"))
        checks.append(el)
        return
    lx0, ly0 = sx0 - x0, sy0 - y0
    crop = (slice(ly0, ly0 + (sy1 - sy0)), slice(lx0, lx0 + (sx1 - sx0)))
    off_canvas = 1 - float((a_logo[crop] > 0.5).sum()) / total
    sl = (slice(sy0, sy1), slice(sx0, sx1))
    a_logo_c, rgb_logo_c = a_logo[crop], rgb_logo[crop]

    # outline
    a_out = None
    out_col = None
    if ol:
        a_out = np.clip(float(ol.get("width", 6)) + 0.5 - ndi.distance_transform_edt(a_logo < 0.5), 0, 1)
        a_out = np.maximum(a_out, a_logo)[crop]
    foot = (a_out if a_out is not None else a_logo_c) > 0.5

    # background colour for the contrast check (before painting)
    ring_w = max(8, int(0.15 * min(h, w)))
    ring = ndi.binary_dilation(foot, iterations=ring_w) & ~foot
    bg = np.median(albedo[sl][ring], axis=0) if ring.any() else albedo[sl].reshape(-1, 3).mean(0)
    logo_px = a_logo_c > 0.5
    logo_col = rgb_logo_c[logo_px].mean(0) if logo_px.any() else np.array([0, 0, 0])

    op = float(L.get("opacity", 1.0))
    fin = resolve_finish(L.get("finish"), "sticker")
    if ol:
        oc = ol.get("colour", ol.get("color", "auto"))
        if oc == "auto":
            out_col = (255, 255, 255) if rel_luminance(logo_col) < 0.18 else (0, 0, 0)
        else:
            out_col = parse_colour(oc)
        composite(albedo, spec, sl, solid(out_col, a_out.shape), a_out * op, resolve_finish(ol.get("finish"), fin_name(L, "sticker")))
    composite(albedo, spec, sl, rgb_logo_c, a_logo_c * op, fin)

    # ---- placement checks ---------------------------------------------
    m_on = ctx.labels[sl] > 0
    n_foot = float(foot.sum()) or 1.0
    outside = float((foot & ~m_on).sum()) / n_foot + off_canvas
    isl, cnt = np.unique(ctx.labels[sl][foot & m_on], return_counts=True)
    touched = [int(i) for i, c in zip(isl, cnt) if c / n_foot > 0.002]
    allowed = L.get("allow_seam", False)
    if outside > 0.005 and not allowed:
        el["issues"].append(("ERROR", f"{outside * 100:.1f}% of it is off the paintable area (will be cut off)"))
    if len(touched) > 1 and not allowed:
        el["issues"].append(("ERROR", f"spans {len(touched)} panels {touched} (crosses a seam)"))
    inside_d = ctx.dist[sl][foot & m_on]
    min_edge = float(inside_d.min()) if inside_d.size else 0.0
    if min_edge < ctx.edge_margin and outside <= 0.005:
        el["issues"].append(("WARN", f"only {min_edge:.0f}px from a panel edge (margin {ctx.edge_margin}px) — may wrap or hide"))
    ko = float((foot & ctx.keep[sl]).sum()) / n_foot
    if ko > 0.02:
        el["issues"].append(("WARN", f"{ko * 100:.0f}% overlaps a sim-stamped number/sponsor area"))
    for kl, km, _ in ctx.extra_keepout:
        ov = float((foot & km[sl]).sum()) / n_foot
        if ov > 0.01:
            el["issues"].append(("ERROR", f"{ov * 100:.0f}% inside keep-out '{kl}'"))
    dens = float(ctx.density[sl][foot].mean()) if foot.any() else 0
    if dens > 0.7:
        el["issues"].append(("WARN", f"sits on a curved/complex area (curvature {dens:.2f}) — expect distortion"))
    eff = contrast_ratio(logo_col, bg)
    if out_col is not None:
        eff = max(eff, contrast_ratio(logo_col, out_col))
    if eff < 1.5:
        el["issues"].append(("ERROR", f"almost invisible: contrast {eff:.1f}:1 against its background"))
    elif eff < 3.0:
        el["issues"].append(("WARN", f"low contrast {eff:.1f}:1 — recolour it or add an outline"))
    ys, xs = np.nonzero(foot)
    fh, fw = (ys.max() - ys.min() + 1, xs.max() - xs.min() + 1) if ys.size else (0, 0)
    if min(fh, fw) < 40:
        el["issues"].append(("WARN", f"small ({fw}x{fh}px) — unreadable in the sim beyond a few metres"))
    if up > 1.5 and L["type"] == "logo":
        el["issues"].append(("WARN", f"source image upscaled {up:.1f}x — will look soft; get a bigger/vector logo"))
    el.update({
        "bbox": [int(sx0 + xs.min()), int(sy0 + ys.min()), int(sx0 + xs.max() + 1), int(sy0 + ys.max() + 1)] if ys.size else None,
        "center": [cx, cy], "size": [int(fw), int(fh)], "islands": touched, "min_edge_px": round(min_edge),
        "contrast": round(eff, 2), "file": L.get("file"),
    })
    checks.append(el)


def fin_name(L, default):
    f = L.get("finish", default)
    return f if f is not None else default


def do_image(ctx, L, albedo, spec):
    im = Image.open(ctx.p(L["file"])).convert("RGBA")
    S = ctx.S
    if L.get("full_canvas"):
        if im.size != (S, S):
            im = im.resize((S, S), Image.LANCZOS)
        x0 = y0 = 0
    else:
        if "width" in L:
            im = im.resize((int(L["width"]), int(round(L["width"] * im.height / im.width))), Image.LANCZOS)
        if L.get("rotation"):
            im = im.rotate(float(L["rotation"]), resample=Image.BICUBIC, expand=True)
        if "center" in L:
            x0, y0 = int(L["center"][0] - im.width / 2), int(L["center"][1] - im.height / 2)
        else:
            x0, y0 = L.get("position", [0, 0])
    a = np.asarray(im.getchannel("A"), np.float32) / 255.0 * float(L.get("opacity", 1.0))
    rgb = np.asarray(im.convert("RGB"), np.float32)
    sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(S, x0 + im.width), min(S, y0 + im.height)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    crop = (slice(sy0 - y0, sy1 - y0), slice(sx0 - x0, sx1 - x0))
    composite(albedo, spec, (slice(sy0, sy1), slice(sx0, sx1)), rgb[crop], a[crop], resolve_finish(L.get("finish"), "keep"))


# ---------------------------------------------------------------------------
# proof
# ---------------------------------------------------------------------------

def make_proof(ctx, albedo_img, checks, out):
    S = ctx.S
    base = albedo_img.convert("RGBA")
    over = np.zeros((S, S, 4), np.uint8)
    over[ctx.lines] = (0, 0, 0, 70)
    edges = ctx.labels != ndi.grey_erosion(ctx.labels, size=(5, 5))
    edges &= ctx.labels > 0
    over[edges] = (0, 230, 255, 255)
    yy, xx = np.mgrid[0:S, 0:S]
    hatch = ((xx + yy) // 10) % 3 == 0
    over[ctx.keep & hatch] = (255, 0, 60, 170)
    for _, km, _ in ctx.extra_keepout:
        over[km & hatch] = (255, 0, 255, 200)
    img = Image.alpha_composite(base, Image.fromarray(over, "RGBA"))
    v = to_view(img)
    draw_grid(v, S)
    d = ImageDraw.Draw(v, "RGBA")
    sc = v.width / S
    f = label_font(15)
    for lbl, _, poly in ctx.extra_keepout:
        x, y = poly[0]
        d.text((x * sc, y * sc), lbl, fill=(255, 0, 255), font=f, stroke_width=2, stroke_fill="black")
    for el in checks:
        if not el.get("bbox"):
            continue
        sev = worst(el)
        col = {"ERROR": (255, 30, 30), "WARN": (255, 190, 0), "OK": (40, 220, 80)}[sev]
        x0, y0, x1, y1 = [c * sc for c in el["bbox"]]
        d.rectangle([x0, y0, x1, y1], outline=col + (255,), width=2)
        d.text((x0, max(0, y0 - 16)), el["label"][:28], fill=col + (255,), font=f, stroke_width=2, stroke_fill="black")
    v.convert("RGB").save(out)


def worst(el):
    sevs = [s for s, _ in el["issues"]]
    return "ERROR" if "ERROR" in sevs else ("WARN" if "WARN" in sevs else "OK")


# ---------------------------------------------------------------------------
# design hints
# ---------------------------------------------------------------------------

def design_hints(ctx, spec, checks):
    hints = []
    layers = spec.get("layers", [])
    finishes = {json.dumps(spec.get("base", {}).get("finish", "gloss"))}
    shapes = 0
    colours = set()
    for L in layers:
        if L.get("finish") not in (None, "keep"):
            finishes.add(json.dumps(L["finish"]))
        if L["type"] == "shape":
            shapes += 1
            if isinstance(L.get("fill"), str):
                colours.add(L["fill"].lower())
            f = resolve_finish(L.get("finish"), "keep")["rgb"]
            if f and f[0] > 200 and isinstance(L.get("fill"), str) and rel_luminance(parse_colour(L["fill"])) < 0.05:
                hints.append(f"'{L.get('label', 'shape')}' is metallic over a very dark colour — it will read near-black; lighten the albedo.")
    if spec.get("base", {}).get("colour") or spec.get("base", {}).get("color"):
        colours.add(str(spec["base"].get("colour", spec["base"].get("color"))).lower())
    if len(finishes) < 2:
        hints.append("Spec map is one uniform finish. Finish contrast (gloss vs matte vs metallic zones) is the cheapest way to stop a livery looking flat.")
    if shapes < 2:
        hints.append("Body is close to a single flat colour. Add one dominant graphic that runs nose to tail, plus a dark grounding colour low on the car.")
    if len(colours) > 5:
        hints.append(f"{len(colours)} solid colours used — more than 3 main colours plus black/white usually reads as busy.")
    area = sum((c["size"][0] * c["size"][1]) for c in checks if c.get("size"))
    if area > 0.35 * float((ctx.labels > 0).sum()):
        hints.append("Logos/text cover over a third of the body — cluttered. Fewer, bigger logos with clear space read better.")
    files = {}
    for c in checks:
        if c.get("file"):
            files.setdefault(c["file"], []).append(c)
    for fname, els in files.items():
        for i in range(len(els)):
            for j in range(i + 1, len(els)):
                a, b = els[i], els[j]
                dd = math.dist(a["center"], b["center"])
                if dd < 2.5 * max(a["size"] + b["size"]) and set(a["islands"]) & set(b["islands"]):
                    b["issues"].append(("WARN", f"same logo as '{a['label']}' only {dd:.0f}px away on the same panel"))
    return hints


# ---------------------------------------------------------------------------
# twins: render a layer again on the mirrored panel (e.g. right side -> left side)
# ---------------------------------------------------------------------------

def transform_layer(L: dict, name: str, T: dict) -> dict:
    import copy
    sx, sy = T["scale"]
    ox, oy = T["offset"]
    imap = {int(k): int(v) for k, v in T.get("islands", {}).items()}
    mirrored = sx * sy < 0

    def pt(p):
        return [sx * p[0] + ox, sy * p[1] + oy]

    def rect(r):
        (x0, y0), (x1, y1) = pt(r[:2]), pt(r[2:])
        return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]

    def isl(ids):
        return [imap.get(int(i), int(i)) for i in ids]

    L2 = copy.deepcopy(L)
    L2.pop("twin", None)
    L2["label"] = f"{L.get('label', L['type'])} [{name}]"
    if "points" in L2:
        L2["points"] = [pt(p) for p in L2["points"]]
    if "rect" in L2:
        L2["rect"] = rect(L2["rect"])
    if L2.get("clip_region"):
        cr = L2["clip_region"]
        L2["clip_region"] = rect(cr) if (len(cr) == 4 and not isinstance(cr[0], (list, tuple))) else [pt(p) for p in cr]
    if "center" in L2:
        L2["center"] = pt(L2["center"])
    if "islands" in L2:
        L2["islands"] = isl(L2["islands"])
    if isinstance(L2.get("clip"), list):
        L2["clip"] = isl(L2["clip"])
    fill = L2.get("fill")
    if isinstance(fill, dict):
        g = fill.get("gradient") or fill.get("pattern")
        if g is not None:
            for k in ("from", "to"):
                if k in g:
                    g[k] = pt(g[k])
            if mirrored and g.get("kind") in ("stripes", "halftone"):
                g["angle"] = -float(g.get("angle", 45))
    if L2["type"] in ("logo", "text", "image"):
        # The other side of the car is a 3D mirror image, so a plain template mirror would make text read
        # backwards there. Add one more flip along the car's length ("sprite_flip") so it reads correctly.
        # "twin_mirror": a graphic (not text) that should be a true mirror image on the other side, e.g. pointing nose-wards
        sf = "none" if L.get("twin_mirror") else T.get("_sprite_flip", "none")
        ex, ey = {"x": (-1, 1), "y": (1, -1), "none": (1, 1)}[sf]
        dx, dy = sx * ex, sy * ey
        rot = float(L2.get("rotation", 0))
        if dx == -1 and dy == -1:
            L2["rotation"] = rot + 180
        elif dx == -1:
            L2["flip_x"] = not L2.get("flip_x", False)
            L2["rotation"] = -rot
        elif dy == -1:
            L2["flip_y"] = not L2.get("flip_y", False)
            L2["rotation"] = -rot
    return L2


def resolve_sprite_flip(T: dict, labels: np.ndarray) -> str:
    """'auto' = flip along the target panel's long axis (the car's length on side panels)."""
    sf = T.get("sprite_flip", "auto")
    if sf != "auto":
        return sf
    targets = [int(v) for v in T.get("islands", {}).values()]
    if not targets:
        return "none"
    ys, xs = np.nonzero(np.isin(labels, targets))
    if ys.size == 0:
        return "none"
    return "x" if (xs.max() - xs.min()) >= (ys.max() - ys.min()) else "y"


def expand_twins(spec: dict, labels: np.ndarray) -> list:
    tdefs = {k: dict(v) for k, v in spec.get("transforms", {}).items()}
    for T in tdefs.values():
        T["_sprite_flip"] = resolve_sprite_flip(T, labels)
    out = []
    for L in spec.get("layers", []):
        out.append(L)
        tw = L.get("twin")
        if not tw:
            continue
        for name in ([tw] if isinstance(tw, str) else tw):
            if name not in tdefs:
                die(f"layer '{L.get('label')}' asks for twin '{name}' but \"transforms\" has no '{name}'")
            out.append(transform_layer(L, name, tdefs[name]))
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def next_version_dir(base: Path) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    nums = [int(m.group(1)) for p in base.iterdir() if (m := re.fullmatch(r"v(\d+)", p.name))]
    return base / f"v{(max(nums) + 1) if nums else 1:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("livery_json")
    ap.add_argument("--out")
    args = ap.parse_args()
    sp = Path(args.livery_json).resolve()
    spec = read_json(sp)
    ctx = Ctx(sp, spec)
    S = ctx.S
    cid = str(spec.get("customer_id", "000000"))
    if not cid.isdigit():
        die("customer_id must be your numeric iRacing customer ID")
    out = Path(args.out) if args.out else next_version_dir(sp.parent / "builds")
    out.mkdir(parents=True, exist_ok=True)
    (out / "crops").mkdir(exist_ok=True)

    base = spec.get("base", {})
    albedo = np.empty((S, S, 3), np.float32)
    albedo[:] = parse_colour(base.get("colour", base.get("color", "#808080")))
    spec_img = np.empty((S, S, 3), np.float32)
    if spec.get("spec_base"):
        sb = Image.open(ctx.p(spec["spec_base"])).convert("RGB").resize((S, S))
        spec_img[:] = np.asarray(sb, np.float32)
    else:
        spec_img[:] = resolve_finish(base.get("finish", "gloss"))["rgb"]

    checks = []
    for i, L in enumerate(expand_twins(spec, ctx.labels)):
        if L.get("hidden"):
            continue
        t = L.get("type")
        if t == "shape":
            do_shape(ctx, L, albedo, spec_img)
        elif t == "logo":
            do_sprite(ctx, L, albedo, spec_img, checks, Image.open(ctx.p(L["file"])))
        elif t == "text":
            do_sprite(ctx, L, albedo, spec_img, checks, text_sprite(L))
        elif t == "image":
            do_image(ctx, L, albedo, spec_img)
        else:
            die(f"layer {i}: unknown type '{t}' (shape, logo, text, image)")

    alb = Image.fromarray(np.clip(albedo, 0, 255).astype(np.uint8), "RGB")
    spc = Image.fromarray(np.clip(spec_img, 0, 255).astype(np.uint8), "RGB")
    paint_name = f"car_{cid}.tga"
    save_tga(alb, out / paint_name)
    if spec.get("custom_number"):
        save_tga(alb, out / f"car_num_{cid}.tga")
    save_tga(spc, out / f"car_spec_{cid}.tga")
    to_view(alb).save(out / "preview.png")
    to_view(spc).save(out / "spec_preview.png")

    hints = design_hints(ctx, spec, checks)
    make_proof(ctx, alb, checks, out / "proof.png")
    for el in checks:
        if el.get("bbox"):
            x0, y0, x1, y1 = el["bbox"]
            p = 24
            c = alb.crop((max(0, x0 - p), max(0, y0 - p), min(S, x1 + p), min(S, y1 + p)))
            if max(c.size) > 640:
                c.thumbnail((640, 640), Image.LANCZOS)
            safe = re.sub(r"[^A-Za-z0-9_-]+", "_", el["label"])[:40]
            c.save(out / "crops" / f"{safe}.png")
    shutil.copy(sp, out / "livery.json")

    n_err = sum(1 for c in checks for s, _ in c["issues"] if s == "ERROR")
    n_warn = sum(1 for c in checks for s, _ in c["issues"] if s == "WARN")
    report = {
        "build": out.name, "customer_id": cid, "errors": n_err, "warnings": n_warn,
        "files": sorted(p.name for p in out.glob("*.tga")),
        "elements": [{**{k: v for k, v in c.items() if k != "issues"}, "status": worst(c),
                      "issues": [f"{s}: {m}" for s, m in c["issues"]]} for c in checks],
        "design_hints": hints,
    }
    write_json(out / "report.json", report)

    print(f"build {out.name} -> {out}")
    print(f"  {', '.join(report['files'])}")
    print(f"\nPLACEMENT CHECKS ({len(checks)} elements): {n_err} errors, {n_warn} warnings")
    for c in checks:
        st = worst(c)
        print(f"  [{st:5}] {c['label'][:30]:30} panel(s) {c.get('islands')} size {c.get('size')} contrast {c.get('contrast')}")
        for s, m in c["issues"]:
            print(f"           {s}: {m}")
    if hints:
        print("\nDESIGN HINTS:")
        for h in hints:
            print(f"  - {h}")
    print(f"\nlook at: {out / 'proof.png'}  and  {out / 'preview.png'}")
    if n_err:
        print("Fix the errors before installing (install_paint.py refuses builds with errors unless --force).")


if __name__ == "__main__":
    main()
