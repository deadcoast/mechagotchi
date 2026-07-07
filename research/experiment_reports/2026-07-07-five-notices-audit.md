# Experiment Report: The Five Player-Notices Audit (E5) — The Living-Ecosystem Claim, Verified

Date: 2026-07-07

## WHY

DR 0021 §a.4 named five felt phenomena, each mapped to a shipped
mechanism — the game's living-ecosystem claim. After cycles 02–05
changed nearly every surface, E5 audits each notice end to end: is it
reachable and player-visible at a REAL surface today? Close what can be
closed; record what can't, honestly.

## The five verdicts

**1. "The weather changes the world" — SHIPPED & VISIBLE (+ provenance
closed this audit).** Forecasts measurably move the soup (storm 1.17x /
stable 0.90x, 58 vs 65 cells at the same seed) and the era cards show
the wreckage and the survived multiplier. Gap closed here: the cards
now cite the CuBFF snapshot provenance the notice promised (snapshot
count on the soup line; the full id list as its tooltip).

**2. "Creatures visibly think" — MECHANISM SHIPPED; TRACE NOT
PLAYER-VISIBLE (the audit's found gap, seeded).** Deliberation is real:
the covenant spends into `deliberation.max_ticks` (C4), and the
confidence-gated CTM loop genuinely changes decisions (R1,
parity-pinned). But `choose_action` returns only the action STRING —
the `deliberation.tick_count` record is computed inside the switchboard
decision and discarded before episode history, so no replay or page can
render a thinking pause. Closing this means threading the deliberation
record into the episode history entries — a parity-pinned history-shape
change (the "engine grows the number first" path) — plus a scrubber
readout. RECORDED AS THE NEXT CYCLE'S SEED, not silently skipped.

**3. "The species becomes easier to read" — SHIPPED & VISIBLE;
DIRECTION CORRECTED BY MEASUREMENT.** The learned model steers every
era (C1) and legibility shows on every era card. The measured truth:
at Stage-0 scale legibility DRIFTS DOWN across chained eras (0.401 →
0.014, C1's finding) — the mechanism the notice promised is live and
visible; the optimistic wording yields to the measurement, and the
drift itself is a real dynamic the Keeper watches.

**4. "Your creature's blood persists" — GAP FOUND AND CLOSED THIS
AUDIT.** The inspector's ancestry browsing shipped in cycle 01 — but
the Keeper SESSION never admitted workshop releases: DR 0021's
Contribute step ("released creatures enter the next era as founders")
was wired into the preview/lab loop only. Closed: `advance_campaign`
gains `released_grids` (releases LEAD the founder pool ahead of the
prior era's elites — the T1/DR 0016 founders-lead rule; admissions and
verbatim rejections recorded in the era report), `advance_keeper_state`
gains `released_dir`, the workshop server passes its real released
directory, and the lab CLI gains `--released-dir`. Pinned by tests:
admitted-release-leads, broken-release-rejected-verbatim, releases
ahead of elites in era 2+, `None` byte-identical, and the server flow
test now releases a creature and founds a storm era with it.

**5. "Absence hurts" — SHIPPED, WITH THE HONEST READING RECORDED.**
Persistence (state + SQLite ledger + replay files) and the Review step
(per-era recorded replays on the Keeper page) ship: returning, the
Keeper sees exactly what the bloodline endured, deterministically
reproducible from stored seeds. The "soup simmered while away" phrasing
is FRAMING — eras run when the Keeper runs them; no background
simulation exists, and none should (the engine's determinism is the
game's spine). The notice's substance ships; its metaphor is read
honestly.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/game_loop -p "test_*.py"
Ran 68 tests in 9.006s
OK

PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
OK    # the flow test now releases a creature, founds a storm era with
      # it (founders_admitted 1, parent_source founders_plus_seed_pool),
      # and the Keeper test server is isolated from the repo's live
      # releases (its own temp released_dir)
```

## Decision

Adopt — E5 developed to its description: every notice audited at its
real surface; two gaps found; one (the Contribute step) closed with the
full gate set, one (the deliberation trace) recorded as the next
cycle's seed with its exact engineering path named. Four of five
notices are fully live; the fifth thinks but cannot yet be seen
thinking.

## Sources

- `research/decision_records/0021-game-loop.md` (§ the five notices; step 3)
- `research/decision_records/0016-evolve-founder-grids.md` (founders-lead)
- `research/experiment_reports/2026-07-07-readability-selection-promotion.md` (notice 3's measured direction)
- `packages/mecha_engine/src/mecha_engine/lifecycle/_policy.py` (notice 2: the discarded decision record)
- `labs/game_loop/session_runner.py` (+ `test_session_runner.py`)
- `workshop/server/workshop_server.py`, `workshop/session/session.html`
- `workshop/tests/test_workshop_server.py`
