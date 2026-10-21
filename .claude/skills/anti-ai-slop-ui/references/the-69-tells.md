# The 69 Tells: Full Reference

Each entry: **Looks like** (concrete specifics), **Why it reads as AI**, **Instead**, and **Detect** (`scan` = the scanner can flag it, `eye` = manual review only).

Strength markers: most tells are well evidenced across multiple detectors and designer communities. Items marked *(weaker)* are flagged by tools but are contested or rarely complained about by real readers; fix them if cheap, don't obsess.

## Contents
- A. Colour and gradients (1–11)
- B. Typography (12–23)
- C. Layout and spacing (24–35)
- D. Cards, components and shape (36–44)
- E. Buttons and badges (45–48)
- F. Icons and illustration (49–55)
- G. Imagery (56–60)
- H. Motion (61–65)
- I. Theme and background (66–67)
- J. Copy tied to visuals (68–69)
- Scoring and interpretation

---

## A. Colour and gradients

### 1. Indigo / violet / purple primary
- **Looks like**: primary buttons and links in Tailwind `indigo-500` `#6366f1`, `indigo-600` `#4f46e5`, `violet-500` `#8b5cf6`, `violet-600` `#7c3aed`, `purple-500` `#a855f7`.
- **Why AI**: it was the default accent in Tailwind UI for years, so it dominates training data. Tailwind's creator publicly apologised for making every AI-generated UI indigo. Readers see it as "nobody picked a colour".
- **Instead**: derive the accent from the brand or reference. If the brand genuinely is purple, pick a specific, off-default value and pair it with non-default neutrals so it reads as chosen.
- **Detect**: scan.

### 2. Purple-to-blue (or purple-to-pink) hero gradient
- **Looks like**: diagonal `bg-gradient-to-br from-purple-500 to-blue-600` (or `via-pink-500`) washing the hero or whole page.
- **Why AI**: the signature 2024–2026 generated-site look; the single most upvoted design complaint in large Reddit threads about AI sites.
- **Instead**: a solid, confident surface. If a gradient earns its place, keep it subtle, analogous (neighbouring hues), and limited to one element.
- **Detect**: scan.

### 3. Gradient text on headlines or stats
- **Looks like**: `bg-clip-text text-transparent bg-gradient-to-r ...` or `-webkit-background-clip: text` on the H1 or a big number.
- **Why AI**: decoration with no meaning; a one-line trick models reach for to make text "pop".
- **Instead**: solid colour. Create emphasis with size, weight, or placement.
- **Detect**: scan.

### 4. Gradient body text
- **Looks like**: gradient applied to paragraphs or long runs of text.
- **Why AI**: almost no real brand does this; it screams generated and hurts legibility.
- **Instead**: never gradient running text.
- **Detect**: scan (same pattern as 3; check where it is applied).

### 5. Gradients on many surfaces at once
- **Looks like**: hero, buttons, cards, borders and badges all gradient-filled (5+ gradients on a page).
- **Why AI**: shows no restraint or hierarchy; everything shouts equally.
- **Instead**: zero or one gradient accent per page.
- **Detect**: scan (counts gradients).

### 6. Coloured glows and coloured shadows
- **Looks like**: `shadow-[0_0_60px_rgba(139,92,246,0.5)]`, `shadow-purple-500/50`, `box-shadow: 0 0 80px` in saturated purple, blue, cyan or pink behind cards and buttons.
- **Why AI**: fake depth used to make flat generated layouts feel "premium".
- **Instead**: depth from contrast, layering and spacing. If you need shadow, a neutral, tight one that describes elevation.
- **Detect**: scan.

### 7. Cream + serif + sage/forest green
- **Looks like**: warm off-white page (`#faf8f5`, `#f5f1ea`, `bg-stone-50`, `bg-amber-50`), Instrument Serif or Fraunces headline, sage or forest-green accent, often with an italic accent word.
- **Why AI**: Anthropic/Claude's own house style, now the default "tasteful" output of anti-slop prompting. The fastest-rising tell of mid-2026; readers call it a dead giveaway.
- **Instead**: don't launder purple slop into cream slop. Choose colours from the actual reference and brand.
- **Detect**: scan (partial: cream hex values, the fonts, green accents); eye for the combination.

### 8. Reflex cream/beige background
- **Looks like**: any warm cream page surface chosen because it feels "less techy" rather than for a reason. Measured on roughly three quarters of generated pages in one large tool audit.
- **Why AI**: the reflex substitute for a considered palette.
- **Instead**: pick neutrals with a source: tinted toward the brand hue, a paper stock from a reference, a true white, a real dark.
- **Detect**: scan (partial).

### 9. Neon-on-dark by default
- **Looks like**: `text-cyan-400`, `text-green-400`, `fuchsia-500` on near-black with glow.
- **Why AI**: the "cyberpunk developer tool" cliché.
- **Instead**: only if it genuinely is the brand, and used sparingly.
- **Detect**: scan (partial).

### 10. Grey text on coloured backgrounds
- **Looks like**: neutral mid-grey copy on a coloured panel, looking washed out.
- **Why AI**: grey is applied as "secondary text" without looking at the background.
- **Instead**: a darker or lighter tint of the background's own hue; check contrast.
- **Detect**: eye.

### 11. Failing contrast
- **Looks like**: `text-gray-400` / `text-zinc-400` / `text-slate-400` body copy on dark backgrounds, light grey on white. Large tool audits found the vast majority of generated pages fail the contrast floor.
- **Why AI**: models optimise for "subtle" looks, not legibility.
- **Instead**: body text at least 4.5:1, large text at least 3:1 (WCAG AA). Verify, don't guess.
- **Detect**: scan (flags common low-contrast pairings); verify with a checker.

---

## B. Typography

### 12. Inter for everything
- **Looks like**: Inter for headings and body, at default weights.
- **Why AI**: default of countless starters; explicitly named in Anthropic's own list of fonts to avoid.
- **Instead**: choose a display face for the product's voice and a body face for reading. Inter is fine as a deliberate body choice paired with a characterful display face.
- **Detect**: scan.

### 13. Geist as the unexamined pick
- **Looks like**: Geist Sans / Geist Mono on a generated dev-tool page.
- **Why AI**: Vercel's house font and v0's default; reads as "built in v0, never touched".
- **Instead**: treat it as a real decision or pick something else.
- **Detect**: scan.

### 14. Autopilot font combos
- **Looks like**: Space Grotesk, Instrument Serif, Fraunces, Playfair Display, DM Sans, Plus Jakarta Sans appearing as the "interesting" choice.
- **Why AI**: models converge on the same handful of "distinctive" fonts across generations, so they stop being distinctive.
- **Instead**: pick from outside the obvious top set, for a reason you can state (see `default-overrides.md`).
- **Detect**: scan.

### 15. Italic serif accent word in a sans headline
- **Looks like**: "Build *beautifully* crafted products" with one word in italic serif.
- **Why AI**: a now-ubiquitous generated flourish.
- **Instead**: one or two typefaces used consistently; emphasis via weight or colour if needed.
- **Detect**: scan (partial: `<em>`/`italic` with serif font in headings); eye.

### 16. Oversized italic serif hero by reflex
- **Looks like**: a huge italic Playfair/Instrument Serif H1 on a startup page.
- **Why AI**: the stock "elegant AI startup" hero.
- **Instead**: match the typeface to the product's register.
- **Detect**: eye.

### 17. H1 that fills the whole first screen
- **Looks like**: a 40+ character headline at 72px+ occupying the viewport.
- **Why AI**: size used instead of clarity; nothing else fits above the fold.
- **Instead**: shorter headline or smaller size; leave room for what it is and a real visual.
- **Detect**: scan (flags `text-7xl`+ / 72px+); eye.

### 18. Crushed display tracking
- **Looks like**: `tracking-tighter` or `letter-spacing` below -0.05em so letters collide.
- **Why AI**: found on roughly three quarters of generated pages in one large tool audit.
- **Instead**: modest negative tracking on large display sizes (around -0.01 to -0.03em), tuned by eye.
- **Detect**: scan.

### 19. Wide tracking on body text
- **Looks like**: letter-spacing above 0.05em on paragraphs.
- **Why AI**: "airy" styling applied indiscriminately.
- **Instead**: keep body text at the font's default spacing.
- **Detect**: scan (partial).

### 20. All-caps micro-labels everywhere
- **Looks like**: `uppercase tracking-widest text-xs` above every section.
- **Why AI**: generated sections all get the same eyebrow label.
- **Instead**: sentence case; reserve caps for a few short labels with a job.
- **Detect**: scan (counts).

### 21. Flat hierarchy
- **Looks like**: headings and body nearly the same size; three sizes spanning less than 2x.
- **Why AI**: nothing leads the eye; everything is "medium".
- **Instead**: a clear type scale (ratio around 1.25–1.5) with distinct roles.
- **Detect**: eye.

### 22. Monospace body copy
- **Looks like**: paragraphs in a code font so the page reads like a terminal.
- **Why AI**: "developer aesthetic" by default.
- **Instead**: mono only for code, data, or a deliberate small accent.
- **Detect**: eye.

### 23. One face at one weight throughout
- **Looks like**: everything in the same family at 400/600, no texture.
- **Why AI**: no typographic decisions were made.
- **Instead**: vary weight and size deliberately or add a second family.
- **Detect**: eye.

---

## C. Layout and spacing

### 24. Centered hero floating in space
- **Looks like**: centered H1, subhead, two buttons, nothing anchoring it.
- **Why AI**: the default hero of every template.
- **Instead**: asymmetric composition with a real product visual, or a layout derived from the reference.
- **Detect**: eye.

### 25. Hero + 3 cards + CTA skeleton
- **Looks like**: hero, three-column feature cards, testimonial row, pricing, CTA band, footer. Recognisable before any colour loads.
- **Why AI**: the single most common generated landing-page structure.
- **Instead**: let the page goal set the structure. Break the grid at least once: one oversized screenshot or video, a long-form section, a comparison, a real demo.
- **Detect**: eye.

### 26. Identical icon-topped feature cards
- **Looks like**: 3 or 6 same-size cards, each icon chip, bold label, grey two-line blurb.
- **Why AI**: treats all features as equally important; content is interchangeable.
- **Instead**: rank features; give the important one more space and a real visual; merge or drop weak ones.
- **Detect**: scan (partial: repeated `grid-cols-3` card patterns); eye.

### 27. Bento grid by reflex *(weaker)*
- **Looks like**: mixed-span rounded-card wall in the Apple keynote style.
- **Why AI**: 2026's default "modular" layout. Readers rarely complain, so it's a weak tell alone.
- **Instead**: fine when content has genuinely different sizes and importance; don't force it.
- **Detect**: eye.

### 28. Unsourced stat banner
- **Looks like**: "10k+ users · 99.9% uptime · 4.9★ rating" with no source.
- **Why AI**: models invent proof to fill space.
- **Instead**: only real metrics with context. No metrics yet? Leave the row out.
- **Detect**: scan.

### 29. Decorative 01 / 02 / 03 numbering
- **Looks like**: big "01", "02", "03" above steps already in reading order.
- **Why AI**: decoration pretending to be structure.
- **Instead**: let clear step verbs carry order; number only when users need to reference steps.
- **Detect**: scan.

### 30. Excess whitespace with everything centered
- **Looks like**: huge vertical padding (`py-32` on every section), every block centered.
- **Why AI**: "premium" faked with emptiness.
- **Instead**: vary alignment; size padding to content and grouping.
- **Detect**: scan (partial); eye.

### 31. Cards nested in cards
- **Looks like**: a card inside a card inside a card, each with padding, border and shadow.
- **Why AI**: component composition without a layout idea.
- **Instead**: flatten; use spacing, dividers and headings for grouping.
- **Detect**: eye.

### 32. Monotonous equal spacing
- **Looks like**: identical gaps everywhere, so nothing groups visually.
- **Why AI**: one spacing value repeated.
- **Instead**: related items close, groups clearly further apart (between-group gap roughly 2–3x within-group).
- **Detect**: eye.

### 33. Arbitrary spacing values
- **Looks like**: `p-3` here, `p-7` there, `mt-[37px]`.
- **Why AI**: values patched ad hoc; the eye reads it as machine-made.
- **Instead**: one scale (e.g. 4 or 8 based) applied consistently.
- **Detect**: scan (flags arbitrary bracket values).

### 34. Near-misalignment
- **Looks like**: edges and gutters off by a few pixels.
- **Instead**: align to a grid; check at several widths.
- **Detect**: eye.

### 35. Text overflow or clipping
- **Looks like**: headings running past containers; buttons with wrapped labels; long names breaking cards.
- **Why AI**: real string lengths never tested.
- **Instead**: test with real and worst-case content at mobile and desktop widths.
- **Detect**: eye.

---

## D. Cards, components and shape

### 36. Coloured accent stripe on a card edge
- **Looks like**: `border-l-4 border-indigo-500` (or top border) on rounded cards.
- **Why AI**: a designer described it as almost as reliable a sign of AI design as em-dashes are for text.
- **Instead**: remove it unless it encodes real status (error, warning).
- **Detect**: scan.

### 37. Same large radius on everything
- **Looks like**: `rounded-2xl`/`rounded-3xl` on cards, inputs, images and buttons alike.
- **Why AI**: one soft radius applied globally.
- **Instead**: a small radius scale with intent (tighter on small controls, or square for editorial). Radius should match the brand's character.
- **Detect**: scan (counts).

### 38. Pill buttons only
- **Looks like**: every button `rounded-full`.
- **Instead**: pills occasionally and deliberately.
- **Detect**: scan (counts).

### 39. Radius that blobs small cards
- **Looks like**: 32–48px radius on small cards.
- **Instead**: scale radius to element size.
- **Detect**: scan (partial).

### 40. Hairline border + wide soft shadow on one card
- **Looks like**: `border` plus `shadow-lg` both defining one edge.
- **Instead**: pick the border or the shadow.
- **Detect**: scan (partial).

### 41. Untouched shadcn Card
- **Looks like**: `rounded-lg border bg-card text-card-foreground shadow-sm`, slate/zinc neutrals, repeated with no theming.
- **Why AI**: the most cited cause of "they all look the same"; spottable from a screenshot.
- **Instead**: theme the tokens (see `default-overrides.md`). Test: could someone tell your Card from the shadcn docs Card?
- **Detect**: scan.

### 42. Decorative graph-paper grid background
- **Looks like**: faint grid lines behind sections that measure nothing.
- **Instead**: keep grids for canvases, maps, data.
- **Detect**: scan.

### 43. Diagonal stripe filler texture
- **Looks like**: `repeating-linear-gradient` stripes as background noise.
- **Instead**: plain surface or a texture from the reference.
- **Detect**: scan.

### 44. Filler FAQ accordion
- **Looks like**: stock collapsible FAQ with invented questions.
- **Instead**: only with real questions from real users.
- **Detect**: eye.

---

## E. Buttons and badges

### 45. Eyebrow pill above the H1
- **Looks like**: small `rounded-full` pill ("✨ New", "Now in beta", "Introducing X →") directly above the headline.
- **Why AI**: competes with the H1 and looks clickable when it isn't.
- **Instead**: fold the useful word into the headline or subhead; use an announcement bar only for real news with a link.
- **Detect**: scan.

### 46. Uppercase label with dot or trailing line
- **Looks like**: "• FEATURES ——" micro-label chrome.
- **Why AI**: decoration dressed up as design.
- **Instead**: remove.
- **Detect**: scan (partial).

### 47. Gradient CTA button
- **Looks like**: primary button in the purple-to-blue gradient.
- **Instead**: solid brand fill with a clear hover and focus state.
- **Detect**: scan.

### 48. Gradient-initial avatars
- **Looks like**: testimonial avatars as a single letter on a gradient chip.
- **Instead**: real faces, or omit avatars.
- **Detect**: scan (partial).

---

## F. Icons and illustration

### 49. Lucide icon in every feature card
- **Looks like**: outline Lucide icon per card (shadcn's default set).
- **Why AI**: stack fingerprint; not wrong alone, but adds up.
- **Instead**: a set that suits the brand, custom icons, or no icons where text suffices.
- **Detect**: scan (info level).

### 50. Icon in rounded tile above a heading
- **Looks like**: `w-12 h-12 rounded-lg bg-primary/10` tile holding an icon, above a card title.
- **Instead**: icon inline with the heading, or drop the container.
- **Detect**: scan (partial).

### 51. Icon tiles bigger than their content
- **Instead**: icons subordinate to the text they support.
- **Detect**: eye.

### 52. Emoji as icons or bullets
- **Looks like**: 🚀 ⚡ 🔒 🎯 ✅ 💡 🔥 as feature icons or list bullets.
- **Why AI**: no asset pipeline needed; readers immediately doubt the maker.
- **Instead**: a real SVG icon set, or none.
- **Detect**: scan.

### 53. ✨ sparkles as the "AI" signifier
- **Looks like**: the Sparkles icon or ✨ on any AI feature.
- **Instead**: show what the feature does.
- **Detect**: scan.

### 54. Blob or undraw-style placeholder art
- **Instead**: real screenshots or commissioned art.
- **Detect**: eye.

### 55. Crude hand-coded SVG mascot
- **Instead**: a well-made illustration or none.
- **Detect**: eye.

---

## G. Imagery

### 56. No real images at all
- **Looks like**: text and icons where a product shot, screenshot or photo belongs.
- **Instead**: at least one real visual on each important page. If there's nothing to show, the page isn't finished; say so to the user and leave a clearly marked slot.
- **Detect**: scan (counts images); eye.

### 57. AI 3D blobs and iridescent renders as hero art
- **Instead**: real product visuals.
- **Detect**: eye.

### 58. AI-generated stock people
- **Looks like**: too-perfect lighting, plastic skin, odd hands, diverse team around a laptop.
- **Instead**: real team or product photography, or none.
- **Detect**: eye.

### 59. Initial squares instead of faces
- **Instead**: real photos or omit.
- **Detect**: eye.

### 60. Overlay so heavy the image vanishes
- **Looks like**: `bg-black/90` over a photo.
- **Instead**: lighter overlay or no image.
- **Detect**: scan (partial).

---

## H. Motion

### 61. Everything fades in on load
- **Looks like**: every element fades up 20px at once, ~300ms ease.
- **Why AI**: motion without intent, visible within one scroll.
- **Instead**: at most one considered, staggered entrance for the key element.
- **Detect**: scan (counts animation usage).

### 62. Fade-up on every section while scrolling
- **Looks like**: `whileInView` / `data-aos` / IntersectionObserver fade on every block, so content pops in late.
- **Why AI**: makes the page feel broken rather than polished.
- **Instead**: content visible on arrival; reserve scroll motion for moments that explain something.
- **Detect**: scan.

### 63. Hover-scale on every card
- **Looks like**: `hover:scale-105`, `whileHover={{ scale: 1.05 }}` on all cards.
- **Instead**: hover states that signal what will happen (cursor, colour, underline, reveal).
- **Detect**: scan.

### 64. Bounce or elastic easing on routine actions
- **Instead**: quick ease-out (roughly 120–200ms) for UI; playful easing only where the brand wants play.
- **Detect**: scan (partial).

### 65. Pulsing dots, blinking cursors, marquees for decoration
- **Looks like**: `animate-pulse` status dot, blinking terminal cursor on static text, auto-scrolling logo marquee.
- **Instead**: motion only for real activity. Static logo rows are fine.
- **Detect**: scan.

---

## I. Theme and background

### 66. Unrequested permanent dark mode with grey body text
- **Looks like**: `bg-zinc-950`/`#09090b` page, `text-zinc-400` body, all-caps labels. The most common single tell in the Show HN audit (about a third of pages).
- **Instead**: choose the theme from the brief; if dark, meet contrast and give it a real palette.
- **Detect**: scan.

### 67. Aurora or radial spotlight glow behind the hero *(weaker)*
- **Looks like**: `blur-3xl` gradient blobs, radial halo behind the headline.
- **Why AI**: flagged by detectors; real readers complain less than expected.
- **Instead**: attention through hierarchy, not glow.
- **Detect**: scan.

---

## J. Copy tied to visuals

### 68. Vague aspirational headline
- **Looks like**: "Transform your workflow", "Supercharge your team", "Build the future", "Unlock the power of...", "Seamless", "Effortless", "Next-gen", often in gradient text.
- **Why AI**: the copy cliché travels with the visual one.
- **Instead**: say what it does, for whom, specifically. Swap test: if a competitor could use the same line, rewrite it.
- **Detect**: scan.

### 69. Em-dashes everywhere, fake stats and testimonials
- **Looks like**: dozens of em-dashes in marketing copy; "Sarah M., Marketing Director" with an initial avatar; unsourced numbers.
- **Why AI**: the model wrote the copy too, so the AI-writing fingerprint sits beside the visual one.
- **Instead**: plain punctuation; real names, roles and faces with permission, or nothing. Never invent testimonials or metrics; use clearly marked placeholders and tell the user.
- **Detect**: scan.

---

## Scoring and interpretation

- Count **unjustified** tells (justified exceptions don't count, but list them).
- **0–1**: clean, ship.
- **2–3**: mild; fix before shipping.
- **4+**: heavy; the tokens or page structure are wrong. Go back to Gate 1 or 2 instead of patching.
- Scanner hits are prompts to check, not verdicts. A hit inside a code sample, an admin screen where the user asked for shadcn defaults, or a genuine brand colour may be fine. Conversely the scanner cannot see layout (24–35), imagery quality (54–60) or overall sameness, which often matter most. Always finish with a manual pass.
- These tells shift over time. When something new becomes the effortless default (as cream + serif did in 2026), it becomes a tell. The durable rule is not the list; it is the reason behind each choice.
