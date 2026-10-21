# iRacing paint files, folders and sharing

## Where files go

```
Documents\iRacing\paint\<car folder>\car_<ID>.tga          paint (sim-stamped numbers)
Documents\iRacing\paint\<car folder>\car_num_<ID>.tga      paint with the number painted on (custom number)
Documents\iRacing\paint\<car folder>\car_spec_<ID>.tga     spec map source; sim makes car_spec_<ID>.mip
Documents\iRacing\paint\<car folder>\car_decal_<ID>.tga    optional decal layer (rarely needed)
Documents\iRacing\paint\<car folder>\car_team_<TEAMID>.tga team paint (also car_num_team_, car_spec_team_)
Documents\iRacing\paint\helmet_<ID>.tga, suit_<ID>.tga     default helmet/suit (or per car folder)
```

- **`<ID>`** is the user's numeric iRacing customer ID.
- **The car folder** is created the first time they drive the car. Its name is iRacing's internal one,
  e.g. `mx5 mx52016` for the Global MX-5 Cup or `porsche9922cup`. `find_paint_folder.py` lists them.
- **OneDrive.** If Documents is redirected to OneDrive the path is `...\OneDrive\Documents\iRacing`.
  iRacing support says OneDrive backing up this folder causes problems. If paints misbehave, stop
  OneDrive backing up Documents.
- **Backups.** `install_paint.py` keeps them in `Documents\iRacing\paint_backups\<car>\<timestamp>\`,
  outside the paint folder so Trading Paints' cleanup never touches them.

## Formats

| file | size | format |
|---|---|---|
| Paint | 2048×2048 (legacy 1024) | **24-bit TGA, RLE compressed** (iRacing's stated format) |
| Spec map | Same | 24-bit TGA, or 32-bit when it uses the specular-mask alpha |
| Decal layer | Same | 32-bit TGA with alpha |

Some PSD templates carry an alpha channel. Saving the paint as 32-bit can make it show all black for
others, so always 24-bit. Trading Paints also accepts PNG uploads and converts them.

## Templates

- **Downloading.** In the iRacing UI: *My Content → Car Manager → Download Template*, or the Paint Shop's
  *Download Template* for a car. You get a zip with a PSD.
- **Guide layers.** Templates contain a "Turn Off Before Exporting TGA" group (wireframe, number blocks,
  sponsor stamp guides, items the sim stamps on), the paintable artwork, and on most cars a custom spec
  map group. Each template has layers showing where numbers and sponsors are stamped.
  `inspect_template.py` classifies these by name; override with `--mask-layer`, `--wire-layer` or
  `--keepout-layer` if a template uses odd names.
- **Shared UV areas.** Some parts share one template area for both sides of the car. Reported examples
  include the wing support bar on the BMW M4 GT4. Whatever is painted there appears on both sides, so
  text reads backwards on one of them.

## Seeing changes

1. Open the car in a test session or the Paint Shop.
2. Press **Ctrl+R** to reload paints. The car flashes white, then shows the update.
3. In replays, iRacing doesn't reload cars sitting in their pit stall. Move the replay to a point
   where the car is on track.

## Numbers

- **Sim-stamped number paint (default).** iRacing stamps the number. Number font and colours are set in
  the Paint Booth, not in the paint file.
- **Custom number paint.** `car_num_<ID>.tga` with the number painted in. The sim uses it instead of
  `car_<ID>.tga` and stamps no numbers.
  - To race one through Trading Paints, the user needs **Trading Paints Pro**.
  - Viewers need **"Hide car numbers"** turned on in iRacing's graphics settings (then restart the sim).
  - Everyone else sees the sim-stamped fallback.

## Trading Paints

Other drivers only see a custom paint if they run the Trading Paints Downloader. To publish:

1. Sign in at tradingpaints.com and open **My Paints**.
2. Pick the car.
3. Upload `car_<ID>.tga` (or PNG).
4. Add the spec map as the **`car_spec_<ID>.mip`** that iRacing generated in the paint folder. Don't upload
   the spec TGA.
5. Optionally submit to the Showroom. That requires original work and in-sim screenshots, not
   work-in-progress.

## Troubleshooting

| symptom | cause / fix |
|---|---|
| Paint doesn't change | Ctrl+R; check the file name matches the customer ID exactly; check the car folder is right (the most recently driven car is top of `find_paint_folder.py`); restart the sim |
| Spec map looks old | Delete `car_spec_<ID>.mip` (the installer does) and press Ctrl+R |
| Paint all black (for others) | It was saved 32-bit; or "2048 paint textures" is off in iRacing graphics options |
| Faint default logos show through | The car's default Paint Shop design has a spec map. Pick a plain fallback design in the Paint Shop, or supply your own spec map |
| Others can't see the paint | They need the Trading Paints Downloader running; the paint must be uploaded under My Paints for that car |
| You can't see your own TP paint | Downloader option "Update My Own Paints" must be on; for custom numbers, "Hide car numbers" must be on |
| Logo cut off or hidden | Add the hidden area to `keep_out_extra`, move the logo, rebuild. If unsure where it maps, use the locator |

Sources: iRacing support "Custom Paint Policy" and "Disabling OneDrive backups"; iRacing "Paint
Textures"; Trading Paints help (custom numbers, Showroom submission, all-black paints, ghosted logos,
previewing paints); F1GamerDad "AI iRacing Livery Cheat Sheet".
