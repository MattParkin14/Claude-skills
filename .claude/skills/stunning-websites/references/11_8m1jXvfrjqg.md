# Claude Code: How to Create Beautiful Websites as a Designer
Kyle Skelly · 15 Jul 2026 · https://www.youtube.com/watch?v=8m1jXvfrjqg

## Tactics

- **Design in Figma first, then hand the frame to Claude Code via the Figma dev-mode MCP prompt.** Result "matches the Figma extremely well." The design decision is made by a designer; Claude only implements.
- **Build section by section, starting with the hero - never the whole page at once.** Actual prompt: "make a new folder for this site called Rosewood Cabins, implement this design, let's start section by section starting with the hero."
- **Specify the layout system numerically: 1,400px max-width wrapper, 8px spacing system, and name the framework (Astro).** Without these the output drifts on sizing.
- **Capture the client meeting as structured input.** Meeting transcribed (Granola) -> brief exposed to Claude Code over MCP, so mid-build he can ask "does this match what the client asked for?" The brief becomes part of the build. (Sponsored tool; the pattern is the point.)
- **Responsive comes free but verify it.** No mobile design was made; output stacked correctly, checked by resizing.
- **Let Claude label and wire existing assets rather than re-uploading.** "Use the images we currently have in our assets folder and label them appropriately. Each arrow click should change both images." It correctly tagged wood stove / living room from image content.
- **Animation prompt worth copying verbatim:** "I want to add some tasteful animations. All sections should appear in nicely and appropriately, and I also want our hero to act kind of as a loader to the page. I want that hero image to appear full screen height and width and then scale down into its position where it sits currently. This triggers before all the other elements animate."
- **Deliberate trade-off on hero composition:** cut-out transparent PNG + text behind = more control and parallax, but bigger file and more complexity. He chose baked image + CSS edge fades instead. Judgment call, not a rule.
- **A real client build needs a CMS** (Sanity on Astro) so the client can edit content; a static AI build has no back end.

## Stack
Figma -> Figma MCP -> Claude Code -> Astro -> GitHub -> Cloudflare Pages (free hosting + custom domain).
