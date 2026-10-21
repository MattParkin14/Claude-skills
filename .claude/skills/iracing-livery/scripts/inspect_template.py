#!/usr/bin/env python3
"""Inspect an iRacing paint template (.zip / .psd) and export the maps the build step needs.

Usage:
  python inspect_template.py TEMPLATE.zip|TEMPLATE.psd OUT_DIR [--mask-layer NAME] [--wire-layer NAME]
                             [--keepout-layer NAME ...] [--edge-margin 24] [--min-island 0.0008]

Writes to OUT_DIR:
  layers.json         every layer: path, kind, visibility, bbox, blend mode, guessed role
  composite.png       the PSD as it currently displays (incl. guide layers)
  artwork.png         visible artwork with guide / spec groups hidden (what a TGA export would show)
  wire_mask.png       wireframe lines (white = line)
  mask.png            paintable area (white = on the car)
  keepout.png         areas the sim stamps numbers/sponsors onto (white = keep clear)
  numbers.png         just the number blocks;  stamps.png  just the sponsor/series stamps
  spec_base.png       the template's own spec-map group, if it has one
  islands_labels.png  16-bit label image, pixel value = island id (0 = off-car)
  islands.json        per island: bbox, area, centroid, max inset, safe box, curvature proxy; plus "twins":
                      island pairs with the same shape (e.g. left/right sides) and the transform between them
  view_template.png   1024px artwork + wireframe + coordinate grid (for looking at)
  view_islands.png    1024px island map with ids
  view_safezones.png  1024px logo-safety heat map (green = good, red = risky)
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent))
from livery_lib import draw_grid, label_font, to_view, write_json, die  # noqa: E402

ROLE_RULES = [
    ("wireframe", re.compile(r"wire", re.I)),
    ("mask", re.compile(r"(car\s*mask|^mask$|paint\s*mask|body\s*mask|uv\s*mask)", re.I)),
    ("numbers", re.compile(r"number", re.I)),
    ("stamps", re.compile(r"(sponsor|contingency|stamp|decal|series|club)", re.I)),
    ("spec", re.compile(r"spec", re.I)),
    ("turnoff", re.compile(r"turn\s*off|do\s*not\s*export|guide", re.I)),
]


def extract_psd(src: Path, out: Path) -> Path:
    if src.suffix.lower() == ".psd":
        return src
    if src.suffix.lower() != ".zip":
        die("template must be a .psd or the .zip iRacing gives you")
    dest = out / "template"
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as z:
        psds = [n for n in z.namelist() if n.lower().endswith(".psd") and not n.startswith("__MACOSX")]
        if not psds:
            die(f"no .psd inside {src.name}: {z.namelist()[:10]}")
        name = max(psds, key=lambda n: z.getinfo(n).file_size)
        target = dest / Path(name).name
        with z.open(name) as fsrc, open(target, "wb") as fdst:
            shutil.copyfileobj(fsrc, fdst)
    print(f"extracted {name} -> {target}")
    return target


def layer_path(layer, root):
    parts = []
    p = layer
    while p is not None and p is not root:
        parts.append(p.name)
        p = p.parent
    return "/".join(reversed(parts))


def ancestors(layer, root):
    out = []
    p = layer.parent
    while p is not None and p is not root:
        out.append(p)
        p = p.parent
    return out


def guess_role(layer, root):
    name = layer.name or ""
    in_paintable = any(re.search(r"paintable", a.name or "", re.I) for a in ancestors(layer, root))
    for role, rx in ROLE_RULES:
        if rx.search(name):
            if role == "stamps" and in_paintable:
                return "art"  # decals inside the paintable-area group are optional artwork, not sim stamps
            if role == "spec" and not layer.is_group() and not any(rx.search(a.name or "") for a in ancestors(layer, root)):
                continue  # a stray layer mentioning "spec" is not the spec group
            return role
    for a in ancestors(layer, root):
        if ROLE_RULES[4][1].search(a.name or ""):
            return "spec-part"
        if ROLE_RULES[5][1].search(a.name or ""):
            return "guide"
    return "art"


def render(psd, targets, force=True):
    """Composite only the given layers (and their visible children) onto a full-canvas RGBA image."""
    tids = {id(t) for t in targets}
    anc = set()
    for t in targets:
        for a in ancestors(t, psd):
            anc.add(id(a))

    def flt(layer):
        if id(layer) in tids:
            return True if force else layer.is_visible()
        if id(layer) in anc:
            return True
        for a in ancestors(layer, psd):
            if id(a) in tids:
                return layer.visible
        return False

    im = psd.composite(viewport=(0, 0, psd.width, psd.height), layer_filter=flt)
    if im is None:
        return Image.new("RGBA", psd.size, (0, 0, 0, 0))
    return im.convert("RGBA")


def lines_from_render(im: Image.Image) -> np.ndarray:
    a = np.array(im.getchannel("A")).astype(np.int16)
    if a.min() < 200 and (a > 64).mean() < 0.6:
        return a > 64
    lum = np.array(im.convert("L")).astype(np.int16)
    dark = lum < 110
    light = lum > 145
    return dark if dark.mean() < light.mean() else light


def mask_from_render(im: Image.Image) -> np.ndarray:
    a = np.array(im.getchannel("A"))
    if a.min() < 200 and 0.02 < (a > 127).mean() < 0.98:
        return a > 127
    lum = np.array(im.convert("L"))
    on = lum > 127
    # the paintable area is normally the minority or the white side; if most of the canvas is "on", flip
    if on.mean() > 0.97 or on.mean() < 0.03:
        sat = np.array(im.convert("HSV").getchannel("S")) > 60
        if 0.03 < sat.mean() < 0.97:
            return sat
    return on


def mask_from_wire(lines: np.ndarray) -> np.ndarray:
    closed = ndi.binary_closing(lines, structure=np.ones((3, 3)), iterations=12)
    filled = ndi.binary_fill_holes(closed)
    return ndi.binary_opening(filled, iterations=2)


def find_twins(labels, islands, min_match=0.9):
    """Find island pairs that are the same shape (translated and/or mirrored), e.g. the two car sides."""
    out = []
    rng = np.random.default_rng(0)
    for a in islands:
        for b in islands:
            if b["id"] <= a["id"]:
                continue
            if not (0.9 < a["area_px"] / b["area_px"] < 1.11):
                continue
            ax0, ay0, ax1, ay1 = a["bbox"]
            bx0, by0, bx1, by1 = b["bbox"]
            if abs((ax1 - ax0) - (bx1 - bx0)) > 0.05 * (ax1 - ax0) + 4 or abs((ay1 - ay0) - (by1 - by0)) > 0.05 * (ay1 - ay0) + 4:
                continue
            ys, xs = np.nonzero(labels[ay0:ay1, ax0:ax1] == a["id"])
            if ys.size > 60000:
                pick = rng.choice(ys.size, 60000, replace=False)
                ys, xs = ys[pick], xs[pick]
            xs, ys = xs + ax0, ys + ay0
            scored = []
            for sx in (1, -1):
                for sy in (1, -1):
                    ox = (bx0 - ax0) if sx == 1 else (ax0 + bx1 - 1)
                    oy = (by0 - ay0) if sy == 1 else (ay0 + by1 - 1)
                    tx, ty = sx * xs + ox, sy * ys + oy
                    ok = (tx >= 0) & (ty >= 0) & (tx < labels.shape[1]) & (ty < labels.shape[0])
                    hit = np.zeros(xs.shape, bool)
                    hit[ok] = labels[ty[ok], tx[ok]] == b["id"]
                    scored.append((float(hit.mean()), sx, sy, ox, oy))
            scored.sort(reverse=True)
            best = scored[0]
            if best[0] < min_match:
                continue
            kind = {(1, 1): "translated copy", (-1, 1): "mirrored left-right", (1, -1): "mirrored top-bottom",
                    (-1, -1): "rotated 180°"}[(best[1], best[2])]
            out.append({"from": a["id"], "to": b["id"], "kind": kind, "match": round(best[0], 3),
                        "ambiguous": scored[1][0] > best[0] - 0.02,
                        "transform": {"scale": [best[1], best[2]], "offset": [int(best[3]), int(best[4])],
                                      "islands": {str(a["id"]): b["id"]}}})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("template")
    ap.add_argument("out")
    ap.add_argument("--mask-layer", help="exact layer/group name to use as the paintable mask")
    ap.add_argument("--wire-layer", help="exact layer/group name to use as the wireframe")
    ap.add_argument("--keepout-layer", action="append", default=[], help="layer to treat as a sim-stamped area (repeatable)")
    ap.add_argument("--edge-margin", type=int, default=24, help="px a logo should stay from a panel edge (default 24)")
    ap.add_argument("--min-island", type=float, default=0.0008, help="drop islands smaller than this fraction of the canvas")
    args = ap.parse_args()

    try:
        from psd_tools import PSDImage
    except ImportError:
        die("psd-tools is missing: pip install psd-tools numpy scipy pillow")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    psd_path = extract_psd(Path(args.template), out)
    print(f"opening {psd_path} ...")
    psd = PSDImage.open(psd_path)
    W, H = psd.width, psd.height
    print(f"canvas {W}x{H}, colour mode {psd.color_mode}")
    if (W, H) not in ((2048, 2048), (1024, 1024)):
        print(f"WARNING: unusual canvas size {W}x{H}; iRacing paints are 2048x2048 (or legacy 1024x1024)")

    # ---- layer inventory -------------------------------------------------
    inv = []
    by_role: dict[str, list] = {}
    for layer in psd.descendants():
        role = guess_role(layer, psd)
        inv.append({
            "path": layer_path(layer, psd), "name": layer.name, "kind": layer.kind,
            "visible": bool(layer.visible), "bbox": list(layer.bbox),
            "blend": str(layer.blend_mode).split(".")[-1], "opacity": layer.opacity, "role": role,
        })
        by_role.setdefault(role, []).append(layer)
    write_json(out / "layers.json", inv)
    print("\nLAYER TREE (role in brackets):")
    for e in inv:
        depth = e["path"].count("/")
        vis = "" if e["visible"] else " (hidden)"
        print(f"  {'  ' * depth}- {e['name']} [{e['role']}] {e['kind']}{vis}")

    def pick(names, role):
        if names:
            found = [l for l in psd.descendants() if l.name in names]
            if not found:
                die(f"layer(s) {names} not found")
            return found
        return by_role.get(role, [])

    # ---- full composites -------------------------------------------------
    print("\nrendering composites ...")
    comp = psd.composite(viewport=(0, 0, W, H)).convert("RGBA")
    comp.save(out / "composite.png")
    guide_ids = set()
    for l in psd.descendants():
        if guess_role(l, psd) in ("turnoff", "spec") and l.is_group():
            guide_ids.add(id(l))

    def art_filter(layer):
        if id(layer) in guide_ids:
            return False
        if any(id(a) in guide_ids for a in ancestors(layer, psd)):
            return False
        if guess_role(layer, psd) in ("wireframe", "mask", "numbers", "stamps"):
            return False
        return layer.is_visible()

    art = psd.composite(viewport=(0, 0, W, H), layer_filter=art_filter)
    art = (art or Image.new("RGB", (W, H), (128, 128, 128))).convert("RGB")
    art.save(out / "artwork.png")

    # ---- wireframe -------------------------------------------------------
    wires = pick([args.wire_layer] if args.wire_layer else None, "wireframe")
    if wires:
        lines = lines_from_render(render(psd, wires))
        print(f"wireframe from: {[l.name for l in wires]} ({lines.mean() * 100:.1f}% of canvas)")
    else:
        lines = np.zeros((H, W), bool)
        print("WARNING: no wireframe layer found (pass --wire-layer NAME). Curvature checks will be skipped.")
    Image.fromarray((lines * 255).astype(np.uint8)).save(out / "wire_mask.png")

    # ---- paintable mask --------------------------------------------------
    masks = pick([args.mask_layer] if args.mask_layer else None, "mask")
    if masks:
        mask = mask_from_render(render(psd, masks))
        src = f"layer {[l.name for l in masks]}"
    elif lines.any():
        mask = mask_from_wire(lines)
        src = "wireframe (closed + hole-filled)"
    else:
        mask = np.ones((H, W), bool)
        src = "NONE FOUND - whole canvas assumed"
    # Some templates' "Mask" layer covers the area OFF the car (it masks the background out). Wireframe lines only
    # exist on the car, so if most of them fall outside the mask, the mask is inverted.
    if masks and lines.any():
        inside = float((lines & mask).sum()) / float(lines.sum())
        if inside < 0.5:
            mask = ~mask
            src += f" (inverted: only {inside * 100:.0f}% of wireframe was inside it)"
        elif inside < 0.85:
            print(f"WARNING: only {inside * 100:.0f}% of the wireframe lies inside the mask; check view_islands.png")
    cover = mask.mean()
    print(f"paintable mask from {src}: {cover * 100:.1f}% of canvas")
    if cover > 0.9 or cover < 0.1:
        print("WARNING: mask coverage looks wrong. Look at view_islands.png and re-run with --mask-layer NAME.")
    Image.fromarray((mask * 255).astype(np.uint8)).save(out / "mask.png")

    # ---- keep-out (sim-stamped areas) -------------------------------------
    def coverage(layers):
        acc = np.zeros((H, W), bool)
        for l in layers:
            im = render(psd, [l])
            a = np.array(im.getchannel("A")) > 40
            if a.mean() > 0.6:  # opaque layer: use non-background pixels instead
                lum = np.array(im.convert("L"))
                a = np.abs(lum.astype(int) - int(np.median(lum))) > 30
            acc |= a
        return acc

    if args.keepout_layer:
        num_layers, stamp_layers = pick(args.keepout_layer, "numbers"), []
    else:
        num_layers, stamp_layers = by_role.get("numbers", []), by_role.get("stamps", [])
    numbers = coverage(num_layers)
    stamps = coverage(stamp_layers)
    keep = numbers | stamps
    print(f"number areas from {[l.name for l in num_layers] or 'nothing'}: {numbers.mean() * 100:.2f}% of canvas")
    print(f"stamped sponsor areas from {[l.name for l in stamp_layers] or 'nothing'}: {stamps.mean() * 100:.2f}% of canvas")
    Image.fromarray((numbers * 255).astype(np.uint8)).save(out / "numbers.png")
    Image.fromarray((stamps * 255).astype(np.uint8)).save(out / "stamps.png")
    Image.fromarray((keep * 255).astype(np.uint8)).save(out / "keepout.png")

    # ---- spec base -------------------------------------------------------
    specs = [l for l in by_role.get("spec", []) if l.is_group()] or by_role.get("spec", [])
    if specs:
        render(psd, specs[:1]).convert("RGB").save(out / "spec_base.png")
        print(f"spec base from '{specs[0].name}' -> spec_base.png (check it: R = metallic, G = roughness, B = clearcoat)")

    # ---- islands ---------------------------------------------------------
    clean = ndi.binary_opening(mask, iterations=1)
    lab, n = ndi.label(clean)
    sizes = ndi.sum(clean, lab, index=np.arange(1, n + 1))
    keep_ids = [i + 1 for i, s in enumerate(sizes) if s >= args.min_island * W * H]
    keep_ids.sort(key=lambda i: -sizes[i - 1])
    remap = np.zeros(n + 1, np.uint16)
    for new, old in enumerate(keep_ids, start=1):
        remap[old] = new
    labels = remap[lab]
    Image.fromarray(labels.astype(np.uint16)).save(out / "islands_labels.png")

    dist = ndi.distance_transform_edt(labels > 0)
    density = ndi.uniform_filter(lines.astype(np.float32), size=65)
    on = labels > 0
    dnorm = float(np.percentile(density[on], 95)) if on.any() and density[on].max() > 0 else 1.0
    islands = []
    objs = ndi.find_objects(labels)
    for i, sl in enumerate(objs, start=1):
        if sl is None:
            continue
        sub = labels[sl] == i
        ys, xs = np.nonzero(sub)
        y0, x0 = sl[0].start, sl[1].start
        d = dist[sl] * sub
        safe = d >= args.edge_margin
        sy, sx = np.nonzero(safe)
        dens = float(density[sl][sub].mean() / dnorm) if dnorm else 0.0
        islands.append({
            "id": i,
            "bbox": [int(x0 + xs.min()), int(y0 + ys.min()), int(x0 + xs.max() + 1), int(y0 + ys.max() + 1)],
            "area_px": int(sub.sum()),
            "centroid": [int(x0 + xs.mean()), int(y0 + ys.mean())],
            "max_inset_px": int(d.max()),
            "safe_bbox": ([int(x0 + sx.min()), int(y0 + sy.min()), int(x0 + sx.max() + 1), int(y0 + sy.max() + 1)]
                          if sy.size else None),
            "curvature_proxy": round(dens, 2),
            "panel": None,
            "notes": "",
        })
    twins = find_twins(labels, islands)
    write_json(out / "islands.json", {"canvas": [W, H], "edge_margin": args.edge_margin, "islands": islands, "twins": twins})

    # ---- views -----------------------------------------------------------
    f = label_font(22)
    view = art.convert("RGBA")
    wire_rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wire_rgba.putalpha(Image.fromarray((lines * 150).astype(np.uint8)))
    view = Image.alpha_composite(view, wire_rgba)
    v = to_view(view)
    draw_grid(v, W)
    v.convert("RGB").save(out / "view_template.png")

    rng = np.random.default_rng(7)
    pal = rng.integers(60, 230, size=(len(islands) + 1, 3)).astype(np.uint8)
    pal[0] = (25, 25, 25)
    isl = Image.fromarray(pal[labels])
    ko = Image.fromarray((keep * 255).astype(np.uint8))
    isl.paste((255, 0, 0), mask=ko.point(lambda p: 110 if p else 0))
    vi = to_view(isl.convert("RGBA"))
    draw_grid(vi, W)
    d = ImageDraw.Draw(vi)
    sc = vi.width / W
    for it in islands:
        cx, cy = it["centroid"]
        d.text((cx * sc, cy * sc), str(it["id"]), fill="white", font=f, anchor="mm", stroke_width=3, stroke_fill="black")
    vi.convert("RGB").save(out / "view_islands.png")

    score = np.clip(dist / max(args.edge_margin * 3, 1), 0, 1) * np.clip(1 - density / (dnorm * 1.2), 0, 1)
    score[~on] = 0
    heat = np.zeros((H, W, 3), np.uint8)
    heat[..., 0] = (255 * (1 - score)).astype(np.uint8)
    heat[..., 1] = (220 * score).astype(np.uint8)
    heat[~on] = (20, 20, 20)
    heat[keep] = (heat[keep] * 0.4 + np.array([200, 0, 200]) * 0.6).astype(np.uint8)
    vs = to_view(Image.fromarray(heat).convert("RGBA"))
    draw_grid(vs, W)
    d = ImageDraw.Draw(vs)
    for it in islands:
        cx, cy = it["centroid"]
        d.text((cx * sc, cy * sc), str(it["id"]), fill="white", font=f, anchor="mm", stroke_width=3, stroke_fill="black")
    vs.convert("RGB").save(out / "view_safezones.png")

    # ---- summary ---------------------------------------------------------
    print(f"\n{len(islands)} islands (largest first). safe_bbox = area at least {args.edge_margin}px inside the edge:")
    print(f"  {'id':>3} {'bbox':<26} {'area':>9} {'inset':>6} {'curv':>5}")
    for it in islands:
        print(f"  {it['id']:>3} {str(it['bbox']):<26} {it['area_px']:>9} {it['max_inset_px']:>6} {it['curvature_proxy']:>5}")
    if twins:
        print("\ngeometric twins (same shape, e.g. left/right sides) — usable as a livery.json transform:")
        for t in twins:
            print(f"  island {t['from']} -> {t['to']}: {t['kind']} (match {t['match']}); "
                  f"\"scale\": {t['transform']['scale']}, \"offset\": {t['transform']['offset']}"
                  + ("  [AMBIGUOUS: symmetric shape, confirm with the locator]" if t["ambiguous"] else ""))
    print(f"\nwrote {out}/ — next: look at view_template.png, view_islands.png, view_safezones.png, "
          f"then fill in 'panel' for each island in islands.json (or car_notes.md).")


if __name__ == "__main__":
    main()
