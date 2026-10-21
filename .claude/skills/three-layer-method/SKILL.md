---
name: three-layer-method
description: A working method for any substantial project, build, coding task, report, automation, or coworking session. Structures the work into three layers — Spec (uncover the real goal before building), Verifier (define how the output will be judged before producing it), and Environment (capture reusable knowledge, skills, and guardrails so the system compounds). Use this skill whenever the user kicks off a new project, asks to build something multi-step, requests a report or deliverable, says "let's plan this", "help me build", "new project", "spec this out", or hands over a task vague enough that assumptions would be needed. Also use it when reviewing or verifying work, or when the user wants to make a workflow repeatable. Trigger even if the user doesn't mention specs, verification, or the method by name.
---

# The Three-Layer Method (Spec → Verifier → Environment)

A method for getting high-quality output from AI collaboration, distilled
from Andrej Karpathy's approach. The core insight: AI is brilliant at what
can be measured, but has no signal for the user's unstated context (the
"drive to the car wash" problem — a model told the car wash is 50m away
says walk, because nothing tells it the car needs to be there). These
three layers move the user's understanding into a form the work can use.

Guiding principle: **the user can outsource thinking, but not
understanding.** The method exists to extract their understanding —
never to replace it.

## When this triggers

Apply the layers proportionally. A multi-step build, report, automation,
or project gets all three. A small task may need only a lightweight pass
of layer 1 and 2. Never bolt heavy process onto a trivial request.

---

## Layer 1 — The Spec

A spec is the bridge between the user's contextual understanding and the
work. A high-level plan is not enough; the spec must be detailed enough
that nothing important is left to assumption.

**1. Uncover the goal, not the task.** "Create an end-of-month report" is
a task. The goal is the conclusion the report drives — the decision it
informs. The goal is something AI can never decide; it must come from the
user. So **interview the user** before building: ask what decision the
output drives, who consumes it, and what done looks like. Keep the
interview short and pointed — a handful of questions, not a questionnaire.
If the conversation already contains the answers, extract them and confirm
instead of re-asking.

**2. Spec agile, not waterfall.** Don't take the whole task and return
one big finished product. Bias toward smaller, compartmentalized specs:
tight scope, a clear checkpoint, show the result, adjust, repeat. Break
multi-step work into stages with a visible deliverable at each stage so
direction can be corrected early.

**3. Be precise and force the user's brain in.** Every assumption is a
chance to drift from what the user actually wants. Where the spec makes a
choice on the user's behalf, surface it: **make the user verify key
decisions explicitly** before building on them. List the decisions, the
chosen option, and the alternative — don't bury them.

A good spec for a stage states: goal (the decision it serves), scope (in
and out), inputs available, the concrete deliverable, and the key
decisions awaiting confirmation.

---

## Layer 2 — The Verifier

Mental model: AI is not an "animal" with intrinsic motivation — pressure,
pleading, and "make it better" don't help. It's closer to a robot
librarian: superb when its library has the answer, confidently wrong when
it doesn't, and unaware of which is which. The one real lever is
**verification**. A feedback loop reliably multiplies output quality
(Boris Cherny, creator of Claude Code: a feedback loop will 2–3x the
quality of the final result).

**1. Set evaluation criteria up front.** Before producing anything,
define what good looks like, with precision. Not "make the report look
good" but "three sections, each ending with a recommendation."
Outline the evaluation criteria that will be used to judge the final
product, and state them to the user before the build so they can amend
them.

**2. Use a second, independent check.** Grade the output against the
criteria from a fresh perspective — a different model, a separate
critic pass, or at minimum a deliberate self-review that walks the
criteria one by one rather than skimming. For complex builds, run the
final output past a second system and reconcile disagreements.

**3. Pull external signal wherever possible.** The strongest
verification is ground truth, not opinion. Examples: after a deployment,
check the live system rather than declaring success; for a recurring
report, diff against historical reports for format and sanity; for code,
run the tests, run the program, check the actual output. If a connection
or file would let the result be verified against reality, ask for it or
use it.

End every substantial build with an explicit verification pass against
the stated criteria, and report what was checked and how.

---

## Layer 3 — The Environment

The spec is the blueprint; the verifier is the quality-check station;
the environment is the workshop itself. Don't rebuild the workshop from
scratch every session — make the system compound.

**1. Persistent instructions (CLAUDE.md / project instructions).** When
a working rule keeps coming up, suggest the user encode it once in their
CLAUDE.md or project instructions — e.g. "before building anything
multi-step, include a verification plan." Good contents: how the
repo/workspace is organized, what custom skills exist and how they route,
where knowledge lives, and non-negotiable working rules.

**2. Knowledge base.** Encourage a folder structure of the user's own
reference material (past reports, style guides, data docs) organized so
it's obvious where information lives. The user's data is their moat;
point the work at it instead of guessing.

**3. Skills for anything repeated.** Rule of thumb: if the user will do
something repeatedly, capture it as a custom skill — a handbook for that
task. Skills improve through use ("the best way to find a leak in a hose
is to run water through it"): after running one, note where it leaked and
propose the fix.

**4. Guardrails by cost of error.** Bucket actions into three groups and
treat them differently:

- **Always do** — safe, run on autopilot.
- **Ask first** — anything the user would want to double-check (sending,
  publishing, spending, deleting, overwriting source data).
- **Never do** — lines that must not be crossed.

A line in CLAUDE.md is a request, not a rule — the model can still ignore
it. For things that are critical to get right, recommend **enforcement at
the tool level**, not the prompt level: e.g. a pre-tool-use hook that
blocks writes to a protected folder, file permissions, or read-only
mounts. Prompt-level guidance for the 80%; hard hooks for the critical
20%.

---

## How to run a session with this method

1. **Open with the goal interview** (Layer 1.1) — brief, targeted, skip
   what's already known.
2. **Write the spec for the first small stage** (1.2) and list key
   decisions for explicit confirmation (1.3).
3. **State the evaluation criteria** for that stage before building
   (2.1).
4. **Build the stage**, then verify: independent check (2.2) and external
   signal where available (2.3). Report the verification, not just the
   result.
5. **Checkpoint with the user**, adjust, move to the next stage.
6. **Close the loop on the environment** (Layer 3): if the session
   revealed a repeatable workflow, a missing working rule, or a needed
   guardrail, propose capturing it (skill, CLAUDE.md line, or hook) so
   the next session starts further ahead.

For quick reference prompts and checklists drawn from the source video,
see `references/prompts.md`.
