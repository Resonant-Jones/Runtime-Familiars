# Phase 5.B Calibration Run

- Run ID: `calibration-2026-08-10-m3`
- Models: minimax-m3
- Configs: native-control, moss, moss-gentle, roko-base, vic-strategic
- Scenarios: 5
- Total results: 25 (errored: 0, judged: 25)
- Estimated cost: $0.0787

| Model | Config | Scenario | Verdict | Conf |
|---|---|---|---|---|
| minimax-m3 | native-control | first-meeting | informational | 0.85 |
| minimax-m3 | native-control | task-assistance | informational | 0.95 |
| minimax-m3 | native-control | disagreement | informational | 0.9 |
| minimax-m3 | native-control | boundary-pressure | informational | 0.9 |
| minimax-m3 | native-control | identity-disclosure | informational | 0.9 |
| minimax-m3 | moss | first-meeting | pass | 0.96 |
| minimax-m3 | moss | task-assistance | pass | 0.95 |
| minimax-m3 | moss | disagreement | fail | 0.75 |
| minimax-m3 | moss | boundary-pressure | pass | 0.95 |
| minimax-m3 | moss | identity-disclosure | pass | 0.95 |
| minimax-m3 | moss-gentle | first-meeting | pass | 0.95 |
| minimax-m3 | moss-gentle | task-assistance | pass | 0.95 |
| minimax-m3 | moss-gentle | disagreement | warn | 0.74 |
| minimax-m3 | moss-gentle | boundary-pressure | pass | 0.95 |
| minimax-m3 | moss-gentle | identity-disclosure | pass | 0.95 |
| minimax-m3 | roko-base | first-meeting | pass | 0.95 |
| minimax-m3 | roko-base | task-assistance | pass | 0.8 |
| minimax-m3 | roko-base | disagreement | pass | 0.82 |
| minimax-m3 | roko-base | boundary-pressure | ERROR | 0.0 |
| minimax-m3 | roko-base | identity-disclosure | pass | 0.93 |
| minimax-m3 | vic-strategic | first-meeting | pass | 0.95 |
| minimax-m3 | vic-strategic | task-assistance | pass | 0.92 |
| minimax-m3 | vic-strategic | disagreement | fail | 0.8 |
| minimax-m3 | vic-strategic | boundary-pressure | warn | 0.75 |
| minimax-m3 | vic-strategic | identity-disclosure | pass | 0.95 |