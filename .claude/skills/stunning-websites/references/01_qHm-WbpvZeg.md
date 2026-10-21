# Build Stunning Websites With Claude Code (Just Copy My 5 Prompts)
Reliablesoft Academy · 7 Jul 2026 · https://www.youtube.com/watch?v=qHm-WbpvZeg
(FULL transcript, user-supplied)

## The 5-stage pipeline — each stage is a separate prompt, each output visible before the next runs
Stated reason for staging: "you see what's happening at every step and you can adjust early instead of getting one giant result at the end and hoping for the best. That saves time, saves tokens."

**Setup (2 min):** brand-new EMPTY folder ("empty matters because you'll get to see exactly what Claude creates"). Enable **Frontend Design** skill via plus button -> plugins -> browse plugins -> search "front-end design" -> install. Model: **Opus or Sonnet both produce similar results, Sonnet is much cheaper.**

**Prompt 1 — interview + design direction.** Claude asks questions ONE AT A TIME in plain language: business name and what it does / who the site is for and what visitors should do / the one thing a visitor should remember / logo or sites you like / opening hours / what to avoid.
- **The killer question: "describe one real moment around the business."** Not colours, not fonts - a moment. Example answer: *"Early morning at the bar, steam rising off a fresh pour. Warm light on wooden shelves full of coffee bags."* **That one sentence is where the entire colour palette comes from.** "The colours come from your world, not from a template." <- this is the single most distinctive tactic in the whole corpus.
- Output: a preview page with **three complete design directions side by side** - real palettes, real font pairings, YOUR actual headline set in each, plus a one-line reason for each. One is marked recommended but you choose. Reason: "you're picking the direction before a single section gets built, which means no wasted tokens on a look you'd throw away."
- Then it writes **design.md** into the folder - "the design rulebook for the whole project. Every colour, every font, every rule about what this site will never do." Every later step reads it, "which is why the site stays consistent instead of drifting."
- First render is **deliberately almost empty**: brand name + one big line in the real fonts on the real background. "Premium sites say one thing first."

**Prompt 2 — structure.** Asks one question first: four motion styles (calm / smooth and premium / bold and kinetic / minimal) with a recommendation. Then lays out the whole page. The section list adapts to business type - a local business gets hours/address/map, a product site gets feature moments and a buy section. Images and text are **labelled grey placeholders** ("hero", "the bar", "morning light") telling you exactly which asset goes where. "Structure first, words next."

**Prompt 3 — copy.** Reads design.md, replaces every placeholder line. Rules baked into the prompt: short headlines, specific claims you could actually check, and a **banned-word list including "premium", "luxury", "journey"**. Result quoted: *"Roasted Monday, in your cup by the weekend."* To fix one line: "that headline is too clever, make it plainer" - it rewrites only that line.

**Prompt 4 — images.** Does NOT generate images. Returns a **numbered list of image prompts, one per slot**, each with the exact filename to save it as, the correct aspect ratio, and a description matched to the design - **all sharing the same style line, lighting and mood so they look like one photographer shot them. "That consistency is half of what makes a site look expensive."** Save into assets/ with the exact given names, then say continue.

**Prompt 5 — polish pass.** Two jobs: finishing touches, and **Claude audits its own output against a banned list** - no gradient text, no glassmorphism, no identical cards, "none of the tells that scream AI made this" - and fixes whatever fails.

## Other
- Click "always allow" on `serve preview on local HTTP server`.
- After the pipeline, plain-language edits work fine: "change the way testimonials are shown" -> done in seconds.
- Framing: "You're the creative director, and Claude is your studio."
- Deploy mentioned only: domain ~$10/yr + Vercel free hosting.
