# Build $10,000 Websites using Claude Code (Ultimate Guide)
Metics Media · 29 May 2026 · 872k views · https://www.youtube.com/watch?v=VMvZuhcDdnw

## The 8-pillar checklist (what separates a $10k site from a $200 one)
point of view · typography · colour · hierarchy · imagery · motion · mobile · "the invisible stuff that makes a site feel fast and finished".
Grouped as **taste / substance / felt quality**. Used twice: to set the bar before building, and as a scoring rubric after.

## Tactics

- **Install two design skills before writing any build prompt.**
  - *Frontend Design* (by Anthropic) - runs in the background always; "bans the most overused fonts on the internet" and pushes bold design direction over generic AI output. Also responsible for restrained, sensory copywriting. Install: paste the link + "Install this skill", install globally.
  - *UI/UX Pro Max* (community) - 57 UI styles, 95 colour palettes, 56 font pairings; invoked explicitly with `/ui-ux-pro-max` when you want a big design intervention. Install phrasing matters: **"Install this plugin using NPM"** - that exact wording gets a clean terminal install.
- **Switch to auto mode** so Claude doesn't stop for permission at every step.
- **Collect 3-5 reference screenshots before prompting** from Dribbble, Awwwards, Pinterest. "It's a lot easier to show Claude what you want than to describe it" - and scrolling references clarifies your own taste. Not copying; conveying direction.
- **The single highest-leverage line in the build prompt: "Ask me clarifying questions."** It makes Claude stop and think before building. Claude came back with 7 questions (name, style direction, sections, who writes content, tech stack, animation level, anything else) **and offered three named style directions to choose from**. "This is the most important moment in the entire build. The answers you give here become the entire site. The more specific you are at this stage, the less you'll have to fight Claude later."
- **Expect ~3 minutes of thinking before a line of code, then ~4-5 minutes building.**
- **Imagery is the one pillar Claude can't solve alone - bring assets.** Order of preference: real custom photography > AI generation. **Have Claude write the image-generation prompt for you** (it already knows the project and aesthetic), then paste that into the image tool - matches brand on the first try. Workflow shown: GPT image model -> use output as first frame for Veo 3.1 video -> upscale with Topaz.
- **Pull pre-made components from 21st.dev** - copy its "prompt" button output straight into Claude Code to recreate a component in your project.
- **Trust Claude when it pushes back on architecture.** It refused to drop a React component into a static single-file HTML project because it would change how the project works. "Claude protects the architecture you set up. It doesn't break things just because you asked." Whether it says yes to React tells you which hosting tier you need later.
- **When something breaks, keep pushing rather than reverting.** Explain what happened and what you expected; it took three rounds (Claude eventually opened the page in a browser and inspected it live) to fix the scroll hero.
- **Re-grade against the checklist mid-build:** paste the checklist back in and ask *"Where does this site land against each of these criteria? Be honest."* Expect a mixed scorecard; that tells you exactly what's left.
- **Fix in batches, and lead with intent, not specifications.** Exact prompt used: *"We need more handcrafted micro-interactions. The lower sections feel a bit generic. We don't need to make them busier, just more expensive."* Reasoning: "Claude is better at translating intent into specifics than most people are at writing specifications." Batching = less back-and-forth, fewer tokens, more cohesive result than drip-feeding tweaks.
- **The flat-section pass is the step most people skip and it does the most work.** Scroll section by section yourself - "Claude won't catch them because Claude can't feel your site the way you can." For each flat section add exactly ONE cursor interaction or motion, then push back with "make it more subtle, more refined". Examples: embers that react to cursor with parallax; a candlelight halo that trails the cursor with lag. This is the difference between a site that *looks* expensive and one that *feels* expensive.
- **Ban Inter.** "So overused on AI-generated sites it instantly screams 'AI made this'." Swapped for Geist. (Claude picked Fraunces + Inter; only Inter was replaced.)
- **Colour restraint signals quality**: 5 hex values total - near-black, warm cream, oxblood, brass, slate. No rainbow palettes.
- **Hierarchy is explicit sizing**: city name huge, address medium, room description small - "telling your eye what to read first, second, third."
- **Copy: restraint, not adjectives.** "Six dishes, one fire." / "Dry-Aged Ribeye, 16 ounce, 60-day, hearth-fired." AI copy by default over-explains, over-adjectives, tries to sound impressive.
- **Mobile needs a dedicated pass - responsive != designed for phones.** Ask explicitly what should be hidden on small screens, what should be tighter, what should resize. Result: nav collapses, wordmark tightens, buttons get a smaller variant.

## Deploy / cost
- Static single-file HTML is deliberately chosen to make deployment trivial.
- Zip the **files inside** the project folder, not the folder itself - otherwise the host unzips one directory deeper and the domain loads blank. index.html must sit at the top level of the zip.
- Hostinger Premium for static sites; **Business tier if Claude built a backend/Node app** - "remember when Claude said no to React? That's the moment that tells you which plan you need." ~$43/yr + ~$20 Claude Pro = ~$60 total.
