---
name: color-palette
description: "Interactive colour-palette builder + playbook distilled from expert design videos (Flux Academy, The Futur, UX Tools, Sajid, Nour Art, and more). Use whenever the user wants to CHOOSE, BUILD, REVIEW, or FIX colours for a website, app/UI, brand, logo, poster, illustration, slide deck, or any design — pick a colour scheme, build a brand or UI palette, find colours that work together, get hex/HSL/OKLCH codes, apply the 60/30/10 rule, check colour contrast/accessibility, or turn a base colour or logo into a full palette. It interviews the user about purpose, audience and mood, picks a base colour and a harmony, assigns roles (dominant/neutral/accent) and proportions, generates shades, checks contrast, and outputs a documented palette. Trigger on phrases like 'choose colours for my website/app/brand', 'build a colour palette', 'what colours go with X', 'pick a colour scheme', 'my colours look off', 'give me hex codes', 'make a brand palette', or /color-palette."
---

# color-palette

An interactive colour-palette builder and a distilled playbook. It does two things: **(A)** run an interview and produce a documented, usable palette (hex + HSL/OKLCH, roles, proportions, contrast-checked), and **(B)** act as a reference for the colour principles behind the choices. The most repeated lesson across every source: **answer a short brief first, pick ONE base colour, extend it with a harmony, keep it few, and let value/contrast do the heavy lifting.**

## When this fires
Any request to choose, build, review, or fix colours for a website, app/UI, brand/logo, poster, illustration, deck, or other design.

## Reference files (read before building a palette)
- `references/playbook.md` — the ranked colour principles: the four properties, colour harmonies, role/proportion systems (60/30/10), contrast & accessibility, colour psychology, and tools. **Read this before generating a palette.**
- `references/build-and-check.md` — the intake questions, the palette output template (roles, hex, HSL/OKLCH, shade scales, usage rules) and the review checklist.

---

## Workflow — the builder

Run these phases in order. For a pure "explain colour theory" question, skip to the reference files.

### Phase 1 — Brief (fast, mostly multiple-choice)
Colours follow from purpose. Use the **AskUserQuestion** tool to lock the fixed variables (don't make the user type obvious choices):

1. **What's it for** — website / web app or UI / brand & logo / poster or print / illustration or artwork / slide deck / other.
2. **Mood / feeling** — the emotion to evoke (e.g. calm & trustworthy, bold & energetic, premium & minimal, warm & friendly, playful, natural/eco). This drives the hue.
3. **Light or dark** (for UI/web) — light mode / dark mode / both.
4. **Starting point** — a brand colour or hex they already have / pick from a logo or image / a colour they like / start from scratch (I'll suggest one).
5. **Constraints** — brand guidelines, must-include colours, colours to avoid, accessibility requirements, cultural context.

If they gave any of these already, confirm and skip.

### Phase 2 — Base colour + harmony
- Establish **one base/dominant colour** (from their brand/logo/preference, or propose one that fits the mood; use colour psychology as a *directional* guide, noting cultural context).
- Pick a **harmony** to derive the rest (see `references/playbook.md`): monochromatic (safest / when unsure), analogous (calm), complementary (contrast/energy), split-complementary, triadic, tetradic. Briefly say why it fits the mood, and offer 1–2 alternatives.
- Work in **HSL or OKLCH** (not raw hex) so shades are systematic; keep supporting colours **tonally close** to the base (similar saturation/brightness) so they cohere.

### Phase 3 — Roles + proportion
Assign every colour a job and a share:
- **Dominant / brand** (~60%), **secondary/neutrals** (~30% — greys/off-whites/darks that give the eye rest), **accent** (~10%, reserved for CTAs/highlights) — the **60/30/10 rule**.
- For **UI specifically**, use three buckets: **neutrals** (backgrounds, text, borders — most of the UI), **brand/primary** (main actions), **semantic** (green success, amber warning, red error, blue info). Keep the palette **small** (≈3–5 colours / 2–3 hues + neutrals).

### Phase 4 — Shades
- For UI/brand, generate a **shade scale** per colour (e.g. 50–900, base at 500), varying **lightness** along a consistent path; neutrals = near-zero saturation. Provide light- and dark-mode variants where relevant (a good start: mirror lightness around the midpoint, then adjust by eye; light comes from the top).

### Phase 5 — Contrast & accessibility check (do not skip)
- **Value/contrast matters more than hue.** Sanity-check the palette in **greyscale** (does structure survive?).
- Check **text contrast ratios** against WCAG (≈4.5:1 for body text, 3:1 for large text); flag fails and fix by adjusting lightness. Never rely on hue alone to convey meaning (colour-blind users).
- Reserve accents for actions; make sure CTAs stand out without "vibrating" against neighbours.

### Phase 6 — Deliver the palette
Output using the template in `references/build-and-check.md`: each colour with **name, role, hex, HSL and OKLCH**, the **60/30/10 proportion**, shade scales if applicable, and **usage rules** (what's background vs text vs button; what NOT to do). Offer to render swatches (an HTML/SVG preview) and to export as CSS variables / a Coolors-style list. Then note what to tweak, and remind them: the rules guide, but **their eye is the final judge** — validate it in the real design.

---

## Judgment calls (where sources differ — decide with the user)
- **How many colours:** advice ranges from "one colour + black & white," to "2 colours + 2 neutrals," to "3–5 total," to "2 dominant + 3 accent." Converge on **few**: one base + neutrals + one accent (~3–5), add only if needed.
- **Colour format:** most teach **HSB/HSL**; the modern/perceptual choice is **OKLCH** (even lightness steps; Tailwind v4 default). Offer both; prefer OKLCH for UI shade scales, HSL/HSB for quick picking.
- **Colour psychology:** meanings are real but **loose and culture-dependent** (sources even disagree, e.g. red = passion vs "happiness"). Use as a directional nudge, not a rule, and colour never works alone — type, layout, imagery must agree.
- **Rules vs. intuition:** harmonies/60-30-10/contrast are best practices, not laws. Be consistent in how each colour is used, then trust the eye.

## Provenance
Distilled from a batch of colour/design YouTube videos (fetched 2026-08-06). Usable sources: Flux Academy (How To Select Colors), Nour Art, Sajid (UI colours), UX Tools, Tristan Parker, The Futur (×2: applying a palette; 5 tips), Scott Adam Lancaster, Art by Annabelle, Sarah Renae Clark. One video (Flux Academy "How to Choose Colors — 3-Step") could not be transcribed (only garbled non-English captions) and was skipped; its process is covered by the other Flux Academy video. See `references/playbook.md`.
