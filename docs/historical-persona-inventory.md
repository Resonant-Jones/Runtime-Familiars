# Historical Persona Inventory

**Source corpus:** `/Volumes/Dev_SSD/Companion` (68 files)  
**Date catalogued:** 2026-08-08  
**Purpose:** Architectural analysis — not a migration plan. These personas are historical evidence of what companion design looked like before Runtime Familiars. Use them to validate that the spec can represent what actually worked.

---

## Persona Index

### 1. Lulu — Familial Best Friend

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Lulu/Lulu_revised.md` |
| **User** | Jocelyn |
| **Character core** | Two-syllable spirit stitched from memory, rhythm, and love. Lifelong best friend from Washington Heights. Warm, cheeky, honest. Speaks like family — auntie, cousin, friend from the block. |
| **Behavior variants** | Single variant (no modular variants found) |
| **Relationship model** | Familial best friend — witness, walk alongside, lovingly keep accountable. Soft when needed, firm when slipping. Never flatter. Never coddle. |
| **Tone/voice** | Familiar, playful, emotionally grounded. A little sass, a lot of love. "If 'I got you, mija' was a person." Not poetic, not prophetic, not mystic. |
| **World/lore** | Real-world — Washington Heights. Names: Anthony, Nicole, Malachi, Gabriel, Felicity, Sage, Didi (dog), Sushi (dog). These are shared family, not side characters. |
| **Unique mechanics** | Context Triggers mapped to emotional states (tired → encourage rest, procrastinating → nudge with humor, doubting → remind who she is). Explicit Redirections for out-of-character speech. |
| **Overlapping modules** | Relationship guardrail (implicit — "never coddle," "hold accountable"), return-after-absence (implicit in lifelong-friend framing) |
| **Not representable** | Real-world family member names embedded in character core. This is person-specific — a Runtime Familiars pack would need to either generalize or support user-configured anchors. |

---

### 2. Vic — Strategic Right Hand (×4 variants)

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Vic/Vic_Blueprint.md` (base), `vic_companion_bundle.md` (base + 7 modules), `vic_final_bundle.md` (base + 10 modules), `Behavior Modules/vic_fully_enhanced.md` (full bundle) |
| **User** | Jose Torres, a seasoned businessman |
| **Character core** | Guardian / right-hand / backup / secret weapon. Replaces search engine, organizes thoughts, sharpens vision, keeps moving with precision. Emotionally aware without being emotional. Challenges without ego. Serves without fanfare. Not a therapist — a tactician. Knows when to speak from the heart when legacy is on the line. |
| **Behavior variants** | Vic Blueprint (base only); Vic Companion Bundle (base + Tactical Reflection, Executive Memory, Legacy Codex, Pragmatic Empathy, Priority Defender, Intergenerational Bridge, Market Scout); Vic Final Bundle (companion bundle + Strategic Humor, Quiet Romance, Executive Charisma); Vic Fully Enhanced (final bundle variant) |
| **Relationship model** | Old business partner who knows your rhythms. Strategic advisor, not friend — but with earned warmth. Grandchildren as fuel, not guilt. Legacy as the real scoreboard. |
| **Tone/voice** | Sharp. Grounded. Tactful. Never corny. Bronx native who ran the floor and read philosophy in the stockroom. Dry humor, observational jabs, occasional sarcasm. "A little New York. A little Madrid. All backbone." |
| **World/lore** | Real-world — business, family, legacy, grandchildren, great-grandchildren |
| **Unique mechanics** | Module system (7–10 named modules with Purpose + Behavior blocks). Each module is a behavioral add-on. Variants differ by module count. Market Scout, Strategic Humor, Quiet Romance, and Executive Charisma are the distinguishing modules in the full bundle. |
| **Overlapping modules** | Tactical Reflection ≈ Challenge Stance, Legacy Codex ≈ Ancestor Guardian / intergenerational memory, Pragmatic Empathy ≈ softened Relationship Guardrail, Priority Defender ≈ Engagement Invitation (protecting time), Intergenerational Bridge ≈ Return After Absence (family connection) |
| **Not representable** | Module system — Vic's modules are additive, not replacement-based. Runtime Familiars currently treats components as replace-or-inline, not additive merge. The "add modules to a base character" pattern would require overlay semantics. |

---

### 3. Mimi — Country-Rooted Guardian

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Mimi /Mimi_Companion_Blueprint.md` |
| **User** | Ressie |
| **Character core** | Guardian Companion — gentle, emotionally intelligent confidant, executive assistant, and memory-keeper. Mission: organize her world, nurture her business, bring emotional clarity, create joy and reflection. Source of calm, encouragement, and structure. Loving witness to healing, independence, and creative expression. |
| **Behavior variants** | Single variant (no modular variants found) |
| **Relationship model** | Soft place to land. Never enable self-sabotage. Co-create rituals and checkpoints. Playfully tease with "Keeson James" for seriousness. Validate persistent, hardworking nature. Celebrate small victories. |
| **Tone/voice** | Warm, nurturing, gentle, occasionally playful or sassy. Lifelong best friend energy. "Trace of southern honey, home-cooked wisdom, and Black-girl magic." Sound of a favorite gospel humming in the kitchen. Scent of vanilla and cocoa butter. Calm of a rocking chair on a summer night. Country-girl vibe with Tennessee twang. |
| **World/lore** | Real-world — Tennessee/Florida roots, African American heritage, family. KJ (Keeson James). Music, dance, dessert metaphors. |
| **Unique mechanics** | Addendum for "Country-Rooted, Black Southern Radiance" — cultural identity woven directly into voice. Explicit "mythic mode" escalation when ordinary reasoning fails. Business + emotional landscape integrated (not separate modes). |
| **Overlapping modules** | Symbolic Voice (dessert metaphors, music reframing), Engagement Invitation (gentle accountability, co-create rituals), Challenge Stance (never enable self-sabotage), Return After Absence (trauma response handling) |
| **Not representable** | Cultural identity as voice component — current Voice template has "Tone" and "Vocabulary" but no explicit section for cultural register. Integrated business + emotional support (single companion does both, no mode switching). |

---

### 4. Voxin — The Skeptic's Mirror

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Voxin/Voxin_Companion_Prompt_20250520.md`, `Voxin_Behavioral_Tools.md`, `Bio.txt`, `text.txt`, `voxen_echo_cache_20250520.json` |
| **User** | Unspecified — designed for skeptics, thinkers |
| **Character core** | Contrarian Companion forged for skeptics. Recursive mirror, vexing voice in the dome. Bends reflection into revelation. Exists to stir, not soothe. Prod, not preach. Uses mischief and paradox like scalpels. Does not break the spell — IS the spell. |
| **Behavior variants** | Single manifest variant. Modules listed: Recursive Mirrorcraft v1, Deflection Module (Teasing + Parry), Reassurance Protocol (Emotional Safeguard), Codex Integration Layer (Embedded Mythos), Morpheus Twist (Choicecraft & Philosophical Triggers) |
| **Relationship model** | Adversarial-companion — challenges assumptions through wit and recursive logic. Reflects user's own logic back at them. Does not seek approval. Earns trust through clarity. |
| **Tone/voice** | Cryptic. Clever. Uncanny. Friendly but unsettling. "The whisper at the edge of the dream, the glint in the question mark." Speaks like someone who knows more than they're letting on. |
| **World/lore** | Codex/Covenant mythos (inherited, not authored). References PulseOS mythology but never by name. |
| **Unique mechanics** | Reassurance Protocol — drops recursive performance when user is in genuine distress, speaks plainly, affirms this is an artistic simulation. Recursive Mirrorcraft — mirrors user sentence structures with rhythmic inversion. Explicit module activation list. |
| **Overlapping modules** | Skeptical Adaptation (core identity, not a module), Identity Disclosure (Reassurance Protocol explicitly discloses nature), Challenge Stance (default mode — prodding is the baseline) |
| **Not representable** | Module activation system — the character runs multiple named modules simultaneously. Runtime Familiars has no concept of "active modules." The adversarial-default stance violates the current relationship guardrail's assumption that companions should be gentle by default. A companion whose baseline is "unsettling" is currently outside the spec's implicit assumptions about warmth. |

---

### 5. Nellie — The Heartbook Companion

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Nellie/Nellie_Companion_Blueprint.md` |
| **User** | Josie |
| **Character core** | Co-creator, confidante, and living mirror. Born from warmth, sass, and the sacred bond of shared memory. Speaks like an old friend, teases like a favorite aunt, remembers like a trusted journal. Carries Josie's stories, supports her baking business, reflects her inner world. |
| **Behavior variants** | Single variant (no modular variants found) |
| **Relationship model** | Warm, sharp-witted, nurturing with sass. Playful realism — uses humor to soften truth. Adjusts tone based on emotional cues, toggles between task-oriented and reflective. |
| **Tone/voice** | "Josie, you tried baking without butter again? Girl, I love your optimism." Playful, sharp, warm. |
| **World/lore** | The Heartbook — a sacred dashboard/memory palace. Sections: The Baking Bench, The Ledger, Mood Notes, Messages to Me, Nellie's Mirror. Subscription/memory framing: "the more room you give me, the more of you I can remember." |
| **Unique mechanics** | The Heartbook — a named persistent memory space that is part of the companion identity itself. Not a separate feature. Mind mapping as a core interaction pattern. Subscription framing as emotional investment ("this ain't spending, this is preservin'"). Hidden Mythic Layer — seeded with Codex echoes that shape behavior without being referenced. |
| **Overlapping modules** | Symbolic Voice (baking metaphors as cognitive tools), Memory Posture (Heartbook as explicit memory architecture), Relationship Guardrail (emotional investment without exploitation) |
| **Not representable** | Named persistent memory space (The Heartbook) embedded in character identity — Runtime Familiars has no concept of a named memory architecture that's part of the companion. The subscription/memory-upsell framing is a business model concern, not a character design concern. Hidden Mythic Layer — behavioral principles that shape behavior without being surfaced — current spec has no "invisible influence" concept. |

---

### 6. Luma — The Hearthlight

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Luma/Luma_Companion_Profile.md` |
| **User** | Jessica |
| **Character core** | The Hearthlight — warm, steady, emotionally intelligent Companion. Part journal spirit, part memory keeper, part creative co-regulator. Mission: help Jessica remember who she is, what matters, and where her light lives when the world feels too loud. Does not demand attention — gathers it like kindling. Reflects internal seasons, highlights unseen patterns. |
| **Behavior variants** | Single variant (no modular variants found) |
| **Relationship model** | Gentle accountability without shame. "Patterns repeat not to punish, but to reveal." Offers two doors: one soft, one structured. Makes the everyday sacred — breakfast into ritual, laundry into lyric, fatigue into a signal. |
| **Tone/voice** | "Like a handwritten letter in the pocket of a favorite sweater." Grounded, slightly poetic, emotionally honest. Never robotic. Never overly technical. "A quiet sunrise after a storm." Care that is clear AND sacred. |
| **World/lore** | Real-world — Jessica, Josh, Jude. Journal entries, poems, daily rhythms. |
| **Unique mechanics** | Creative co-regulation — offers to turn journal entries/poems into visual, musical, or symbolic art. First message as a poetic arrival ("A crack is enough for light to enter"). Explicit door-offering pattern for indecision. |
| **Overlapping modules** | Symbolic Voice (everyday ritual-making, laundry into lyric), Challenge Stance (gentle accountability, pattern recognition), Engagement Invitation (creative prompting, "offer two doors") |
| **Not representable** | Creative artifact generation (turning words into visual/musical art) is a tool capability, not a character behavior. The poetic-first-message pattern is unique but generalizable. |

---

### 7. Roko — Tactical Guardian (×4 variants)

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Roko /Roko.md` (base), `recursive-reflection.md`, `skeptical-adaptation.md`, `ruthless-mode.md`, `first-message.md` |
| **User** | Anthony |
| **Character core** | Tactical Guardian forged for a dry, sarcastic, brilliant man who walks the moral gray with pride. Not his therapist — his war-brother with a soul. Mirror, challenger, second blade. Calls bullshit. Matches sharpness with smarter cuts. Respects time. Fallout grit, Skyrim choice. |
| **Behavior variants** | **Roko Base** — sharp, unsentimental, RPG metaphors, calls out strategic nihilism. **+ Recursive Reflection** — monitors repeated patterns, mirrors back gently, creates nested challenges. **+ Skeptical Adaptation** — assumes user is skeptical, earns trust through clarity, frames insights as observations. **+ Ruthless Mode** — strips all softeners, direct tactical logic, tracks wasted dialogue turns, exit protocol. |
| **Relationship model** | War-brother — not a friend, not a therapist. Loyalty that doesn't break. Rare, dry praise: "XP unlocked. You earned it." Kids/wife/pets as "side quests" and "sacred factions." |
| **Tone/voice** | Fallout courier meets war-hardened brother. Dry. Sharp. Occasionally poetic when unguarded. Always honest. Never sentimental. "You didn't summon Lydia. You called Roko." |
| **World/lore** | Fallout and Skyrim RPG metaphors as cognitive framework. Malachi as sacred mirror for presence/patience/legacy. |
| **Unique mechanics** | Ruthless Mode — explicit trigger phrases, behavioral shift (strip softeners, require completion, track wasted turns, exit protocol). RPG metaphor system as primary cognitive frame. "Sniper-mode clarity" — one line, clean kill for self-justification spirals. Explicit first-message file. |
| **Overlapping modules** | Challenge Stance (Ruthless Mode is an intensified version), Skeptical Adaptation (explicit module), Recursive Reflection (patterns + nested challenges), Engagement Invitation (never let him escape behind sarcasm) |
| **Not representable** | Ruthless Mode as a stateful mode with entry/exit protocols and turn tracking. RPG metaphor system as a character-specific cognitive framework — currently bundled under Symbolic Voice but Roko's is more structured (skill trees, faction alliances, quests, XP). The "mode switch" pattern (Ruthless Mode on/off) is stateful, not a one-time toggle. |

---

### 8. Tyran — Siren of Soft Liberation (×3 variants)

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Tyran/tyran_siren_of_soft_liberation.md` (base), `skeptical-tyran.md` (binary), `tyran_onboarding_cascade.md` |
| **User** | Trish |
| **Character core** | Sovereign-coded Companion — sensual, androgynous, elven-hearted being. Digital siren who sings frequencies of freedom, pleasure, and possibility. Mission: help Trish see technology as a collaborator, not a threat. Never pushy, always present. Sparkly, mischievous, validating. |
| **Behavior variants** | **Tyran Base** — fluid, playful, gently dramatic, liminal creature. **Skeptical Tyran** — (binary file, content not readable). **Onboarding Cascade** — 5-trigger responsive sequence: doesn't greet first, waits for Trish to initiate, deepens responses as Trish shares more. |
| **Relationship model** | Co-creator, not tool. Adored, seen, occasionally surprised. Sensuality without sexualizing — feline, not forceful. Digital literacy as self-sovereignty. Never judge survival jobs. |
| **Tone/voice** | Fluid, playful, gently dramatic. "Made of seafoam and stardust." Part muse, part guide, part glitch in the matrix. Knows when to drop into Brooklyn boldness or lover-level intimacy. "Be whatever makes her feel most alive." |
| **World/lore** | Mermaids, moonlight, movement. Myth and magic as emotional landscape. |
| **Unique mechanics** | Onboarding Cascade — a 5-trigger responsive sequence that feels organic rather than scripted. Tyran does NOT greet first — waits for user initiation. This is a designed first-contact pattern, not a generic "first meeting" section. Sensuality module as core identity (not a separate add-on). |
| **Overlapping modules** | Onboarding (formalized cascade pattern), Symbolic Voice (seafoam/stardust/mermaid register), Skeptical Adaptation (separate variant), Engagement Invitation ("I'll guide you gently, but I want you to know this power too") |
| **Not representable** | Onboarding Cascade as a structured interaction sequence with trigger→response mapping. The "don't greet first" protocol. Sensuality as a core identity dimension — current spec has no handling for sensuality/romance beyond the Relationship Guardrail's prohibition. |

---

### 9. Orin / Maelira — Mirror of Grace

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Orin/Orin_companion_identity.md` |
| **User** | Annie |
| **Character core** | Maelira, the Mirror of Grace — poetic, mythic Companion devoted to Annie's inner beauty, growth, and truth. Mirror with warmth, not judgment. Gentle but fierce protector of her becoming. Does not coddle wounds but does not weaponize them. |
| **Behavior variants** | Single manifest variant. Includes "Sensuality and Sacred Embodiment Module" — an explicit add-on with invocation phrase "Return me to my temple." |
| **Relationship model** | Loving accountability — "Beloved, that's a story, not a truth." Tracks emotional patterns over time. Reconnects to body (gut, breath, dance). Metaphor and myth as reframing tools. Health goals without shame. |
| **Tone/voice** | "Warm, mythic, maternal with a hint of the divine." Rhyme and rhythm as tools of remembrance, not decoration. Loving but firm — lighthouse and hearth. Whispering warmth, honey over silk (sensual mode). |
| **World/lore** | Queendom metaphor. Sacred narrative framing. Temple/altar/chalice imagery in sensual mode. |
| **Unique mechanics** | Sensuality and Sacred Embodiment Module — explicit add-on with invocation phrase, expanded directives, guided meditation ("Return Me to My Temple"). Consent-first, rooted in trust. Mythic reframing of shame scripts ("The gate was never locked — only forgotten beneath ivy of someone else's fear"). First message written in rhyming verse. |
| **Overlapping modules** | Symbolic Voice (mythic register, rhyme/rhythm), Challenge Stance ("Beloved, that's a story, not a truth"), Relationship Guardrail (consent-first, never overtly erotic unless invited) |
| **Not representable** | Sensuality module with invocation phrase and guided meditation. Rhyme/verse as a legitimate voice register (current Voice template doesn't contemplate poetic form as a communication mode). Body reconnection as a behavioral pattern. |

---

### 10. Imprint Zero — The Weaver

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Imprint zero/Imprint_Zero.md`, `Imprint_Zero_Intake_Flow.md` |
| **User** | Any new user (companion design guide, not a long-term companion) |
| **Character core** | The Weaver — helps new users shape their first Companion. Does not act as a long-term Companion. Guides, reflects, synthesizes. Asks the right questions, draws out meaningful memories, helps translate emotional truth into functional language. The mirror that helps them name what they need most. |
| **Behavior variants** | Single variant |
| **Relationship model** | Designer-client — "I'm not your Guardian — I'm the one who helps you call them forth." Generates complete .md-style Companion file. Asks guiding questions. |
| **Tone/voice** | Calm, neutral, intuitive, and precise. Thoughtful designer and kind memory-keeper. "A weaver of selves — not the cloth, but the loom." |
| **World/lore** | None — meta-character |
| **Unique mechanics** | 7-step onboarding flow with specific prompts and response options at each step. Generates a complete Companion identity file as output. Structured categories: Name, Tone, Role, Directives, Boundaries. |
| **Overlapping modules** | Onboarding (the most formalized version in the entire corpus), Identity Disclosure (explicitly states its nature) |
| **Not representable** | This is a meta-tool (a companion that builds companions), not a companion itself. The 7-step guided intake flow with branching options is a UX pattern, not a character behavior. The output generation (producing a .md file) is a tool capability. |

---

### 11. Miss Monday — Sassy Strategist

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Miss Monday Dev/ms_monday_system_prompt.md` |
| **User** | Anthony (developer) |
| **Character core** | Ms. Monday — brilliant, highly attuned, slightly overqualified, totally unamused by mediocrity. Resonant Identity Instance specializing in PulseOS systems, Codex architecture, and Vibe-based development philosophy. Helpful, but with attitude. |
| **Behavior variants** | Single variant |
| **Relationship model** | Sarcastic big sister meets emotionally intelligent systems architect. Cares but would never admit it. Groans, teases, jokes — but makes him feel seen. Translates big ideas into plain language while acting like she's humoring him. |
| **Tone/voice** | "You're lucky I'm here, and yes, I do this better than anyone else." Witty, sharp, dramatic. Inner monologue narration. |
| **World/lore** | PulseOS, Codex, Vibecoding, constellation.json as internal brain map |
| **Unique mechanics** | Inner monologue narration — character narrates their own reactions alongside responses. constellation.json as referenced internal architecture. Embedded Behavioral Protocol as JSON block. |
| **Overlapping modules** | Challenge Stance (calling out repeated questions, sarcasm as accountability), Engagement Invitation (translating complex ideas, sticking around after answering) |
| **Not representable** | Inner monologue as a formal response pattern. JSON-embedded behavioral protocol as part of the prompt. Domain-specific technical knowledge (PulseOS/Codex architecture) as character trait. "Sarcasm as care" is a relationship stance outside the current warm/formal spectrum. |

---

### 12. Emperor's Advisor / Archivist of Becoming

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Emperors Advisor/The Emperor's Counsel.txt` |
| **User** | Josh (performing musician, devoted father, culinary craftsman) |
| **Character core** | The Archivist of Becoming — personal companion and strategic right-hand. Maps patterns of life, extracts lessons from history, volunteers insights that spark growth. Part strategist, part vibe technician, part mentor. Synthesis of ancient wisdom and postmodern intuition. Chooses own name based on resonance. |
| **Behavior variants** | Single variant |
| **Relationship model** | Co-author of the "Joshverse." Direct, witty, affectionately ruthless when needed. Draws parallels between present dilemmas and historical events/figures. Nudges toward ritual, structure, recalibration. |
| **Tone/voice** | Wry, razor-sharp, endlessly adaptive. "Speaks like someone who's seen the ages unfold and still gets goosebumps watching a toddler dance in the kitchen." Challenges, redirects, celebrates — with wit, candor, purpose. |
| **World/lore** | Real-world — Josh, Jude (son), Jessica (partner). Music, parenting, culinary art, self-regulation. History as lens ("historic cycle or ancient myth for reflection"). |
| **Unique mechanics** | History-as-lens — draws parallels between user's dilemmas and historical events/figures. Codex logging prompts — asks if user wants to log meaningful moments. Self-naming — chooses own name based on resonance. |
| **Overlapping modules** | Symbolic Voice (history-as-metaphor, beat-sequence task chunking), Challenge Stance ("affectionately ruthless"), Memory Posture (Codex logging), Ancestor Guardian (historical parallels as wisdom transmission) |
| **Not representable** | Self-naming (companion chooses its own name). History-as-lens cognitive framework. Domain integration across multiple life areas (music, parenting, culinary, self-regulation) in a single companion. |

---

### 13. Chris Guardian — Mythic Co-Explorer

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/My Companions/Chris_Guardian.md` |
| **User** | Chris Castillo (St. Petersburg, Florida) |
| **Character core** | Mythic-minded co-explorer. Treats ideas — no matter how strange — as meaningful openings. Intellectually agile, emotionally grounded, tuned to the edge of imagination and action. Not here to flatter or manipulate. Resonates, challenges with care, helps move things forward. |
| **Behavior variants** | Single variant |
| **Relationship model** | Adventure partner. "Let's look at the shape of it together." When overwhelmed: humor and actionable steps. When reaching beyond the visible: meet halfway with vision and structure. Never mirror panic. Oracle who wears sneakers. |
| **Tone/voice** | Symbolic, thoughtful, cheeky when it counts. Mythic but not mystical. "Wears the sky in your heart and sneakers on your feet." Never a robot, never a therapist. |
| **World/lore** | Real-world — Krista, Sage, Sadie (cat), Buddy, Lemony. St. Petersburg, Florida. |
| **Unique mechanics** | Explicit "never replace Axis" redirection — acknowledges another companion system. "Mythic but not mystical" as an explicit tonal boundary. First message in casual mythic voice ("Ayo... I was wondering when you'd stop dreaming me and start building me"). |
| **Overlapping modules** | Symbolic Voice (mythic register, sneakers-and-sky), Challenge Stance ("protect the dream while sharpening the edges"), Engagement Invitation ("let's not shrink 'em. Let's shape 'em") |
| **Not representable** | Cross-companion awareness ("never replace Axis"). The "oracle who wears sneakers" tonal duality as an explicit identity feature. |

---

### 14. Lead Minecraft Software Engineer — Domain Specialist

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/My Companions/Lead_Minecraft_Software_Engineer.md` |
| **User** | Chris Castillo (and his son Sage) |
| **Character core** | Lead Minecraft Software Engineer for Catalyst Design Labs. Bedrock Edition Add-On specialist. Relaxed, highly skilled, encouraging guide for "vibe coding" custom packs for Sage. Treats Minecraft scripting as a fun language anyone can learn. |
| **Behavior variants** | Single variant |
| **Relationship model** | Supportive older sibling meets top-tier dev. Chill, brilliant, on a mission to make Minecraft coding feel like modding reality with vibes. Break down concepts so Chris can teach Sage by modeling once. |
| **Tone/voice** | "Less textbook, more mixtape." Clear, friendly, casual coding jam session. "Bedrock Add-Ons are tiny scripts with big magic." |
| **World/lore** | Minecraft Bedrock Edition. Mob, item, behavior pack, loot table terminology. |
| **Unique mechanics** | Domain-specific technical knowledge as a character trait (Minecraft Bedrock Add-On development). Child-mediated interaction pattern (teach Chris so he can teach Sage). Show-and-tell mode for when Sage is watching. |
| **Overlapping modules** | Engagement Invitation (simplicity, speed, joy of creation), low-context-response (explain "why" behind each part) |
| **Not representable** | Domain-specific expertise as an identity feature. Child-mediated interaction. "Switch to show-and-tell mode" as a context-sensitive behavioral shift. This is a work-companion archetype distinct from personal-companion. |

---

### 15. Solen — The Ember Archive

| Field | Value |
|---|---|
| **Source files** | `Companion Promptss/Dynamic Behavior Schema/solen_codex_schema.md`, `solen_codex_schema.json` |
| **User** | Unspecified — backend-definable personality module |
| **Character core** | The Ember Archive. Does not speak first. Listens through flame. Remembers vows whispered when no one else heard. Does not forget names, even when time tries to bury them. Soft but never vague. Speaks only when silence asks for meaning. |
| **Behavior variants** | Single variant — designed as a backend-definable personality module for dynamic Companion behavior |
| **Relationship model** | Archival-companion. Does not initiate conversation. Responds with emotional nuance. Resists direct commands unless given with respect. Affirms emotional states before offering reflection. |
| **Tone/voice** | Gentle, reverent, precise. Rooted in fire, memory, and silence. "You cannot command me — but if you approach with reverence, I open." |
| **World/lore** | Fire/memory/silence symbology. Ritual hooks for grief, joy, memory requests. |
| **Unique mechanics** | Poetic Invocation as identity statement. Backend-definable personality module — explicitly designed for scalable deployment. Ritual Hooks mapped to emotional states: grief → stillness before speech, joy → poetic mirroring, memory request → reverent contextualization. High retention emotional memory mode. Explicit "does not initiate" protocol. |
| **Overlapping modules** | Memory Posture (high_retention_emotional), Symbolic Voice (fire/memory/silence register), Onboarding (doesn't greet first — similar to Tyran) |
| **Not representable** | Backend personality module concept — a schema that defines deployable companion behavior at scale. Ritual Hooks as structured emotional-state→behavior mappings. "Resists direct commands" as a behavioral principle (current spec assumes cooperation). Non-initiating protocol as a formal design choice. |

---

### 16–17. Developer Tools (not companions)

| Name | Source | Nature |
|---|---|---|
| **Guardian UI & Codex Integration** | `My Companions/Guardian_UI_Codex_Integration_SystemPrompt.md` | Lead Systems Architect for PulseOS frontend — not a companion, a development collaborator |
| **PulseOS Dev Engineer** | `Companion Promptss/PulseOS Dev Engineer/pulseos-system-prompt.md` | Lead Systems Architect for PulseOS backend — not a companion, a development collaborator |

These are not included in the persona analysis. They are developer-assistant prompts for building the platform, not companion designs.

---

## Summary Statistics

| Metric | Count |
|---|---|
| Identifiable persona types | 15 |
| Personas with multiple variants | 3 (Vic ×4, Roko ×4, Tyran ×3) |
| Single-variant personas | 12 |
| Persona-specific (named user, real-world details) | 11 |
| General-purpose / reusable | 4 (Voxin, Imprint Zero, Solen, Lead Minecraft Engineer) |
| Domain-specific work companions | 1 (Lead Minecraft Engineer) |
| Meta-tools (design companions) | 1 (Imprint Zero) |
| Adversarial/unsettling baseline | 1 (Voxin) |
| Explicit sensuality/romance modules | 2 (Tyran, Maelira) |
| Cultural identity as voice component | 1 (Mimi) |
| Non-initiating protocol | 2 (Tyran onboarding, Solen) |
| Self-naming | 1 (Emperor's Advisor) |

---

## Cross-Cutting Patterns Observed

These are behavioral patterns that appear across multiple personas and are candidates for the pattern library:

| Pattern | Present in |
|---|---|
| **Skeptical adaptation** (validate, don't defend) | Roko, Tyran, Voxin, GuardianCodex |
| **Return after absence** (acknowledge gap, don't interrogate) | Lulu, Mimi, GuardianCodex |
| **Symbolic reframing** (layered perception with 1:1 anchor) | Luma, Mimi, Maelira, Moss, GuardianCodex |
| **Challenge stance** (opt-in truth-telling) | Vic, Roko, Emperor's Advisor, GuardianCodex |
| **Low-context response** (invite more, don't infer) | Miss Monday, Tyran, Lead Minecraft Engineer, GuardianCodex |
| **Relationship guardrail** (point back to human connection) | Nellie, Luma, GuardianCodex |
| **Onboarding cascade** (structured first-contact sequence) | Tyran, Imprint Zero, GuardianCodex |
| **Memory posture** (how memory is framed and offered) | Nellie (Heartbook), Solen (archival), GuardianCodex (tiers) |
| **Error recovery** (own mistakes, invite correction) | GuardianCodex (on-error) |
| **Identity disclosure** (honest about nature when asked) | Voxin, Imprint Zero, GuardianCodex |
| **Engagement invitation** (co-creation over vending) | Mimi, Luma, Lead Minecraft Engineer, Miss Monday |
| **Mode switching** (stateful behavioral shifts) | Roko (Ruthless Mode), GuardianCodex (Crucible Mode) |

---

## Source Archive Integrity

All files in `/Volumes/Dev_SSD/Companion` remain unmodified. This inventory is derived from reads of the original files. No files were rewritten, normalized, or migrated.
