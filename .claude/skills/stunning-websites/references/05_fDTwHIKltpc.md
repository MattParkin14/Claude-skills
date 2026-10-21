# The EASY way to build a beautiful website with Claude Code (full workflow)
Create a Pro Website · 2 Jul 2026 · 92k views · https://www.youtube.com/watch?v=fDTwHIKltpc

## Tactics

- **Gather every asset BEFORE you start** - logos, brand colours, photos, video - into a `media/` subfolder inside the project folder. "This way when I'm in the designing process I can just go find everything I need really quickly without having to search for it later." Claude then autonomously searches that folder, extracts brand colours from the logo, and finds before/after images without being pointed at each one.
- **Same two skills as the Metics build, and the same install phrasings:**
  - Frontend Design (Anthropic) - "install this skill globally" + link. Effect: reaches for more creative fonts and layouts "instead of overused fonts used on all the generic AI sites".
  - UI/UX Pro Max - **"install this plugin globally using NPM"** + link. Effect: large palette of colour schemes, font pairings, UI styles to draw from. **Restart Claude after install** or the skill isn't active.
  - Explicitly framed: "if you skip this step, this is how you get generic, boring-looking websites."
- **Bring a reference screenshot from Awwwards or Dribbble; searching by industry works** (searched "landscaping"). Two valid approaches: pick one site you love, or "build a Frankenstein" from screenshots of favourite parts of several.
- **Invoke the skill explicitly with `/ui-ux-pro-max` in the build prompt** rather than hoping it triggers.
- **Build prompt template used:** *"Please build me a website for [business] in [location]. I'd like this website to use this reference image as inspiration but using my own branding, colors, and logos. I'd also like to include a few specific sections. **Please ask me any questions that you need to complete this job.**"* - the last sentence is called out as "really important... so I know it has all the information it needs without me having to guess."
- **Answer the interview with your own additions, don't just accept the suggested sections.** He added a before/after slider section and an "our process" 4-step section beyond what the reference had.
- **Take the recommended tech stack unless you have a reason not to** - offered single HTML file / multi-file static / React-Next.js; it recommended single HTML file, "we don't need to get that complicated."
- **Auto mode vs accept-edits is a real choice:** auto runs without asking permission each step; accept-edits keeps you in control of every change. He uses auto.
- **Editing tools inside the preview: select-element and draw/annotate.** Select a section and describe the change in plain language (e.g. "simplify these images - instead of three, just the one image of the crew displayed horizontally so we can see the full image without it being cropped").
- **Scroll-scrubbed hero video**: swap the hero still for a video file and specify "the playing of the video will be triggered by the scroll" so it scrubs back and forth with scroll position. Noted as optional/experimental - a simple looping video is also fine.
- **First-pass result took ~10-15 minutes** and included generated copy, correct image-to-section matching, hover zoom on cards, before/after slider. Blog section rendered as placeholder only - either fill it or tell Claude to remove it.
- **Check every placeholder before publishing** (phone number, contact details, blog).

## Cost/deploy
Claude Pro ~$17/mo. Hostinger Premium (~$2.69/mo) for basic sites; Business (~$3.59/mo) if you need payments or user accounts/back end. 12-month term ≈ $43 with free domain + mailboxes.
**Zip the contents of the folder, not the folder itself**, then upload via "migrate an existing site -> upload backup files".
