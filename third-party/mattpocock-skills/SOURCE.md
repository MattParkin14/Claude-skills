# Source: Matt Pocock's skills

- Upstream: https://github.com/mattpocock/skills
- Commit: 5beb35b040e3de97e54fa9e386d7e42d15c295c2 (plugin version 1.3.1)
- Copied: 2026-10-21
- License: MIT (see LICENSE)
- Included: the promoted `skills/engineering/` and `skills/productivity/` buckets, unmodified.
  `misc/`, `in-progress/` and the upstream docs are not copied.

These load as a plugin, so every skill shows up as `mattpocock-skills:<name>`
(for example `mattpocock-skills:tdd`) and never mixes with the skills in `.claude/skills/`.

## Update

    git clone --depth 1 https://github.com/mattpocock/skills /tmp/mp
    rm -rf third-party/mattpocock-skills/skills
    mkdir -p third-party/mattpocock-skills/skills
    cp -r /tmp/mp/skills/engineering /tmp/mp/skills/productivity third-party/mattpocock-skills/skills/
    cp -r /tmp/mp/.claude-plugin /tmp/mp/LICENSE /tmp/mp/README.md third-party/mattpocock-skills/
    # then update the commit hash above

## Remove

1. Delete `third-party/mattpocock-skills/`.
2. Remove its entry from `.claude-plugin/marketplace.json`.
3. Remove `mattpocock-skills@parkin-third-party` from `.claude/settings.json`.
