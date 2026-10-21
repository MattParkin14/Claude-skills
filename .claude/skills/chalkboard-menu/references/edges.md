# Edges, tints, and the chalk itself

Four edges times three tints is twelve looks from one template. That is enough
that no two venues on your books need to look alike, which is the whole
argument for productising this rather than building each one.

## Edges

Set with a class on `.frame`. Exactly one at a time.

**`e-drawn` — drawn rule.** A double chalk line inset on the slate, run through
the same displacement filter as the type. This is what a signwriter actually
does, it costs nothing to render at any size, and it survives being scaled down
to a phone. Default, and the right answer most of the time.

**`e-bleed` — bleed.** No edge at all; the slate runs to the corners and the
drop shadow does the work. Best on mobile, where a frame just eats width. Ages
the best of the four. Choose it when the venue's own branding is strong enough
that the menu shouldn't compete.

**`e-steel` — steel rim.** A 5px powder-coated lip with a highlight along the
top. Industrial. Suits craft beer, roasteries, anywhere with exposed ductwork.
Wrong for a wine bar.

**`e-brass` — brass mount.** A hairline held off the board with a gap, like a
print in a mount. The most restrained and the most upmarket. Pairs best with
the navy tint.

Deliberately not included: timber. A wooden frame reads as theme-restaurant and
dates fast. If a client asks for it, show them `e-drawn` first.

## Tints

Set with a class on `<body>`: `t-slate` (green-black, the default and the most
convincingly like real slate), `t-charcoal` (neutral, safest against warm
interior photography), `t-navy` (cooler, pairs with brass).

Never pure black. Real chalkboards are desaturated dark green or grey, and the
eye reads pure black as a screen rather than a surface.

## How the chalk effect works

Four layers, and it falls apart if you drop any of them:

1. **Displacement filter.** An SVG `feTurbulence` feeding `feDisplacementMap`
   at `scale="1.7"`, applied via `filter: url(#chalk)` on the type. This breaks
   up the letter edges. The filter element must be present in the page — it
   lives inline at the top of both templates.
2. **Slate grain.** A tiled fractal-noise data URI on `.board::after` at
   `mix-blend-mode: overlay`. Without it the board reads as a flat div.
3. **Dust halo.** A soft `text-shadow` in the chalk colour, no offset.
4. **Off-white chalk.** `#F2EDE4`, never `#FFF`. Pure white reads as neon.

Tuning: raise `baseFrequency` for finer grain, raise `scale` for rougher chalk.
Past `scale="2.5"` the type stops being legible at body sizes — check on a
phone before shipping anything higher.

## Legibility

Every board ships with plain mode (`.plain` on `<body>`), which drops the
display faces and the filter for a clean sans. This is not decoration. Hand
lettering at small sizes in a dark room is the most common genuine complaint
about chalkboard menus, and having the toggle ready answers the objection
before a client raises it.

Print inverts to black on white. A slate rectangle is not a door poster and
drinks a toner cartridge.
