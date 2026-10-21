#!/usr/bin/env bash
# Zip each skill in .claude/skills into dist/<name>.skill for uploading to claude.ai (Settings > Skills).
# Usage: scripts/package-skills.sh [skill-name ...]   (no names = every skill)
set -euo pipefail
cd "$(dirname "$0")/../.claude/skills"
out=../../dist
mkdir -p "$out"
names=("$@")
[ ${#names[@]} -eq 0 ] && names=(*/) 
for n in "${names[@]}"; do
  n=${n%/}
  rm -f "$out/$n.skill"
  zip -qr "$out/$n.skill" "$n" -x '*.DS_Store'
  echo "dist/$n.skill"
done
