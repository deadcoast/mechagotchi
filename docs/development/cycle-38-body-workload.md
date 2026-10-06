# Cycle 38: shared body workload response (preregistered 2026-10-06)

Slice: `x7-x8-body-workload`. This extends the existing X7/X8 development specification in `cycle-38-lived-care-and-thought.md` and `cycle-38-surviving-populations.md`; neither original refused outcome is replaced. Exact working repository, owner HEAD d4b4337d0dacbdfa816d990297c03a5da2d0cdca, branch phase-l-gate, repo Python 3.13.9. No Git publication or alternate checkout. Entry bytes and hashes: `.development/body-workload/entry.json` and `entry-source.zip`.

## Authority and proposed mechanism

Research plan 323 requires body -> behavioral affordances -> survival history -> lineage. DR0021:62-71 requires real engine stakes and explicit successor inheritance. Remaining-life-mechanisms report identifies the missing live response and adopted reset/repair/sampling semantics. This equation is a falsifiable designed game mechanic, not a discovered biological law or an already adopted numeric specification. Food access remains unchanged in both native begging and automatic evaluator feeding.

Model identifiers: absent or API `legacy` is the unchanged incumbent; `workload-v1` is explicit opt-in. Unknown identifiers refuse. No default promotion. Per-life and campaign choices are immutable; a conflicting requested/saved choice refuses before writes. Successors inherit the explicit model choice and morphology, never trained Q-table state. Covenant neediness, sleepiness, curiosity, risks and rewards retain their species meanings. Individual variation is the inherited body's actual capacity to perform an action, not personality, neediness descriptors, a history hash or a cosmetic reward bias.

For a validated grid, occupied coordinates have nonempty cell role AND nonvoid material. Let M be their unique count. Let F be math.fsum of (1 - damage) at the sorted unique occupied coordinates referenced by organs with semantic role body_core or locomotion. Names, list ordering and duplicate references do not alter F. Damage must be finite in [0,1]; zero occupied mass refuses in the active model. All validator-supported body dimensions are supported; no new size filter. Integrity uses damage only; stress already affects existing physiology.

The sole changed action effect is play's energy decrement:

`floor = max(1.0, M * 0.07 / 0.34)`

`play_energy_cost = round(0.07 * M / max(F, floor), 6)`

Use full precision for F/floor; round only the cost to six decimals before normal lifecycle arithmetic. The 0.07 reference is existing play cost; 0.34 upper bound is existing sleep restoration. A fully functional body reproduces the old play cost. The one-cell floor prevents singularity and expresses a minimum unit of modeled support. This is engineering normalization, not fitted physiology. No constants are tuned on outcome data. Only play energy changes; drift, other action effects, rewards, death thresholds and action policy remain the incumbent. No-op/body metadata must not create non-play physiological effects.

Initial/repaired bodies recompute the same projection when each episode starts. Existing fixed-body episodes retain this projection; no residual injury or repair energy cost is invented. Opt-in state/report carries body_response and body_workload with exact occupied_mass, functional_capacity, capacity_floor, play_energy_cost; history exposes configured and applied action cost unambiguously. Shared arithmetic must be used by native session, contextual care evaluation and population evaluation. Public exports remain stable where possible.

## Persistence and compatibility

Legacy state, reports, history, errors, RNG and saved outputs are byte-identical to retained pre-seam outputs, not merely to a second invocation of new code. Engine lab mirrors remain equivalent. Capture baseline lifecycle/native/runtime hashes before source edits. Existing care v1/v2 receipts and original failures remain immutable.

Use conditional active-only `body_response: workload-v1` fields in current care contexts/receipts/state where strict validators can bind them without reinterpreting old records. Absence means legacy; explicit malformed or unsupported fields refuse. Context-to-model conflicts refuse. New immutable era input `body_response_inputs_v1` records exact model and is digest-bound to report, founder/care inputs, runtime closure and reproduction. Legacy input manifests remain byte-identical. Validate active episode projections and model identity at serialization/load/reproduction boundaries; do not accept forged costs merely because internal metadata agrees.

Expose an explicit new-life choice and legible current/history readout. Restart, adoption, newborn cold state, genuine death/successor, immutable reproduction and recovery share the model. Existing saved lives/campaigns are not silently migrated. Repeated/held inputs, unknown versions, interrupted writes and explicit recovery preserve identity and prior bytes. Retain earned roles/density qualification without restudying those claims.

## RED, causal gates and preregistered outcomes

Preregister before RED/source changes. Each owner records actual RED/GREEN commands. Operational tests cover exact arithmetic, bounds, semantic rename/order/duplicate nulls, malformed integrity, lab/package parity, all paths, history, persistence and original off hashes. These deterministic tests establish implementation only.

Before untouched outcome holdouts require: (1) same physiological starting state and different functional bodies yield different actual play energy trajectories in real native session; (2) matched no-play stream yields exact physiological null (exclude declared projection metadata only); (3) actual production repair output is consumed with its recomputed projection; nonsaturated changed functional projection changes play response while exact restored projection is a null; (4) repeat determinism, legacy baselines and native/persistence regression tests pass. Repair contrasts use declared engineered calibration fixtures, never holdout winners; do not search seeds or token models after a refusal. Freeze these fixture payloads and histories before observing their trial outcomes. Saturated cost nulls are reported as such, not mislabeled sensitivity.

Fresh care holdouts: retained product_learning_gate_stage1 input_manifest founders indices 20..29, seeds 20261107, 20261117, 20261127 in seed-major order, 30 paired contexts, pool size 8. Use existing pristine and morphology-stress evaluators with terminal-survival v2 ranking. Capture actual workload-v1 native source histories using the prior 12 requested ticks and fed-at-3/6/9/12 versus neglect protocol, retain originals and matched common prefix. Freeze all histories, ordered founder/model/covenant payloads and candidate seeds before selection. Metadata-only context changes and repeat/lab mirrors are controls. Each evaluator independently requires all old welfare, elapsed-survival and terminal-alive nonregressions against candidate index 0, plus at least one structurally different selected descendant in 30 pairs with different complete rankings. A score offset, synthetic fixture difference, or different ranking without changed selected structure cannot qualify care. Record all candidate trajectories/admissions/deaths/choices. Any failed acceptance remains REFUSE; do not retune or inspect extra seeds.

Production survival is bounded observation, not a promised extinction. Fixed matched legacy/workload-v1 pairs at seeds 20261130, 20261201, 20261202, existing stress-survivor semantics, six generations, 16 candidates, two repair cycles, 16 ticks, dropout .2, full sorted 50-body corpus and existing 40-body/40-epoch repair model seed20260707. Exact weather/input/config bytes frozen. Care policy off, mutation legacy, density off; no food/reset/repair/refill change. Six eras only, one immutable workload-v1 reproduction of the first active era, and a legacy duplicate for noise. Report terminal breeders, all episode deaths, structural and trajectory differences. Extinction requires genuine recorded terminal lifecycle deaths and zero eligible breeders. If none occurs, genuine extinction/successor/inherited-era qualification remains OPEN and contingent demonstration is NOT_RUN. No artificial empty cohort may qualify it. Synthetic persistence tests remain clearly separate. If a fixed qualifying outcome exists, select first by registered order for one explicit native successor/inherited unlock/next-era demonstration; otherwise no extra trial.

## Freeze, budgets and refusal handling

One integrator owns the gate and runner. Nonoverlapping source owners: lifecycle; runtime/storage/execution; game native; new measurement instrument. Independent reviewer owns no implementation. Before outcome execution retain exact source closure (all relevant engine/game/lab modules, models/config/weather, contracts), input manifest and artifact hashes. No qualification source may change during measurement. Per trial write started receipt before launch and terminal status/output/hash afterward. Detect changes and unknown versions; fail closed. Preserve every failure/interruption. Resume only at a completed clean boundary with identical frozen bytes and cumulative budget; never auto-retry failed/interrupted trials.

Total fresh measurement budget is 1200 wall seconds, charging setup, causal/native stages, all care originals/repeats/mirrors, six production eras, one active reproduction, legacy noise duplicate and conditional native successor. Stage caps: setup/native 60s each, causal/care pair30s, each production/reproduction120s. Use remaining total as an upper bound on every child timeout; own and terminate child trees on timeout/exit. Explicit NOT_RUN for contingent/blocked stages. Prior care study64.428071s and prior six-era earned study221.1167044s justify this conservative bound. Source iteration/unit regressions, final sweep and build are separate operational work, not uncharged outcome trials. Do not launch holdouts if causal gates or independent readiness review fail.

## Closing and preserved limits

Run focused iteration and final full DR0062 sweep with source mutation/artifact/diff checks. Produce an additive Windows folder build, verify detached source reproduction/restart and active model identity, retain manifests and screenshots/native SDL event evidence. SDL injected events are not OS keyboard or human usability evidence. Audit every entry preservation hash; prior builds, live saves and all original data/reports/evidence remain exact. Record local gates separately from unobserved exact-published-SHA Windows/Ubuntu CI. No commits, sync or push.

Preserve learning qualifiers: aggregate welfare +11.710698%/+12.071991%, individual regressions including an additional death per comparator, all400nonattentive deaths per arm. X6 operative mutation remains refused/lab-only. Original v1/v2 care0/30 and X8 extinction0/10 refusals remain. Continuous aging, finite reproduction and offline catch-up are excluded. Prior duplicate workshop fixture repair remains qualified; separate HTTP abort cause remains unproven.

At any bounded stop write exact resume, actual work/tests/trials/build/preservation, pending checks and active process state. No documentation-only completion or scientific qualification from unit tests.

## Sources

- research/reports/2026-10-06-remaining-life-mechanisms.md
- docs/project-research/research.md:323; validity-research.md:73,203-212
- research/decision_records/0021-game-loop.md:62-71
- docs/development/cycle-38-lived-care-and-thought.md
- docs/development/cycle-38-terminal-survival-care.md
- docs/development/cycle-38-surviving-populations.md
- docs/development/cycle-38-earned-preparation.md
- research/experiment_reports/2026-10-06-earned-preparation.md
- docs/development/local-cycle.md

## Prefirst-RED fixture/input clarification

The production input payload is reused exactly from `.development/x8/study/setup/inputs.json`, including the existing trained models, corpus, storm weather and configuration; no retraining/calibration. Run `stress_probe` evaluator, stress-survivor regime, explicit empty founder_grids with founder_start_mode bootstrap as in the prior protocol; zero breeders never bootstrap during continuation. Each paired seed uses the same frozen inputs except body_response.

Causal repair fixture is explicitly engineered, outside the holdouts: valid 8x8 grid with four contiguous core cells, one required sensor and one adjacent trim/decoration cell; remove the trim coordinate via fixed damage event. Use the production repair kernel with synthetic rich-vocabulary model: zero weights and fixed B (body) bias for the changed-projection arm, fixed D (decoration) bias for the null arm. It restores the identical occupied position. D->B increases F by one at fixed M; D->D exactly restores projection. Freeze exact authored grid, damage event/model bytes before causal observation. Real runtime live cycle must consume the repaired grid with its recomputed workload. This isolates consumed projection arithmetic; only the separate fixed production trials provide trained-model outcome evidence. Do not call this fixture biological adaptation, field performance or care holdout success.

Fresh source histories are collected under workload-v1 as specified above and their context declares the model. Paired fed/neglect selection differs only by the frozen history, keeping ordered candidate pools/evaluator/model identical. Legacy off parity uses retained pre-seam baseline controls, not reinterpretation of workload histories as legacy care. All inputs are hashed before any selection outcome. The same chosen actual action tape may be replayed across causal active/off contrasts, explicitly distinguished from natural autonomous rollout.

## Premeasurement accounting clarification

The fixed comparison contains exactly six original eras (three paired seeds), one active reproduction and one legacy noise duplicate. If and only if one original active era qualifies genuine extinction, one additional successor next-era is a separate contingent slot with a 120-second cap, charged to the same 1200-second total; its native explicit-succession interaction uses a separate 60-second slot. Otherwise both contingent slots are NOT_RUN. This clarifies counting, without adding a search, retry or replacement. Frozen trained-production corpus/admission/model/weather identities are distinct from engineered causal B/D fixture identities.
