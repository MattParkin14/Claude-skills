# Overriding the Defaults (Gate 2)

Untouched framework defaults are the largest single source of sameness. This file gives the override checklist and methods for choosing values. It deliberately does **not** give you a palette or font pair to copy: any fixed recipe handed to every project becomes next year's slop (this is exactly how cream + serif + sage happened). Values must come from the project's brief and reference.

## Contents
1. The token checklist
2. Where the defaults live (Tailwind, shadcn/ui, plain CSS)
3. Choosing a palette from a reference
4. Choosing type
5. Radius, spacing, shadow
6. Motion policy
7. Contrast
8. Finding a reference
9. DESIGN.md decision-record template

---

## 1. The token checklist

Set every one of these deliberately before building components. Each needs a one-line reason.

- [ ] Brand / accent colour (and what it *means*: primary action, active state)
- [ ] Neutral ramp (background, surface, border, muted text, body text), tinted with intent
- [ ] Semantic colours (success, warning, error) that fit the palette
- [ ] Display typeface and body typeface (or one family with a clear weight system)
- [ ] Type scale (sizes, line heights, tracking per role)
- [ ] Radius scale (or a deliberate "square")
- [ ] Spacing scale and section rhythm
- [ ] Shadow / elevation approach (or none)
- [ ] Motion policy (what moves, how fast, reduced-motion behaviour)
- [ ] Icon approach (set, custom, or none)
- [ ] Imagery plan (what real visuals exist, what's a marked placeholder)
- [ ] Theme (light, dark, both) and why

## 2. Where the defaults live

### Tailwind v4 (CSS-first config)
Override in the `@theme` block so utilities pick up your values instead of the stock palette:

```css
@import "tailwindcss";

@theme {
  /* Every value below must come from the brief. Comments say where. */
  --color-brand: /* sampled from <reference> */;
  --color-brand-ink: /* text-on-brand, contrast checked */;
  --color-surface: /* neutral, tinted toward brand hue or reference paper */;
  --color-ink: /* body text, >= 4.5:1 on surface */;
  --color-muted: /* secondary text, still >= 4.5:1 */;
  --font-display: /* chosen face */, /* fallback stack */;
  --font-body: /* chosen face */, /* fallback stack */;
  --radius-sm: ...; --radius-md: ...; --radius-lg: ...;
}
```

Then **use your tokens** (`bg-brand`, `text-ink`, `font-display`) and avoid reaching for stock hue utilities like `indigo-*`, `violet-*`, `purple-*`, `slate-*`, `zinc-*` in components.

### Tailwind v3 (`tailwind.config.js`)
Put brand tokens under `theme.extend.colors`, `fontFamily`, `borderRadius`. Same rule: components use the named tokens, not stock hues.

### shadcn/ui
shadcn styles components through CSS variables in `globals.css`. The untouched values (zinc/slate neutrals, `--radius: 0.5rem`, default primary) are what make every shadcn app look alike. Override at minimum:

- `--background`, `--foreground`
- `--card`, `--card-foreground`, `--popover`, `--popover-foreground`
- `--primary`, `--primary-foreground`
- `--secondary`, `--muted`, `--muted-foreground`, `--accent`
- `--border`, `--input`, `--ring`
- `--radius`
- the `.dark` equivalents if dark mode ships

Then revisit the component classes themselves: the stock Card (`rounded-lg border bg-card shadow-sm`) usually needs a different edge treatment (border *or* shadow, not both), padding that fits your spacing scale, and a radius from your scale. **Screenshot test**: could someone tell your Card, Button and Input from the shadcn docs? If not, you haven't finished.

### Plain CSS
Define the same tokens as custom properties on `:root` (and a dark variant if needed) and reference only tokens in component styles.

### Page builders (v0, Lovable, Bolt, Framer, Webflow)
These don't steer away from the defaults on their own. Put the brief and tokens into the prompt or project knowledge up front, and re-apply the checklist after every generation, because regenerations drift back to the median.

## 3. Choosing a palette from a reference

1. Start from the brand if it exists (logo, packaging, signage, existing site). Otherwise from the reference anchor.
2. Sample 3–5 candidate colours from it. Pick **one** accent with a job; the rest become neutrals or supporting tints.
3. Build neutrals *from the palette*: tint greys slightly toward the accent's hue or the reference's paper/material, instead of stock slate/zinc/stone.
4. Check the accent's hue isn't sitting in the overused bands by accident (roughly indigo/violet/purple for "techy", sage/forest green on cream for "tasteful") unless the brand says so.
5. Check contrast for every text/background pairing (section 7).
6. Use the accent sparingly; it should mean "act here" or "you are here".

## 4. Choosing type

**Autopilot faces** (the ones you'll reach for without thinking, and that readers now associate with generated sites): Inter, Roboto, Open Sans, Lato, Poppins, Montserrat, Geist, Space Grotesk, Instrument Serif, Fraunces, Playfair Display, DM Sans, Plus Jakarta Sans, Manrope. None is banned; each needs an explicit reason if used, and they should not be the first idea.

Method:
1. Write the voice in three adjectives from the brief (e.g. "exacting, calm, industrial").
2. Look for faces whose construction matches: grotesque vs humanist vs geometric sans, transitional vs slab vs didone serif, etc. Browse beyond the top of popularity lists (Google Fonts sorted by something other than "popular", Fontshare, the brand's licensed foundry fonts).
3. Pair a display face with a body face that contrasts in role but shares a quality (proportion, era, x-height). Or use one family with a real weight system.
4. Set a type scale with clear steps (ratio roughly 1.25–1.5), body 16–18px, line length around 60–75 characters, display tracking modestly negative only if the face needs it, body tracking at default.
5. Specify fallbacks and check licensing for anything not open source.

## 5. Radius, spacing, shadow

- **Radius** expresses character. Square or near-square reads precise/editorial; medium reads friendly; large reads soft/consumer. Pick the character from the brief and apply a *scale* (small controls tighter than large surfaces), never one big radius on everything.
- **Spacing**: one scale (4- or 8-based). Within a group, tight; between groups, clearly larger (roughly 2–3x); between sections, larger again. Vary section padding with content rather than giving every section the same huge `py-*`.
- **Shadow**: decide if the design uses elevation at all. If yes, neutral and tight, describing real layering. Never coloured glows as decoration. Don't combine a border and a wide shadow on the same edge.

## 6. Motion policy

Write the policy in one line in the brief, e.g. "Motion only for state feedback; one entrance on the hero visual."

- UI transitions: short (roughly 120–200ms), ease-out, on the property that changes.
- At most one considered entrance on first load. Content should be readable immediately without waiting for scroll triggers.
- Hover states communicate the result (colour, underline, cursor, reveal), not a generic scale-up.
- No decorative infinite loops (pulses, marquees, blinking cursors) unless they represent something live.
- Always respect reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## 7. Contrast

- Body text: at least 4.5:1 against its background (WCAG AA).
- Large text (roughly 24px regular or 19px bold and up): at least 3:1.
- UI boundaries and focus indicators: at least 3:1.
- Check dark themes especially: mid-grey body text on near-black is the most common failure.
- Compute it (relative luminance formula or a checker); don't eyeball.

## 8. Finding a reference

Good anchors come from the product's own world, not from other SaaS sites:
- The client's existing brand assets, premises, packaging, vehicles, uniforms.
- The industry's physical artifacts: manuals, labels, instruments, signage, forms, maps, menus.
- Print: a specific magazine, newspaper, book series, poster tradition.
- A specific, named non-template website whose *principles* (not pixels) fit.
- For internal tools: the data itself. Let density, tables and the real workflow drive the design.

Borrow principles (proportion, rhythm, colour logic), never copy another site's design wholesale.

## 9. DESIGN.md decision-record template

For multi-page or ongoing projects, write this file at the project root and keep it updated. It stops later generations drifting back to defaults. Keep it short.

```markdown
# Design decisions: <project>

## Brief
- Audience and job:
- Point of view (one sentence):
- Reference anchor(s):

## Tokens (each with its reason)
- Accent: <value> because ...
- Neutrals: <values> because ...
- Display type: <face> because ...
- Body type: <face> because ...
- Type scale: ...
- Radius scale: ... because ...
- Spacing scale and rhythm: ...
- Elevation: ...
- Motion policy: ...
- Icons: ...
- Imagery: real assets available / placeholders marked

## Justified exceptions to the anti-slop list
- Tell #<id>: kept because ...

## Last audit
- Scanner score: ... Manual review: ... Unjustified tells remaining: ...
```
