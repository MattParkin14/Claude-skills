# Design playbook

## Contents

1. Concept first
2. Palette
3. Layout archetypes
4. Making it read on the 3D car
5. Logo placement rules
6. Numbers and stamped items
7. Polish checklist (what separates pro from amateur)
8. Anti-patterns
9. Giving the user concepts

## 1. Concept first

Every good livery has **one big idea**, and everything else supports it. Write it down in one sentence
before drawing anything. For example:

- "A teal-to-blue metallic sweep that rises from the rear wheel to the A-pillar over a matte black car."
- "A white car with a single bold red wedge from the nose."
- "Silver fern shards fading into deep navy."

If you can't say it in a sentence, the livery will look random.

The idea should:
- **Run nose to tail.** It connects the front, side and rear so the car looks like one object rather
  than five decorated panels.
- **Lean forward.** Shapes that rise or point toward the nose (typically a 5–15° rake) read as speed.
  Shapes that droop toward the front look like they're braking.
- **Use the car's own lines.** Align breaks with the beltline, the door shut line, wheel arches or the
  rear haunch. If a colour break deliberately crosses a body line, cross it clearly; don't miss it by
  a few pixels.

## 2. Palette

- **Proportions of about 60 / 30 / 10.** Dominant colour (60%), secondary (30%), accent (10%), plus black
  and/or white for logos and pinstripes. More than three main colours almost always reads as busy.
- **Start from the brand.** Pull the logo's main colours (`prep_logos.py` lists them) and build around
  those. A neutral base (black, white, graphite, navy) with brand colours as the graphic is the safest
  strong combination.
- **Value contrast beats hue contrast.** Red on green of the same lightness turns to mush at distance.
  Check in your head, or by desaturating `preview.png`, that the main shapes still separate in greyscale.
- **Saturated and dark don't mix well under metallic.** Metallic darkens the albedo, so lighten colours
  that will be metallic (see `finishes.md`).
- **Ground the car.** A darker colour low on the car (sills, lower bumper, diffuser) makes it look lower
  and faster. A contrasting roof (black or carbon) is cheap and almost always helps.

## 3. Layout archetypes

Pick one and adapt it. These are proven on real race cars.

| archetype | description | suits |
|---|---|---|
| **Sweep** | One large curved or diagonal field rising from rear-low to front-high on each side, carried over the hood as a matching wedge or stripe. | Modern GT, touring, cup cars |
| **Split** | Car divided into two colours along a strong diagonal or the beltline, with a pinstripe at the break. | Clean corporate brands |
| **Wedge / arrow** | A bold chevron from the nose that grows toward the rear. | Formula cars, prototypes, aggressive looks |
| **Stripes** | Twin centre stripes nose to tail over hood, roof and rear, with offset stripes on the sides. | Heritage, muscle, MX-5 / club racers |
| **Fade** | One colour dissolving into another through halftone dots or shards. | Tech, esports, "edgy" brief |
| **Block colour + accents** | Solid body, accent-coloured panels (mirrors, splitter, wing, roof) and big logos. | Minimal, or when the logo is the star |

## 4. Making it read on the 3D car

- **The side view is what people see most.** Doors and rear quarters carry the main logo; the hood is
  what the TV cam and the rear-view mirror see.
- **Left and right should match in car space.** The graphic should point to the nose on both sides, and
  text must read normally on both. Design one side and use `"twin"`, which handles the mirroring and
  the logo and text flips. Use `car_notes.md` to know each side panel's orientation in the template.
- **Size for distance.** Details under ~40px of template disappear beyond a few car lengths. The main
  logo on a door is typically 350–600px wide on a 2048 template; secondary logos 150–300px.
- **Hood graphics must line up with the sides** where the hood meets the fenders. Check the front-3/4
  screenshot specifically.
- **Wheel arches and lower edges eat graphics.** Anything thin near an island's bottom edge often
  disappears into the arch or under the sill.

## 5. Logo placement rules

1. **Hierarchy.**
   - Primary logo: both doors (or rear quarters) plus the hood.
   - Secondary: front fenders, rear bumper, roof, rear wing.
   - Tertiary: sills, mirrors, wing endplates, A-pillars.
2. **Clear space at least the logo's height around it.** Nothing else (other logos, colour breaks,
   pinstripes) intrudes on that space. This is the single most effective anti-clutter rule.
3. **Inside a safe zone.** Keep logos within `safe_bbox` from `islands.json`, away from seams, panel
   edges, dense-wireframe (curved) areas and `keep_out_extra` zones. The build check enforces this.
4. **Consistent angle.** If one logo follows a diagonal, every logo near it uses the same angle.
   Otherwise keep logos horizontal relative to the car (use the panel's orientation).
5. **Outline for separation.** A 4–8px black outline (white if the logo is black) makes logos read as
   stickers and keeps them legible over gradients and patterns. Use the `sticker` finish so they look
   like vinyl.
6. **Contrast at least 3:1** against what's behind them. Recolour mono logos to white or black rather
   than leaving them in a colour that fights the base.
7. **One brand mark per surface.** The same logo twice on one panel looks like a mistake; the check
   warns about it.
8. **Respect real-car conventions** when the user wants realism. Look at the reference photos: windscreen
   banner, door number boards, series stickers on the front fenders, manufacturer badges where the car
   has them.

## 6. Numbers and stamped items

- **Sim-stamped numbers (the default).** iRacing stamps the number in the areas shown as
  `numbers` / `keepout.png`. Give those areas a calm, single-colour background that contrasts with the
  number colour the user picks in the Paint Booth. Never put a logo under them.
- **Custom number.** Paint the number yourself as a `text` layer on the number boards and set
  `custom_number: true`. Others only see it if they have "Hide car numbers" on and the user has
  Trading Paints Pro; everyone else sees the stamped fallback.
- **Stamped sponsor and series decals** take the spec finish of whatever is under them. A satin or gloss
  area there looks right; a chrome area makes the stamped stickers chrome too.

## 7. Polish checklist

Go through this before showing the user a build. Each item is a common reason a livery looks amateur.

- [ ] **Finish contrast.** At least two finishes, e.g. gloss body, matte or satin graphic, metallic
      accent, carbon roof. Uniform spec is the number-one cause of "flat".
- [ ] **Pinstripes at colour breaks.** A 4–8px white, black or accent line between colour fields looks
      deliberate, and hides small seam mismatches.
- [ ] **Depth in big fields.** A gradient, halftone fade, subtle `grain`, or shard texture with
      roughness jitter. No large perfectly flat CG-looking areas.
- [ ] **Grounding.** Darker lower body or sills.
- [ ] **Hierarchy obvious.** One logo clearly dominates; the rest step down in size.
- [ ] **Clear space respected** everywhere.
- [ ] **Sides match** in car space, and the hood graphic lines up with the sides.
- [ ] **Nothing important within the edge margin**, under stamped zones, or in known hidden zones.
- [ ] **Readable from distance.** In `preview.png` at 25% size, the idea and the main logo still read.
- [ ] **Small parts done.** Mirrors, wing endplates and splitter are painted in an accent or
      carbon, not left as base colour.

## 8. Anti-patterns

| anti-pattern | why it fails | fix |
|---|---|---|
| Logos placed on the flat template "where there's space" | Space in the flat template is often a seam, an arch or a hidden underside | Check `view_safezones.png`, use the locator and trust the build check |
| One colour with logos scattered over it | No idea, no flow; reads as a rental car | Pick an archetype and give the logos a structure to sit in |
| Same logo repeated everywhere | Looks like wallpaper; kills hierarchy | One primary placement per side and one on the hood |
| Tiny logos and thin fonts | Disappear in the sim | Bigger, bolder, fewer |
| Drop shadows and bevels on logos | Look fake on a 3D car under real lighting | Outlines and finish contrast instead |
| Rainbow palettes | No hierarchy | Use 60/30/10 |
| Upscaled web-grab logos (pngegg, Google Images) | Soft, jagged edges, often watermarked | Get the vector or a large PNG from the brand |
| Stripes that change width or angle across panels | Seams make the mismatch obvious | Measure the stripe at each panel join from the locator screenshots |
| Metallic on dark colours | Turns near black | Lighten the albedo or use the `metallic_soft` finish |
| Chrome everywhere | Mirrors the track; nothing reads | Chrome as an accent only |

## 9. Giving the user concepts

Offer 2–3 directions, one or two lines each, and recommend one. For example:

> **A — Fern Shards (recommended).** Navy gloss car; silver-teal shard field rising from the rear arch to the
> A-pillar with per-shard roughness; white fern on both doors and hood with black outlines; carbon roof.
> Palette #0b1f3a / #00c2a8 / #e8f1f2.
> **B — Heritage Stripes.** White car; twin black centre stripes nose to tail; red pinstripe; kiwi in a roundel on
> the doors; matte stripes on a gloss body. Palette #f4f4f2 / #111 / #c8102e.
> **C — Split.** Black/teal split at the beltline with a white pinstripe; metallic teal; logos white.

After they pick one, build it. If they mix ("A but with B's stripes"), fold that in without re-asking.
