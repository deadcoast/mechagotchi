# Experiment Report: The Keeper/Era Loop in the Client (Cycle 14 · GAME · F4)

Date: 2026-07-12

## WHY

DR 0021 is the game's governing design: the player is a Keeper whose
bloodline evolves inside a soup they steward — eras (evolve runs)
chained by founder elites, progression as unlock FACTS earned from
engine metrics, roguelite extinction stakes, and species memory the
player can hold. The G2/G4 session lab proved every semantic
lab-side; F4 puts the loop in the LAUNCHABLE client.

## WHAT

**One engine export first (RED-first, additive):**
`mecha_engine.runtime.learned_readability_score` — the DR 0025
verbatim port already scoring the readability-selection path
internally, exported so `evolve`'s injected `readability_scorer` hook
can be the SAME learned signal in consumers (a client must never
re-implement an engine number). Spec section + contract pin updated
together; pinned by `test_runtime_readability_surface.py`
(subprocess-probe convention); package suite 295 green.

**`game/src/mecha_game/campaign.py`** — the session lab's semantics
mirrored over engine publics only (`evolve`,
`train_generation_model`, `train_repair_model`,
`learned_readability_score`, the `storage` ledger): one era = one
promoted evolve run at the A4-calibrated session scale (6×16); era
seeds at the lab's stride; founders = the previous era's elites in
niche-key order (records spread verbatim); the unlock table mirrored
as tuning data with the lab's exact rule (met must unlock, unmet must
not, earned never re-earned — falsifiable by test); the earned
legibility blend; synthetic weather verbatim (real CuBFF drops into
the same seam at Phase G); extinction → `successor()` carrying only
the unlocks at the disjoint seed band; persistence through
`open_ledger`/`record_campaign`/`record_era` (blob-authoritative,
idempotent re-save). One DOCUMENTED divergence: the game injects the
LEARNED readability scorer as the evolve hook (DR 0019 primary; the
lab session used the historical proxy) — recorded here, not smuggled.

**The client's era bench** (`app.py`): lazily trained on first use
(model training never taxes pure companion play); **E** runs an era
under the selected forecast (**1/2/3** = calm/stable/storm), the
footer shows the era's species memory verbatim (niches, qd, elites,
unlock count, extinction), and **A adopts the era's best elite as the
companion** — through the same engine adoption gate, the two loops
joined: the pet comes from the evolving bloodline. `--eras N
--era-scale tiny|session` run the bench headless for verification.

**Measured** (`data/game_client/keeper_campaign_stage0.json`, status
complete, SESSION scale): a calm→stable→storm campaign ran 3 eras and
SURVIVED; **nine unlock facts earned across all five axes**
(niche_mastery to tier 3, quality_diversity tier 2, legibility
tier 2, bloodline_depth 1, storm_record 1 — each fact citing metric
path/value/threshold); founders chained verbatim; the first era
twin-run byte-equal; the best elite adoptable; the ledger
round-trips losslessly (report blobs equal). 79 game tests; a real
window ran an era and exited 0.

## Verification

```powershell
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_runtime_readability_surface.py"
Ran 0 tests ... FAILED (errors=1)   # RED: not exported
# after export + spec + pin:
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 295 tests ... OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 79 tests in 4.533s
OK
PS> uv run python -B game/evidence.py   # five artifacts, statuses complete
PS> uv run python -B game/run_game.py --ticks 6 --eras 1 --era-scale tiny --keeper-dir <tmp>   # exit 0
```

(The campaign mirror's pure tests were written in the same change as
the module — the session lab is their behavioral spec; the engine
export followed strict RED-first.)

## HONEST REMAINDER

1. **The Review step shows summary metrics, not the replay** — the R5
   scrubber remains the named consumer for era replays (G3); the lab
   records them, the client does not yet.
2. **DR 0021's Contribute step (workshop releases as founders)** waits
   for the client↔workshop bridge; the engine seam (`founder_grids`)
   is already consumed by the era chain.
3. **The archive scale-geometry seam was NOT demanded** by this
   consumer (the client's eras run the A4 session scale) — recorded
   per the Phase-E remainder; it stays unpromoted.
4. **Covenant editing (the SLIP budget spend) is not in the client** —
   unlock facts are earned and shown; spending them into the covenant
   is the next era-loop rung (the lab's `covenant_budget` is the
   proven source).
5. **Era pacing**: session-scale model training (~6 s) is lazy;
   an era is ~1–2 s of blocking run — acceptable at MVP 0.1, a
   progress animation is F5+ polish.

## Sources

- `audits/TODO.md` (cycle 14 F4), `research/decision_records/0021-game-loop.md` (the design input)
- `labs/game_loop/session_runner.py` (the mirrored semantics), `research/decision_records/0022-storage-module.md` (the ledger)
- `research/package_specs/mecha_engine_runtime_interface_spec.md` (the additive scoring surface)
- `packages/mecha_engine/src/mecha_engine/runtime/__init__.py`, `packages/mecha_engine/tests/test_runtime_readability_surface.py`
- `game/src/mecha_game/campaign.py` (+ `game/tests/test_campaign.py`), `game/src/mecha_game/app.py`
- `data/game_client/keeper_campaign_stage0.json` (evidence)
