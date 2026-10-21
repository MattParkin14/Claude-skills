# 5 Ways to ACTUALLY Build Beautiful Websites Using Claude for FREE
Mikey Website · 1 Aug 2026 · https://www.youtube.com/watch?v=83geKREHQY0
(Demos run in Base44 with the model set to Claude; techniques are prompt-level and tool-agnostic.)

Core thesis: "It's not a Claude problem, that's a prompting problem." Premium != more animations/effects. Beautiful sites are not more complicated, they are **more directed**.

## The 5 techniques

1. **Mood/dark mode - never say "make it dark".** A vague dark prompt goes muddy and flat. Specify base colour, ONE dominant accent, and exactly where the accent may appear (CTAs, active nav states, hover only - not headings, not body, not decoration). Good dark accents: electric blue, emerald, teal, gold, amber, violet. Give Claude "a visual world to design from, not just a background colour" - e.g. dark academia, dark luxury fashion editorial, "the inside of a high-end watchmaker's workshop at night".
   - Stats cited: ~82% of smartphone users prefer dark mode; Apple/Vercel/Linear/Notion paid tiers use dark for elevated feel.
   - **Caveat (disagreement-worthy): dark is not universal.** Healthcare, education and government sites work better light - clarity and trust beat drama.

2. **Typography as the fastest quality signal.** Claude's defaults (Inter, Roboto, Open Sans) are what every AI builder reaches for - Anthropic's own design guidance flags these as fonts to avoid when you want non-generic output. Prompt instead for: Space Grotesk, Playfair Display, Crimson Pro, Clash Display, Satoshi, Cabinet Grotesk, IBM Plex, Bricolage Grotesque.
   - Pairings: Playfair Display + Inter (editorial/luxury); Poppins + Work Sans (SaaS/corporate); DM Serif Display + Inter (startup landing); Merriweather + Roboto (content-heavy B2B).
   - Minimum viable direction: heading font, body font, and how strong the hierarchy should feel. Exact sizes/tracking optional.
   - Evidence cited: Errol Morris 2012 Baskerville-vs-Helvetica experiment, ~45,000 respondents, Baskerville ~1.5pp more believable, statistically significant. Font affects trust, not just decoration.
   - Strong version: "typography becomes the entire design system" - Clash Display bold + wide tracking for headings, IBM Plex Mono for body/UI, no gradients or illustrations, let type do the work.

3. **White space as an explicit directive.** AI builders lean tight because they fill the visible screen. Distinguish **micro** whitespace (line height, letter spacing, paragraph gaps) from **macro** (section gaps, card padding, gaps between content blocks). The single line that does most of the work: **"white space is the primary design directive"** plus "add more space when in doubt". Reference brands: Apple, Airbnb, Linear.
   - **Caveat: doesn't fit everything.** SaaS finance/dashboard pages need visible information density; balance spacing against usability.

4. **Engineer the hero, don't accept the default one.** Users form a visual opinion in **17-50 ms**; eye-tracking order is headline -> visual -> CTA, and the headline carries ~**60-70% of the persuasion load**.
   - The 5 required hero elements: (a) value-prop headline written around the *customer's outcome*, (b) sub-headline with one concrete layer of specificity, (c) ONE primary CTA with specific copy ("claim your first week free", not "get started"), (d) real product visual / interface screenshot / defined image slot, (e) one trust signal - logo bar, customer count, testimonial, or a concrete result stat.
   - Typical AI failure: headline describes the business instead of the outcome; generic CTA; abstract stock art.
   - **His #1 pick if you only do one thing: the hero.** "If the hero is vague, the whole site feels vague."

5. **Define a colour system up front - 60/30/10.** 60% dominant (backgrounds/main surfaces), 30% secondary (cards, nav, dividers, supporting surfaces), 10% accent (CTAs, links, active states, key data callouts) and nowhere else. Two to three colours, each with a named job.
   - Accessibility: prompt for at least **4.5:1 contrast for normal text, 3:1 for large text**, and "keep all text clearly legible against its background."
   - Describe colours with real-world references, not names: "the deep black of a Bloomberg terminal", "the dark slate of the bezel around a luxury watch face", "an accent like the glow on a heart-rate monitor." Hex codes when the client has brand colours; upload mood boards / brand guides as image references.
   - Failure mode being fixed: without a system, blues drift between sections and accents get overused - the page looks "assembled rather than designed".

## Other
- Set the model deliberately before the first prompt (in Base44, pick Claude Sonnet/Opus in the model selector) - "the most important setup step".
- Beginners should start with typography or white space: biggest visible before/after. Then combine all five in one prompt for the real jump.
