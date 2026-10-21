---
name: "demo-sites"
description: "Build fast, accurate spec demo sites for local businesses and show them in person or send the link after an fb-dm-outreach yes. Covers recon, scope, craft, deploy, walk-in and follow-ups."
---

# Demo Sites

Building a demo the prospect can hold, and the words that turn it into a
job. Scope is deliberately narrow: **the artifact and the pitch.** Finding
prospects lives in `cold-email` / `cold-sms` / `fb-dm-outreach`; onboarding
and billing live elsewhere.

Triggers include: "demo site", "spec site", "mock up a site for", "build a
site for this café", "I'm pitching a barber", or /demo-sites. Trigger even
if the user only supplies a business name, an Instagram handle or a Maps
link and asks for "a quick site".

**Coming from `fb-dm-outreach`:** the prospect has already said yes to
seeing a link. Use their Facebook page as recon, run Steps 1–5, skip the
walk-in, send the link with the "rough" framing from Step 6 in text form,
then Step 7 follow-ups (the link message counts as the first touch). Aim to
send within about a day of their yes.

## The one rule

**Zero invented facts.** Every name, price, opening hour, phone number and
menu item on the demo traces to something the user actually supplied or
that was fetched from a verifiable public source. No lorem. No plausible
placeholder. No "typical" hours.

This is not pedantry — it's the entire mechanism. The demo sells because
they see *their* flat white at *their* price on a screen. One wrong detail
(a price that changed, a pastry they stopped doing) and the whole thing
reads as generic, which is worse than not showing up. An absent price is
fine. A wrong price is fatal.

When a fact can't be verified, do one of two things: leave it off, or turn
it into the question they get asked in person. Missing information is a
conversation opener, not a gap.

---

## Step 1 — Classify before building

**Ask the business type first.** Do not start until it's known — the type
determines the second section, the CTA, the open loop, and when to walk in.

Then read `references/verticals.md` and load the matching block:

| Type | Second section | CTA |
|---|---|---|
| Café / food | Menu | Call / Directions |
| Tattoo studio | Portfolio grid | Enquire |
| Trades | Before/after gallery | Get a quote |
| Barber / salon | Services + prices | Book |
| Services (gym, studio, cleaner) | Offer block | Call / trial |
| Dentist / clinic | Services | Book appointment |

If the business straddles two (a café that's really a bakery, a salon that
does tattoos), pick the one matching what they'd want to be *found* for and
say which was chosen.

---

## Step 2 — Reconnaissance, remote

The content comes off a screen; the pitch happens face to face. So recon is
done before you ever set foot in the place.

**Google Business Profile is the spine.** Public, fetchable, and carries the
things that must be right: legal name, address, phone, hours, review count,
photos. Start here every time.

**Instagram supplies the look:** hero photo, tagline, tone, what they're
proud of. Note that Instagram is largely login-walled, so it usually can't
be fetched directly — ask the user to paste the handle plus screenshots, or
to paste the bio text. Say so up front rather than failing quietly.

**Facebook** is often the only "site" a trade or small café has. Worth
checking — and its absence of a real website is the reason you're pitching.
After an `fb-dm-outreach` yes it is usually the whole recon source.

Minimum viable recon before building anything:

- [ ] Exact business name, as they write it
- [ ] Address + a maps link that resolves
- [ ] Phone number, in `tel:` format, dialled once to confirm it rings
- [ ] Opening hours, current
- [ ] One strong hero photo, theirs
- [ ] Six to ten items for the second section
- [ ] Their accent colour, taken from signage or logo
- [ ] Owner's name and when they're usually in

**Dating rule for prices:** only publish a price sourced from something
dated within ~3 months. Older than that, run the section without prices.

---

## Step 3 — How much to build

Less than feels right, and the reason is counterintuitive.

**Aim for about two hours: a hero and one section, mobile-first.** Their
photo, their real name and tagline, their real items, hours, address, and a
phone number that works. Stop there.

The temptation is to build the whole thing so it looks impressive. Resist
it, for three reasons:

**A too-finished demo makes the price feel wrong.** Hand over something
that looks done, then name a setup fee and a monthly, and they do quick
maths: he built this in an afternoon and wants that much. A rough-but-real
demo positions the setup fee as the start of work, not a receipt for work
already done.

**A too-finished demo invites critique instead of a decision.** Show
someone a complete site and they respond to details — wrong shade of green,
that photo's from before the refit, we don't sell that anymore. Now it's a
revision conversation before anyone's been hired. Show a hero and one
section and they respond to the idea.

**It's unpaid speculative work.** At scale this is what kills people. Five
or ten demos to land two or three clients. Two hours times ten is a
manageable investment. Eight hours times ten is a month of your life given
away.

**What makes it land is accuracy, not completeness.**

**One visible open loop.** A greyed-out "Order online" button or a nav item
that goes nowhere yet. It shows the shape of what they'd be buying without
it having been built. Open loops sell better than closed ones. Exactly
one — three reads as unfinished rather than deliberate.

---

## Step 4 — Craft

**Rough in extent, premium in execution.** These pull in opposite
directions and both matter. A demo that's rough in *craft* reads as "he's
not very good" and kills the sale. A demo that's rough in *extent* reads as
"there's more where this came from", which is exactly the position wanted.
So: fewer sections, but the sections that exist look expensive.

- **390px first.** Their customers find them on a phone. Design for the
  phone in the hand at the counter, not for a desktop that will never see
  this.
- **One accent colour, taken from their world** — signage, awning, logo,
  apron. Not a designer's choice. This is the single strongest anti-generic
  move available and it costs nothing.
- **Their photograph does the work.** A real photo of their actual food,
  chairs, or finished job. Never stock, never gradients, never illustration.
- **Type: system stack, sized with intent.** No webfonts — they break
  offline, which is where this demo has to work. Personality comes from the
  photo, the colour and the copy, not from a downloaded typeface.
- **Copy in their voice.** Pull phrasing from their own Instagram captions.
  If they say "best pies in the Waikato", the tagline is that, not
  "Artisan Baked Goods".
- **Contrast and focus states** are part of looking professional. Check the
  accent passes contrast on both paper and ink.

The hero rules from the `landing-pages` skill apply, with one exception
noted in Judgment Calls below.

`assets/template.html` is the shell — mobile-first, one CSS variable for
the accent, hero + one section + sticky CTA bar + one locked button. Fill
it; don't rebuild it. The two-hour figure only holds because it exists.

---

## Step 5 — Build and deploy

1. Copy `assets/template.html`, fill every `{{PLACEHOLDER}}`. **Any
   placeholder left in the file is a failed build** — they are written to
   be loud for that reason.
2. Save the hero photo **locally** alongside the HTML. Never hotlink from
   Instagram: it breaks, and it breaks in the room.
3. Deploy to Cloudflare Pages (the user has the connector). Clean, readable
   slug: `demo.theirdomain.co.nz/rosies-cafe`, never a random hash. They
   will glance at the address bar, and a readable URL reads as "built for
   me" and is memorable if they look again after you leave.
4. `noindex` is already in the template head. Add a `robots.txt`
   disallowing everything. Their branding must not end up indexed on
   someone else's domain.
5. **Save it offline before walking in.** Concrete-walled barbers and
   back-of-house offices eat reception, and a demo that spins is a live
   demonstration of an unreliable website — the worst possible outcome.
   Add to home screen, keep a local copy, and take full-page screenshots
   as a silent last resort. (Not needed when sending the link by DM.)
6. Open it on the actual phone, at the actual size, before leaving or
   sending.

---

## Step 6 — The walk-in

Timing is per-vertical — see `references/verticals.md`. Universally: never
during their rush.

**The phone, not the iPad.** Their customers find them on a phone, and a
phone-shaped demo is honest about what's being sold. The iPad is for
showing three finished sites afterwards, if they ask.

**Ask for the owner by name.** Recon should have supplied it.

**Say "rough" out loud.** Something close to:

> "This is rough — took me an afternoon. I just thought it'd be easier to
> show you than describe it."

That one sentence does three jobs: pre-empts criticism, makes the effort
feel proportionate rather than desperate, and makes clear the real thing is
better.

**Then hand over the phone and stop talking.** Let them scroll. The silence
is where the sale happens. Do not narrate features.

**Open with the gap, not the price.** The first question after they've
scrolled is the one recon left deliberately unanswered — "what are the
prices actually now?", "is Thursday still late night?". It gets them
correcting the demo, which is them taking ownership of it.

### The four responses

**Interested** — don't close on the spot with a number pulled out of the
air. Get the correction list (they will have one, it's a good sign), agree
what happens next, and put a time on it.

**"We've already got a guy."** Fine. Ask what they've got and when it was
last touched. Most of the time it's a Facebook page or a site from 2016
that isn't mobile-first. Show them their own site on the same phone next to
the demo. Don't disparage the incumbent — let the comparison do it.

**"How much?"** They're interested. Give the number plainly, without
apology or padding, then stop. The rough demo has already done the work of
making the number feel like a beginning rather than a bill.

**Brush-off** — "leave it with me", "email me something". Take the email,
send the link, leave. Do not push. The demo is already built and the URL
already exists; the cost of a slow yes is zero.

**Owner not in:** establish when they *are* in, leave nothing, come back.
A demo shown by a receptionist to an owner is a demo with no one in the
room to answer the questions.

---

## Step 7 — Follow-ups

Different animal from cold outreach — they've met you (or replied to you)
and seen the thing. The job is to make the demo **re-findable**, not to
re-pitch. Do not reach for `cold-sms` templates here; the relationship has
already started.

**Same day, within a couple of hours:**

> "Good to meet you — here's the link: [url]. No rush, have a look when
> you've got a minute."

Nothing else. No pitch, no pricing, no "as discussed".

**Four to five days later, once:**

> "Any thoughts on it? Happy to fix the prices if you send me the current
> ones."

The ask is a small, concrete, low-cost action — not a decision.

Then stop. Two touches after a face-to-face (or after sending the link by
DM) is the ceiling. Third contact reads as needy and burns a prospect who
might have come back in three months. Keep the URL live; a slow yes is
still a yes.

---

## Verification — run this before it leaves

1. **Zero invented facts.** Walk the page and point at the source for every
   name, price, hour and number. Any that can't be sourced come off.
2. **No `{{PLACEHOLDERS}}` remain.** Grep the file.
3. **Phone dials, maps link resolves, hours match Google.**
4. **Works offline**, on a phone, at 390px, with airplane mode on.
5. **Two sections.** If it looks finished, it failed.
6. **Exactly one open loop.**
7. **Accent colour came from their signage**, not from taste.
8. **Not indexed** — `noindex` present, `robots.txt` disallowing.
9. Script and both follow-up messages drafted, in the user's voice.

Report what was checked, not just that it's done.

---

## Judgment calls

- **Polish vs roughness.** `landing-pages` says premium polish creates a
  halo in ~50ms and clutter poisons everything below it. This skill says
  stay rough. Resolution: rough in *scope*, premium in *craft*. Fewer
  sections, executed well.
- **Open loop vs "never a dead end."** `dashboard-saas-redesign` says never
  ship an empty container or a dead end. That rule is for shipped product;
  a demo is an argument. The greyed-out button is deliberate and labelled
  "coming soon", which is not a dead end — it's a promise.
- **Conversion structure vs demo structure.** `landing-pages` prescribes a
  full doubt-clearing journey — proof, PAS, FAQ, closer. A demo has an
  audience of one who already knows the business, so all of that is
  omitted. When the job is *won* and the real site is built, the
  `landing-pages` structure applies in full. Don't confuse the two
  artifacts.
- **Speed vs personalisation.** The template makes builds fast; the accent
  colour, photo and copy make them specific. Never let speed take the
  colour or the copy — those are the parts that make it theirs.
- **Building before contact.** Building for someone who never asked is
  speculative work; that's the accepted cost of the walk-in play. Keep it
  at two hours, keep it unindexed, and take it down if they say no. For
  prospects found on Facebook, `fb-dm-outreach` offers first and builds on
  yes.