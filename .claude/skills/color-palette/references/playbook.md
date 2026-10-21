# Colour Playbook

Distilled from 10 expert design videos (1 more was unavailable). Actions ranked by cross-source consensus. Read this before building a palette.

## Top actions (ranked by consensus)

1. **Start from a brief, not a colour picker (~6/10).** Before choosing anything, answer: what are the **constraints** (brand, format)? what **guidance** exists? what do you want the viewer to **do**? what do you want them to **feel**? Mood/purpose drives every later decision, and the brief becomes your rationale when presenting.

2. **Know the four properties and work in HSL/OKLCH, not hex (~7/10).** **Hue** (the colour itself, 0–360 on the wheel), **Saturation/Chroma** (vivid ↔ greyed), **Value/Brightness/Lightness** (light ↔ dark; +white = tint, +black = shade, +grey = tone), and **Temperature** (warm ↔ cool). Hex/RGB are opaque; **HSL/HSB/OKLCH** let you build shades with simple, predictable maths.

3. **Pick ONE base colour, then extend it with a harmony (~7/10).** Choose a single dominant hue (from brand/logo/preference or the mood), then let a colour-harmony formula pick the rest. "Find one colour you like and let science do the rest." When unsure, **monochromatic is the safe default**.

4. **Assign roles + proportions — the 60/30/10 rule (~6/10).** Give every colour a job: **dominant/brand ~60%**, **secondary/neutrals ~30%**, **accent ~10%** (reserved for CTAs/highlights). A palette only works when each colour has a purpose *and* a share.

5. **Keep it few — less is more (~6/10).** Overuse and oversaturation are the two most common mistakes. Aim for roughly **3–5 colours / 2–3 hues + neutrals**; start with a base + a couple of neutrals and add only if needed. (Cooking analogy: use the few spices that make the dish, not the whole rack.)

6. **Contrast/value is king — check in greyscale; protect legibility & accessibility (~5/10).** A colour's **value matters more than its hue** — "if it works in greyscale, it works in colour." Convert to greyscale to test structure. For **text, lightness contrast is what governs readability** — meet WCAG (~4.5:1 body, 3:1 large text), and never encode meaning in hue alone (colour-blind users).

7. **Lean on neutrals (~5/10).** Neutrals (blacks, whites, greys, browns; warm or cool) are the supporting cast/"negative space for colour" — they give the eye rest and make bold colours pop. You need more neutral than you think; most of a UI is some form of grey.

8. **Reserve accents for actions; don't dilute them (~5/10).** The accent/highlight colour is for CTAs, links, key highlights. Don't scatter it through decoration or backgrounds, or it stops signalling "this is special." Buttons use the accent, never a primary that's already everywhere.

9. **Match tones so colours cohere (~3/10).** "Tone" = tint + shade together (adding grey). Colours read wrong when their tones sit in different places; keep supporting colours' **saturation/brightness within ~5–10 of the base** and desaturate/brighten until they agree.

10. **Use colour psychology as a directional nudge, with cultural context (~5/10).** Common associations (loose, not laws): red = passion/energy/danger; blue = trust/calm/reliability; green = growth/health/eco; yellow = optimism/energy (or instability); purple = luxury/royalty; black/white/grey = neutral/premium. Each has a positive and negative side, varies by culture/politics/religion/sport, and **colour never works alone** — type, layout and imagery must agree.

11. **Steal palettes from nature, reference, and tools (~6/10).** The best inspiration is nature or existing designs — sample colours from a pleasing photo/flower, or a Pinterest "colour inspiration" board (pin 15–20, zoom out, colour-pick). Tools: **Coolors.co** (generate/lock/export), **Adobe Color** (harmony rules → hex), **Illustrator Color Guide / Procreate colour-harmony tool**, and eyedropper/colour-pick from a logo.

12. **Build shade scales for UI/brand (~2/10 but essential for UI).** Generate a scale per colour (e.g. 50–900, base at 500) by varying **lightness** along a consistent arc; neutrals ≈ zero saturation. Do the light and dark ends first, then the midpoints. Keep to ≈10 shades max; tweak rather than add.

13. **Test, then trust your eye (~4/10).** Review the palette: is it **functional** (supports the info, guides the eye, legible, consistent)? **appealing**? **on-brief**? Line up shade scales and **squint/blur** to check each spans the same light-to-dark range. Pass a **contrast checker**. Then remember: harmonies and rules only guide — **you are the final judge**; be consistent in how each colour is used so viewers understand the system.

---

## Colour harmonies (pick one to extend the base)
- **Monochromatic** — one hue, varied tints/shades/tones. Easiest, cohesive, organized; the safe default and great for UI neutrals-of-a-hue.
- **Analogous** — 2–4 adjacent hues on the wheel. Calm, natural, "belong together"; use one dominant + the rest as accents, and rely on **value** for contrast since hues are close.
- **Complementary** — two opposite hues. Strong contrast, vibrant, attention-grabbing; can overpower, so use one as main + the other as accent.
- **Split-complementary** — base + the two hues either side of its complement. Complementary contrast with more variety and less tension.
- **Triadic** — three evenly spaced hues. Bold and vibrant; usually one lead + two accents.
- **Tetradic (double-complementary)** — four hues = two complementary pairs. Maximum variety; anchor on one main colour, others as accents.

## Colour-role systems
- **Brand/marketing (60/30/10):** dominant/brand 60% · secondary/neutral 30% · accent 10%. A common brand kit = **2 dominant + 3 accent** (one accent as the highlighter, two as light/background neutrals). A strong minimal move: **one colour + black + white**.
- **UI/app (three buckets):** **Neutrals** (backgrounds, text, borders, secondary buttons — the majority), **Brand/Primary** (main actions, character — 1–2 colours), **Semantic** (green = success, amber/orange = warning, red = error/danger, blue = info). Keep semantic colours tonally consistent with the brand.

## Contrast, value & accessibility
- Value (lightness) is the backbone; **greyscale test** = the fastest reliability check.
- Text readability = **lightness contrast**; target WCAG AA (~4.5:1 body, 3:1 large/UI).
- Don't convey state by hue alone; pair with text/icons. Avoid "vibrating" saturated complementary pairs behind text.

## Tools mentioned
Coolors.co (generate, spacebar, lock, upload logo to pick, Explore library, export PDF/CSS) · Adobe Color (harmony rules, export hex) · Adobe Illustrator Color Guide · Procreate colour-harmony tool · Pinterest boards + eyedropper for sampling · OKLCH (Tailwind v4 default) for perceptually even scales.

## Source map
02 Flux Academy – brief → hue → HSB → build → review, 60/30/10, tone-match · 03 Nour Art – wheel, HSL, harmonies, text=lightness contrast, nature, emotions · 04 Sajid – UI roles (neutral/brand/semantic), HSL/OKLCH, shade lightness, depth cues · 05 UX Tools – brand/supporting/neutral, HSB, 100–900 scales, squint test, contrast · 06 Tristan Parker – source from brand/logo/scratch, 3–5 colours (accent/neutral/CTA), Coolors · 07 The Futur – 60/30/10, apply-a-palette, background pairing rules, accent=CTA · 08 Scott Adam Lancaster – brand consistency/memorability, 2 dominant + 3 accent, Coolors · 09 Art by Annabelle – value B&W check, limited palette, overlay/curves cohesion, background-first · 10 The Futur – harmonies, neutrals, less-is-more, greyscale contrast, balance, consistency · 11 Sarah Renae Clark – wheel + 4 properties + all harmonies, one dominant, few colours, inspiration. (01 Flux Academy 3-step: transcript unavailable.)
