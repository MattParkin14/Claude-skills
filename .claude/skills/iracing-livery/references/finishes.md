# Spec maps and finishes

The spec map is `car_spec_<ID>.tga`. It is the same layout as the paint, and each pixel's RGB holds
material data instead of colour:

| channel | controls | 0 | 255 |
|---|---|---|---|
| **Red** | Metallic | non-metal (paint, vinyl, plastic) | full metal |
| **Green** | Roughness | mirror-smooth | very rough / matte |
| **Blue** | Clearcoat | **no clearcoat** | dullest clearcoat (**16 = shiniest clearcoat**) |
| Alpha (optional) | Specular mask | lighting effects off | on |

### The clearcoat channel

Blue was unused until iRacing's 2023 Season 1 build added clearcoat on it. Trading Paints' notes on
that change say it ranges from very dull at 255 to very shiny at 16, and to set it to 0 for no
clearcoat. **Values 1–15 are undocumented; avoid them.**

The F1GamerDad cheat sheet describes blue as "0 = full gloss coat, ~10 = none". That contradicts the
documented behaviour, so this skill follows the documentation. If a finish looks wrong in the sim,
test blue at 0 versus 16 on one panel and look.

### Alpha

Leave the spec map 24-bit unless you really need the specular mask. With alpha it must be saved as
32-bit, and most cars don't use it.

## Presets (`finish` names in livery.json)

| preset | R / G / B | look | source |
|---|---|---|---|
| `gloss` | 0 / 60 / 16 | Clear-coated solid paint | — |
| `gloss_noclear` | 0 / 30 / 0 | Glossy, no clearcoat layer | — |
| `satin` | 0 / 110 / 0 | Satin paint | — |
| `matte` | 0 / 175 / 0 | Matte paint or wrap | — |
| `flat` | 0 / 230 / 0 | Rubber, primer, flat black | — |
| `sticker` | 0 / 105 / 0 | Satin vinyl, so logos read as stickers | Cheat sheet used 0/105/10; blue moved to 0, see above |
| `metallic` | 255 / 85 / 0 | Standard metallic | TP "March Metallic" |
| `metallic_deep` | 255 / 64 / 18 | Deep, smooth metallic with clear | TP "Shiny Side Up" |
| `metallic_soft` | 217 / 115 / 0 | Soft lustre; forgiving on darker colours | TP "Twilight Shimmer" |
| `brushed` | 255 / 128 / 64 | Brushed alloy | TP "Brushed Alloy" |
| `patina` | 229 / 178 / 0 | Sun-baked semi-flat metal | TP "Arizona Patina" |
| `pearl` | 255 / 26 / 217 | Shiny clear-metallic; changes the colour a lot | TP "Freshly Waxed" |
| `matte_metal` | 28 / 131 / 0 | Velvety matte | TP "The Mattedor" |
| `chrome` | 255 / 15 / 0 | Mirror chrome; needs near-white albedo | Cheat sheet used 255/22/0 |
| `carbon_gloss` | 0 / 45 / 16 | Lacquered carbon; pair with the `carbon` pattern | — |
| `carbon_matte` | 0 / 150 / 0 | Dry carbon | — |

TP = Trading Paints' published spec-map starters.

You can also use any `[r,g,b]`, or `{"preset":"matte","roughness":150,"roughness_jitter":25}`.

## Rules that matter

- **Metallic darkens the paint.** iRacing's own docs say metallic albedo colours need to be much lighter
  than normal, and a chrome pixel should be white or nearly white. Lighten anything you make metallic.
- **Stamped items inherit the spec underneath.** Numbers and sponsors that iRacing stamps take
  whatever finish your spec map has in that spot. Keep stamped areas at gloss, satin or sticker, never
  chrome.
- **Finish contrast is a design tool.** Gloss body plus matte graphic plus metallic accent instantly
  reads as expensive. Per-shard `roughness_jitter` (40–80) makes a shard pattern sparkle as the car turns.
- **"Ghosted" logos under a custom paint.** Some cars whose default Paint Shop design has its own spec
  map show faint logos through a custom paint: the BMW M4 GT3, Mercedes-AMG GT3 2020 and GT4,
  Porsche 992 Cup, Ford Mustang GT4, Corvette C8.R and others. Fix it by choosing a plain fallback
  design in the Paint Shop, or by shipping your own spec map (which this workflow always does).

## How the sim uses the spec map

- For the player's own car, iRacing loads `car_spec_<ID>.tga` and generates `car_spec_<ID>.mip` next to
  it when the TGA is newer or the .mip is missing.
- Ctrl+R regenerates it without restarting.
- If the spec still looks old, delete the .mip. The installer does this.
- Trading Paints takes the **.mip**, not the TGA.

Sources: iRacing "Paint Textures" (iracing.com/custom-paint-textures); Trading Paints help and blog
(spec map guide, update notes December 2022, spec-map starter posts).
