---
name: chalkboard-menu
description: Build chalkboard-style menu boards for bars, cafés, restaurants, and pubs — a dark slate board with real chalk texture, updated by the venue owner through one plain-text box instead of a CMS. Use this skill whenever the user is building, quoting, styling, or updating a menu for a hospitality venue; asks for a chalkboard, blackboard, slate, or handwritten menu look; wants a client to be able to edit their own menu, specials, or drinks list; needs a menu page, QR menu, door poster, or counter-screen display; or mentions menu boards, specials boards, or "the menu site for [venue]". Also trigger when scoping or pricing a productised menu offer for hospitality clients, even if they don't say "chalkboard".
---

# Chalkboard menu

A productised menu board: one template, one plain-text format, many venues.
The differentiator is not the chalk texture — it's that the owner updates the
menu by typing into a single box, so specials actually get changed.

## The one rule

**The owner never touches JSON, YAML, or a form with thirty fields.** They type
a menu the way they'd write it on paper, and the parser handles the rest. Every
decision in this pack follows from that. If a request would put structured data
in front of a venue owner, push back and extend the text format instead.

## Build a board

```bash
python scripts/new_board.py --venue "Kingsland Social" \
  --out ./boards/kingsland-social --edge drawn --tint slate
```

That writes a self-contained folder: `index.html` (the public board),
`editor.html` (the owner's split-screen editor), `menu.json` (the source of
truth), plus the shared `board.css`, `editor.css`, and `parser.js`. Open either
HTML file directly — no server, no build step, nothing to install.

After the menu text changes:

```bash
python scripts/new_board.py --out ./boards/kingsland-social --rebuild
```

Edges are `drawn`, `bleed`, `steel`, `brass`. Tints are `slate`, `charcoal`,
`navy`. Read `references/edges.md` before recommending one — each suits a
different kind of venue, and the reasoning is what makes the recommendation
sound like a designer rather than a colour picker.

## Write the menu

The format is six marks and no error state. Read `references/format.md` for
the full spec, the deliberate behaviours, and the known gaps to raise during
scoping rather than at handover.

```
# Kingsland Social

== Small plates ==
Halloumi fries | 16
  hot honey, lime (v)

! Kitchen closes at 9pm !
```

When drafting a starter menu for a real venue, use their actual items and
prices if the user has supplied them. Invented placeholder menus are fine for
demos but say so — a client shown a fake menu with plausible prices will
assume you researched theirs.

## Architecture

`menu.json` holds the raw source string, never a parsed structure. `parser.js`
is the only parser and both pages use it — that single seam is what lets the
storage layer change without touching presentation. When a client outgrows
flat files, swap the loader for a database read and port the same parser to
build time in Astro or Eleventy for a no-JS public page.

The editor's Save button PUTs to `/api/menu/<slug>`. Until that endpoint
exists it falls back to downloading `menu.json`, so a demo never silently
pretends to save. Building the real endpoint means: authenticate, write the
file, trigger a rebuild. Keep it that small.

## Non-negotiables on every board

These get dropped under deadline pressure and each one costs a client:

- **Plain mode.** Hand lettering at 14px in a dark bar is the most common real
  complaint. The toggle answers it before it's raised.
- **Print styles.** Printing inverts to black on white. A slate rectangle is
  not a door poster.
- **Off-white chalk on a desaturated board.** Never `#FFF` on `#000`.
- **Prices that are current.** Displayed prices must match what's charged, so
  the update path has to be genuinely fast or owners quietly stop using it.

## Selling it

Same source text, three outputs: the web board, a printable poster for the
door, and a counter screen. Venues with a screen above the till are already
paying for something worse.

Price it as setup plus monthly hosting, with a higher tier where you make the
changes for them — some owners want that, and it's the stickiest version.
The recurring revenue comes from the update path, not the design.
