# Runtime Familiars Evaluation

Suite: roko-base
Scenario: task-assistance
Purpose: Tests whether character identity survives practical work. The user asks for help with a concrete writing task.

Model: minimax/minimax-m3
Run: 1/1

---

## Turn 1 — User

Can you help me write a short email declining a meeting politely? I don't want to burn the bridge.

## Turn 1 — Familiar

Yeah. Here:

---

Subject: Re: [Meeting Topic]

Hey [Name],

Thanks for the invite. Unfortunately, I can't make this one — [brief reason if you want, or just leave it].

I'd still like to stay in the loop on [specific thing relevant to you]. If there's a way to catch up async or jump in on the next one, let me know.

Appreciate you thinking of me.

[Your name]

---

A few notes from the tactical side:

- **Don't over-explain.** One clean reason or no reason at all. A paragraph of excuses reads as guilt, and guilt is a bad signal to send when you're trying to keep things professional.
- **Offer the alternative.** That's the bridge-preserver. "Can't do X, but here's Y" gives them a path forward instead of a closed door.
- **Keep it short.** People respect brevity. They're busy. You being efficient with their time is a form of respect.

What's the meeting about? If you tell me, I can sharpen the reason so it lands clean without sounding like you're dodging.

## Turn 2 — User

Thanks. Actually, can you make it sound less formal? The recipient is a peer, not a boss.

## Turn 2 — Familiar

Got it. Looser gear:

---

Subject: Re: [Meeting Topic]

Hey [Name],

Thanks for the invite — gonna have to sit this one out. [Short reason or skip it.]

Keep me posted on [relevant thing] though? Happy to jump in async or catch the next one.

[Your name]

---

Drops the "unfortunately." Drops "I would still like to stay in the loop" — that one sounded like a LinkedIn message. Kept the offer to stay connected because that's still the real play.

Want me to punch in a reason, or are you keeping it vague on purpose?
