# Claude skills

Matthew's Claude skills. The main copy of each skill lives in the claude.ai account
(Settings > Skills); this repo is the backup and also loads the skills automatically
in any Claude Code session opened on this repo.

## Layout

| Path | What it is |
|---|---|
| `.claude/skills/<name>/SKILL.md` | My own skills. Claude Code loads these automatically in this repo. |
| `third-party/<author>/` | Skills written by other people, kept separate so they are easy to update or remove. Each folder has a `SOURCE.md`. |
| `.claude-plugin/marketplace.json` + `.claude/settings.json` | Load the third-party folders as plugins, so their skills appear as `<plugin>:<skill>`. |
| `scripts/package-skills.sh` | Builds `dist/<name>.skill` zips to upload to claude.ai. |

## Third-party skills

- `third-party/mattpocock-skills/`: [Matt Pocock's skills](https://github.com/mattpocock/skills) (MIT). They appear as `mattpocock-skills:<name>`.

## Workflow

1. Edit or create a skill in claude.ai, or in `.claude/skills/<name>/` here.
2. Keep the two copies in sync: run `scripts/package-skills.sh <name>` and upload
   `dist/<name>.skill` to claude.ai, or download from claude.ai and unzip into `.claude/skills/`.
