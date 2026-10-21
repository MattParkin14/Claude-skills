---
name: "iracing-livery"
description: Design and build custom iRacing car liveries (paint schemes) end to end. Reads the iRacing PSD paint template, maps which flat panel is which part of the car, places logos so they are not hidden or cut off, renders the car_ID.tga paint and car_spec_ID.tga spec map (metallic, roughness, clearcoat) in code, installs them into Documents/iRacing/paint with backups, and iterates from Paint Shop screenshots. Use whenever the user mentions an iRacing livery, paint, skin, wrap, paint scheme, spec map, Trading Paints, a paint template, PSD or TGA for a sim-racing car, putting their logos or branding on an iRacing car, or fixing logo placement on a car paint, even if they only say "make me a livery for the MX-5" or paste Paint Shop screenshots.
compatibility: Python 3 with pillow, numpy, scipy and psd-tools. Best run in Claude Code on the Windows PC that runs iRacing, so it can read and write Documents/iRacing/paint directly.
---

# iRacing livery

You produce two files iRacing loads for the user's car: `car_<customerID>.tga` (the paint) and
`car_spec_<customerID>.tga` (the spec map: metallic, roughness and clearcoat per pixel). You build them
in code from a `livery.json`, check them, install them, then improve them from in-sim screenshots.

Two failures ruin most first attempts, and this workflow exists to prevent both:

1. **Logos hidden or cut off.** The template is the car's skin unwrapped flat. Panels are split at seams,
   some are rotated or mirrored, and parts are hidden under wings, inside arches or behind mirrors.
   You cannot see any of that in the flat image. Fix: measure the car once with the locator paint,
   keep logos inside safe zones, and let the build script check every placement.
2. **Flat, amateur design.** Typical causes are one body colour with logos scattered on it, no finish
   contrast, timid sizes and no idea running through the car. Fix: decide the concept before
   drawing anything, follow `references/design-playbook.md`, and use the spec map deliberately.

You can't see the car in 3D until the user shows you. Never call a livery finished from the flat
proof alone; the screenshots in step 9 are what make round two and three good.

## Setup

```bash
pip install pillow numpy scipy psd-tools
```

The scripts live in `scripts/` next to this file. Run them with `python <skill-dir>/scripts/<name>.py`;
each has `--help`. Keep the work in one place so per-car knowledge is reused across liveries:

```
~/Documents/iracing-liveries/
  _cars/<car folder>/            once per car, reused by every livery for that car
    template.zip                 iRacing's template download
    inspect/                     output of inspect_template.py
    car_notes.md                 panel map, orientation, hidden zones (template at the end of this file)
  <car folder>/<livery name>/
    livery.json
    builds/v01, v02, ...
  logos_clean/                   output of prep_logos.py
```

## Workflow

### 1. Brief: one round of questions

Ask everything in one go, as multiple choice where you can (use AskUserQuestion when it is available).
Don't ask for things you can find yourself, such as the paint folder, the car folder name or ID candidates.

- **Car**, and confirm they have driven it at least once (that creates its paint folder).
- **Template**: the zip from the iRacing UI (*My Content → Car Manager → Download Template*, or
  *Paint Shop → choose the car → Download Template*). Trading Paints also hosts templates.
- **Logos or branding**: PNGs with transparent backgrounds are best. Ask for brand colours if known.
- **Direction**: offer 3–4 options, such as bold modern, classic stripes, heritage race car or aggressive
  geometric. Real-car photos of the series they like are a big help.
- **Numbers**: sim-stamped (the default and free; keep the number areas clear) or custom-painted
  (needs Trading Paints Pro and "Hide car numbers" turned on).
- **Customer ID**: suggest the candidate from step 2 and get them to confirm it.

### 2. Find the paint folder and customer ID

```bash
python scripts/find_paint_folder.py            # add --car mx5 to filter
```

This shows the paint folder (OneDrive-redirected Documents are handled), the car folders with the most
recently used first, and customer-ID candidates. iRacing's MX-5 folder, for example, is `mx5 mx52016`.

### 3. Inspect the template (once per car)

```bash
python scripts/inspect_template.py _cars/<car>/template.zip _cars/<car>/inspect
```

Look at `view_template.png`, `view_islands.png` and `view_safezones.png`, and read the layer tree it
prints. Each numbered island is one piece of the car's skin. Work out which panel each island is:
hood, roof, left side, right side, front bumper, rear, wing, mirror.

Orientation clues:
- The template's own stamped artwork (number blocks, sponsor stamps, manufacturer badges) reads
  correctly in the orientation it has on the car.
- Wheel-arch cut-outs mark the bottom edge of a side panel.
- Light and grille cut-outs mark the nose.

The inspector also prints **geometric twins**: island pairs with the same shape (usually the two sides)
and the exact mirror transform between them. Record it in `car_notes.md`. In step 7 you design one side
and let `"twin"` render the other, which keeps both sides identical and their text readable.

Real templates vary. Some "Mask" layers cover the background instead of the car (the inspector detects
this from the wireframe and flips it). Decal layers inside the paintable-area group are optional artwork,
not sim stamps. On some cars (NASCAR) the sides, roof and hood are one connected island, so use
`clip_region` to keep graphics on their panel. Parts such as the nose are often mirrored by the 3D
model, so the template may show only one headlight. That's normal; check in the sim.

If the mask coverage or the layer roles look wrong, re-run with `--mask-layer`, `--wire-layer` or
`--keepout-layer`. Record what you learn in `car_notes.md`.

### 4. Calibrate with the locator paint (once per car; strongly recommended)

```bash
python scripts/make_locator.py _cars/<car>/inspect _cars/<car>/locator --customer-id <ID>
python scripts/install_paint.py _cars/<car>/locator --paint-dir "<paint dir>" --car "<car>" --customer-id <ID>
```

The locator paints a labelled grid (A01, B07 and so on) over the whole template. Ask the user for
screenshots from front 3/4, rear 3/4, both profiles and top, plus close-ups of the nose, tail and wing.

From those screenshots you can read off:
- which template cells land on which part of the car, so you know the exact island-to-panel map;
- **mirroring**: labels that read backwards mean the panel is mirrored, so text needs `flip_x`;
- **rotation**: tilted or sideways labels give the panel's rotation, which sets text `rotation`;
- **hidden areas**: cells that appear in no screenshot, or sit under the wing, inside arches or behind
  mirrors, go into `car_notes.md` as `keep_out_extra` polygons;
- **shared UV areas**: one template area painted onto both sides (common on wing uprights and
  mirrors). Text there reads backwards on one side, so use symmetric graphics instead.

Tell the user in one line why you're doing this: it is the step that stops logos ending up hidden or
cut off. Afterwards restore their old paint with `install_paint.py --restore ...`, or just
overwrite it in step 8.

### 5. Prep the logos

```bash
python scripts/prep_logos.py <logo files or folder> --out logos_clean
```

This removes solid backgrounds, trims the margins, writes white and black mono versions, and flags small
files, JPEGs and files whose extension doesn't match their real format (web grabs are often WEBP).
Look at `logos_sheet.png`. A primary logo needs roughly as many pixels as it will cover on the car, so
a 450px-wide door logo needs a source at least ~450px wide. Ask for a better file rather than upscaling.

### 6. Design the concept before drawing anything

Read `references/design-playbook.md`. Then give the user 2–3 concept directions, one or two lines each,
each with:
- a palette as hex values,
- the big idea (the one graphic that runs through the car),
- where the main logos go,
- the finish plan.

Recommend one, then build it. Concepts are cheap to change; build rounds are not.

### 7. Build and review it yourself

Write `livery.json` (the format is in `references/livery-json.md`; finish choices are in
`references/finishes.md`). Draw side graphics, side logos and numbers on one side only and add
`"twin"` to them. Then:

```bash
python scripts/build_livery.py <car>/<livery>/livery.json
```

Each run writes the next `builds/vNN/`. Review it in this order before the user sees anything:

1. **The printed checks.** Zero ERRORs is required, and the installer refuses a build with errors.
   Fix every WARN or have a reason to keep it: a stamped-area overlap is fine when the number is
   custom-painted, for example.
2. **`proof.png`.** It shows the panel outlines (cyan), wireframe, sim-stamped zones (red hatching),
   your keep-out zones (magenta) and every logo box coloured by status.
3. **`crops/`.** Logos at 1:1. Check for soft edges, fringing and outline quality.
4. **`preview.png`** against the polish checklist in the playbook. If it would pass for a flat colour
   with stickers on it, it isn't finished.

### 8. Install and look in the sim

```bash
python scripts/install_paint.py <livery>/builds/vNN --paint-dir "<paint dir>" --car "<car>" --customer-id <ID>
```

The installer backs up the existing files to `iRacing/paint_backups/<car>/<timestamp>/` and removes the
stale spec `.mip` so iRacing rebuilds it. Tell the user to open the car in a test drive or the Paint
Shop, press **Ctrl+R**, and send the same set of screenshots as in step 4.

### 9. Fix from screenshots (usually 2–3 rounds)

For each problem you see:
1. Identify the panel.
2. Map the problem to template coordinates using `car_notes.md` or the locator cells.
3. Edit `livery.json`.
4. Rebuild and reinstall.

When you discover a hidden area, add it to `keep_out_extra` **and** to `car_notes.md`, so no later livery
on this car repeats the mistake. Real-car photos are the best guide to logo placement conventions.
Keep one change-set per build and say what changed in a line.

### 10. Finish and share

Other drivers only see custom paints through Trading Paints. On the Trading Paints site, go to
*My Paints*, pick the car, and upload:
- `car_<ID>.tga` (or a PNG);
- the `car_spec_<ID>.mip` that iRacing generated in the paint folder. Upload the `.mip`, not the spec TGA.

Custom-number paints need Pro. Details and troubleshooting are in `references/iracing-files.md`.

## Rules worth knowing why

- **Paint files are 2048×2048, 24-bit, RLE TGAs.** 32-bit paint TGAs can show as all black for other
  drivers. The scripts write the correct format; don't hand-convert outputs.
- **Build from scratch, don't flatten the PSD.** The template's guide layers (wireframe, number blocks,
  "Turn off before exporting TGA") must never end up in the paint.
- **Extend colour fields past island edges.** Use `clip` deliberately rather than stopping shapes exactly
  at the edge, so seams don't show the base colour as a hairline.
- **Never delete or overwrite other drivers' files** in the paint folder. Only touch `car*_<ID>` files, and
  only through the installer, which backs up first.
- **Brand logos on a personal paint are common.** If the user plans to share publicly (the Showroom), remind
  them once that they need the right to use any logo on a public car.

## Reference files

- `references/livery-json.md`: the build format with a full example. Read it before writing `livery.json`.
- `references/design-playbook.md`: concept, palette, layout archetypes, logo placement rules, polish
  checklist and anti-patterns. Read it before designing.
- `references/finishes.md`: spec-map channels, finish presets with RGB values, and the albedo rules for
  metallic and chrome.
- `references/iracing-files.md`: file names, folders, formats, custom numbers, Trading Paints and
  troubleshooting ("paint doesn't change", "spec looks old", "others can't see it", "all black").

## car_notes.md template

```markdown
# <car display name> — paint folder `<car folder>`
Template: <zip name>, 2048×2048. Verified with locator: yes/no (date)

| island | panel | orientation in template | notes |
|---|---|---|---|
| 1 | right side | nose → right, roof up | door number block ~[1000,300,1200,450] |
| 2 | left side | nose → right, mirrored top-bottom | twin of 1 |
| ... | | | |

Twin transform (from inspect_template.py, confirmed with locator):
"to_left": {"scale": [1, -1], "offset": [0, 1200], "islands": {"1": 2}}

Hidden / unsafe zones (copy into keep_out_extra):
- "under rear wing": [[x,y],...]
Shared/mirrored UV areas: wing uprights (island 7) — use symmetric graphics
Stamped areas: numbers on doors and hood; series sticker on front fenders
```
