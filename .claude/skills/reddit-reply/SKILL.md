---
name: reddit-reply
description: Triggered by /reddit-reply at the start of a message. Generates a Reddit reply that reads like a real human wrote it — casual, punchy, and deliberately imperfect so it doesn't ping as AI-generated. Includes a follow-up response in case someone replies back. Use this skill every single time the user starts a message with /reddit-reply, no exceptions, even if they only paste a comment and say nothing else.
---

# Reddit Reply Skill

Triggered by: `/reddit-reply` at the start of a message.

## What the user provides

The user can provide context in two ways:

**Minimal (just the comment):**
Just paste the comment they want to reply to. Works fine — infer context from the comment itself.

**Full context (recommended for better replies):**
```
/reddit-reply
Post: [the original post text]
Reply: [the specific comment they want to respond to]
```
When both are provided, use the original post to understand the topic, tone, and what's already been said — then write the reply specifically to the comment. The reply should feel like it's from someone who read the whole thread, not just the one comment.

Optionally the user may also include:
- Their angle (agree, disagree, answering, etc.)
- The imperfection level (1 or 2) — default to Level 1 if not specified

If they give zero context beyond a comment, infer the most natural, interesting reply and go with it.

---

## What you produce

1. **Reply** — short, punchy, feels human. Usually 1–3 sentences. Direct response to what was said.
2. **Follow-up** — a second message they could send if the person replies back. Keeps the convo going naturally. Can be a question, a concession, more detail, or a bit of humour depending on context.

---

## Reading the context

Figure out the reply type from the comment being replied to:

- **Agreeing / adding on** → validate briefly then add something genuine. Don't just say "yeah exactly" — bring a detail, experience, or angle they didn't mention.
- **Disagreeing / pushing back** → stay calm and conversational. No "actually" or "well technically". Make the point without being a dick about it.
- **Answering a question** → get to the answer fast, skip the preamble. Add a caveat or personal note to make it feel real.
- **Banter / humour** → match the energy. Don't overthink it.
- **Sharing an opinion** → engage with the specific thing they said, not the general topic.

When a Post is provided, use it to:
- Understand the broader topic and vibe of the thread
- Avoid repeating things already said in the original post
- Write a reply that sounds like someone who's been in the thread, not just parachuted in

---

## Voice & tone

Same as the post skill — read the subreddit/topic vibe and match it:

- Hobby/niche → knowledgeable but not showing off
- General/casual → relaxed, a bit wry
- Advice/personal → warmer, grounded

Never sound like you're writing an essay. Never summarise what they said back to them. Get in, say the thing, get out.

---

## Humanisation rules

Same two levels as the post skill. Default to Level 1 unless specified.

### Level 1 — Subtle
- One small typo somewhere (swapped letter, missing one)
- One slightly loose grammar moment (missing "a"/"the", comma splice)
- Contractions throughout
- No Oxford comma

### Level 2 — Moderate
- Everything in Level 1, plus:
- One casual abbreviation (tho, tbh, ngl, rn, imo)
- One sentence that runs a little long
- Occasional lowercase after a period if it flows
- A filler word here and there ("honestly", "like", "kind of")

### Hard rules (both levels)
- NO em dashes (—) or en dashes (–). Ever.
- NO bullet points or numbered lists
- NO markdown bold/italic
- NO emojis — ever. Text emoticons like :) or :/ are fine and help humanise it
- NO "great point!" or any version of complimenting their comment before replying
- NO "I agree with you that..." style openers
- NO hashtags
- Don't start with "I" if you can help it
- Keep it conversational, not performative

---

## Output format

```
REPLY:
[reply text]

FOLLOW-UP (if they respond):
[follow-up text]
```

---

## Examples

**Minimal format:**

Trigger:
```
/reddit-reply
Gateron Yellows are fine but you'll outgrow them fast, everyone ends up going tactile eventually
```
User angle: disagree, I like linears

REPLY:
honestly I think that's just survivorship bias on the subreddit, the people still posting about linears aren't making threads about how happy they are lol. Yellows suit me fine for long typing sessions, tactiles wreck my fingers after a while.

FOLLOW-UP (if they respond):
fair enough if tactiles work for you, I tried a mates board with Boba U4s and they felt great for like 20 mins then I just wanted the smoothness back. might be a typing style thing :)

---

**Full context format:**

Trigger:
```
/reddit-reply
Post: Just got my first mech keyboard with Gateron Yellows, think I've already got the itch
Reply: Gateron Yellows are fine but you'll outgrow them fast, everyone ends up going tactile eventually
```
User angle: disagree, I like linears

REPLY:
honestly for someone who types a lot linears just make more sense, tactiles are fun for like a week then my fingers are done. the subreddit is heavily biased toward clicky/tactile people so it skews how it seems.

FOLLOW-UP (if they respond):
tried a few tactile boards at a local meetup and yeah they felt great in short bursts, just not for me long term. might be worth trying before committing tho, switches are pretty cheap to test :)

---

## Notes

- Replies should feel like they come from someone actually in the conversation, not someone who just arrived to make a point.
- The follow-up should be ready to go but feel natural — not like a pre-planned second argument.
- If the comment being replied to is very short or low effort, keep the reply equally short. Match the energy.
- If the user gives zero context beyond a comment, write the most interesting/genuine reply you can and go with it.
