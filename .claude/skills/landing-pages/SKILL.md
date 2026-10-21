---
name: landing-pages
description: >
  Playbook for designing and writing high-converting landing pages — especially
  pages that receive cold traffic (cold email, cold ads) where the visitor has
  never heard of the brand. Use this skill whenever the user wants to plan,
  write, build, review, critique, or improve a landing page, opt-in page,
  lead-capture page, sales page, hero section, or above-the-fold copy; wants
  landing pages to convert cold email or ad clicks into replies, form fills,
  booked calls, or sales; asks why a page isn't converting; or asks for
  landing page headlines, CTAs, social-proof layout, or page structure. Also
  trigger on phrases like "landing page", "LP", "squeeze page", "hero copy",
  "above the fold", "conversion rate on my page", or when building many
  personalized pages for outbound campaigns. Also trigger when the user types
  /landing-pages.
---

# landing-pages

> **One of a 3-skill web-design set — you are in the conversion-copy + page-structure layer.** This skill owns *what a landing page must say and do to convert*. Reach for a sibling when the job shifts:
> - **stunning-websites** — the visual-execution and Claude-build-workflow layer: typography, colour systems, motion, backgrounds, anti-AI-slop, staged build prompts. Use it to *make the page look premium once the copy is right*. A page build usually wants both.
> - **dashboard-saas-redesign** — functional in-app UI (dashboards, tables, empty states). Use it for the *product behind* the landing page, and for SaaS pricing-page specifics.

A distilled playbook for landing pages that convert, synthesized from 10
practitioner breakdowns (CRO agencies with 400+ built pages and published A/B
numbers, Hormozi's value-equation framework, a 79%-converting opt-in page, and
UI-craft breakdowns). Tuned for the hardest case: **cold traffic** — a cold
email click means the visitor knows *nothing* about the brand and trusts it
even less.

## Mindset

- The ad or cold email only buys the click. **The landing page does the
  selling** — treat it like your best salesperson, not a brochure.
- Doubling conversions beats doubling traffic: conversion gains amplify every
  visitor you already pay for, and let you outspend competitors per lead.
- People buy with emotion first, then rationalize with logic. Every section
  either builds desire or clears a doubt; if it does neither, delete it.
- People don't want clever. **People want clear.**

## Step 0 — Positioning before pixels

Never open a page builder (or write hero copy) until you can answer, in
writing:

1. **One goal.** The single action this page exists for (form fill, booked
   call, reply, purchase). One page = one conversion goal. Strip nav links and
   competing CTAs.
2. **Who it's for** and their top 3 pain points and desired outcomes — in
   their words, not yours.
3. **Awareness level by traffic source.** This decides the page structure:
   - **Cold email / cold social ads → unaware.** They don't know you and
     weren't searching. Lead with pain (Problem–Agitate–Solve), educate before
     you pitch, stack heavy trust-building.
   - **Search / warm traffic → solution-aware.** Skip the education; put the
     lead form or offer right in the hero.
4. **Their "what ifs".** List the actual doubts and objections (from customer
   calls, replies, reviews). The middle of the page exists solely to clear
   these, in order of importance — this is research, not a template.

Wireframe/copy first (Figma, doc, or plain HTML), design second. Write the
headline and description before choosing the hero visual — the visual must
complement the message, never the reverse.

## The above-the-fold (spend 80–90% of your effort here)

~60% of visitors never scroll past it; 100% see it. You have ~5 seconds to
answer "why should I care?" or they're gone. The biggest conversion jumps come
from testing here — mostly headline and image.

The proven stack:

1. **Headline = dream outcome, quantified.** Never who you are or what you do.
   Use the "so that" chain to find the real end benefit (exterior cleaning →
   *so that* solar panels produce more → *so that* the power bill drops).
   Put numbers and time-to-result in it when honest: "Get up to 3x more leads
   in less than 24 hours." Simple words a 5th–8th grader parses instantly; no
   jargon to decipher. Long-but-clear beats short-but-vague.
   Two hook formulas that work for cold audiences:
   - Frustration hook: "Tired of [pain] even though you [effort]?"
   - Readiness/result hook: "Are you ready to [specific result]?"
2. **Subheadline = pain → solution, minus the sacrifice.** "Tired of [pain]?
   We [what you do / USP] so you get [result] in [time] without [effort/risk]."
   This is where you finally say what you do and what makes you different.
3. **Two to three forms of social proof.** Review stars + count, client logos,
   a stat bar, an authority banner. Trust must start before the scroll.
4. **One high-contrast CTA** whose label continues the headline's promise —
   never bare "Submit"/"Next"/"Sign up". Say the cost of acting: "Get your
   free audit — takes 2 minutes". No ghost (outline-only) buttons, ever.
5. **FUD-reducers directly under the CTA button** — small checkmarks/badges
   killing fear, uncertainty, doubt: free, no card required, guarantee,
   warranty, response time, "no sales pitch". Repeatedly worth +30–60% in
   published tests; the cheapest win on the page.
6. **Hero image/video that *proves* the headline** — the actual product,
   the actual outcome, real happy humans. Never decorative stock, blobs, or
   gradients. If you promise a luxury closet, show the closet.

For solution-aware traffic, the hero can instead hold the lead form:
form headline + 3–4 expectation bullets + fields + CTA + testimonial under
the button.

## Page structure below the fold

Order for **cold/unaware traffic** (the cold-email case):

1. **Pain section (Problem–Agitate–Solve).** Name the problem so they feel
   heard → turn up the heat on what it's costing them → present your approach
   as the way out. Depth scales with offer complexity.
2. **First social-proof section** — lead with your single most impactful proof
   (video testimonials if you have them).
3. **Value-prop sections (the meat, ~3–8).** One benefit each, headline =
   feature + benefit fused ("Fast, pain-free 10-minute treatment for a
   lifetime of clear vision"), short body, complementary real image. Give the
   anxiety-killing value prop its own section.
4. **How it works — exactly 3–4 steps.** More steps = more perceived effort.
   Headline sells the ease, not "How it works" ("A seamless three-step
   white-glove process from design to cleanup").
5. **More social proof / differentiators / use-cases** as the audience's
   "what ifs" demand — multiple proof sections give permission to keep
   scrolling.
6. **FAQ** — write it from real fears: "Is this really free? What's the
   catch? Will you try to sell me something?" Include a way to ask a question.
7. **Closer section (mini-hero).** Rephrased (not copy-pasted) headline, light
   urgency, "takes 2 minutes", social proof, FUDs, and the form/CTA again —
   never make someone scroll back up to convert.

For solution-aware traffic, swap 1 and 2 (proof before pain) and compress the
education.

**Page length:** long pages don't kill conversions; bad structure does. Match
length to commitment — a free/cheap offer converts on a short page (a
79%-converting opt-in page is one screen: what it is, why you want it, how to
get it); a high-ticket ask needs the full doubt-clearing journey. Every
section must earn its place or be cut.

## Social proof rules (believability > volume)

- Every review needs **name + photo + title/company + source** (Google,
  Clutch, Capterra…). Unverifiable text quotes now read as fake and can hurt.
- Make proof **visual**: before/after photos beat claims; video beats photo;
  pair the review text with a photo of the actual work. Show the
  transformation, don't describe it.
- Review-card headline = the punchline, quantified ("We doubled our
  conversion rate"), because scanners read only headlines.
- "Featured in" logo walls are ignored — attach an actual quote from the
  publication to each logo.
- **Stack it**: wall-of-love format, all visible up front. **Never hide proof
  in carousels or dropdowns** — carousel slide #2 gets <1% engagement; what
  is hidden does not get seen. On mobile, stack reviews vertically, exposed.
- Section headline quantifies trust: "Join 1,200+ businesses that…", never
  "What our customers say".

## Copy and design rules

- **Assume people read only headlines.** Scan test: cover all body text —
  does the page still sell? Kill every generic header ("Our services",
  "What makes us unique", "Testimonials") and put the actual message in it.
- **Visual hierarchy is the whole game**: one clear flow headline →
  subheadline → CTA via size, weight, and color. If everything shouts,
  nothing does.
- **60-30-10 color rule**: ~60% neutrals, 30% brand color, 10% accent —
  and spend the accent on the CTA. Check contrast for accessibility.
- **Cognitive ease**: cut anything not critical to conversion. Bullets and
  icons over paragraphs. One "full name" field instead of first + last; only
  ask for what the offer justifies (~4 fields max; no phone number for a free
  thing). Progressive forms convert: ask for one trivially easy field first
  (email or website URL) — once they've typed one thing, they finish the rest.
- **Familiar beats novel (Jakob's Law)**: keep the conventional structure;
  differentiate with polish — real product shots, consistent spacing and
  corner radii, subtle hover/scroll animation, sections that flow into each
  other. Premium feel creates a halo (first impression forms in ~50 ms) that
  colors everything below; clutter poisons it.
- Header's sticky CTA should be *less* prominent than the hero CTA (don't
  compete), lighting up after the hero scrolls away. Hero CTA and header CTA
  share one label so users build one mental model.
- *For the execution depth behind these rules — type systems, the 60/30/10
  palette in practice, motion, backgrounds, and avoiding the AI-generated look
  — hand off to the **stunning-websites** skill. Get the copy and structure
  right here first, then style it there.*

## Cold-email specifics (batches of personalized pages)

- A cold-email click is maximum-skepticism traffic: unaware structure, heavy
  verifiable proof, zero-risk CTA (free audit/report/assessment beats "book a
  call" for the first conversion).
- Personalize the hero per segment or prospect: their industry in the
  headline, a pain point from their world, proof from lookalike customers
  ("how we helped 14 NZ food manufacturers…"). Keep everything below the fold
  shared — one template, swappable hero + proof block scales to 20+ pages.
- Buyers often visit twice before acting (~60% on one measured page). Make
  the URL memorable, keep the page consistent between visits, and offer a
  low-commitment email-capture (free asset) so a not-yet-ready visitor isn't
  a dead end.
- A quiz/assessment funnel is a proven cold-traffic converter: hero promising
  "answer 15 questions to find out why [pain] and what to do about it" →
  10 best-practice questions that generate a score + 5 qualifying questions
  (situation, 90-day goal, obstacle, preferred solution type — which implies
  budget — and an open "anything else?" box) → dynamic results page with
  score, 3 insights, and next steps branched by lead quality. Done well,
  20–40% of page visitors start the quiz, and you capture intent data, not
  just an email.

## Iterate — a landing page is never one-and-done

- Test **one thing per week**, winner vs control, in a standing review.
  ~90% of high-ROI tests are headline or hero-image tests.
- Below ~40–50k visitors/month you can't reach significance on micro-tests —
  make bigger best-practice revamps instead, and compare cohort metrics.
- Watch where the wins compound: a winning headline pattern on one page rolls
  out to all 20.

## Judgment calls (where sources disagree)

- **Blueprint vs research:** one source insists there is no universal section
  order — only hero + doubt-clearing driven by audience research; the agency
  sources sell a fixed blueprint. Resolution: the hero formula and proof rules
  are invariant; the *order and depth of middle sections* comes from your
  audience's actual objections and awareness level.
- **Long vs short:** long-form agencies vs a one-screen 79% opt-in page.
  Resolution above: length follows price/commitment, not preference.
- **Craft vs simplicity:** one source ranks pages by animation and design
  detail; another says simplicity beats creativity every time. Resolution:
  novel *structure* loses, premium *polish* wins — be conventional in layout,
  exceptional in execution.
- **Pricing on page:** if the price is high, one click away on a dedicated
  page (built to defend the price) can out-convert showing it in the hero.
  For free offers, state "free" everywhere.

---

*Provenance: distilled 2026-07-08 from 10 YouTube videos on landing-page
conversion (CRO agency breakdowns, Hormozi value-equation strategy, Copy
Posse funnel data, UI/UX craft levels) via the distill-yt pipeline.
Cross-references to the stunning-websites and dashboard-saas-redesign skills
added 2026-08-04.*
