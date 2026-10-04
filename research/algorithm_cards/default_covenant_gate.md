# Default covenant adoption

## Name

Q3 / DR 0064: measured default cleanliness and covenant continuity.

## Purpose

Give new players the adopted clean mechanic while keeping old lives and
historical evidence attached to their original covenants.

## Mathematical basis

ADOPT is the conjunction of six preregistered checks; false or missing checks
REFUSE. The 400-tick attentive and tick-10 neglect constraints come from the
committed companion-loop artifact. The 72-tick scripted keeper cleans when
cleanliness <= 1 - CLEANLINESS_CLEAN_RESTORE; no post-run tuning occurs.
Behavior and statistical definitions remain those of DR 0059.

## Inputs

Default 16x16 beetle, incumbent and v0.2 candidate profiles, committed loop and
mechanic metrics, engine health binding word, actual client and built bundle.

## Outputs

ADOPT/REFUSE, exact scripted observations, an enumerated artifact plan, and
separate observed native-release results.

## Strengths

Checks the instrument first. Judges the candidate before changing defaults.
Tests real event routing and frozen executable save/campaign continuation.
Separates product defaults from explicitly named experimental inputs.

## Weaknesses

One species and scripted keepers; geometry and key routing are not a human
usability study. Bundle hashes/sizes are host observations, not portable pins.

## Failure modes

Silent profile replacement on resume, a campaign choosing another covenant,
an omitted bundled profile, historical studies inheriting a moving default,
or an unreadable clean control despite a correct engine state.

## Integration risk

New lives gain an optional care tick and bounded dirt-to-stress pressure.
Existing lives keep their covenant. Explicit --slip plus an existing save now
fails unless --new is supplied; this prevents silently ignoring user intent.

## License status

Existing project/package policy; no new dependency. Uses the declared game
and lab groups and the existing PyInstaller release builder.

## Prototype result

ADOPT: attentive 400 ticks / 79 feeds; neglect tick-10 starvation unchanged;
scripted care 72 ticks / two cleans / health 0.976; real window and native
bundle continuity pass. Zero historical artifacts regenerated.

## Decision

Adopt the default for new product lives; preserve existing stored covenants.

## Go-No-Go gate

All six acceptance checks, landing regressions, actual bundle observations,
full local sweep and source-preservation audit. Remote CI remains independent.

## Sources

- `research/decision_records/0064-default-covenant-cleanliness.md`
- `docs/development/q3-default-covenant.md`
- `labs/game_loop/default_covenant_gate.py`, `verify_default_release.py`
- `data/game_client/default_covenant_gate_stage0.json`, `default_covenant_release_stage0.json`
