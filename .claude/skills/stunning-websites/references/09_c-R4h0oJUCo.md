# Build a Website using Claude Design — Just a Few Prompts!
Saddam Kassim · 26 Jun 2026 · 60k views · https://www.youtube.com/watch?v=c-R4h0oJUCo
(FULL transcript, user-supplied; Hindi/English mix)

Opening definition of a $10k site: "great colour theme, proper font styling, smooth animations, cursor effects, highly converting page structure."

## Tactics

- **Design system = a rule book, defined concretely.** His own list of what belongs in it: which fonts for headings and their sizes, which font for paragraphs, button styling, **button hover background colour**, **form placeholder colour**, and spacing between containers/columns. "This is what big companies follow to keep their websites consistent."
- **Seed the design system from a published brand kit rather than describing taste.** A library of design systems for BMW, Dell, HP, Airbnb, Airtable etc. — open the brand, click **design.md**, copy the whole thing, paste it into the design system's **"any other notes"** box. Generation takes ~5 minutes. Result mirrored Airbnb's brand colours and button/hover styles exactly.
- **Publish the design system after generating it** (and optionally set it as default). Easy step to miss; without it the design isn't selectable for the build.
- **Design system covers STYLE; a reference screenshot covers LAYOUT.** Explicitly separated: "the design system defines typography, styling, border radius — but for what the page layout should look like, we use a reference website." He grabbed a full-page snapshot of an awards-winning site (Spark Interact) using the FireShot browser extension.
- **Practical limit: Claude's attachment cap is 20 MB.** His full-page snapshot was 25 MB; compressed it at iloveimg.com down to 7.4 MB with the same visible quality.
- **Use ChatGPT to write the Claude prompt.** Verbatim structure of what he asked: *"I have used Claude Design to create a design system, it's ready in Claude Design. Here I'm attaching a website snapshot, and I want Claude to design a website for my web design agency, and the website design should be similar to the snapshot attached. Can you write a proper prompt for Claude so it can use my design system and this website snapshot as a reference to design my website?"* — attach the snapshot to ChatGPT too so it can read the layout. Output was **387 lines**, opening with *"Act as a senior UI/UX designer and creative director. Design a complete premium homepage…"* His comment: "if we sat down to write this ourselves we probably couldn't write one this perfect."
- **Do not fire the prompt and walk away — Claude asks reconciliation questions and they matter.** The ones it asked him:
  - *"The reference is dark cinematic but Aura is built around white + ink. How should I reconcile?"* → he chose **lean cinematic**.
  - Keep the brand's pink accent, or shift it for an IT-agency feel → **pink primary + one cool secondary (electric blue / cyan) for a tech feel**.
  - Portfolio mockups: empty image-slot placeholders vs tasteful stock/Unsplash URLs.
  - Output fidelity: full hi-fi homepage with scroll reveals.
  - Explore variations per section, or one homepage.
  - Tech logo strip: real brand logos vs styled wordmarks → **SVG logos**.
- **Watch your usage meter — Claude Design is expensive.** Profile → Settings → Usage. He went 62% → 64% → 76% over a single build and hit his session limit before finishing, then had to wait for a ~5-hour reset. "Don't do useless work with Claude even on the Pro plan."
- **Live tweak panel after generation** — accent colour and glow colour can be swapped from the right-hand controls without re-prompting.
- **Fix a weak section by screenshotting THAT SECTION and attaching it**: *"I don't like this section. Can you add some relevant images or icons, and also match this section with the entire website."* The last clause is the important one — it keeps the fix consistent with the rest of the page. Turned a flat white "What we do" block into proper per-service cards.
- **Export options: PDF / PowerPoint / project zip / standalone HTML.**

## Deploy (shared hosting, not a static host)
Upload the HTML into `public_html`, then **select the file and rename it to `index.html`** — the site will not load otherwise. Hostinger Premium (3 sites) vs Business (50 sites); Business+AI recommended because it also hosts Node.js apps. Free domain for one year on either. Affiliate link + coupon.

## His own honest caveats
The result has no backend features and needs further functionality added through Claude afterwards. Also concedes ready-made WordPress/HTML themes already give good design — Claude Design is for when you want a **highly professional customised** design.
