# Cycle 38 X8 prospective contract: surviving populations and earned stewardship

Status: prospective contract, reviewed 2026-10-06 before implementation or new measurements. The integration owner registers this only after the current X7 closing full gate. The unregistered draft and independent interface reviews remain in the task workspace. No measurement informed these prospective revisions. Final registration evidence resides in `.development/x8/registration.json`.

## Authority, intended delivery and exclusions

Use only `C:/Users/ryanf/github/_shelved/mechagotchi` and its `.venv/Scripts/python.exe` with `-B`. Expected owner branch/HEAD: `phase-l-gate` / `d4b4337d0dacbdfa816d990297c03a5da2d0cdca`; recheck actual identities and dirty files at registration. Preserve all X1-X7 work, both live saves, released builds, historical artifacts, interrupted evidence and negative results. No commits, sync, push, source mirror, alternate environment, archive pruning, hidden worker, offline catch-up or credential changes.

The selected existing TODO outcome is meaningful earned preparation followed by measured survival/failure and a real campaign extinction -> successor -> inherited unlocks -> next-era journey. Companion death and `Session.succeed()` are distinct from population extinction and `KeeperCampaign.successor()`.

Deliver operationally correct, explicitly selectable new-campaign choices first. They remain labeled experimental until their own current-cohort gates pass. Passing runtime/API/recovery tests alone does not qualify survival, balanced difficulty, better quality, adaptation, or any biological claim. This contract does **not** authorize changing the default for existing or new campaigns: the existing legacy/sheltered default remains. A successful scientific gate permits a qualified selectable new-campaign mode; a future default decision needs its own explicit prospective decision and supporting cohort. Imported covenants remain an intentional new base, not an alleged bypass.

## Existing findings that this work must preserve

- `.development/x6/dependency-audit.json` already proposes separate `survival_regime` and `population_policy`, the ten boundary seeds below, and explicit empty continuation. This contract develops that existing scope.
- Current cumulative archive parenting cannot distinguish current breeders from historical records. An archived creature can have died in evaluation. Within-era archive monotonicity is not proof that extinction across fresh eras is impossible.
- Current `live_cycle` runs independent `run_episode` evaluations (each initializes a state) and does not stop on episode death. New reporting must not call these a single continuously aging organism.
- Current campaign `founder_pool or None`, runtime seed fallback, ledger founder loading and recovery's ordered-elite override all need version-aware handling together.
- X6 operative mutation remains REFUSE and must not be enabled. Preserve the existing disconnected-repair/C6 failure limits, validity guard, mortality arithmetic, requested horizons and negative results.
- The July stress experiment's 10/48 deaths and -0.097222 survival change are retained observations, not current product qualification.

## Policy and terminal semantics

Keep three independent explicit inputs in the new contract:

| Input | Legacy/off | New option |
| --- | --- | --- |
| `population_policy` | `legacy_archive` | `generation_survivors_v1` |
| `survival_regime` | `sheltered` | `stress_probe` |
| `cubff_density_pressure` | `False` | `True`, when earned and qualified |

Omitted arguments preserve historical output bytes, RNG consumption, seed arithmetic, errors and archive semantics. All experiment call sites name these settings; no measured artifact inherits a moving default. New optional fields appear only for the versioned policy that defines them.

`generation_survivors_v1` is a designed generational replacement mechanism. It does not assert biological reproduction, continuous individual age, natural selection in nature, attachment, personality or trained-Q inheritance. Breeders are actual accepted bodies that completed the declared survival qualification episodes; previous-generation parents are retired from that generational pool, not recorded as killed.

For each candidate, require all of the following before admitting it to the next breeder cohort:

1. Candidate genome is valid; the actual founder/parent occurrence passed alignment and size admission.
2. Every requested damage cycle completed; every repaired body was valid and aligned.
3. Every completed cycle has a real episode with `alive is True` and `death_cause is None` at its endpoint.
4. The separately declared final scoring episode completed and has `alive is True` and `death_cause is None`.

An episode dead on its last requested tick fails eligibility even if `survival_ticks == ticks`. Missing episodes, invalid repairs and alignment loss fail eligibility but are recorded as their actual structural/admission outcomes, never relabeled physiological death. Zero requested damage cycles, if supported by the public runtime, use the actual final episode as survival authority; product campaigns here still request two cycles.

In the new policy, terminate evaluation of that candidate at its first invalid/unaligned repair or dead episode; record which stage ended it. Do not reset and continue a dead candidate through more cycles or a fresh scoring life. A completed final episode, if reached, is recorded even if dead. Archive scoring/insertion remains independent of breeder eligibility: record actual available metrics under declared rules and retain already archived history. Do not invent missing final metrics to archive a prematurely ended candidate. The legacy branch retains its exact existing behavior.

Use only the immediately preceding generation's breeder cohort for the next generation. Preserve every eligible candidate occurrence, including a survivor that did not win an archive niche; membership must not depend on historical archive insertion. Deterministic base ordering is evaluation order `(generation_index, candidate_index)`. Apply any existing explicit parent ordering (fitness/readability) to this eligible cohort only, using occurrence order as the stable tie-breaker. Parentage records identify occurrences and grid hashes, not just potentially repeated grid IDs or niche keys. Preserve care origin with the exact selected occurrence.

An empty cohort after **any** evaluated generation, including the last requested generation, means no living continuation under this model. Historical archive size does not override this outcome. Generation count alone is insufficient to derive extinction. The report distinguishes lifecycle deaths, structural disqualifications, admission failures, no submitted continuation, surviving cohort size and campaign-ended reason.

## Bootstrap, continuation, successor and history

Introduce captured `founder_start_mode` with explicit `bootstrap` or `continue` for the new population contract. Omitted/null start mode with `generation_survivors_v1` refuses at call time. Legacy accepts null or explicit bootstrap, and refuses explicit continue because it cannot honor that contract. This is distinct from X5's existing transport-level `founder_mode=none|list`.

- `bootstrap`: only a genuinely new campaign or newly created successor may establish from the declared aligned seed corpus; explicit releases lead under the existing admission law. Record actual seed assistance. A nonempty requested release list that is entirely rejected still records every rejection; seed assistance is visible because bootstrap was explicitly selected.
- `continue`: use only the ordered submitted continuation bodies plus explicit releases. Never append the seed corpus. `[]` means empty continuation, never `None` or bootstrap. All submitted founders rejected means admission failure/ended continuation, not invented deaths. Valid releases can sustain a still-active continuing campaign, but cannot reopen an already extinct predecessor.
- An extinct campaign refuses another era. The client visibly offers creation of its successor; that new identity starts bootstrap with the existing `+50_000_000` seed offset and carries inherited unlock facts and the selected base covenant according to current X1 authority. No spent caps or old physiological/learning state are smuggled into it.
- Historical elite adoption is explicitly a newly created cared life from a saved genome. It does not modify an extinct campaign's status or refill that campaign's breeder population.

Version campaign state/preparation/recovery dispatch. Existing saves remain legacy and are readable without migration. New saves require their named population/start-mode evidence; missing or corrupt breeder evidence refuses with preserved originals. Do not reinterpret historical elite rows as survivors. Expose an additive `load_era_breeders`/equivalent rather than silently changing legacy `load_founder_pool` semantics for all old callers.

Store ordered final breeder records and immutable genome bytes separately from `ordered_elites_sha256`; the archive remains historical. Bind population policy, regime, start mode, density flag, breeder digest, endpoint outcomes and ordered care origins to the report and X5 execution manifest. Recovery, completed-era journals, reproduction, succession, and storage validation must agree. Extend the manifest-reference closure; no unreferenced output blobs or unverified inline genomes. A separate SQL schema change is unnecessary if report plus verified output blobs suffice; if required, preregister its schema version and old-read contract before its RED.

## Operative progression: roles

Add optional `grid.allowed_organ_roles` for SLIP 0.2.0 only (0.1.0 remains frozen), with the named semantic contract `organ_role_permissions_v1`, using the existing genome role vocabulary: `body_core`, `sensor`, `expression`, `locomotion`, `ornament`, `effect`. Absence means unrestricted as before. Required roles must be a subset; unknown, duplicated, empty or contradictory values refuse. Preserve old schema documents/artifacts as history; new authoritative/schema/Pydantic/package semantics must match.

Enforce via the same SLIP authority at founder admission, generator proposals/final acceptance, hatch/preview and repair acceptance. An over-budget request changes nothing. No UI-only counter; an allowed-role spend changes the effective captured covenant and actual admissibility.

Read-only inventory in the exact shipped 16x16 corpus and `slip_v2_cleanliness` found ten aligned seeds. Core/sensor/expression alone admits zero. Adding locomotion admits four (beetle/mantis/hopper/warden); adding ornament instead admits two (snail/sprout); adding effect instead admits one (drone). Therefore nominate an **explicit optional starter covenant** with core/sensor/expression/locomotion, then niche-mastery tier 1 permits ornament and tier 2 permits effect. Preserve thresholds 16/26/36; tier 3 has no invented seventh role. This optional base does not replace the historical cleanliness covenant. Old/unrestricted or imported bases remain valid; no artificial new restriction is imposed.

Role qualification is an authority/effect gate, not a quality-gain claim:

- Exhaustively inventory all 50 frozen shipped genomes before and after each role spend. Required invariants are zero false accepts of forbidden roles, zero false rejects caused by the new field when absent, all required roles retained, and at least one viable aligned seed at each supported starter stage.
- Before spending, selected blocked corpus genomes must refuse. After the actual earned fact authorizes spending, at least one previously blocked genome for **each offered role** must pass and reach actual era evaluation. The first qualifying genome in sorted source order is used; do not hunt generated seeds.
- Run exactly 30 generation cases: the ten registered seeds below crossed with the starter, starter+ornament, and starter+ornament+effect covenants. Use exact parent `data/seed_grids_16x16/mg_seed16_001_beetle.json` for every case, after preflight confirms admission in all three profiles; failure refuses rather than selecting another parent. Use the same frozen generation and repair model bytes as the product cohort. Then run one actual repair exposure per accepted generated candidate using dropout .2 and damage seed `run_seed * 10 + 1`, retaining the existing named C6 failure regression separately. All accepted outputs must satisfy role authority. Rejection/failure rates are reported, not erased with a fallback genome or by loosening validity.
- Repeat the starter-covenant generation and repair case at seed 20260700 once as the duplicate control; it must have exact identical decisions and outputs. The required effect is a strict admissibility/input difference versus the measured zero-difference control, not an arbitrary percentage gain.
- Existing campaigns and imported new bases retain their documented behavior. Tests of invented unlock facts verify guards only; actual native progression qualification must earn the fact through play.

If a role cannot be earned or cannot reach evaluation in the declared current protocol, keep that role's product claim OPEN/REFUSE. Do not lower thresholds or advertise that role as newly qualified.

## Operative progression: weather and difficulty

Expose the already specified DR0045 input name `cubff_density_pressure`, preserving weight 0.5, organization ceiling 25.6 and multiplier band [0.5, 1.6]. Keep `calm`, `stable_soup`, `storm`, `real`, `callback` source identities and bytes unchanged. Density does not synthesize replication or lineage channels. It is distinct from morphology stress and from verification scale.

An actual inherited/earned storm-record tier 1 (existing >=1.1 survived multiplier) permits the density-pressure choice for a weather source with recorded snapshots. A selection with no source refuses rather than silently doing nothing. Existing weather choices remain available; the added earned choice is the named density channel. Do not retune the existing tier-2 1.4 threshold or invent a forecast to force it. The preparation UI and `advance_era` authority both enforce permission before capturing/running inputs. A loaded forbidden selection must be visibly refused, not silently replaced.

Weather gates retain DR0045's old reference values and limits:

- `data/game_client/density_pressure_stage0.json`: checkpoint early/post means OFF .818009/.783716; ON .857880/.864204; callback .772726/1.034884. Reproduce the old named computation on its original committed inputs, with exact per-snapshot values and G1-G5 decisions. Density adoption is historical; current public-runtime/native wiring is new work.
- Current named-source OFF calls equal omitted calls exactly. Duplicate controls establish a zero noise floor. ON must produce a strictly positive effective-dropout difference on at least one frozen real snapshot, no negative multiplier deltas, unchanged source hashes, and unchanged absent upstream channels. Every multiplier stays in the existing band.
- For actual consequences, use all ten registered seeds with matched OFF/ON inputs. For seed ordinal i, rotate the **frozen ordered real weather list** by i modulo its length, identically in both arms, then run a one-generation, 16-candidate, two-cycle, 16-tick exposure pair with sheltered/legacy policies, dropout .2, no care selection. Record this fixed coverage probe as `real_rotation_probe_v1`, not as the normal user forecast order. It covers distinct actual source snapshots without selecting by simulated outcome; all rotations are declared before running. Native product verification separately uses one six-generation production era with the normal unrotated real forecast and must expose an actual changed generation within those six. If none changes, native density effect remains OPEN; no extra eras or reordered product weather. Require exact candidate-body/first-cycle seed equality before damage, no reduction of total first-cycle removed cells, and at least one extra removed cell versus the duplicate-control difference of zero. Repeat the OFF exposure at seed 20260700 exactly once as the weather duplicate control; this is a separate receipt and time debit. Later-cycle effects are reported, not used as a monotonicity assumption. If granularity masks all damage differences, this consequence gate refuses; do not raise rates, lengthen exposure or switch records after seeing it.
- These are mechanistic/directionality gates. They do not claim improved survival or that a .006324 ordering gap predicts human difficulty. The morphology `stress_probe` has its own current survival gates below.

## Historical instrument check (before population/source changes)

Reference artifact: `data/runtime_integration/mecha_engine_evolution_hard_regime_stage0.json`, SHA256 `bf686da1a5efc6163a3d8f7d2cee8e9c9a530e6ae9b4941030e4c91ebafade1f`.

Reference report: `research/experiment_reports/2026-07-05-stress-regime-evolution.md`.

Actual existing script: `labs/runtime_integration/mecha_engine_runtime_loop.py`. Its legacy evolution path constructs the 8x8 `labs/grid_genome/corpus_builder.py:build_seed_grids` corpus, reads `data/slips/valid/slip_lcd_seed.json`, trains repair on its first 40 grids for 150 epochs at the run seed, and uses the historical injected readability scorer. Freeze all those source/input identities and verify no worker is mutating them before the check.

Prospective command (not executed while drafting):

```powershell
& .\.venv\Scripts\python.exe -B labs/runtime_integration/mecha_engine_runtime_loop.py --mode evolution --regime stress_probe --generations 6 --population 8 --damage-cycles 3 --ticks 72 --dropout-rate 0.2 --rng-seed 20260512 --output-dir .development/x8/historical-stress-01
```

Run it under the foreground watchdog and cumulative bound below, never directly overwriting `data/`. Compare original candidate/parent IDs, episode outcomes, scores and summary, not just the headline. Reference summary includes 48 candidates, 144 damage events, 10 final-episode deaths, 25 archive niches, QD 21.265377, guard substitutions 19, load delta -.093813 and survival delta -.097222. Only report `date`, `purpose`, `source_artifacts`, and `next_research_step` prose/trace links may differ without failing the numerical instrument check; preserve those differences in the receipt. No candidate IDs, parent IDs, episodes, scores, summary values, decisions, or RNG outputs may be projected away. Scientific/RNG drift fails reproduction. Do not restore old source, regenerate the historical artifact, silently normalize changed scores, or substitute a different cohort. A reproduction mismatch is retained and diagnosed before qualifying the new instrument; a prospective correction appendix is required before further measurements. Independent API implementation may proceed after a mismatch, but no changed numerical or identity field may be normalized away to claim historical reproduction.

## Frozen product survival cohort

The following are prospective fixed choices, not measured results:

- Seeds: exactly `[20260700,20260701,20260702,20260703,20260704,20260705,20260706,20260707,20260708,20260709]` in that order.
- Corpus: all 50 `data/seed_grids_16x16/*.json` in sorted filename order, captured as exact ordered JSON bytes.
- Covenant: exact `data/slips/valid/slip_v2_cleanliness.json`, with no new role restriction in this comparison. This isolates survival/population effects and does not qualify a changed starter covenant's balance.
- Generation model: existing trainer over that exact ordered corpus. Repair model: existing `prepare_campaign_models` contract, first 40 grids, 40 epochs, model-training seed 20260707, dropout rates [.1,.2,.3,.4], one damage instance, learning rate 1.5, live-class weight 3.0, `vocabulary='legacy'`. Capture model and training bytes once; no live-save cache is touched.
- Readability: exact shipped `data/readability_benchmark/adopted_readability_model.json`; current campaign scorer and base blend .7, captured explicitly. No learned new calibration.
- Every first era: generations 6, population 16, damage_cycles 2, ticks 16, dropout_rate .2; explicit `bootstrap`, no released founders, no care history, care policy off, legacy mutation arm, density flag False.
- Weather: exact six `build_weather_source('storm')` records, frozen before the run; the same six records in all arms. This lets genuine surviving storm eras earn the unchanged >=1.1 fact while keeping weather out of the arm contrast.

| Arm | population_policy | survival_regime | Purpose |
| --- | --- | --- | --- |
| A | legacy_archive | sheltered | Product incumbent control |
| B | legacy_archive | stress_probe | Stress input without new population semantics |
| C | generation_survivors_v1 | sheltered | Population semantics without added stress |
| D | generation_survivors_v1 | stress_probe | Combined experimental survival campaign |

Run seed-major in A/B/C/D order: one 40-trial first-era package cohort. Before it, run exact lab/package parity on seeds 20260700 and 20260709 crossed with all four arms (eight paired cases, sixteen bounded runs); these are correspondence controls, not extra scientific samples. Run A/B/C/D at seed 20260700 once more as four lab duplicate controls after the cohort, preserving their own receipts and time debits. Compare against the prior lab parity cases. No control inflates the scientific sample. A and B preserve the legacy evaluation/scoring behavior. C and D use the new stop/eligibility rules above. Report their different opportunity counts; do not compare only survivors or completed generations. Before causal interpretation, compare identical first-generation generated bodies and seeds across arm pairs.

Keep both observed counts and fixed denominators: attempted candidate count; requested slots 96/era; admitted founders; candidate-generation/repair errors; lifecycle deaths by cause and stage; alive endpoints; generations completed; terminal breeders; archive insertions/QD/coverage; all actual cycle and final-episode survival/welfare. Unexecuted slots are visibly unexecuted, never fabricated deaths. Report requested-slot-normalized living yield alongside conditional rates; zero dead tails apply only to defined welfare calculations, not invented states.

Scientific gates are intentionally falsifiable:

1. Full 40-trial cohort, immutable source/input receipts and runtime bounds pass, with no unhandled operational failures.
2. New/off equivalence and first-generation comparability pass; original failure/repair acceptance criteria remain unchanged.
3. Current harder-input evidence: B has strictly more actual final-episode deaths than A among the matched first-generation candidates (16 requested candidates x ten paired seeds). Death is explicit alive=False with a recorded cause, including death on the last tick; elapsed survival ratio cannot substitute for terminal state. Missing final episodes are recorded as missing, not deaths. Candidate identities and pre-damage bodies must match before this contrast. An isolated read-only evaluation callback captures actual legacy final episodes without adding default report fields or resimulating outcomes. Callback receives a deep copy and cannot alter inputs/RNG/report. Duplicate controls must have an exact zero difference. Report D versus C separately, because changed parenting changes subsequent opportunities. No minimum gain or biological adaptation claim is introduced.
4. Actual modeled survival and failure: D contains at least one campaign with a nonempty terminal breeder population and at least one genuine lifecycle-driven extinction. An all-rejected bootstrap or structural-invalid-only run cannot satisfy the extinction clause; report those failures separately. Extinction requires real candidate lifecycle deaths in the recorded terminal generation and zero eligible breeders, without injected deaths or archive removal.
5. Native connection: reproduce the lowest-seed declared D extinct result through the normal client in an isolated campaign and verify its matching engine result, persisted extinction, restart, visible successor creation and one sheltered successor era. The earned-unlock journey below is separately required if that direct replay earned no fact; an empty inheritance is not evidence of inherited unlocks. Do not search outside the ten.

If gate 3 or 4 fails, the new runtime can be operationally sound while the X8 harder-survival outcome remains REFUSE/OPEN. No additional seeds, severity changes, shrinking populations, dropping difficult rows, relaxed death definitions, or post-hoc threshold tuning is authorized by this contract.

## Native connected journey and earned-fact fallback protocol

A single failed first era may earn few facts. For the native demonstration only, when the direct D replay earned no unlock, create a **separate fresh isolated campaign** using the same lowest qualifying registered base seed and run its previously registered **sheltered/survivor** preparation era at the same production settings and storm source to earn actual facts, then its stress/survivor continuation at the existing ERA_SEED_STRIDE 1,000,000. Predeclare this as a distinct two-era journey, not one of the 40 cohort trials and not a rescue for a failed scientific gate. If it does not yield both an actual earned fact and later real extinction, report the journey limitation; no extra eras or seed search.

Run this distinct two-era journey at most once, only when needed for actual inherited-unlock evidence, using the lowest registered seed whose D cohort result met genuine extinction and explicit start modes bootstrap then continue. Never reset the extinct D replay to active or overwrite its save. Historical archives remain present. On genuine extinction restart the client, inspect prior archive/history, create the successor via the visible action, verify the same Keeper identity and unchanged inherited fact fields, explicitly select sheltered and run one successor bootstrap era. Verify its source/seed/profile/permissions and cold new life when a companion is adopted. A prior archived phenotype may be chosen as a new cared life, with an honest origin; this cannot refill the ended predecessor.

Role/density spends must use facts actually earned by these declared eras or by an existing isolated recorded campaign with verifiable real-play provenance. Do not inject facts to claim play-earned progression. If the declared journey does not earn niche tier 1/2 or storm tier 1, those native permission demonstrations remain OPEN even when guard/unit tests pass. The contract does not add an unbounded grind protocol.

After source native events pass, build a fresh named Windows bundle without replacing prior builds; run the same selected protocol from a relocated copy outside repository ancestry with isolated save homes and source-bound receipts. Include a normal SDL launch, preparation/consequence/review screens, restart, and completed-journal recovery. Distinguish injected native events, EXE invocations, actual OS keyboard use and human usability evidence. Final full sweep and preservation audit run against final integrated source.

## Resource bounds, receipts and resumption

One foreground simulation worker only. Before any setup/model loading, record monotonic/wall start times and source/input identities. Budget accounting sums the actual elapsed durations of every measured stage and retained attempt; implementation/review intervals between source freezes are not experiment execution time. No setup, loading, waiting on an experiment child, or publication time may be omitted from its measured stage. Setup budget 120 seconds; every era/reproduction trial budget 120 seconds; **all measurement stages together budget 1,200 seconds**, including historical reproduction, role/weather probes, lab cohort, package parity, native journey simulation and retained failed/interrupted work. Build/full-suite durations are reported separately and do not buy more experiment time. Training is setup, not free work outside the clock.

The fixed measurement order is historical reproduction, frozen setup/model capture, operational corner-case/parity measurements, the 40-trial package cohort, four duplicate controls, role qualification, weather qualification, then qualified native journeys/reproduction. Unit tests and source-review work are separately reported; any actual qualification simulation within a test or verifier must be debited as a measured stage. Parent alone launches these stages; no concurrent scientific worker. Reserve 600 seconds for the cohort and 120 seconds for native journeys from the common 1,200-second pool; earlier stages may not consume those reservations. The already-planned first cohort trial may provide a runtime projection, without changing arms, seeds, criteria or trial order. If the remaining fixed plan cannot fit, stop incomplete rather than resizing it or granting more time. Every failed/interrupted attempt consumes the same total and its stage reservation.

Each trial gets an exclusive directory and immutable plan/source/input digest plus start receipt **before** execution. Write terminal success/refusal/error/timeout receipts with elapsed time, complete available outcomes and checksum-linked outputs. The parent coordinator alone publishes aggregate progress atomically; workers do not concurrently replace it. Preserve partial stdout/stderr and interrupted receipts. Timeouts terminate the bounded child; no hidden continuing worker.

Resume only the same frozen plan/source/model/input identities. Completed trials are reused after integrity validation. An interrupted or failed simulation is not silently rerun: retain its time debit and mark the attempt incomplete/REFUSE; a new simulation attempt requires a fresh prospective instrument/attempt appendix, without resetting the total budget or erasing the original. Source drift or input drift stops immediately. Missing remaining budget stops before the next trial. Never launch a larger/unbounded run after failure is established. Allow at most one explicitly recorded I/O publication repair if it changes no simulation inputs/results; that repair still consumes the same budget and cannot relabel a failed simulation as completed.

## Dependency order and file ownership

1. **Integration owner preregisters.** Close/record X7 decision; capture incoming source/save/build inventory, preserve v1 evidence, register contract and expected suite list. Historical instrument check runs on that frozen starting source before new algorithm edits.
2. **Laboratory population lane first.** Own new `labs/runtime_integration/survival_population.py` prototype/gate/tests and minimal legacy-loop hooks. Prove explicit empty continuation, terminal eligibility, disqualified archive distinction, final-generation extinction and exact legacy controls in the lab. Do not edit package runtime or shared game files yet.
3. **Role authority lane, separately owned.** Own new-role schema/lab authority/Pydantic tests and later package `slip/authority.py` port/parity. It can work concurrently with prototype construction, but no evidence-bound cohort runs while it writes imported authority code. The default absence behavior must remain exact. Resolve all schema/code changes before the measurement freeze.
4. **Promote the lab algorithm only after operational prototype checks pass.** Transfer `runtime/evolve.py`/`runtime/live.py` ownership from the completed X7 care lane to the population lane. Mirror private algorithm helpers rather than importing labs; package never imports lab code. Add package contract tests and complete lab/package parity. This promotion exposes an experimental API; it does not imply scientific ADOPT.
5. **Storage lane.** Own `labs/game_loop/campaign_store.py`, package `storage/store.py`/exports and additive storage parity tests. Agree breeder/execution record shape with owner first. Do not edit `execution.py`, `campaign.py` or recovery. Respect X7 care-origin/manifest closure.
6. **Campaign integration lane**, under the sole integration owner: own `campaign.py`, `campaign_recovery.py`, `execution.py`, `era_plan.py` and new campaign tests. **Integration owner** owns `covenant.py`, `covenant_io.py`, `app.py`, UI/review/readout, lab covenant mirror, shared game tests, documentation/ledger/workflow, source freezes, coordinated experiments, release and final gates. Agree all shared interfaces before parallel writes. The role authority lane may own a new bounded role/density instrument; its execution remains serialized by the owner.
7. **Freeze all affected source.** Independent reviewer inspects integrated contract/runtime/storage/SLIP/provenance. Capture final experiment closure including complete lab and package modules, all schemas, instrument code and input/model bytes. No agent edits these during cohort runs; documentation results may be appended only outside the bound source closure.
8. **Measure final package after laboratory proof.** The lab prototype must accept exact frozen product corpus/model/profile/weather bytes. Run the sixteen predeclared parity calls, then the single forty-trial package cohort and four duplicate controls above. Compare complete algorithmic result contents and ordered genomes, including numerical metrics, identities, endpoints, breeder records and care provenance. Only known existing lab wrapper prose/labels (`lab_id`, `date`, `purpose`, `source_artifacts`, `composition`, `next_research_step`, `decision.adoption`) may differ; list every projection explicitly in the instrument and receipt. No unexplained key/value, score, endpoint or identity may be dropped. Cohort source stays frozen across all stages. Stop incomplete if any required comparison or fixed budget fails. Native journeys follow only gates they actually cover.
9. **Close cohesively.** Focused tests, native evidence, final aggregate, artifact validation, source-mutation check, diff review and preservation audit are mandatory. Record actual RED/GREEN commands and measured verdicts in report/card/metric/ledger together. Native Windows/Ubuntu CI on a published SHA remains separately unmet; owner retains Git publication.

## Agreed runtime and persistence interface

The public runtime remains a two-result `(archive, report)` API. Add optional
`population_policy='legacy_archive'`, `founder_start_mode=None`,
`survival_regime='sheltered'`, `cubff_density_pressure=False` and an optional
read-only `evaluation_callback`. Omitted/default calls preserve prior bytes.

Use `report.living_population`, because `report.population` is already the
requested count. Its format is `generation_survivors_v1`, with population_policy,
founder_start_mode, survival_regime, initial_parent_occurrences,
requested_candidate_slots, evaluated_candidates, unexecuted_candidate_slots,
final_breeders, and termination. Termination records ended, reason
(`requested_horizon_complete`, `empty_continuation`, `all_founders_rejected`,
`no_eligible_breeders`), generation_index (nullable before evaluation),
lifecycle_deaths, structural_disqualifications and genuine_lifecycle_extinction. Those death/disqualification counters refer only to the terminal evaluated generation (zero when none). ended is false only for requested-horizon completion with a nonempty breeder cohort; full-era totals are separately derived from every recorded candidate.
Final breeders remain evaluation-ordered flat records: generation_index,
candidate_index, grid_id, grid, grid_sha256, fitness, learned_readability,
care_context and care_context_origin. Nullable context and origin appear together.
Origin names the submitted founder occurrence and context digest. Canonical grid
identity uses the existing care-grid digest convention. Each creature's breeding
record retains occurrence, parent_occurrence, candidate_grid_sha256,
final_grid_sha256, cycles_requested/attempted/qualified, actual final_episode or
null, eligible, and a named stop stage/reason with nullable cycle index.

Execution input blob `population_inputs_sha256` has format
`survival_population_inputs_v1` and population_policy, founder_start_mode,
survival_regime, cubff_density_pressure. Capture nondefault legacy stress/density
as well as the survivor policy. New execution format v2 is used for those inputs;
legacy default v1 remains valid unchanged. `ordered_breeders_sha256` references
the exact insertion-ordered final_breeders list and is required only for the
survivor policy. Full runtime records in the report and a separate output blob
are intentionally redundant and must match exactly. Add the reference to the
complete closure validator; no unverified output or silently missing empty list.

`load_era_breeders` returns None only for verified historical absent policy,
[] for verified explicit empty output, and refuses missing/corrupt new evidence.
Every `era_breeder` founder source binds campaign_id, prior era_index,
source_position, generation_index, candidate_index and grid_sha256 to the exact
prior verified slot, including null-care cases. A continuing source list must contain the entire immediately preceding ordered breeder cohort as the exact tail after explicit releases, slots 0 through n-1 without gaps or duplicates; bootstrap forbids era_breeder sources. Empty prior breeders retain an explicit empty tail. Per-source validity cannot authorize selectively dropping the prior living cohort. Old `era_elite` remains historical.
New campaign state v2 and preparation v4 dispatch without migrating old v1 state
or prior preparation v1-v3; recovery, journal, successor and reproduction use the
same branch. Legacy archive rows remain intact, independently of living cohorts. For generation_survivors_v1 the immutable ordered founder_occurrences are the authoritative submission evidence, including duplicate-ID era_breeder occurrences. The schema-v1 unordered founders table projects only uniquely attributable workshop_release rows and omits era_breeder rather than mislabeling it era_elite. Versioned recovery validates that exact projection; legacy completeness stays unchanged. Bind every new source to the immediately preceding same-campaign breeder slot even with null care. New state population_continuation records founder_start_mode, era_index and ordered_breeders_sha256: bootstrap uses null index/digest, continue uses the previous era index and exact digest, including explicit empty. Campaign population_policy is fixed at construction. Per-era survival_regime and density are explicit preparation settings; advance_era derives bootstrap/continue from real history, never a player-supplied start override. Successor retains selected population policy. Existing loaded campaigns never silently change mode.

## Operational gates versus scientific/product gates

Operational/API promotion can pass with a scientific refusal. Required operational checks: deterministic same-input replay; exact absent/off legacy parity; lab/package parity; immutable inputs; valid/aligned accepted offspring; role authority enforcement; no resurrection or empty refill; occurrence-bound care provenance; final-generation extinction; historical archive preservation; old/new read dispatch; malformed/missing evidence refusal; save/restart/pending-journal exactly-once behavior; inherited fact integrity; early and late generation termination accounting; no trained-Q transfer; source-bound native payload.

Required regression controls include: death exactly at horizon; survivor losing archive competition still breeding; high-fitness dead archive entry excluded; empty continuation with nonempty seeds; all-rejected continuation distinguished from death; explicit bootstrap recorded; duplicate genome IDs with separate care origins; final cohort empty with nonempty archive; historical-state reader unchanged; corrupted breeder blob refused; recovered pending extinction consistent across state/ledger/journal; imported base plus successor preservation; density off/omitted equality; earned permission refusal without mutations.

Scientific survival gate additionally requires current cohort harder-input directionality, real survival **and** lifecycle extinction, and the declared connected native journey. Role/weather product qualification additionally requires actual earned facts, actual input/behavioral consequences, and persistence. Failures remain first-class findings and do not close TODO X8. Neither implementation completion nor an experiment's ADOPT alone changes defaults.

## Sources

- `AGENTS.md`, `ONBOARDING.md`, `CLAUDE.md`, `sunsetted/TODO.md`
- `docs/development/local-cycle.md`, `.development/x6/dependency-audit.json`, `.development/x7/resume.json`
- `research/experiment_reports/2026-10-06-lived-care-and-thought.md`
- `research/decision_records/0021-game-loop.md`, `0045-density-as-pressure.md`
- `research/experiment_reports/2026-07-05-stress-regime-evolution.md`
- `data/runtime_integration/mecha_engine_evolution_hard_regime_stage0.json`
- `data/game_client/density_pressure_stage0.json`, `data/game_client/real_weather_harshness_stage0.json`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`, `labs/runtime_integration/test_mecha_engine_runtime_loop.py`
- `labs/cubff_transducer/cubff_transducer.py`, `labs/cubff_transducer/test_density_pressure.py`
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py`, `runtime/live.py`, `runtime/_cubff.py`
- `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py`, `archive/_metrics.py`, `storage/store.py`, `slip/authority.py`
- `labs/game_loop/campaign_store.py`, `labs/game_loop/session_runner.py`, `labs/game_loop/session_soak.py`
- `game/src/mecha_game/campaign.py`, `campaign_recovery.py`, `execution.py`, `era_plan.py`, `covenant.py`, `covenant_io.py`, `app.py`, `session.py`
- `research/grid_genome/grid_genome.schema.json`, `research/slip/slip.schema.json`, `labs/slip_validator/pydantic_contract.py`
