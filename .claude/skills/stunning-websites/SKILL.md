---
name: stunning-websites
description: "Playbook for designing and building websites with Claude that look professionally designed rather than AI-generated. Use whenever the user wants to build, design, redesign, restyle or critique a website, landing page, marketing site, portfolio or hero section; asks why their AI-built site looks generic, templated, or 'like AI slop'; wants help with typography, colour systems, white space, hero sections, backgrounds, animations, 3D elements or design references; is setting up a project in Claude Code or Claude Design to build a site; or asks what to prompt to get a premium-looking result. Trigger on phrases like 'build me a website', 'make this look less AI', 'why does my site look generic', '$10k website', 'design system', 'hero section', 'pick fonts for my site', 'add animations', 'make it look expensive', 'clone this site's style'. Also trigger on /stunning-websites."
---

# Stunning websites

> **One of a 3-skill web-design set — you are in the visual-craft + Claude-build-workflow layer.** It applies to *any* site type. Reach for a sibling when the job shifts:
> - **landing-pages** — conversion copy & page structure for landing/opt-in/sales pages, especially cold traffic. Use it for *what the page must say to convert*; use this skill for *how it looks and how you drive Claude to build it*. A marketing-site build usually wants both.
> - **dashboard-saas-redesign** — functional product UI: dashboards, data tables, empty states, in-app design systems. Use it when the artifact is an *app*, not a marketing page.

The gap between a generic AI website and a professionally designed one is not complexity — it is **direction**. Same model, same effort. The difference is a handful of specific decisions made before the first build prompt and between each revision.

Two ideas underpin everything below:

> "It's not a Claude problem, that's a prompting problem."
> "The first generation is never the product. It's just the starting point."

Piling on more animation and more effects is exactly what makes AI sites look like AI sites. Beautiful sites aren't more complicated — they're more directed.

---

## Phase 0 — Before you prompt anything

**Create an empty project folder.** Empty matters: you want to see exactly what gets created.

**Put a `claude.md` in it.** The paragraph that does the work is the role line:

> *Behave like a senior UI designer and front-end developer.*

Two independent sources converged on this exact framing — one in `claude.md`, one at the top of a generated build prompt. It changes the output.

**Install the design skills.**

- **Frontend Design** (Anthropic) — always-on. Bans the most overused fonts and pushes bold direction over safe defaults; it's also what produces restrained, sensory copy instead of adjective soup. Install with `install this skill globally` + link, or via plus → plugins → browse plugins → search "front-end design".
- **UI/UX Pro Max** (community) — 57 UI styles, 95 colour palettes, 56 font pairings. Invoke explicitly as `/ui-ux-pro-max` when you want a large design intervention. Install with the exact phrase `install this plugin globally using NPM` + link — that wording is what makes it install cleanly via the terminal.
- **Restart Claude after installing**, or the skill isn't live.

**Gather every asset into the folder first** — logo, brand colours, photography, video — in a `media/` or `assets/` subfolder. Claude will then find the logo unprompted, extract the palette from it, and label images by their actual content. Retrofitting assets later means redoing layout work.

**Collect 3–5 visual references.** Awwwards, Dribbble, Pinterest, Mobbin. Search by industry ("landscaping", "modern restaurant"), not by adjective. You can also just ask Claude to find beautiful sites in your category. Either pick one site whose whole feel you want, or build a Frankenstein from screenshots of your favourite parts of several.

> Showing beats describing — and scrolling references is how you work out what your own taste actually is before you commit.

For a full-page reference, use a screenshot extension. **Claude's attachment cap is 20 MB** — compress the image if you exceed it rather than cropping it.

---

## Phase 1 — The design system

Build the rule book before any page exists. Everything downstream reads it, which is what keeps twelve sections and five pages coherent instead of drifting.

Write it to a file — `design.md` or a brand kit — containing at minimum:

- Colour palette with hex values, and what each colour is *for*
- Heading font and body font, with sizes and hierarchy
- Button styling, including hover background colour
- Form and placeholder colours
- Spacing between containers and columns, border radii
- Logo, slogan, positioning, mood, brand story
- **The rules about what this site will never do**

Three ways to seed it, in rough order of effort:

1. **From a published brand kit.** Sites like getdesign.md publish complete design systems for 68 major brands (Airbnb, Airtable, Apple, BMW, Dell, HP). Copy the `design.md` text, paste it into the design system's "additional notes" field, generate. Roughly five minutes, and you inherit a coherent professional system rather than inventing one.
2. **From a single inspiration image.** Claude Design's design-system tool accepts visual assets, a Figma file, a GitHub repo, or a local codebase. One image is enough to produce navigation, type scale, colour blobs, wordmark, brand colours, animations, elevations and radii — work described as "a few days in Figma."
3. **From an interview.** See the palette trick below.

**Publish the design system** once generated (and set it default if you'll reuse it). Easy step to miss; without it the system isn't selectable for the build.

### The palette trick

The single most distinctive move in the whole corpus. During the intake interview, ask the user:

> **"Describe one real moment around the business. Not colours, not fonts — a moment."**

Example answer: *"Early morning at the bar, steam rising off a fresh pour. Warm light on wooden shelves full of coffee bags."*

That one sentence generates the entire colour palette. The colours come from their world, not from a template — which is precisely why the result doesn't look like everyone else's.

### Separate style from structure

The design system supplies **style**. A reference screenshot supplies **structure**. Say so explicitly: *"use the attached screenshot for the structure of the page, and the design system for all branding."* The output keeps the reference's layout while wearing your brand — so it isn't a clone.

---

## Phase 2 — The build prompt

**Always end with: "Please ask me any questions you need to complete this job."**

This is the highest-leverage line in the process. It stops Claude building immediately and produces the questions that actually determine the site — name, audience, sections, who writes the copy, stack, animation level — plus reconciliation questions you would never have thought to answer, e.g. *"the reference is dark cinematic but your brand is white and ink — how should I reconcile these?"*

> This is the most important moment in the build. The answers become the entire site. Every minute of specificity here saves an argument later.

Ask the questions **one at a time** in plain language if you're running the interview yourself. It's less overwhelming and the answers are better.

**Offer three named design directions before building a single section.** Render them side by side with real palettes, real font pairings, the user's actual headline set in each, and a one-line rationale for each. Mark a recommendation, but let them choose.

> You're picking the direction before anything is built, so no tokens are spent on a look that gets thrown away.

**Consider having a model write the build prompt.** Describe the project in a few sentences and ask for a detailed prompt or spec `.md` in return, then feed that to the builder. One creator's generated prompt ran 387 lines: *"if we sat down to write this ourselves we probably couldn't write one this good."*

**Build in visible stages, not one giant result.** A staging that works:

1. **Direction** — three options, pick one, write `design.md`.
2. **First render, deliberately almost empty** — brand name and one big line, in the real fonts on the real background. Premium sites say one thing first.
3. **Structure** — full page, sections chosen for the business type (a local business gets hours/address/map; a product site gets feature moments and a buy section). Images and text as **labelled grey placeholders** ("hero", "the bar", "morning light") so you know exactly which asset goes where. Structure first, words next.
4. **Copy.**
5. **Images.**
6. **Polish pass.**

Set the session to **auto mode** so it doesn't stop for permission on every step — unless the user prefers to approve each edit, which is legitimate.

Expect roughly three minutes of planning before a line of code, then four to five minutes building.

---

## Phase 3 — The quality levers

### Typography

Claude's defaults — **Inter, Roboto, Open Sans** — are what every AI builder reaches for. Inter in particular "instantly screams AI made this," and Anthropic's own design guidance flags these as fonts to avoid.

Reach for: Space Grotesk, Playfair Display, Crimson Pro, Clash Display, Satoshi, Cabinet Grotesk, IBM Plex, Bricolage Grotesque, Geist, Fraunces.

| Site type | Pairing |
|---|---|
| Editorial / luxury | Playfair Display + Inter |
| SaaS / corporate | Poppins + Work Sans |
| Startup landing | DM Serif Display + Inter |
| Content-heavy B2B | Merriweather + Roboto |

Minimum viable direction: heading font, body font, and how strong the hierarchy should feel. Google Fonts is the browsing source and it's free — sort by category (handwriting, informal, formal, upright) to browse by feel rather than by name.

Type moves trust, not just taste. In Errol Morris's 2012 experiment (~45,000 respondents) the same statement was measurably more believable set in Baskerville than Helvetica — about 1.5 percentage points, statistically significant.

Strongest version: make typography the entire design system. One display face at bold weight with wide tracking for headings, a mono for body and UI, no gradients, no illustrations — let the type carry the page.

### Colour — 60/30/10

- **60%** dominant — backgrounds and main surfaces
- **30%** secondary — cards, navigation, dividers, supporting surfaces
- **10%** accent — CTAs, links, active states, key callouts, **and nowhere else**

Two or three colours, each with a named job. One premium build shipped on five hex values total: near-black, warm cream, oxblood, brass, slate. Without a system, blues drift between sections and accents get sprayed around — the page reads as *assembled* rather than *designed*.

Describe colours as real-world references rather than names: "the deep black of a Bloomberg terminal", "the dark slate of a luxury watch bezel", "an accent like the glow on a heart-rate monitor."

Always specify contrast: **≥4.5:1 for body text, ≥3:1 for large text**, plus "keep all text clearly legible against its background."

### White space

AI builders lean tight because they try to fill the visible screen. The line that does most of the work:

> **"White space is the primary design directive. Add more space when in doubt."**

Distinguish **micro** (line height, letter spacing, paragraph gaps) from **macro** (section gaps, card padding, breathing room between blocks).

### Hero

*(For the conversion side of the hero — outcome-headline formulas, FUD-reducers, cold-traffic sequencing, social-proof placement — defer to the **landing-pages** skill. This section covers the visual execution of that hero.)*

Users form a visual opinion in **17–50 milliseconds**. Eye-tracking order is headline → visual → CTA, and the headline alone carries roughly **60–70% of the persuasion load**. If the hero is vague the whole site reads as vague — engineer it explicitly even if you do nothing else.

Five required elements:

1. **Headline** built around the customer's *outcome*, not what the business does.
2. **Sub-headline** with exactly one concrete layer of specificity.
3. **One primary CTA** with specific copy — "Claim your first week free", never "Get started".
4. **A real visual** — product shot, interface screenshot, or a defined image slot. Not abstract stock art.
5. **One trust signal** — logo bar, customer count, testimonial, or a concrete result stat.

Typical AI failure: headline describes the business, CTA is generic, visual is decorative.

When the hero matters — it always does — ask for three alternative layouts of **that section only**, keeping the rest of the page unchanged. Common strong options: split (text left, full-height image right, editorial feel); centred over a full-width image; and an inset frame with the heading lower-left and a product card layered in so the product is visible on load.

### Background

Worth treating as its own step, especially on minimal pages. A radial gradient with blurred colour circles positioned around the page "adds texture and character — makes it feel more complete" without adding content.

### Motion

Motion is what takes a site from *looks* professional to *feels* expensive, and it's where people overshoot most.

- Offer a motion style up front: **calm / smooth and premium / bold and kinetic / minimal**, with a recommendation.
- **GSAP** for scroll-triggered entrances, **Framer Motion / motion.dev** for hover and interaction states. `demos.greensock.com` is browsable.
- **Name the timing.** Hover enlarge over ~300 ms — instant is jagged, slow is sludge.
- A reliable hero pattern: the hero image opens full-screen then scales down into its resting position, triggering before all other sections animate in, so the hero doubles as a page loader.
- Scroll-scrubbed hero video reads as premium — specify that playback is driven by scroll position so it scrubs both ways. Keep the underlying footage slow and smoothly panning or overlaid text becomes unreadable.
- Ready-made components: **21st.dev** (copy its generated prompt straight into Claude).
- **Check for clipping after adding animation** — entrance animations routinely clip subtitles and section edges.
- When an effect is too obvious: "make it more subtle, more refined." Adding lag or trailing motion is usually the fix.

### 3D

**Three.js** for generative background graphics. **Spline** for hand-picked scenes: free account → Community tab → Remix into your project → **delete the demo text and stray logos first** (otherwise you get text layered on text) → Export → code export → paste the link with "use this Spline graphic above the fold for the background." Expect a hard edge where the graphic ends; fix it with a gradient from the graphic's colour to transparent so it fades into the page.

### Imagery

The one pillar Claude can't solve alone. Real photography beats generated. When generating:

- **Have Claude write the image prompts** — it already knows the brand and aesthetic, so assets match on the first attempt instead of the fifth.
- Ask for a **numbered list, one prompt per slot**, each with the exact filename to save it as, the correct aspect ratio, and a description matched to the design — **all sharing one style line, one lighting description, one mood**, so the images look like a single photographer shot them. That consistency is half of what makes a site look expensive.
- Save into `assets/` with the exact filenames given, then continue.
- Replace SVG-style illustrations with real photography where you can — generated illustrations are one of the strongest AI tells.

### Copy

AI copy over-explains, over-adjectives and tries to sound impressive. Bake the rules in: short headlines, specific claims someone could actually check, and a **banned-word list — "premium", "luxury", "journey"**.

Good: *"Roasted Monday, in your cup by the weekend."* / *"Six dishes, one fire."* / *"Dry-aged ribeye, 16 ounce, 60-day, hearth-fired."*

To fix one line: "that headline is too clever, make it plainer" — it rewrites only that line and leaves everything else in place.

---

## Phase 4 — Refine

**Large changes before small ones.** Structure first, then visual direction, then individual elements. Otherwise you redo the small adjustments every time the big pieces move.

**Point, don't describe.** Three granularities, all of which remove ambiguity about what you mean:

- **Select the element** and describe the change
- **Draw/circle** a region and describe the change
- **Screenshot** the section, attach it, describe the change

Screenshot editing is called "one of the most effective ways" to revise. When fixing one section, add: *"and also match this section with the entire website"* — that clause is what keeps the fix consistent.

If inline comments don't register — they're research-preview — don't fight the interface, paste the same instruction into chat.

**Snapshot before you explore.** "Save what we have now so we can come back to it" before asking for variations.

**Batch your fixes, and lead with intent rather than specification:**

> *"We need more handcrafted micro-interactions. The lower sections feel a bit generic. We don't need to make them busier, just more expensive."*

Claude is better at translating intent into specifics than most people are at writing specifications. Batching costs fewer tokens and produces a more cohesive result than drip-feeding one tweak at a time.

**Do the flat-section pass yourself.** Scroll the whole site and find the sections that still feel dead — there are always two or three. Claude won't catch them because it can't feel the page the way you can. Give each flat section exactly **one** motion or cursor interaction.

**Interact with the build, don't just look at it.** Click the calculator, try the drag-and-drop, open the blog link. Functional gaps hide behind good-looking sections.

**Run a self-audit against a ban list.** Have Claude grade its own output and fix what fails:

> no gradient text · no glassmorphism · no identical cards · no default AI fonts · no rainbow palettes · none of the tells that scream "AI made this"

And against a quality checklist: **point of view · typography · colour · hierarchy · imagery · motion · mobile · the invisible stuff that makes a site feel fast and finished.** Ask *"Where does this site land against each of these? Be honest."* Expect a mixed scorecard — that's the to-do list.

**Hierarchy is explicit sizing.** City name huge, address medium, description small. It tells the eye what to read first, second, third. Without it a page reads flat no matter how good the fonts are.

**Do a dedicated mobile pass.** Responsive is not the same as designed for phones, and phones will outnumber desktops. Ask explicitly what should be hidden on small screens, what should be tighter, what should resize.

**Kill every placeholder** before anyone sees it — stock names, lorem sections, empty blog pages. Either fill them or delete the section.

**When something breaks, push rather than revert.** Describe what happened and what you expected. One scroll-video bug took three rounds; Claude eventually opened the page in a browser and inspected it live to find the real cause.

**Trust Claude when it refuses on architecture.** It will decline to drop a React component into a static single-file project because that changes how the project works. That refusal is protecting your setup.

---

## Spending tokens where they matter

Design tools burn budget fast — one creator hit his session limit mid-build, twice. The economics that work:

- **Stage the build** so you can course-correct early instead of regenerating a whole site.
- **Pick the direction before anything is built**, not after.
- **Batch fixes** instead of drip-feeding.
- **Do the expensive design reasoning once on the strong model, then hand off to a cheaper model to build the code** — the hard thinking is already captured in the design system.
- Check the usage meter (Settings → Usage) before starting something large.

---

## Judgment calls — the sources genuinely disagree

Don't average these. Read the situation, or ask.

**One-shot vs section-by-section.** One creator one-shots a five-page site with a single Next.js + GSAP prompt and gets a near-pixel-perfect result. Another builds strictly section by section starting with the hero, because sizing and spacing drift otherwise. A third does one big build then many polish passes. → One-shot when the design system and reference are locked; section-by-section when implementing a specific design faithfully.

**Stack.** Single-file static HTML (what Claude itself recommends for a brochure site) vs Next.js vs Astro vs Tailwind + shadcn/ui. → Static for a marketing page with a contact form; a framework the moment you need auth, payments, a database or a CMS. Client work needs a CMS so they can edit their own content.

**Design-first vs prompt-first.** Design in Figma and have Claude implement it (highest fidelity, needs a designer) vs generate the design in a design tool and hand off (fastest) vs never leave the prompt (fine for simple sites). All three ship.

**Clone vs inspire.** One creator gives Claude a live URL *and* a screenshot and asks it to analyse and clone the site outright. Another states explicitly: "we're not copying anyone's work, we're just using it for inspiration." → The safe and usually better version is structure-from-reference, style-from-your-design-system.

**Dark mode.** Presented as the fastest premium signal — dark isolates what matters, saturated colours read richer, ~82% of smartphone users prefer it, and Apple/Vercel/Linear/Notion use it for elevated surfaces. But the same source caveats: **healthcare, education and government work better light**, where clarity beats drama. Never say "make it dark" — that goes muddy. Specify base colour, one dominant accent, and exactly where the accent may appear.

**White space vs density.** Excellent for portfolios, editorial brands and premium landing pages. Wrong for SaaS dashboards and finance UIs that need information on screen.

**Hero composition.** A cut-out transparent PNG with text stacked behind gives more control and enables parallax — at the cost of a large file and fiddly layout. A baked image with CSS edge fades is the pragmatic default.

---

## Anti-patterns

- "Make it modern and professional" — vague in, default out.
- "Make it dark" with no base, accent, or accent placement.
- More animation as a substitute for direction.
- Leaving Inter in the output.
- A different highlight colour in every section.
- Describing where an element is in prose instead of selecting or screenshotting it.
- Drip-feeding one tweak per prompt.
- Firing the build prompt and walking away while Claude waits on questions.
- Treating the first generation as the deliverable.
- Shipping the desktop layout squashed and calling it mobile.
- Shipping placeholder names and empty blog pages.

---

*Distilled 2026-08-04 from 11 full transcripts on building websites with Claude. Per-source notes and consensus counts are in `_distill_work/`. One source — a Reddit thread — could not be retrieved. Cross-references to the landing-pages and dashboard-saas-redesign skills added 2026-08-04.*
