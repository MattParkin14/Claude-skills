---
name: distill-yt
description: "End-to-end pipeline that turns a batch of YouTube video URLs into (1) a ranked, deduplicated list of top actions and (2) a brand-new reusable skill containing that playbook. Use this whenever the user provides — or wants to provide — YouTube links on a topic (e.g. cold email, sales outreach, copywriting, hooks, productivity) and wants the transcripts fetched, summarized, and boiled down into concrete actions, or wants those learnings packaged into a skill they can reuse. Trigger on phrases like 'distill these videos', 'summarize these YouTube links', 'top takeaways from these', 'turn these videos into a skill', or any time a list of YouTube URLs is paired with a request to extract tactics, lessons, or action items. Also trigger when the user types /distill-yt."
---

# distill-yt

Turn a batch of YouTube videos into a ranked, deduplicated set of top actions, and then a brand-new reusable skill containing that playbook.

The whole thing runs inside Claude Code or Cowork with **no Anthropic API key and no external AI calls**. The only code that executes is a transcript fetcher (plain HTTP). Every bit of summarizing and distilling is done by you — the model already in this session. Keep it that way: never route the reasoning steps through an API.

## Inputs

You need two things:

- A **topic label** in kebab-case (e.g. `cold-email`, `outreach`, `youtube-hooks`). It names the output skill.
- **Up to 20 YouTube URLs.**

Accept inputs from any of these, in priority order:

1. Arguments after the command: `/distill-yt cold-email <url> <url> ...`
2. A `urls.txt` file in the working directory (one URL per line; lines starting with `#` are ignored).
3. URLs pasted inline in the user's message.

If you have a topic but no URLs, ask for the URLs (or point them at `urls.txt`). If you have URLs but no topic, infer a short kebab-case topic from the content and confirm it with the user before naming the output skill.

## Pipeline

### Step 1 — Fetch transcripts

Run the bundled fetcher. It pulls each transcript with no API key and writes one cleaned text file per video plus a manifest.

```bash
# First run only — install the single dependency:
pip install youtube-transcript-api

# URLs as arguments:
python3 scripts/fetch_transcripts.py --out ./_distill_work <url1> <url2> ...

# ...or from a file:
python3 scripts/fetch_transcripts.py --out ./_distill_work --urls-file urls.txt
```

Outputs land in `_distill_work/`:

- `transcripts/NN_<videoid>.txt` — one per video, with a title/URL header
- `manifest.json` — which videos succeeded, which failed, and word counts

Read `manifest.json` first. Tell the user briefly how many transcripts came back and name any that failed (private video, no captions, or region-blocked) so they can swap them. Continue with whatever succeeded — don't halt because one or two failed.

Blocking note: fetching from a normal home/residential connection just works. Only if the user runs this on a cloud server (AWS/GCP/Azure/VPS) will YouTube likely block the IP — in that case point them at the PROXY NOTE at the top of `scripts/fetch_transcripts.py`. For personal local use this won't come up.

### Step 2 — Map: one note per video

Do **not** load all 20 transcripts into context at once — it's wasteful and it blurs the per-source signal. Work through them in small batches (~3–5 at a time). For each transcript, write a compact note to `_distill_work/notes/NN_<videoid>.md` capturing only what's reusable:

- The 3–7 most concrete tactics or claims — specifics, not vague advice.
- Any actual numbers, templates, scripts, or step sequences worth keeping.
- The speaker's stated reasoning for each, so the final playbook can explain *why*, not just *what*.

Keep each note tight — bullets, no transcript quoting. The notes are your working memory; once a note exists you can forget that raw transcript.

### Step 3 — Reduce: synthesize the top actions

Read the small note files (not the transcripts) and produce one ranked list of **top actions** with:

- **Consensus signal** — for each action, how many videos endorsed it. Things multiple creators independently land on are stronger; surface those first.
- **Deduplication** — collapse the same idea phrased different ways into one action.
- **Disagreements** — where creators contradict each other, say so rather than averaging it away. These are often the most useful parts.
- **Specificity** — keep the concrete version (the actual template, the actual number); drop the platitude.

### Step 4 — Present to the user

Show the ranked top actions in chat, grouped sensibly, with the consensus signal visible (e.g. "Personalize the first line — 9/12 videos"). Keep it skimmable. Ask whether they want to adjust emphasis before you bake it into a skill.

### Step 5 — Build the output skill

Once the user is happy, generate a new skill folder named after the topic (e.g. `cold-email/`). Use `references/output_skill_template.md` as the scaffold. Fill in:

- A **pushy description** so the skill actually triggers later — list the contexts where the playbook should fire (the template shows the pattern).
- The **body** = the distilled playbook: the ranked actions rewritten as clear imperative guidance, organized into a workflow the model can follow, with the concrete templates and numbers kept in. Record the disagreements as explicit judgment calls.
- A short **provenance** footer: topic, date, number of source videos.

Write it to `./<topic>/SKILL.md`, under ~400 lines.

### Step 6 — Install instructions

Tell the user exactly how to put the new skill into both tools — it's the same folder in two homes:

- **Claude Code, personal (all projects):** copy the folder to `~/.claude/skills/<topic>/`
- **Claude Code, one project (shareable via git):** copy to `<repo>/.claude/skills/<topic>/`
- **Cowork:** add it through Cowork's skills directory the same way.

After it's in place it's available as `/<topic>` and will also auto-trigger whenever its description matches the task.

If packaging tooling is available and the user wants a single installable file instead, package the folder into a `.skill` with skill-creator's `package_skill.py`.

## Notes

- API-free by design: the fetcher is plain HTTP; all distillation is your own reasoning in-session.
- Re-running is cheap. To refresh a playbook, add URLs and run again — regenerate or merge the output skill.
