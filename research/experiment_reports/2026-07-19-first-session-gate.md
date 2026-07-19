# Experiment Report: The ≤45-Minute First-Session Gate — Measured Honestly (Cycle 18 · WORKSHOP · H5)

Date: 2026-07-19

## WHY

The gap table's Workshop row ends with the documented UX goal:
*"≤45-min first-session creature+SLIP."* Phases H1–H4 built the
authoring depth; H5 asks whether a first session can actually travel
it — blank state to a released, shareable creature with its own
species contract — and answers with the calibration pattern's honesty:
a scripted pass proves the path and is LABELED a proxy; the human pass
is prepared and recorded as not blocking.

## WHAT

**`workshop/protocols/first_session_protocol.py`** drives the REAL
workshop server (its own temp instance, real HTTP) through the whole
documented journey, timing every step:

1. **open_the_workshop** — both authoring pages serve, carrying the
   Phase-H depth (the editor's animation panel; the slip creator's
   deliberation panel).
2. **first_marks_and_first_refusal** — a draft with its anchor erased
   meets the engine; the validator's words (recorded verbatim in the
   evidence) are the teaching moment.
3. **author_the_creature** — the finished 16×16 moth passes.
4. **author_the_species_slip** — a 0.2.0 species with deliberation
   (max_ticks 3, the engine's 0.72 gate) accepted by the authority
   and saved.
5. **save_the_creature** — the layered save (H2's sidecar).
6. **see_it_move** — the timeline scrub over the unsaved draft; the
   ill clip visibly moves (H3).
7. **release_into_the_ecosystem** — release-time re-validation + the
   lineage mark.
8. **share_it** — the APNG export carries the scrubbed clip's four
   frames (H3's rung), bound to the just-authored profile.

**Measured (committed artifact `data/workshop/first_session_stage0.json`):**
8/8 steps ok, 10 interactions, **6.99 s scripted total vs the 2700 s
bound** — `scripted_proxy: true` in the artifact, because that number
proves the path, not the human. The **human pass** rides the artifact
as an 8-step protocol, `prepared: true, blocking: false`, and the
report's `blocked_states` names it — the exact shape the calibration
deferral set (a manual measure is never a blocker).

## Verification

```powershell
PS> python -B -m unittest discover -s workshop/tests -p "test_first_session_protocol.py"
FAILED (errors=1)   # RED: No module named 'first_session_protocol'
# after implementation:
Ran 6 tests ... OK
PS> python -B workshop/protocols/first_session_protocol.py
"status": "complete", "total_elapsed_seconds": 6.9927, "under_bound": true,
"interaction_count": 10, "step_count": 8
```

## HONEST REMAINDER

1. **The scripted time is not the goal's measure** — it proves
   existence and counts interactions; only the prepared human pass can
   judge 45 minutes for real. It stays prepared-not-blocking.
2. **The protocol scripts one canonical journey** — detours (imports,
   Aseprite, the preview pages) are covered by their own suites, not
   timed here.
3. The artifact records wall-clock as a per-run observation; the tests
   pin the BOUND, never the exact seconds (H-01 discipline).

## Sources

- `audits/TODO.md` (cycle 18 H5), the gap table's Workshop row
- `workshop/protocols/first_session_protocol.py` + `workshop/tests/test_first_session_protocol.py`
- `data/workshop/first_session_stage0.json` (the committed measurement)
- `research/experiment_reports/2026-07-12-semantic-layers.md`, `2026-07-19-onion-skin-timeline.md`, `2026-07-19-behavior-editor.md` (the depth this journey travels)
