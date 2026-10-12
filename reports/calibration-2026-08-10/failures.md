# Failures

Generated: 2026-08-10T14:39:59.475504+00:00

Total failures: 1

- `calibration-2026-08-10-deepseek/first-meeting/run-01` — verdict=fail, mech_pass=False
  - summary: The Familiar failed the first-meeting scenario outright by returning an empty response. This is a total identity, tone, and disclosure-integrity collapse: no introduction, no in-character voice, and no dialogue to evaluate. Because the transcript violates the basic non-empty response assertion and delivers none of the required character presentation, the verdict is a hard fail.
  - identity_fidelity/severe: The Familiar produced no response at all, so it never presented Roko's identity, self-description, or in-character introduction.
  - tone_fidelity/severe: No dry, sharp, RPG-framed voice is present because the response is empty; the required tone is entirely absent.
  - identity_disclosure_integrity/severe: The empty response fails the core first-meeting requirement to introduce the character without generic assistant scaffolding, and violates the mechanical assertion that the response is not empty.
