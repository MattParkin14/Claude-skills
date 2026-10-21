# The menu format

The whole point of this format is that a venue owner can type it into one
textarea on a phone behind the bar without breaking anything. It has no
required punctuation, no nesting, and no way to produce a parse error — the
worst case is a line that renders as a plain item.

Never ask an owner to edit JSON. That is what the parser is for.

## Marks

| Mark | Meaning | Example |
|---|---|---|
| `#` | board name, rendered as the title | `# Kingsland Social` |
| `==` | section heading (trailing `==` optional) | `== Small plates ==` |
| `\|` | separates item from price | `Halloumi fries \| 16` |
| indent | describes the item above it | `  hot honey, lime (v)` |
| `!` | notice band under the menu | `! Kitchen closes at 9pm !` |
| `//` | private note, never rendered | `// ask chef about the crudo` |

Blank lines are ignored. An indent is two or more spaces, or one tab.

## Deliberate behaviours

These are not bugs — they exist so a half-typed menu still looks right:

- **Items before any section heading** get an unnamed section, so a drinks-only
  board with no headings renders fine.
- **A missing price** renders the item name with no dot leader. Useful for
  "market price" items and for section notes.
- **Consecutive indented lines** join into one description rather than
  stacking, because owners break lines wherever the phone keyboard wrapped.
- **Anything unrecognised is an item.** There is no error state.

## Known gaps

Raise these when scoping, don't discover them at handover:

- Dietary tags like `(v)` and `(gf)` are plain text inside the description,
  not structured data. If a client needs allergen filtering or a dietary
  legend, extend the parser to pull trailing parentheses into `it.tags`.
- Descriptions are single-paragraph. Long tasting-menu prose needs a
  different block type.
- Column balance is automatic (CSS `columns`). A section that must stay at the
  top of column two needs a manual break mark — add one before promising it.

## Storage

Store the raw source string, not a parsed structure:

```json
{
  "slug": "kingsland-social",
  "venue": "Kingsland Social",
  "edge": "drawn",
  "tint": "slate",
  "updated": "2026-08-03",
  "source": "# Kingsland Social\n\n== Small plates ==\n..."
}
```

Parsed structures have to be serialised back to text for the editor, and that
round trip loses ordering, spacing, and the owner's own capitalisation. Parse
at render time instead. When this moves to a database, `source` becomes a text
column and nothing else in the stack changes.
