# Quick-reference prompts and checklists

Ready-to-use lines (for the user to paste, or for Claude to apply as
behavior) distilled from the method.

## Layer 1 — Spec

Kick-off prompt (combine all three):

> Interview me to identify the goal of this project — the decision the
> output drives, not just the task. Bias towards smaller, more
> compartmentalized specs with a clear checkpoint after each. Make me
> verify key decisions explicitly to ensure nothing is missed.

Spec template per stage:

- **Goal**: the decision/conclusion this serves
- **Scope**: what's in, what's explicitly out
- **Inputs**: files, data, connections available
- **Deliverable**: the concrete thing shown at the checkpoint
- **Key decisions**: choice made → alternative → awaiting confirmation

## Layer 2 — Verifier

Verification prompt:

> Before touching anything, outline the evaluation criteria you will use
> to ensure a high-quality final product. Be precise. If this turns into
> a complex build, run the final output past a second model/critic to
> ensure both agree. Pull in external signal where possible (run it,
> diff against historical examples, check the live system) rather than
> declaring success.

Verification checklist at the end of a build:

- [ ] Output checked against each stated criterion, one by one
- [ ] Independent critic pass done (second model or deliberate review)
- [ ] External signal consulted (tests run, output executed, live system
      checked, historical reference diffed)
- [ ] Verification reported to the user, not just the result

## Layer 3 — Environment

Environment audit prompt:

> Audit my setup: (1) What belongs in my CLAUDE.md / project
> instructions — repo overview, skill routing, knowledge locations,
> non-negotiable rules? (2) What reference material should live in a
> knowledge base folder, organized so it's obvious where to look?
> (3) What do I do repeatedly that should become a custom skill?
> (4) Bucket my actions into always-do / ask-first / never-do, and for
> the never-do items, recommend tool-level enforcement (hooks,
> permissions) rather than prompt-level requests.

Example hard guardrail (Claude Code): a pre-tool-use hook on Write/Edit
that rejects any path under a protected folder — enforced at the tool
level so it cannot be bypassed by the model, unlike a CLAUDE.md line.

## Closing principle

You can outsource your thinking, but you can't outsource your
understanding. Every layer is a mechanism for moving the user's
understanding into the system — never a substitute for it.
