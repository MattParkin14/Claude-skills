# livery.json format

`build_livery.py` turns this file into the paint and spec map. All coordinates are **template pixels**
(0–2048, origin top-left, as in `view_template.png`'s grid). Relative paths resolve from the folder
that holds `livery.json`.

Layers draw in order, so the first layer is lowest. A typical stack:
1. base colour
2. big colour fields and the main graphic
3. patterns and textures
4. pinstripes
5. logos
6. text

## Top level

```json
{
  "customer_id": "123456",
  "inspect_dir": "../../_cars/mx5 mx52016/inspect",
  "edge_margin": 24,
  "seed": 1,
  "custom_number": false,
  "base": {"colour": "#0b1f3a", "finish": "gloss"},
  "spec_base": null,
  "keep_out_extra": [
    {"label": "under rear wing", "polygon": [[1400,1450],[1900,1450],[1900,1520],[1400,1520]]}
  ],
  "layers": [ ... ]
}
```

| key | meaning |
|---|---|
| `customer_id` | The user's numeric iRacing customer ID. It sets the output file names. |
| `inspect_dir` | The folder `inspect_template.py` wrote. Needs `mask.png`, `islands_labels.png`, `wire_mask.png` and `keepout.png`. |
| `edge_margin` | How many px a logo should stay inside a panel edge. Default 24; use 32–40 on curvy cars. |
| `seed` | Random seed for patterns. Change it to get a different shard layout. |
| `custom_number` | When true, also writes `car_num_<id>.tga`. Use it when the number is painted on the car yourself. |
| `base` | Colour and finish for the whole canvas. Extend beyond the islands; it is the "bleed". |
| `spec_base` | Optional image to start the spec map from, e.g. `inspect/spec_base.png`. When set, `base.finish` is ignored. |
| `keep_out_extra` | Polygons logos must avoid, such as hidden areas found from screenshots. Copy them from `car_notes.md`. |
| `transforms` | Named mirror/copy transforms between twin panels, used by a layer's `twin` key. See "Twins" below. |

When `custom_number` is true, the number blocks stop counting as keep-out, because you paint the
number there yourself. Sponsor and series stamps still count.

## Twins: one layer, both sides of the car

`inspect_template.py` prints the **geometric twins** it finds, i.e. island pairs with the same shape,
almost always the left and right sides. It gives the exact transform, e.g.
`island 1 -> 2: mirrored top-bottom; "scale": [1, -1], "offset": [0, 1200]`. Put that in `transforms`
and add `"twin": "<name>"` to any layer drawn on the first side. The build renders a second, correctly
mirrored copy on the other side:

- points, rects, centres, gradient and pattern anchors are mapped;
- island ids in `clip` / `islands` are remapped;
- logos and text get the right `flip_x` / `flip_y` and rotation, so they read correctly on both sides.

```json
"transforms": {"to_left": {"scale": [1, -1], "offset": [0, 1200], "islands": {"1": 2}}},
"layers": [
  {"type": "shape", "label": "sweep", "shape": "polygon", "points": [...], "fill": "#00c2a8", "clip": [1], "twin": "to_left"},
  {"type": "logo",  "label": "door logo", "file": "...", "center": [1080, 330], "width": 420, "twin": "to_left"}
]
```

Always design one side and twin it. Hand-mirrored coordinates are the most common cause of
mismatched sides. The geometric match says nothing about how the panel sits on the car, so confirm
the orientation once with the locator. If the twin is marked AMBIGUOUS (a symmetric shape), the
locator decides which transform is right.

`scale` is per axis, `[sx, sy]` with each ±1, and `offset` is `[ox, oy]`. A point maps to
`(sx·x + ox, sy·y + oy)`. Panels rotated 90° relative to each other can't be twinned; write those
layers directly.

### Text and logos on the twin (`sprite_flip`)

The car's other side is a 3D mirror image, so copying text with a plain template mirror would make it
read backwards there. The twin adds one more flip along the car's length.
- `"sprite_flip": "auto"` (the default) flips along the target panel's long axis, which is right for
  side panels.
- Set `"x"`, `"y"` or `"none"` explicitly for other twins.
- Confirm once in the sim that numbers read correctly on both sides.
- For a graphic (not text) that should be a true mirror image on the other side, e.g. a fern that
  points towards the nose on both sides, add `"twin_mirror": true` to the layer.

## Common layer keys

| key | meaning |
|---|---|
| `type` | One of `shape`, `logo`, `text` or `image`. |
| `label` | A name used in the report and the proof. Always set one; it makes feedback rounds easy. |
| `finish` | A preset name from `references/finishes.md`, `[r,g,b]`, `{"preset":"matte","roughness_jitter":20}`, or `"keep"`. Shapes default to `keep` (spec unchanged); logos and text default to `sticker`. |
| `opacity` | 0–1. |
| `hidden` | `true` skips the layer. Use it to compare variants. |

## `shape`

```json
{"type": "shape", "label": "main sweep R", "shape": "polygon",
 "points": [[1966,300],[1200,330],[700,420],[80,470],[80,560],[1966,560]],
 "fill": "#00c2a8", "finish": "metallic", "clip": "paintable",
 "stroke": {"colour": "#ffffff", "width": 6, "position": "outside", "finish": "gloss"}}
```

`shape` is one of:

| shape | geometry |
|---|---|
| `polygon` | `points` |
| `rect` | `rect` [x0,y0,x1,y1], optional `radius` |
| `ellipse` | `rect` |
| `band` | `points` (a polyline) + `width`, optional `round_caps`. Good for stripes. |
| `island` | `islands` [ids]. Fills whole panels; good for a black roof or a contrasting bumper. |
| `full` | The whole canvas. |
| `mask_file` | `file`, an image whose white or opaque pixels form the mask. |

Other shape options:

- **`fill`**, one of:
  - a colour: `"#hex"` or `[r,g,b]`;
  - `{"gradient": {"from":[x,y], "to":[x,y], "stops":[["#hex",0],["#hex",1]]}}` (linear);
  - `{"pattern": {...}}` (see below);
  - `{"texture": {"file": "carbon.jpg", "scale": 0.8, "angle": 0, "tint": "#hex", "brightness": 1.0}}`:
    tiles an image (carbon weave, brushed metal, camo) in template space, so it runs seamlessly across shapes.
- **`stroke`**: a pinstripe along the shape's own edge. It is not drawn along the panel edges it was
  clipped to. `position` is `outside` (default), `inside` or `center`.
- **`clip`**: `"paintable"` (all islands), `[ids]` (only those islands), or omitted (no clipping).
- **`clip_region`**: `[x0,y0,x1,y1]` or a polygon, intersected with `clip`. Needed on templates where several
  parts are one connected island (e.g. NASCAR: sides, roof and hood in one piece), so a side graphic can't
  spill onto the roof. Twins transform it too.
- **`feather`**: soft edge, in px.
- **`invert`**: true to paint everything except the shape.
- **`grain`**: 0.01–0.04 adds subtle noise, which takes the CG look off big flat fields.

### Patterns (`fill.pattern`)

Patterns that leave transparent gaps (`halftone`, `stripes`, outline-only `hex`) overlay what is already
underneath.

| kind | keys | use |
|---|---|---|
| `shards` | `scale` (cell size, ~60–200), `colours` [..], `gap_width`, `gap_colour`, `shade` (±brightness per cell, default 0.06), `roughness_jitter` (per-cell roughness ±) | Faceted, "edgy" panels. With `roughness_jitter` each shard catches light differently. |
| `hex` | `size`, `line_width`, `line_colour`, optional `colours` (filled cells) | Tech or honeycomb texture in an accent area. |
| `carbon` | `tile` (10–18), `dark`, `light` | Fake carbon weave for roof, splitter, mirrors and sills. Pair with the `carbon_gloss` or `carbon_matte` finish. |
| `stripes` | `angle`, `spacing`, `width`, `colour` | Speed lines, hazard stripes. |
| `halftone` | `from`, `to`, `spacing`, `max`, `min`, `angle`, `colour` | A dot fade from one colour field into another. A pro-looking transition. Dots are biggest at `from` and vanish at `to`. Everything on the far side of `from` is solid colour, so shape the layer to cover only the fade zone. |

## `logo`

```json
{"type": "logo", "label": "door logo R", "file": "../../logos_clean/brand_white.png",
 "center": [1080, 330], "width": 420, "rotation": 0, "flip_x": false,
 "recolour": "#ffffff", "outline": {"colour": "auto", "width": 6},
 "finish": "sticker", "allow_seam": false}
```

- **Size**: give `width` **or** `height`. It applies before `rotation`.
- **Rotation**: degrees, counter-clockwise. Match the panel's orientation from `car_notes.md`.
- **Flips**: `flip_x` / `flip_y` correct mirrored panels; check the locator screenshots.
- **`recolour`**: turns a single-colour logo into any colour while keeping its shape.
- **`outline`**: a sticker-style border. `"auto"` picks black, or white when the logo itself is dark.
  Width 4–8 px is typical. Outlines are what make logos read as stickers and separate them from
  busy backgrounds.
- **`allow_seam`**: only for a deliberate wrap that has been checked in screenshots.

## `text`

```json
{"type": "text", "label": "driver name", "text": "M. PARKIN", "height": 60,
 "center": [600, 300], "colour": "#ffffff", "font": "arialbd.ttf",
 "letter_spacing": 0.05, "rotation": 0, "outline": {"colour": "#000", "width": 4}}
```

- **`height`**: the cap height in px.
- **`font`**: a .ttf filename (looked up in Windows Fonts) or a full path. Bold, wide fonts read best on
  cars; avoid thin weights under ~80px.
- **Number**: when you paint the number yourself (`custom_number: true`), make it a `text` layer on
  the door number board and the hood.

## `image`

`{"type":"image","file":"...","center":[x,y],"width":300}`, or `"full_canvas": true` to lay a full-size
2048 image 1:1 (for example artwork exported from the template). Takes `finish` and `opacity`.

## Checks the build runs on every logo and text element

| severity | condition |
|---|---|
| ERROR | Off the paintable area (it will be cut off) |
| ERROR | Spans two or more panels (it crosses a seam) |
| ERROR | Inside a `keep_out_extra` zone |
| ERROR | Contrast below 1.5:1 (nearly invisible) |
| WARN | Closer than `edge_margin` to a panel edge |
| WARN | Over a sim-stamped number or sponsor area |
| WARN | On a curved or complex area (dense wireframe) |
| WARN | Contrast below 3:1 |
| WARN | Under 40px tall |
| WARN | Source upscaled more than 1.5× |
| WARN | The same logo too close to itself |

Design hints flag a uniform spec map, an almost flat body, more than 5 colours, metallic over very dark
colours, and clutter.

## Worked example (fragment)

```json
"transforms": {"to_left": {"scale": [1, -1], "offset": [0, 1200], "islands": {"1": 2}}},
"layers": [
  {"type":"shape","label":"dark sills R","shape":"polygon","points":[[60,470],[1990,440],[1990,560],[60,560]],
   "fill":"#111111","finish":"satin","clip":[1],"twin":"to_left"},
  {"type":"shape","label":"sweep R","shape":"polygon",
   "points":[[1990,250],[1300,290],[650,420],[60,455],[60,480],[1990,480]],
   "fill":{"gradient":{"from":[1990,0],"to":[60,0],"stops":[["#00e0c0",0],["#0066cc",1]]}},
   "finish":"metallic","clip":[1],"stroke":{"colour":"#ffffff","width":5,"finish":"gloss"},"twin":"to_left"},
  {"type":"shape","label":"shard texture on sills","shape":"rect","rect":[60,470,1990,560],
   "fill":{"pattern":{"kind":"shards","scale":90,"colours":["#101010","#1a1a1a","#242424"],
           "gap_width":2,"gap_colour":"#00e0c0","roughness_jitter":60}},
   "finish":"matte","clip":[1],"twin":"to_left"},
  {"type":"shape","label":"black roof","shape":"island","islands":[5],"fill":"#0d0d0d","finish":"carbon_gloss"},
  {"type":"logo","label":"door logo R","file":"../../logos_clean/brand_white.png",
   "center":[1080,330],"width":420,"outline":{"colour":"auto","width":6},"twin":"to_left"},
  {"type":"logo","label":"hood logo","file":"../../logos_clean/brand_white.png",
   "center":[400,1380],"width":360,"rotation":90,"outline":{"colour":"auto","width":6}}
]
```
