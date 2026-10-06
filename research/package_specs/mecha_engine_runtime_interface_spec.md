# Mecha Engine Runtime Module Interface Spec

Date: 2026-07-05

## Status

Contract reference for `mecha_engine.runtime` (decision record 0008,
**accepted 2026-07-05**). Evidence basis: the runtime integration lab's
two composed-loop artifacts, both green (`runtime_loop_composed`,
`evolution_loop_composed`).

## Why a runtime surface

Six modules are promoted and proven to compose, but composition knowledge
currently lives only in a research lab. A runtime module gives the engine
one supported entry point — the surface the future product (and the
mecha_workshop tooling) builds on — encoding the integration lessons the
lab discovered executable-first:

1. Repair must run SLIP-aware (the alignment seam).
2. Parents are selected from the profile-aligned pool (generation rejects
   profile-incompatible parents).
3. Grid ids are reassigned per damage/repair cycle (64-char cap).
4. A stochastic damage event may destroy zero cells (no-op repair is
   legal).
5. Readability is an injected, visibly-uncalibrated input.

## Proposed public surface

- `live_cycle(grid, slip_profile, repair_model, *, damage_cycles=3,
  ticks=72, dropout_rate=0.2, rng_seed=20260512) -> dict`
  One creature's life under fire: per cycle, a seeded damage event
  (private synthesizer, `removed_cells` reported per the repair
  observability contract), SLIP-aware wound-site repair, and a full
  lifecycle episode. Returns per-cycle digests (removed cells,
  restoration fidelity, guard substitutions, validity, alignment,
  episode) plus a final-state digest. Deterministic; inputs never
  mutated. Injected damage events (a future gameplay source) replace the
  synthesizer via an optional `damage_events` parameter without changing
  cycle semantics.
- `evolve(seed_grids, slip_profile, generation_model, repair_model, *,
  readability_scorer, generations=4, population=8, damage_cycles=3,
  ticks=72, dropout_rate=0.2, rng_seed=20260512) -> (archive, report)`
  Generation 0 parents from the profile-aligned subset of `seed_grids`;
  later parents from archive elites sorted by niche key; every creature
  goes through the live-cycle semantics, then scores and inserts through
  `mecha_engine.archive`. Readability is injected via
  `readability_scorer` (a deterministic callable, the "equivalent
  metrics hook" — no proxy scorer is ported; the record's
  manual-rating status stays visible in every score). Signature
  amendment vs the proposal draft, documented here: `seed_grids` and the
  callable form of the readability hook are required for the evolution
  semantics to be reproducible.

### The learned-readability scoring surface (additive, cycle 14 F4)

- `learned_readability_score(grid, model) -> float` — the DR 0025
  verbatim port (`runtime/_readability.py`, already scoring the
  promoted readability-selection path internally), exported so a
  consumer can inject the SAME learned signal as `evolve`'s
  `readability_scorer` hook. The consumer is the GAME's Keeper/era
  loop (a client must never re-implement an engine number — DR 0021's
  first law); the model argument is the caller's weights dict (the
  committed adopted artifact,
  `data/readability_benchmark/adopted_readability_model.json`, is the
  primary source per DR 0019). Export only; zero behavior change;
  pinned by `tests/test_runtime_readability_surface.py`.

## Hard gates for the port

- Lab-parity pin: reproduce the evolution-loop artifact through the
  package surface over the same seeds — summary equal (32/32, 96 damage
  events, retention 1.0, 15 niches, QD 13.92, fitness-by-generation list
  equal) and per-creature cycle records equal, with the lab's proxy
  readability injected as the scorer. (Amendment vs the proposal draft:
  the single-generation artifact keeps the lab as its harness — its
  pre/post-episode shape is the integration record, not a runtime
  surface — the evolution artifact subsumes the composition claim.)
- Deterministic end to end; JSON-serializable reports; no input
  mutation.
- Stdlib-only; imports only `mecha_engine.*`; no `labs`, no `sys.path`
  (boundary scan).
- The observability and no-template contracts of `repair` pass through
  unchanged; `target_template_used == false` everywhere.
- Zero-cell damage events are handled as no-op repairs (measured lab
  behavior).
- Known non-goal for the first port: lineage-counter accumulation
  through repair (parity-reviewed follow-up; ancestry truth is the
  parent-id chain).

## Non-goals

- No gameplay/UI; the runtime returns data, not frames.
- No readability scorer; no calibration claims (owner-deferred data).
- No new learning surfaces (the `learning` module remains its own
  roadmap item with its own decision record).

## Sources

- `research/decision_records/0008-propose-mecha-engine-runtime-target.md`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `data/runtime_integration/mecha_engine_runtime_loop_stage0.json`
- `data/runtime_integration/mecha_engine_evolution_loop_stage0.json`
- `research/experiment_reports/2026-07-05-mecha-engine-runtime-loop.md`
- `research/experiment_reports/2026-07-05-mecha-engine-evolution-loop.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_repair_interface_spec.md`

## founder_grids (decision record 0016, 2026-07-06)

`evolve` accepts keyword-only `founder_grids: list[dict] | None =
None`: released creatures admitted through the engine's own gates
(validate_grid + SLIP alignment, rejections verbatim in the report's
`founders` block); admitted founders LEAD the generation-0 pool
(`parent_source: founders_plus_seed_pool`). `None` is byte-identical
to the pre-0016 contract (parity pins unmodified).

## Validity gate on episodes (promotion-drift fix, 2026-07-07)

The lab loop has gated cycle episodes on `valid AND aligned` since T1
(commit d382805): an aligned-but-invalid repair (e.g. a disconnected
body core under heavy damage) carries no episode, the creature records
`archive_decision: skipped_invalid`, and scoring requires
`all_cycles_valid AND all_cycles_aligned` with a final-cycle episode.
The first port pre-dated that gate — `live_cycle` ran episodes for any
aligned repair and crashed lifecycle simulation at the measured
boundary (probe 2026-07-07: rng_seed 20260703, dropout 0.95, 4 cycles;
found while building the G2 session runner). The package is synced to
the lab's verbatim semantics; pinned-seed parity artifacts are
byte-identical (no pinned seed produces an invalid repair). Pins:
`labs/runtime_integration/test_invalid_repair_semantics.py` (lab-package
boundary parity) and the `invalid_repair_boundary` probe in
`tests/helpers/runtime_contract_driver.py`.

## record_frames (decision record 0023, 2026-07-07)

`live_cycle` accepts keyword-only `record_frames: bool = False` — the
replay recorder's engine seam (R5). When true, each cycle dict
additionally carries a `frames` block: the wound's `removed_cells`
(verbatim from the damage event's observability contract), the
`repaired_grid`, and the full per-tick `episode_history` (`None` when
the cycle ran no episode). Default `False` is byte-identical to the
pre-0023 contract (contract probe `record_frames_off_equals_stripped_on`
plus the frozen parity pins, unmodified).

## readability_selection (decision record 0025, 2026-07-07)

`evolve` accepts keyword-only `readability_selection: dict | None =
None` — R3's live consumer promoted (DR 0019's learned model as the
PRIMARY readability signal). The arm carries the learned model
(`weights`, `reference_features`, `blend`, default 0.5); elite parents
are ranked by `blend * learned_readability + (1 - blend) *
min-max-normalized fitness` (lab-verbatim ordering, `parent_source:
archive_elites_readability_blend`), taking precedence over
`lineage_preferences` exactly as in the lab loop. The report gains a
rung-conditional `readability_selection` block (authority string,
blend, weights, reference features, per-generation mean learned
readability over candidates). Scoring runs through the verbatim
`runtime/_readability.py` mirror (the `_cubff`/`_damage` private-copy
rule; drift guard `labs/readability_benchmark/
test_package_readability_parity.py`). `None` is byte-identical (frozen
pins unmodified); a weightless arm raises `ValueError`. The manual
rating system remains the fallback and calibration check. Pins:
`labs/runtime_integration/test_readability_selection_parity.py`
(record-for-record lab parity + the promoted-surface A/B) and the
`readability_selection` probe in the contract driver.

## Observational evolution progress (DR 0073, 2026-10-04)

`evolve` additionally accepts keyword-only
`progress_callback: Callable[[int, int], None] | None = None`. A supplied
observer receives `(0, generations * population)` before evaluation, then
`(completed_candidates, requested_candidate_budget)` after each fully recorded
candidate. Values are integers; no mutable engine state is exposed. Exceptions
propagate for caller-owned cancellation. An extinct archive may end below the
budget. No completion percentage, wall-clock estimate or callback data enters
the report. None and observational callbacks preserve complete seeded outputs.

The authoritative lab proved this before promotion.
`labs/runtime_integration/test_evolution_progress.py` pins full off/on equality,
lab/package records and counts, propagated cancellation, input preservation and
early extinction. Existing contract signature assertions include the additive
default-off argument; no scientific threshold changes. The application owns
threading, rendering, cancellation policy and its persistence boundary.


## Original evaluation observation (DR 0074, 2026-10-04)

`evolve` accepts optional keyword-only `recording_callback=None`. An inserted or
replaced candidate that is now best by the existing `(fitness, niche_key)` order
emits one isolated mapping: original candidate grid, actual `live_cycle` output
with DR0023 frames, era and candidate seeds, zero-based generation/candidate
indices, niche/fitness, effective dropout and that generation's recorded weather.
No extra generation, damage, repair, lifecycle, scoring or RNG call is made.
The archive/report remain exactly equal with observation off/on; frame blocks
stay out of the scientific report. Callback exceptions propagate, and callback
mutation cannot alter engine inputs or the returned archive/report.

This is a caller-owned observation channel, not engine retention policy. The
playable consumer retains the latest best record only, with preregistered frame
and byte limits. It never calls the legacy post-era recorder to manufacture
missing original footage. See the U1 contract/report and original-recording tests.


## Ordered admission observation (DR 0084, 2026-10-06)

`evolve` accepts keyword-only `admission_callback: Callable[[dict], None] | None = None`.
After the actual admission decision, each submitted occurrence emits an isolated deep
copy with zero-based `submission_index`, original `grid_id`, boolean `admitted`, and
`rejection_errors` (the actual list for refusal, `None` for admission). Duplicate IDs
remain separate ordered events. `None` and empty founder lists emit no events.
Callback exceptions propagate before candidate evaluation; observation adds no RNG
call, report field, or changed acceptance threshold.

The lab authority additionally accepts an optional direct `founder_grids` list,
mutually exclusive with `workshop_grids_dir`. This arm uses the already-promoted
package DR0029 size gate and preserves input order and duplicates. Direct empty
lists activate the existing empty workshop report projection with
`workshop_grids_dir=None`; the legacy directory arm keeps its original behavior,
including backup skipping. The lab/package reports have their established public
shapes; observer events and scientific results are compared without renaming those
shapes into an invented equality.

`labs/runtime_integration/test_admission_observer.py` retains pre-edit output pins,
complete off/on equality, event parity, mutation isolation, empty/None inputs and
propagated-error controls. The game records these actual decisions alongside immutable
input bytes under DR0084; it does not infer admission from a duplicate-ID map.

## Contextual care selection (DR0086, experimental/default off)

`evolve` adds `founder_care_contexts=None`, `care_selection_policy="off"`,
`care_evaluator="archive_morphology_probe_v1"`. Context lists correspond to
submitted founder occurrences, never grid-ID maps. Actual accepted parent slots
carry immutable contexts through archive insertion/replacement and output elite
order. Sources with no care retain no invented history.

The named `observed_care_selection_v1` uses eight legacy fixed-seed candidates
and a fresh observed-care evaluation within each parent before unchanged
live_cycle/final archive scoring. `runtime.care` exposes the validated selector
and evaluator; `archive.lifecycle_probe_grid` exposes the existing calibrated
probe arithmetic without modification. Pristine is a separate evaluator control.
Absence preserves full incumbent output; off with supplied facts adds provenance
only while preserving genetic/fitness outputs. No trained Q is inherited.
See `docs/development/cycle-38-lived-care-and-thought.md` for registered gates and
`research/experiment_reports/2026-10-06-lived-care-and-thought.md` for outcomes.


## Living population option (DR0089, experimental)

`evolve` adds `population_policy='legacy_archive'`, `founder_start_mode=None`,
`survival_regime='sheltered'`, `cubff_density_pressure=False`, and read-only
`evaluation_callback=None`. Omitted defaults preserve the retained legacy path.
The survivor policy requires explicit bootstrap/continue; continue with `[]`
stays empty and never assists with seeds. `live_cycle` adds the named population
and survival inputs with legacy/sheltered defaults. Observer payloads are deep
copies of actual candidate/parent, cycles, final episode and recorded outcome.

`report.living_population` binds ordered eligible terminal breeders and explicit
termination, separating lifecycle deaths from structural disqualification and
unexecuted slots. Breeders may be archive losers. Death at the requested endpoint
is dead. The separate archive remains historical. Immutable X8 execution output
binds an exact breeder digest including `[]`; `storage.load_era_breeders` returns
`None` only for historical absence and refuses invalid new evidence.

## Cycle38 opt-in shared body response (2026-10-06)

The optional `body_response` argument on lifecycle initialization/episodes and runtime live/evolution selects `legacy` (default) or `workload-v1`. Legacy outputs remain pinned to retained pre-seam results. Active episodes use the actual valid evaluated body, including the repaired grid consumed by the evaluator. Only play's energy cost changes; no food, death, repair, independent-episode, mutation or population-sampling rule changes.

The registered law and eligibility are in `docs/development/cycle-38-body-workload.md`. Conditional active state/report fields record `body_response` and `body_workload` (occupied_mass, functional_capacity, capacity_floor, play_energy_cost). History records configured play cost and actual action energy effect. Model identity binds care contexts/candidate receipts, founder occurrences and immutable era execution bytes; unsupported versions and saved/requested conflicts refuse. Default/cold learning rules are preserved, and previously measured learning gains do not qualify this changed physiology.

This is an experimental game mechanism, not default adoption, biological inference, care selection qualification or extinction evidence. Read the new body-workload report for actual verification and outcome status. Historical v1/v2 care and X8 extinction refusals remain retained.

Sources: `docs/development/cycle-38-body-workload.md`; `research/decision_records/0091-shared-body-workload.md`; `research/experiment_reports/2026-10-06-body-workload.md`.
