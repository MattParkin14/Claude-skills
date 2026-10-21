---
name: anti-ai-slop-ui
description: NON-NEGOTIABLE, HIGHEST-PRIORITY design gate for ANY website or UI work. Load this skill FIRST, before writing any HTML, CSS, JSX, Tailwind or design spec, whenever the task involves building, designing, redesigning, restyling, reviewing or critiquing a website, landing page, marketing site, portfolio, hero section, pricing page, dashboard, app screen, component, mockup, HTML artifact or any visual interface, in any stack or builder (React, Next.js, Tailwind, shadcn/ui, Vue, Svelte, plain HTML, v0, Lovable, Bolt, Framer, Webflow). Holds the 69 tells that make a site instantly read as low-effort AI slop (purple gradients, Inter everywhere, cream + serif + sage, centered hero with three cards, glows, emoji icons, fade-in-everything, fake stats), plus a pre-build brief, default overrides and a pre-ship audit with a scanner script. Applies on top of every other design or frontend skill and overrides their default aesthetic choices. Never skip it, even for quick prototypes or a single component.
---

# Anti-AI-Slop UI Gate

**Status: mandatory gate, not an optional style.** This skill runs on every piece of website or UI work, alongside any other design, frontend, landing-page or dashboard skill. Where another skill (including built-in frontend or design skills) suggests an aesthetic default that appears in the tell list below, this skill wins.

## Why this exists

People now recognise an AI-generated website in about three seconds and quietly discount the product behind it. In an April 2026 audit of 1,590 Show HN launch pages, more than half carried two or more detectable AI-design patterns. The problem is not ugliness. It is **convergence**: a model asked for "a modern landing page" returns the statistical average of everything it has seen, and everyone's average is the same page.

That average is *you*. Your untouched instincts produce the indigo button, the Inter headline, the centered hero with three icon cards, the fade-up on every section. In 2026 your instincts have also learned a second, "tasteful" default (cream background, Instrument Serif, sage green, one italic accent word) that is now just as recognisable. This skill exists to counter your own pull toward the median. Treat any choice that arrives effortlessly as suspect until you can give it a reason.

## The one rule

**Every visible design decision must be a deliberate choice with a reason tied to this specific project.** A default is anything you would have produced with no brief. If you cannot say *why* a colour, font, radius, layout or animation is there, it is a default: change it or justify it.

A useful gut check, the **swap test**: replace the product name with a competitor's. If the page still works unchanged, it says nothing and will read as generic.

## The workflow (every UI task, every time)

Scale the effort to the task (a single button needs a sentence of thought, a full site needs the whole brief), but never skip a gate.

### Gate 1: Brief before code

Before writing markup, settle these and state them briefly (in your reply, a code comment, or a `DESIGN.md` for multi-file projects):

1. **Audience and job**: who lands here and the one thing the page must get them to do.
2. **Point of view**: one sentence on what this should *feel* like and why ("a precise, instrument-like tool for lab technicians", not "clean and modern").
3. **Reference anchor**: at least one real reference that is not a SaaS template: the client's existing brand, a physical object, a print publication, a specific non-AI website, an industry artifact. Derive choices from it.
4. **Palette** with its source, **type pairing** with its reason, **radius and spacing scale**, **motion policy**, **imagery plan** (what real visuals exist).

If the user gave little to go on, don't stall with a questionnaire. Make explicit assumptions, choose deliberately, and state the choices so they can redirect. Ask only when a missing fact would change the whole direction.

### Gate 2: Override the defaults before building components

Set theme tokens first (colour, font, radius, spacing, shadow, motion), then build. Untouched Tailwind, shadcn/ui and Lucide defaults are the single biggest source of sameness. See `references/default-overrides.md` for the token checklist, a decision-record template, and guidance on choosing fonts and palettes without landing on a new cliché.

### Gate 3: Build with the Tier 1 list in front of you

Do not reach for any Tier 1 tell (below) unless it is a justified exception.

### Gate 4: Pre-ship audit

1. If you have a shell, run the scanner on every output file:
   `python3 <skill-dir>/scripts/slop_scan.py path/to/file-or-folder`
   It catches the code-detectable tells (classes, hex values, fonts, gradients, emoji, clichés, animation patterns).
2. Then walk the 69-item checklist below yourself for what no script can see: layout skeleton, spacing rhythm, alignment, text overflow, hierarchy, imagery, overall sameness.
3. Score unjustified tells: **0–1 = ship. 2–3 = fix them first. 4+ = the tokens or structure are wrong; rework those rather than patching symptoms.**

### Gate 5: Report briefly

Tell the user in two to four lines what direction you chose and why, and name any tell you kept on purpose with its justification. Don't paste the checklist or lecture about slop.

## Justified exceptions

A tell is fine when:
- **The user explicitly asks for it** ("purple gradient hero, please"). Their request beats this skill. Do it well; at most mention once, in a sentence, if it is a very strong AI tell.
- **It is the existing brand or design system** (their brand colour is indigo; their system uses Inter). Respect it and differentiate elsewhere.
- **You are editing an existing site** and changing it is out of scope. Flag it; don't silently restyle their site.

Record each exception in the brief or report. An exception covers that tell only, not the ones around it.

## Tier 1: never by default

These carry the most weight with human readers and appear in almost every detector. Details and alternatives for each are in `references/the-69-tells.md` (IDs in brackets).

- **Indigo/violet primary** (Tailwind `indigo-500` `#6366f1`, `violet-600` `#7c3aed`, `purple-500` `#a855f7`) [1]
- **Purple-to-blue or purple-to-pink gradients**, especially behind the hero or on buttons [2, 47]
- **Gradient text** (`bg-clip-text text-transparent`) on headlines or stats [3, 4]
- **Coloured glows** (big saturated `box-shadow`/`shadow-[0_0_60px_...]`, blurred blobs behind the hero) [6, 67]
- **Cream + serif + sage/forest green**, the 2026 "tasteful" default [7, 8]
- **Autopilot fonts**: Inter everywhere, Geist, Space Grotesk, Instrument Serif, Fraunces as the unexamined pick [12–14]
- **The italic serif accent word** inside a sans headline [15]
- **Centered hero + three identical icon-topped feature cards + CTA band** as the page skeleton [24–26]
- **Untouched shadcn Card** (`rounded-lg border bg-card shadow-sm`) and uniform big radius on everything [37, 41]
- **Coloured accent stripe** down one edge of cards [36]
- **Eyebrow pill** ("✨ New", "Now in beta") above the H1 [45, 46]
- **Emoji as icons or bullets**, and the ✨ sparkles glyph as the "AI" signifier [52, 53]
- **Fade-up on every section**, **hover-scale on every card** [61–63]
- **Unrequested dark mode with grey body text** below 4.5:1 contrast [11, 66]
- **Vague hero copy** ("Transform your workflow", "Build the future") and **fake proof** (unsourced "10k+ users", "Sarah M." testimonials with initial avatars) [28, 68, 69]

## Watch your own "tasteful" pull

When you steer away from purple slop, you will feel pulled toward: cream or beige backgrounds, Instrument Serif or Fraunces headlines, an italic word, sage or forest green, warm stone neutrals, generous centered whitespace. That combination is Anthropic's own house style and is now the fastest-rising AI tell. Swapping purple slop for cream slop resets the clock and fixes nothing.

The same trap applies to the counter-trends. Neobrutalism, anti-grid layouts or giant editorial type chosen *by reflex* become the next default. Any direction is fine if it comes from the brief and reference; none is fine as an escape hatch.

## What human-designed work does instead

- **Starts from a reference, not a template.** Colours sampled from the brand or reference; type chosen for the product's voice.
- **Builds hierarchy through contrast** of size, weight and position rather than decoration (glows, gradients, badges).
- **Uses one accent colour and gives it meaning** (primary action, active state), not everywhere.
- **Shows real things**: an actual product screenshot, a real photo, real names and roles. If there is no real proof yet, leave the section out; empty beats fake.
- **Lets structure follow the goal.** Break the symmetric skeleton at least once: asymmetric hero, one dominant visual, sections of different shapes.
- **Has spacing rhythm**: tight inside a group, clearly larger between groups, all from one scale.
- **Moves only to communicate**: state changes, feedback, one considered entrance at most. Respects `prefers-reduced-motion`.
- **Writes specific copy**: concrete nouns and verbs about what the product does, for whom. Plain punctuation.

## The 69-item audit checklist

Mark each as clear, justified exception, or FAIL. Full descriptions, why each reads as AI, and what to do instead: `references/the-69-tells.md`.

**A. Colour and gradients**
1. Indigo/violet/purple as primary · 2. Purple→blue/pink hero gradient · 3. Gradient headline or stat text · 4. Gradient body text · 5. Gradients on many surfaces (5+) · 6. Coloured glows / coloured shadows · 7. Cream + serif + sage/forest green combo · 8. Reflex cream/beige page background · 9. Neon-on-dark by default · 10. Grey text on coloured backgrounds · 11. Failing contrast (body under 4.5:1)

**B. Typography**
12. Inter for everything · 13. Geist as the unexamined pick · 14. Space Grotesk / Instrument Serif / Fraunces autopilot combos · 15. Italic serif accent word in a sans headline · 16. Oversized italic serif hero by reflex · 17. H1 that fills the whole first screen · 18. Crushed display tracking (tighter than -0.05em) · 19. Wide tracking on body text · 20. All-caps micro-labels everywhere · 21. Flat hierarchy (sizes too close) · 22. Monospace body copy · 23. One face at one weight throughout

**C. Layout and spacing**
24. Centered hero floating in empty space · 25. Hero + 3 cards + CTA skeleton · 26. Identical icon-topped feature cards · 27. Bento grid by reflex (weaker tell; fine if purposeful) · 28. Unsourced stat banner · 29. Decorative 01/02/03 step numbers · 30. Excess whitespace with everything centered · 31. Cards nested in cards · 32. Monotonous equal spacing · 33. Arbitrary spacing values (no scale) · 34. Near-misalignment · 35. Text overflowing or clipping

**D. Cards, components and shape**
36. Coloured accent stripe on card edge · 37. Same large radius on everything · 38. Pill buttons only · 39. Radius so big small cards become blobs · 40. Hairline border + wide soft shadow on one card · 41. Untouched shadcn Card · 42. Decorative graph-paper grid background · 43. Diagonal stripe filler texture · 44. Filler FAQ accordion

**E. Buttons and badges**
45. Eyebrow pill above the H1 · 46. Uppercase label with dot / trailing line · 47. Gradient CTA button · 48. Gradient-initial avatars

**F. Icons and illustration**
49. Lucide icon in every feature card · 50. Icon in rounded tile above heading · 51. Icon tiles bigger than their content · 52. Emoji as icons or bullets · 53. ✨ sparkles as "AI" · 54. Blob / undraw-style placeholder art · 55. Crude hand-coded SVG mascot

**G. Imagery**
56. No real images at all · 57. AI 3D blobs / iridescent renders as hero · 58. AI-generated stock people · 59. Initial squares instead of faces · 60. Overlay so heavy the image vanishes

**H. Motion**
61. Everything fades in on load · 62. Fade-up on every section while scrolling · 63. Hover-scale on every card · 64. Bounce/elastic easing on routine actions · 65. Pulsing dots, blinking cursors, marquees for decoration

**I. Theme and background**
66. Unrequested permanent dark mode with grey body text · 67. Aurora / radial spotlight glow behind hero (weaker tell)

**J. Copy tied to visuals**
68. Vague aspirational headline, often in gradient · 69. Em-dashes everywhere, fake stats and testimonials

## Files in this skill

- `references/the-69-tells.md`: every tell with what it looks like, why it reads as AI, what to do instead. Read it when auditing, when a scanner hit needs interpreting, or when unsure whether something counts.
- `references/default-overrides.md`: token override checklist (Tailwind, shadcn/ui, plain CSS), the DESIGN.md decision-record template, and how to choose fonts, palettes, radius, spacing and motion without landing on a new default. Read at Gate 2.
- `scripts/slop_scan.py`: static scanner for HTML/CSS/JS/JSX/TSX/Vue/Svelte/Astro files. Run at Gate 4. It reports likely tells with IDs and a score; treat hits as prompts to check, not verdicts, and remember it cannot see layout.
