# How to Build $10,000 Websites with Claude Code (full workflow with prompts)
Create a Pro Website · 9 Jul 2026 · https://www.youtube.com/watch?v=GQdmqxY1RaI

## Tactics

- **Fixed 5-prompt sequence, in order: (1) brand kit -> (2) reference images -> (3) hero video -> (4) install a web-design skill -> (5) build the site.** Each prompt consumes the artifacts of the prior one. Reasoning: the model needs brand facts and real assets on disk BEFORE it lays out a page, otherwise it invents generic filler.
- **Prompt 1 builds a persistent brand-kit .md file**: colour palette with hex codes, fonts, logo, slogan, positioning, mood, brand story. Claude is told to interview the user first (existing brand or from scratch?). Reasoning: "so it has something to stay consistent throughout all of its design work."
- **Answer the brand interview in a notepad first, then paste the whole thing in.** Detailed answers here are what make the site match the brand rather than look like a template.
- **Generate reference images before any layout; save to assets/references/ with descriptive filenames** (hero, materials, workspace). Named files get re-referenced correctly through the rest of the build.
- **Scroll-driven hero video as the premium signal.** Prompt 3 generates a cinematic video transitioning through the 3 reference images, played on scroll. Reasoning: slow smooth pans keep overlaid text legible - "we don't want it to be too distracting." Interactive storytelling = "how you really make your brand stand out."
- **Install a reusable web-design skill (.md) as prompt 4 with an explicit "install only - do not generate anything yet."** Prevents the model starting the build before design rules are loaded.
- **Iterate with the visual element-selector, not prose descriptions.** Click the section in preview and say what to change; also used to delete whole sections. "Comb through every little detail."
- **When preview fails, just say "the website preview isn't loading"** and let Claude debug (it had killed its own dev server).

## Stack / numbers
- Claude Pro $17/mo unlocks Claude Code + Cowork + Design; Higgsfield added as a custom MCP connector for image/video generation inside Claude.
- Deploy: build output in website/dist/; zip and upload to shared hosting (Hostinger ~$53/yr, free 12-month domain).
