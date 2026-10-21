---
name: dashboard-saas-redesign
description: >
  Playbook for designing or redesigning SaaS product UIs — dashboards, data
  tables, admin panels, settings, empty states, color systems — plus the
  landing/pricing pages that sell them. Distilled from 25 expert sources
  (UI redesign breakdowns, NN/g, data-table UX, color theory, SaaS teardowns).
  Use whenever the user is designing, redesigning, reviewing, or building a
  SaaS app UI, dashboard, admin interface, data table, empty state, onboarding
  screen, KPI card, or SaaS landing/pricing page; asks "make this dashboard
  look good/professional", "improve this table", "pick colors for my app",
  "review my landing page"; or is generating frontend code for any of the
  above. Also trigger on /dashboard-saas-redesign.
---

# Dashboard & SaaS Redesign Playbook

> **One of a 3-skill web-design set — you are in the functional product-UI layer.** This skill owns the *app itself*: dashboards, data tables, empty states, in-app design systems, plus the SaaS-specific pricing page. Reach for a sibling when the job shifts:
> - **landing-pages** — the general marketing-page craft (hero, outcome headlines, social proof, FUD-reducers, cold-traffic structure). Phase 6 below defers to it; use it for the marketing page itself.
> - **stunning-websites** — the visual-execution and Claude-build-workflow layer (typography, colour, motion, anti-AI-slop). Use it to make either the app or its marketing page look premium.

Ranked, deduplicated guidance from 25 expert sources. Consensus counts show how
many sources independently endorsed each action. Follow the workflow order:
foundation → audit → layout → components → states → sell it.

## Phase 1 — Foundation (before any pixels)

### 1. Anchor the redesign in a one-sentence product definition (4 sources)
Write "X is the [category] for [audience] to [core jobs]" and list the 4–6
core jobs ("main quest": home, find, act, manage, account). Judge every
screen and nav item against this list; everything else is a side quest.
Structure the IA around the definition, not around existing pages.

### 2. Start from user problems and copy, not aesthetics (5 sources)
- Collect real user complaints first; design against reported pain.
- Write interface copy/labels first, on a white background, until a
  non-technical person understands what everything does — then style it.
- Design is how the product solves the problem, not the gradient or font.
  If users can't tell what a screen does, it has failed regardless of looks.
- Users must be able to see and control anything "personalized": visible
  filters/tags they can edit, pin/hide/reorder for home content, and an off
  switch for every engagement feature. Never shrink or hide controls to trap
  engagement — it breeds resentment, not retention.

### 3. Audit and consolidate before redesigning (3 sources)
Run three inventories on the existing product:
- **Colors**: collapse to ~12 tokens (2 text, ~5 background, 2 brand, 3 accent).
- **Icons**: one set, one style; same icon = same meaning everywhere.
- **Navigation**: list every option from every nav region, sort each into
  exactly ONE top-level section, delete duplicates. One layout per pattern —
  the same entity must never have two coexisting designs.
Consistency extends across platforms: the same feature exposes the same
options on desktop and mobile.

## Phase 2 — The dashboard shell (visual system)

### 4. Use the tinted-shell recipe (1 source, highly specific)
- Background: slightly tinted off-white (not pure white/gray) in the brand
  hue; white content panel/cards on top for low-contrast separation.
  Dark mode: dark slate base, panels = same hue slightly lightened.
- Radius hierarchy: children get smaller radii than parents (e.g. panel 18 →
  card 14). Same for shadows: child shadows subtler than parent shadows.
- Shadows are colored, never black: desaturated background hue at ~10–20%
  opacity, stacked twice — one large/soft (8/8/40), one tight (4/4/4).
- ONE saturated accent color against a calm shell; hover = same hue darkened.

### 5. Build the palette by locking saturation + brightness (3 sources)
Work in HSB. Pick a category, lock S/B in its range, then vary ONLY hue —
every color generated will sit well together:
- Jewel (rich/luxury): S 73–83, B 56–76 · Pastel: S 14–21, B 89–96
- Earth (muted): S 36–46, B 36–77 · Neutral: S 1–10, B 70–99
- Neon: S 63–100, B 82–100 · Shades: S 0
Combine one main category + neutrals + shades. In practice UI palettes are
monochromatic (tint/shade scale of one primary) or complementary; strong base
for primary buttons, light tints for hover/selected states and backgrounds.
Pick hues by psychology: red = urgent/error, blue = trust/professional,
green = health/success/positive.

### 6. Card anatomy for KPI/stat cards (2 sources)
Small all-caps muted label (≥12–14px) + huge bold value (~40px) + context icon
+ one visualization (pill progress bar or radial gauge in accent). The stat
number is the first thing eyes hit — design that hierarchy deliberately.
Max 2 typefaces; never below 14px for UI text; 50–60 chars max per line.
Separators: 1px lines in a light accent tint, not gray/black.

## Phase 3 — Data tables (the heart of most SaaS UIs)

### 7. Apply the table scannability bundle (3 sources)
- Header visually distinct (tint background), sort icons in accent color so
  sortability is discoverable (gray icons = invisible affordance).
- Light row borders; generous row height; data needs room to breathe.
- Numbers right-aligned (digit-place comparison); text left-aligned;
  bold the record-name column — it anchors each row.
- Statuses as colored chips, not text; dates with abbreviated month names.
- Row actions as icons; bulk-action buttons as icon + label pairs.
- Selected rows get a soft tint highlight, not just a checkbox tick.
- Big, inviting search field; filters visible in a sidebar (plain "Filter"
  label, reset button, hide zero-result options).
- Material spec anchors: header row 56, data rows 52, 16px side padding per
  column, radius 4, no shadows/elevation on tables.

### 8. On mobile, cards — not horizontal scroll (1 source)
Horizontal scroll is the last resort (add prev/next column-jump buttons if
forced). Default: each row becomes a card showing only key fields, with a
3–4 button toolbar — Filters, Sort, bulk actions (appear on select), and a
Customize button so users pick which fields the cards show. Compress wide
tables by finding repeated column groups and turning them into tabs.

### 9. Long lists everywhere get the same kit (5 sources)
Search + sort + filters + grid/list view toggle + bulk actions. This applies
to libraries, histories, settings, playlists, marketplaces — any collection.
Never reshuffle list items as their state changes (downloads jumping between
sections); keep positions stable and let users clear completed items.

## Phase 4 — States and flows

### 10. Design every empty state with the 3-part formula (3 sources, unanimous)
Never ship a blank container — users can't tell "empty" from "loading" from
"broken". Every empty state gets: (1) WHY it's empty, (2) what value fills it /
how the product works, (3) a CTA that resolves it. Anatomy: small visual +
title (reason) + one-line description (value, in product language — never
"no rows in database") + 1–2 CTAs.
- Hunt for them by walking user flows (no search results → "clear filters").
- Never a dead end; never generic ("Nothing here, come back later").
- Go further: offer templates, smart recommendations, or pre-created sample
  content that doubles as onboarding.
- If a process is running, show progress, not emptiness.
- Design success states too (task complete, inbox zero) — congratulate and
  point to the next action.
- Measure: creations started from the empty state, time-to-value, retention.

### 11. Reduce clicks on high-frequency actions; add friction to decisions (3 sources)
One-click for repeated micro-actions (save-for-later without a popup — put
the undo/reminder at the end instead). But if an item has many
decision-affecting details, don't offer instant commit from the list — route
through the detail page. Avoid hover-only and hover-moving controls: static
cards with visible actions beat cards that expand under the cursor.

### 12. Honest, decision-ready data display (2 sources)
Show the numbers users decide with, where they decide: proportional rating
breakdowns instead of vague labels, current market price next to the user's
price, discount end dates on the card, filters tied to meaning-changing
events ("reviews since last update"). Let users edit in place instead of
delete-and-recreate.

## Phase 5 — Delight (selective, on top of a boring backbone)

### 13. Flat + design system is the 80% backbone; spend delight on the 20% (3 sources)
Internal/professional tools can stay plain. For user-facing products, add
depth/texture/motion only to the few elements that matter: the key CTA, a
signature component, an onboarding moment. Safety rule: design the clean flat
structure first — if removing the styled layer changes nothing about
comprehension, it's safe to add.
Cheap differentiators: a distinctive display typeface (not Inter/Poppins),
playful microcopy ("I am awesome" on a save-workout button), optical button
alignment (nudge padding 1px for font quirks — most buttons are misaligned).
Evidence: users often prefer warmth designers dismiss (~90% loved a wooden
background in an A/B test; real users split ~50/50 on flat vs rich).

## Phase 6 — Selling the product (landing + pricing)

> The general marketing-page craft — outcome headlines and banned adjectives,
> hero visuals, social proof, FUD-reducers, page structure, cold-traffic
> sequencing — lives in the **landing-pages** skill. Use it for the marketing
> page itself. Below are only the **SaaS-specific deltas** that landing-pages
> doesn't cover.

### 14. Make the homepage teach the whole product (4 sources)
Beyond the standard outcome-headline + real-screens rules (→ landing-pages):
60–80% of visitors should understand the *entire* product from the homepage
alone, via one step-by-step walkthrough (host → promote → sell), not a grid of
"explore more" links that fragment the story into subpages. Multiply use cases
on the page (visitors arrive with one, should leave with 3–4 worked examples →
faster activation, less churn, more upgrades), and make role-based sections
each target that role's real worry (churn risk, automated reports) — then carry
it past signup: ask role, drip role-specific "did you know" use cases.

### 15. Team collaboration is the growth lever (2 sources)
For SaaS, teams are where the money is and the hardest to switch — so make the
product itself promote inviting and replying. Loom's shift to team-collab
positioning transformed the business, and the UI was rebuilt so every element
pushes invite/reply. Answer switching objections visually (data/template
migration, team learning curve, input/output formats, speed at scale,
compliance); if a well-known competitor exists, say on the homepage why you win,
not in a footer compare link. Integrations as recipes ("after every Zoom call,
a follow-up reminder is created"), not logo walls. Risk-reversal bar: free
trial, free migration, free support.

### 16. Pricing page — defuse your model's confusion (4 sources)
The SaaS-specific heart of the sell. Open with "start free". Defuse your pricing
model's single biggest confusion *visually* — e.g. Coda's "pay only for doc
makers", with a calculator. Plan overview cards, then a grouped comparison table
with a one-line description per plan and per section. Concrete limits let users
self-qualify (2,000 leads/month); explain vague inclusions ("1-on-1 analytics" =
what exactly?). State which company type each plan is for. FAQ at the bottom.
Capture non-buyers with a lead magnet as the alternative CTA.

## Judgment calls (where sources disagree)

- **Flat/minimal vs rich/delightful**: table/data-density sources say no
  elevation, minimal chrome; Malewicz says pure flat killed delight and users
  like warmth. Resolution: data surfaces stay flat and calm; spend richness on
  brand moments and primary actions.
- **Icons vs text**: in-row table actions → icons alone (reduce noise); bulk
  actions and anything ambiguous → icon + label. Never icon-only when the
  icon isn't universally understood.
- **Hover interactions**: fine for revealing labels on a collapsed nav rail;
  bad when they move/expand the element under the cursor or hide the only
  path to an action (touch has no hover).
- **Speed of shipping vs craft**: teardown sources push "clarity now, iterate
  weekly"; craft sources warn each accepted "80% is fine" lowers your bar.
  Resolution: iterate fast on copy/layout, never compromise the consistency
  tokens (colors, icons, spacing) — those are the compounding assets.

---
*Provenance: distilled 2026-07-09 from 25 sources (24 YouTube videos + 1 NN/g
article) on dashboard/SaaS UI redesign, data tables, empty states, color
theory, and SaaS landing-page teardowns. Phase 6 trimmed 2026-08-04 to defer
generic landing-page craft to the landing-pages skill; cross-references added
across the 3-skill web-design set.*
