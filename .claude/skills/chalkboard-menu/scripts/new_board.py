#!/usr/bin/env python3
"""Scaffold or rebuild a chalkboard menu for one venue.

New board:
    python new_board.py --venue "Kingsland Social" --out ./boards/kingsland-social \
                        --edge drawn --tint slate

Rebuild after the menu text changed (reads menu.json, rewrites the pages):
    python new_board.py --out ./boards/kingsland-social --rebuild

menu.json is the source of truth. index.html and editor.html are generated
from it, so never hand-edit them — the next rebuild will overwrite your changes.
"""

import argparse, json, re, shutil, sys
from datetime import date
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
EDGES = ["drawn", "bleed", "steel", "brass"]
TINTS = ["slate", "charcoal", "navy"]

STARTER = """# {venue}
// notes to yourself start with two slashes — they never reach the board

== Small plates ==
Wood-fired focaccia | 12
  whipped butter, sea salt

== Larger ==
Market fish | 34
  seasonal greens, brown butter

== On tap ==
House pilsner | 13

! Kitchen closes at 9pm !"""


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "board"


def write_page(template, out_path, menu):
    html = (ASSETS / template).read_text(encoding="utf-8")
    # json.dumps twice-escaped for a <script type=application/json> block:
    # only </script> can break out, so neutralise it.
    blob = json.dumps(menu, ensure_ascii=False).replace("</", "<\\/")
    for key, value in {
        "{{VENUE}}": menu["venue"],
        "{{EDGE}}": menu["edge"],
        "{{TINT}}": menu["tint"],
        "{{MENU_JSON}}": blob,
    }.items():
        html = html.replace(key, value)
    out_path.write_text(html, encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", required=True, help="folder for this venue's board")
    p.add_argument("--venue", help="venue name, e.g. \"Kingsland Social\"")
    p.add_argument("--edge", choices=EDGES, default="drawn")
    p.add_argument("--tint", choices=TINTS, default="slate")
    p.add_argument("--menu", help="path to a text file holding the menu source")
    p.add_argument("--rebuild", action="store_true",
                   help="regenerate the pages from an existing menu.json")
    args = p.parse_args()

    out = Path(args.out)
    menu_file = out / "menu.json"

    if args.rebuild:
        if not menu_file.exists():
            sys.exit(f"No menu.json in {out} — scaffold the board first.")
        menu = json.loads(menu_file.read_text(encoding="utf-8"))
        # flags still win on a rebuild, so you can restyle without retyping
        if args.edge != "drawn" or "edge" not in menu:
            menu["edge"] = args.edge
        if args.tint != "slate" or "tint" not in menu:
            menu["tint"] = args.tint
    else:
        if not args.venue:
            sys.exit("--venue is required when creating a new board.")
        out.mkdir(parents=True, exist_ok=True)
        source = (Path(args.menu).read_text(encoding="utf-8") if args.menu
                  else STARTER.format(venue=args.venue))
        menu = {
            "slug": slugify(args.venue),
            "venue": args.venue,
            "edge": args.edge,
            "tint": args.tint,
            "updated": date.today().isoformat(),
            "source": source,
        }

    if args.menu and args.rebuild:
        menu["source"] = Path(args.menu).read_text(encoding="utf-8")
    menu["updated"] = date.today().isoformat()

    out.mkdir(parents=True, exist_ok=True)
    menu_file.write_text(json.dumps(menu, indent=2, ensure_ascii=False), encoding="utf-8")

    for asset in ("board.css", "editor.css", "parser.js"):
        shutil.copy(ASSETS / asset, out / asset)
    write_page("board.template.html", out / "index.html", menu)
    write_page("editor.template.html", out / "editor.html", menu)

    print(f"{menu['venue']} — {menu['edge']} edge, {menu['tint']} tint")
    print(f"  board   {out / 'index.html'}")
    print(f"  editor  {out / 'editor.html'}")
    print(f"  source  {menu_file}")


if __name__ == "__main__":
    main()
