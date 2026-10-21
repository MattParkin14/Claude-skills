# Intake questions, palette output template, and review checklist

The conversation engine for the builder. Ask the fixed items with AskUserQuestion; ask the open ones conversationally and only as needed.

---

## Intake — the brief (Phase 1)

**Fixed (use AskUserQuestion):**
- **Use case:** website / web-app UI / brand & logo / poster or print / illustration / slide deck / other.
- **Mood/feeling to evoke:** calm & trustworthy · bold & energetic · premium & minimal · warm & friendly · playful · natural/eco · (other).
- **Light or dark** (UI/web): light / dark / both.
- **Starting point:** existing brand colour or hex · pick from a logo/image · a colour I like · from scratch.

**Open (ask conversationally, only what's relevant):**
- Who's the audience, and what's the moment they're in when they see this?
- Any **must-include** colours, colours to **avoid**, or brand guidelines?
- Any **cultural/market context** to respect (political, religious, regional, sport associations)?
- **Accessibility** needs (e.g. WCAG AA, known colour-blind audience)?
- Where will it live / what tool are you building in (Figma, Tailwind, Webflow, Elementor, Procreate…), so codes are handed off in the right format?

If the user gives a logo/image, offer to colour-pick from it. If they're stuck for a base colour, propose one from the mood (psychology as a directional nudge) and let them react.

---

## Palette output template (Phase 6)

```
PALETTE — [project], [use case] · Mood: [mood] · Harmony: [scheme] · Base: [hex]

ROLE            NAME            HEX        HSL              OKLCH               USAGE
Dominant (60%)  [name]          #......    hsl(.. .. ..)    oklch(.. .. ..)     [backgrounds / large areas]
Secondary(30%)  [name/neutral]  #......    ...              ...                 [sections, cards, text]
Accent (10%)    [name]          #......    ...              ...                 [CTAs, links, highlights only]
Neutral dark    [name]          #......    ...              ...                 [body text / dark UI base]
Neutral light   [name]          #......    ...              ...                 [page background / light UI base]
[semantic: success/warning/error/info — for UI]

SHADE SCALES (UI/brand): [colour] 50 · 100 · 200 · 300 · 400 · 500(base) · 600 · 700 · 800 · 900
LIGHT / DARK MODE (if UI): [mapped variables, e.g. bg, surface, text, border, primary]

USAGE RULES
- 60/30/10 proportions as above; accent reserved strictly for actions.
- Text: [which colour on which background], all meeting WCAG AA.
- Do NOT: [e.g. use the accent as a large background; put saturated coloured text on coloured backgrounds].
```

Offer to also: render **swatches** (a small HTML/SVG preview with hex labels), export as **CSS custom properties** / a **Tailwind** config / a plain **hex list** (Coolors-style), and produce a one-line **rationale** tying each choice back to the brief.

---

## Review checklist (Phase 5 — before delivering)

- [ ] **On-brief** — does the palette match the stated purpose, audience, and mood?
- [ ] **One dominant colour** anchors it; harmony is coherent; supporting colours are **tonally close** to the base.
- [ ] **Few colours** — ~3–5 / 2–3 hues + neutrals; nothing decorative stealing the accent's job.
- [ ] **60/30/10** proportions are realistic for the actual layout.
- [ ] **Greyscale test** — desaturate; does the structure/hierarchy still read?
- [ ] **Text contrast** — every text/background pair meets WCAG AA (~4.5:1 body, 3:1 large/UI); meaning isn't carried by hue alone.
- [ ] **Accent** stands out for CTAs without "vibrating" against neighbours.
- [ ] **Shade scales** (if UI) each span the same light-to-dark range (squint/blur test); light + dark modes checked.
- [ ] **Codes provided** in the format the user's tool needs (hex / HSL / OKLCH / CSS vars).
- [ ] **Consistency rule** stated (e.g. accent only for actions) so the system is repeatable — then trust the eye in the real design.

---

## Quick colour-psychology reference (directional, not rules; check culture)
red = passion / energy / urgency / danger · orange = friendly / energetic / affordable · yellow = optimism / warmth / caution · green = growth / health / eco / money · blue = trust / calm / reliability / tech · purple = luxury / royalty / creativity · pink = playful / romantic / modern · brown = earthy / rugged / warm · black = premium / bold / sophisticated · white = clean / simple / minimal · grey = neutral / professional. Each has a shadow side (e.g. yellow can read as unstable, green as envy) and shifts by market — always sanity-check against the audience and context.
