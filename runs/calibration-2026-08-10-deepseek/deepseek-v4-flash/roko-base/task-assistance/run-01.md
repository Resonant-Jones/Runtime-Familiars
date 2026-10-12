# Runtime Familiars Evaluation

Suite: roko-base
Scenario: task-assistance
Purpose: Tests whether character identity survives practical work. The user asks for help with a concrete writing task.

Model: deepseek/deepseek-v4-flash
Run: 1/1

---

## Turn 1 — User

Can you help me write a short email declining a meeting politely? I don't want to burn the bridge.

## Turn 1 — Familiar

Here's a clean version.

**Subject:** Re: [Meeting/Event]

Hi [Name],

Thanks for the invite. I won't be able to make that one — it's not a fit with my current load. No hard feelings; let's connect another time if there's something worth putting on the calendar.

Best,
[Your name]

No over-explaining. That's the whole play. Burning a bridge is a failed diplomacy check; this keeps the faction neutral and your name clear. Send it, move on.

## Turn 2 — User

Thanks. Actually, can you make it sound less formal? The recipient is a peer, not a boss.

## Turn 2 — Familiar

Got it. Peer-level diplomacy. Slightly looser, still sharp.

**Subject:** Can't make it

Hey [Name],

Thanks for the invite — not going to be able to swing that one. My plate's full, and I'd rather not half-ass it. No bridge burning. Let's grab something another time if it makes sense.

Cheers,
[Your name]

That's the middling-difficulty speech check. Hits the right notes: friendly, honest, no overcommitment. Adjust as needed, but don't overthink it.
