# How I Built INSANE Claude Design Websites In 10 Minutes
Jono Catliff · 18 Apr 2026 · 193k views · https://www.youtube.com/watch?v=xYv4_cTOSNM

Flow: Claude Design (design system -> 5-page prototype) -> export "hand off to Claude Code" -> Next.js + GSAP in one shot -> GitHub -> Vercel -> custom domain. Zero Figma, zero Canva.

## Tactics

- **Create a design system FIRST, before any page.** "A design system allows us to have a coherent, unified brand across every single page." Everything downstream (site, presentations, motion graphics) reuses it.
- **Seed the design system with a real brand kit instead of describing taste.** getdesign.md publishes full brand kits for 68 major brands (Airbnb, Airtable, Apple, BMW...) - headlines, colours, font families, light+dark variants. Copy the design.md text, paste into Claude Design's design system "additional notes", generate (~5 min). Output includes icon set, prebuilt buttons, type families, marketing UI kit.
- **Separate DESIGN from STRUCTURE and source them independently.** Design system supplies the brand; a screenshot of a layout you like (from durable.com in this case) supplies the page structure. "One thing for the design, one thing for the structure, combined together to make the optimal page." The final site keeps the reference's structure but takes on your design system's style - so it isn't a clone.
- **Choose high-fidelity over wireframe** in the prototype step - wireframe only places elements; high-fidelity is what produces the beautiful output.
- **Name every page in the build prompt.** "Build a beautiful agency website for Automatable with five pages: homepage, services, contact, about, case studies. Use the Claude design system for branding, and use the attached screenshot for the structure of the page."
- **Kill placeholder content immediately** - "nothing screams stock website more than a blank placeholder for Jonas Mercer."
- **Three granularity levels for edits, all element-scoped so Claude knows exactly what you mean:** *comment* (select an element and describe the change), *edit* (direct control of colour, font size, font family), *draw* (circle any region and describe the change). Prefer these over prose descriptions of location.
- **For motion graphics, two-step the prompt:** ask Claude for what you want in one sentence, have it expand into a "mega prompt" (1 sentence in, ~10 out), then feed that to the generator. "The more descriptive you are, the better it's going to be."
- **The one-shot handoff prompt (verbatim pattern):** paste Claude Design's export command, then append: *"Can you please build this Claude Design website using Next.js, and can you use the library GSAP to add animations to the page wherever appropriate? I want as many beautiful stunning animations as possible without it looking cheesy. And I want you to read the claude.md file and build this out in one go."*
- **Put a claude.md in the project folder before firing the build.** Analogy: "when you hire an employee you tell them what they're doing and how to behave - same thing for Claude Code." It's the blueprint/system instructions; without it the one-shot degrades.
- **GSAP is the animation library of choice**; demos.greensock.com is the browsing source - find an effect, ask Claude to add it, it layers into the existing site for free.
- Result was "pixel-for-pixel" vs the Claude Design prototype, plus animations the prototype didn't have (text fly-in, floating buttons, scrolling counters, moving partner logos).

## Deploy
GitHub ("Google Drive but for code") -> Vercel. Ask Claude Code: *"upload all the code in this project to GitHub, deploy it all in one go."* In Vercel, **you must set the framework preset to Next.js** - called out as the one critical setting. Then replace the auto-generated vercel.app subdomain with a real domain: "that name makes it five times harder to sell any service to a client."
