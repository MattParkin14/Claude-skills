# How to Use Claude Design To Make Sites 10X More Beautiful
Mikey Website · ~Jul 2026 · 98k views · https://www.youtube.com/watch?v=y2n1NMrMNBo
(FULL transcript, user-supplied — Tavily had been blocked by a CAPTCHA page)

Thesis: **"The first generation is never the product. It's just the starting point."** He gave 100 people the same prompt; almost every result was near-identical. The people who get polished sites "aren't better designers - they're just doing one thing differently after that first draft appears."

## The 4-stage refinement loop

**1. Prompt specificity — the single biggest lever, and it happens before anything is generated.**
A good prompt tells Claude four things: **goal, layout, content, audience.**
Bad: "make me a landing page for a coffee shop."
Good (verbatim structure): *"Create a landing page for a small-batch specialty coffee roaster. The goal is to get local people to come in and buy beans. Lay out a full-width hero with one strong image and a short tagline, then a section telling the brand story, a section showing the beans, and a visit-us block near the bottom. The brand is warm, crafted and slightly premium - single-origin coffee roasted in small batches. Keep the copy in that voice. This is for local coffee lovers who care about quality and craft, not a big chain."*
"The tool didn't suddenly become better between the first version and this one - the instructions became better." Cost: about 30 extra seconds.

**2. Chat = large changes only. Structure and visual direction, in that order.**
- Structural example: *"Move the featured beans section higher up, just below the hero. Show three featured coffees in a clean grid, each with a name and a short description. I want the actual product to be one of the first things people see."*
- Visual-direction example: *"Make the whole page feel warmer and more editorial. Use deeper, richer tones and more generous spacing - the kind of polished look you'd expect from a high-end roaster."*
- **Rule: large changes always before small ones.** "Otherwise you're going to end up redoing small adjustments every time the bigger pieces move around."

**3. Inline comments = small changes.** Click the element itself and leave feedback there - "no guesswork about what you're referring to." His three: enlarge the CTA + more padding + use the primary brand colour prominently; more internal spacing and softer corners on the product cards; bigger, tighter headline. None transformative alone; together they elevate the page. **Known bug: inline comments are research-preview and sometimes don't register - don't fight the interface, paste the same instruction into chat.**

**4. Explore variations before committing on any section that matters.**
- **First, snapshot: *"Save what we have now so we can come back to it. I want to keep this version safe."*** Then: *"Show me three alternative layouts for the hero section only. Keep everything else on the page the same."*
- The three he got: split (text left / full-height image right, editorial magazine feel); centred (headline, sub, buttons over a full-width image - clean and balanced); **inset frame with the heading in the lower-left and a product card layered in, product info visible on load** - he picked this one because it reinforces what the business sells the moment the page opens.
- "Beginners pick a direction and spend all their time refining it. Designers explore multiple options first and then choose the strongest one." A few minutes comparing beats endlessly tweaking the first idea.

## Export options (choose by intent)
Sharing/presenting/feedback -> PDF, PowerPoint, Canva. Going live -> standalone HTML, or the Claude Code handoff (packages everything for development). Also zip download. For feedback alone, don't export at all - generate a share link with view / comment / edit access.

## Note
Claude Design is a research preview on Pro, Max, Team and Enterprise (claude.ai/design); two-panel interface, chat left, live canvas right.
