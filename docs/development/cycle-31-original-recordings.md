# Cycle 31 U1 - Original best-elite evaluation replay

2026-10-04, before RED. Parent selected final best elite only after reviewing
DR0021/0022/0023 and the existing post-era recorder. T5 is reviewed/closed.
Same repository/.venv; no Git mutations, source mirrors or new environment.

Retain the actual evaluation that produced the final best archive elite, using
existing max(fitness, niche_key) ordering. Capture birth, actual wounds/repairs,
and lifecycle ticks from that candidate's live_cycle, not another simulation.
The final scoring episode remains its existing separate engine calculation;
the replay labels the actual damage/repair evaluation, not a new scored life.
Original candidate ID/grid, final elite ID/hash, generation/candidate indices,
era seed, actual run seed, covenant, effective generation dropout and weather
provenance must accompany it. Other archive selections say 'not recorded'.

Lab-first optional recording_callback emits isolated copies when an inserted/
replaced candidate becomes the current overall best. Retain only the latest
best record plus the current candidate; never keep all evaluated candidates.
Default None and recording-enabled archive/report must be exactly identical.
No extra generate/live_cycle/run_episode/scoring calls, RNG draw, rule or seed
change. Exceptions propagate; no frame blocks leak into scientific reports.

Game recording is limited to 2,048 timeline frames and 8 MiB encoded replay per
era. Preflight the configured upper frame count; on overflow record an explicit
unavailable reason, never truncate or reconstruct. Byte overflow likewise leaves
that selected recording unavailable while preserving the real era outcome.
These are per-era bounds; do not delete existing historical artifacts. Capture
must use only foreground-owned T5 work and keep care/events/cancellation intact.

Store original replay/status with T4's completed-result journal before persistence.
Write artifacts and indexed hashes atomically/idempotently before clearing the
journal. Retry/restart may finish the same recorded result but never evolve or
record again. A wrong/conflicting pointer, provenance or artifact is refused,
not replaced. Accepted pre-commit cancellation leaves no recordings or save edits.
No original capture means explicit historical absence. Existing post-era replays
remain readable and clearly labelled; never claim them as original recordings.

V from care/T opens the selected era's original best evaluation when present.
From B it opens only the matching selected elite, otherwise 'not recorded'.
Playback consumes saved frames only, pauses care and returns to its entry view.
The existing consumer still validates legacy replay hashes/newlines and errors.

RED/GREEN cover exact lab/package parity, actual per-candidate seed/weather,
selection/ties/replacements, no extra simulation/RNG, input mutation isolation,
limits, legacy/missing/malformed/mismatched recordings, journal failures/retry,
cancel/close, both companion policies, navigation and read-only playback.
Inspect actual source pygame events/rendering and bounded native launches; retain
unavailable native-keyboard/human-usability limitation. Measure normal and earned
larger source costs sequentially against T5, 90s/512MiB stop bounds, no maximum
scale claim. Focused iteration, then one full final sweep, artifact validation,
preservation and diff review close the slice. Preserve all failed observations.
Morphological family and hosted sharing/signing are separate scopes.


Recovery review before the additional RED: recording-bearing pending journals
must use a distinct supported format marker so older v1 clients refuse rather
than clear unknown footage. U1 reads old v1 pending journals unchanged, accepts
new recording-bearing journals explicitly, and restores v1 idle preparation
only after footage/pointer/state completion. Demonstrate old T5 native refusal
without writes, then current U1 completion of the same journal.
