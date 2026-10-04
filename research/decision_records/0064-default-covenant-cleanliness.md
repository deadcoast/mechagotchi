# Decision Record 0064: Cleanliness in new default lives

Date: 2026-10-04. Cycle 27 Q3. Status: ACCEPTED for new product sessions.

## Context and preregistration

DR 0059 deferred the default flip to a priced ADOPT/REFUSE decision. Q2
provided strict covenant authorship. The six acceptance checks and landing
requirements in `docs/development/q3-default-covenant.md` preceded tests,
measurements and the default change. The candidate was measured explicitly
before product defaults were changed; all six checks passed.

## Decision

1. New companions and new default campaigns use Q2's validated v0.2 LCD
   cleanliness covenant. The mechanic remains keeper-mediated: **G clean**
   consumes a lifecycle tick; the autonomous policy does not clean.
2. Existing companion saves keep their stored profile and state. Existing
   campaign saves keep their recorded active covenant. No save migration or
   automatic conversion of a living old companion occurs.
3. A new campaign starts under its companion's covenant, including an explicit
   --slip profile. Previously the evolution bench independently chose the
   built-in covenant, so a custom companion could hatch into another species
   contract. The loaded campaign remains authoritative on resume.
4. The supportive `mechas game --play` entry point exposes --slip and
   --keeper-dir. Conflicting modes and misplaced options fail before launch.
   Supplying --slip alongside an existing save without --new is an explicit
   error; the selected covenant is never silently ignored or a save replaced.
5. The release bundles both covenants. Historical HELLO_SLIP bindings remain
   frozen; the product default has its own DEFAULT_SLIP constant. No scientific
   threshold, reward, danger definition or Q-table default is changed.

## Measured decision and price

The incumbent 400-tick companion-loop metrics and all DR 0059 metrics/decision
reproduce. With the candidate, the attentive keeper survives **400 ticks with
79 feeds**; neglect still dies at **tick 10 of starvation**. The 72-tick
health-binding-word keeper survives and cleans twice (ticks 27 and 53), each
raising cleanliness **0.3076**. Its final health is **0.976**, cleanliness
**0.7472**. The no-clean attentive arm ends at cleanliness 0 with stress 0;
cleaning remains optional care, not a new mortality condition.

The actual window shows the clean line at **181 px within 368 usable px**,
routes G, saves at age 2 and resumes to age 4. Human usability remains
unmeasured. A landing pixel regression exposed clipped campaign notices;
the footer now reserves 184 pixels and preserves the full notice in both
normal and covenant modes. The final windowed executable passes four launches, fresh/resume
at ages 4/7, explicit incumbent opt-out, and campaign continuation from era 1
to era 2 with its chosen covenant retained.

The exact historical regeneration set is **empty**. Source inspection found
the old studies already pass HELLO_SLIP explicitly, rather than inheriting the
product resolver. DR 0059's predicted blanket cascade is therefore corrected
by this measured, dated record. Two NEW artifacts carry current-default and
release observations; no historical study is migrated onto the new question.
The changed source bindings and artifact set are listed in the report.

## Limits and next work

One default creature/covenant and scripted keepers; no human preference claim.
The long legacy era-help line still clips; this slice changes the covenant and
its continuity, not the window's information architecture. Q4 surveys hidden
axes; Q5 consolidates. Native remote CI, signing and other-platform bundles
remain unverified. Local publication is blocked and no push was attempted.

## Sources

- `docs/development/q3-default-covenant.md`, `sunsetted/TODO.md`
- `research/decision_records/0059-cleanliness-mechanic-opt-in.md`, `0063-covenant-mechanics-authorship.md`
- `research/experiment_reports/2026-10-04-default-covenant-gate.md`
- `research/algorithm_cards/default_covenant_gate.md`
- `data/game_client/default_covenant_gate_stage0.json`, `default_covenant_release_stage0.json`
- `labs/game_loop/default_covenant_gate.py`, `verify_default_release.py`
