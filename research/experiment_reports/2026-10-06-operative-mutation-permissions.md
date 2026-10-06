# Cycle 38 X6: operative mutation permissions

## Current outcome (2026-10-06, bounded stop)

Product promotion is **REFUSED**: the first full operative run measured
1,966.830335 seconds against the unchanged 1,200-second per-run criterion.
Three legacy controls and one operative run completed. The second operative seed
was operationally interrupted at 1,673.498812 seconds of observed wall time; that
is not a completed scientific runtime. The third operative seed was not started.
The full three-seed quality comparison is **incomplete**, with no inferred mean,
missing-run result or changed threshold. The harness has no execution timeout or
early-stop policy; the explicit bounded-resource instruction caused this stop
after an already measured hard-gate failure. No automatic continuation is needed
to establish runtime REFUSE. The named experimental seam remains available;
all product consumers and defaults remain legacy.

`data/archives/operative_evolution_stage0.json` records the four complete runs,
the missing rows and stop provenance with status `incomplete`. It is an integration
checkpoint, not a successful `--finish` output. All 235 bound source/input hashes
and retained completed results match. Scoped worker verification found zero
matching processes after the stop, and root session 70186 returned exit -1.
No unrelated process or security setting was changed. Evidence is retained under
`.development/x6/evolution-science/bounded-stop-01/`.

Full local verification subsequently passed 3,039 tests / 24 suites; its
evidence is run `20261006T054033-39ee58d3` and the linked experiment report. Runtime
permission retention and X6 product completion remain unqualified. X7/X8 have
read-only design audits, with no implementation or measured result in this slice.
Earlier sections preserve the chronology; this disposition supersedes their
statements that measurement is active or remaining runs will continue.

## Why

The existing schema types mutation attributes and locks without defining the
inherited operator semantics X6 needs. This experiment defines those meanings
prospectively and tests an explicit named arm. It preserves legacy behavior and
all earlier scientific evidence. There is no claim of an old lock-rule violation.

## What was preregistered

`docs/development/cycle-38-operative-mutation-permissions.md` preceded RED and
implementation. DR0085 and the algorithm card link its operator contract and
staged G0-G3 plus conditional consumer gates. Source root/branch/HEAD and all
4,306 source files / 172 dirty identities match X5's final handoff. The repository
Python is 3.13.9; .development/x6/baseline.json retains the exact incoming state.
The sole runner entered x6-operative-mutation-permissions REPAIR through the
supported front door. No Git mutation, new environment or mirror is involved.

## Findings

Read-only consumer audit found that damage/repair matrix reconstruction resets
permission fields. Thus implementing a generator alone cannot justify inherited
campaign permissions. The contract explicitly requires a carrier through those
consumers before claiming end-to-end capability, with physical damage independent
of generation locks. New engine tests and scientific measurement are in progress.

## Verification

Actual RED/GREEN commands and measured outcomes will be appended from retained
logs under .development/x6/operator and .development/x6/science. No test count,
scientific adoption, complete local sweep or product completion is claimed yet.

## Sources

- docs/development/cycle-38-operative-mutation-permissions.md; sunsetted/TODO.md X6.
- research/decision_records/0085-operative-mutation-permissions.md.
- research/algorithm_cards/operative_mutation_permissions.md.
- .development/x5/resume.json; .development/x6/baseline.json.
- labs/grid_genome/operative_permissions.py; labs/grid_genome/operative_mutation_gate.py.
- packages/mecha_engine/src/mecha_engine/{generation/generate,runtime/_damage,repair/wound}.py.

## Pre-measurement instrument review (2026-10-06)

G0 reproduced every deterministic metric of the committed formal package row
exactly; the original artifact remains unchanged. The gate's silhouette entropy
uses corpus signature diversity in bits, explicitly distinct from the per-grid
readability feature of the same name. The clarification preceded measurement.

Independent review calculated that the registered adjacent seed blocks share
90 of 100 parent/seed pairs. They remain the fixed registered protocol; their
readability difference is a shifted-block sensitivity control, not an independent
uncertainty or confidence estimate. No seeds or tolerances were changed to improve
an outcome. This limits generalization of any qualification claim.

Integration review caught a trace-counter error before G2/G3: all 36 zero-rate
opportunities were labelled rejected proposals. The retained counter RED failed
`0 != 36`; the repair records opportunities separately and counts only nonempty
proposals as attempts. Suppression/no-op categories remain in outcome_counts,
and accepted+rejected equals actual attempts. Legacy trace is unchanged.

## Sources for instrument review

- .development/x6/science/g0.json; .development/x6/science/g0.log.
- .development/x6/operator/counter-red.log.
- labs/grid_genome/test_operative_permissions.py; labs/grid_genome/test_operative_mutation_gate.py.

## First measured stage (2026-10-06)

G0-G3 **STAGED_PASS**; this is not ADOPT or consumer qualification. All 800
required paired legacy/operative candidates returned valid and aligned. Exact
zero-rate and all-locked controls remained phenotype copies. Actual clone and
ungated-random controls challenged their variation/reliability gates. G0 reproduced
the committed legacy row exactly; G1's independent receipt was bound to the
reviewed source hashes after the run without changing any candidate measurement.
The pre-finalization artifact and stale-receipt RED/GREEN remain retained.

The study retains 1,220 complete candidate records including controls in the
hashed compressed appendix `.development/x6/science/candidates.jsonl.gz`.
The 71,284,176 raw bytes compress to 1,734,616 bytes; committed metric rows bind
each record by ordinal, grid and trace hash. The appendix SHA256 is
9fa6b280300ddcebcd752435edbbcee4384bcac8a1708355e2e210e6cc719a5d.

These measurements expose the ordinary-rate diversity cost rather than hiding it:

| Cohort / seed block | Arm | Learned readability | Morphology novelty | Silhouette entropy (bits) | Parent copies |
| --- | --- | ---: | ---: | ---: | ---: |
| ordinary / 20260706 | legacy | 0.419251 | 0.151401 | 6.191663 | 1.00% |
| ordinary / 20260706 | operative_permissions_v1 | 0.515357 | 0.043155 | 2.692438 | 72.00% |
| ordinary / 20260707 | legacy | 0.440971 | 0.148280 | 6.152662 | 1.00% |
| ordinary / 20260707 | operative_permissions_v1 | 0.510019 | 0.044481 | 2.779448 | 70.00% |
| all_open / 20260706 | legacy | 0.419251 | 0.151401 | 6.191663 | 1.00% |
| all_open / 20260706 | operative_permissions_v1 | 0.341468 | 0.594815 | 6.643856 | 0.00% |
| all_open / 20260707 | legacy | 0.440971 | 0.148280 | 6.152662 | 1.00% |
| all_open / 20260707 | operative_permissions_v1 | 0.354257 | 0.600909 | 6.643856 | 0.00% |

Readability is the existing learned model's score, not a human preference result.
The ordinary-rate first block has 72% copies versus legacy's 1%; inherited rates
now govern actual opportunities, so fidelity can cost variation. All-open results
establish available operator capacity under explicitly changed rates/caps, not
ordinary gameplay quality. The overlapping seed-block limitation remains above.

Next is the already preregistered independent full-evolution condition using
three DR0052 seeds, population 256, 20,480 scored evaluations, 24 lifecycle ticks,
novelty-first and explicit insertion admission. It is evaluated before investing
in runtime permission retention or product controls: every required gate is still
ANDed, and a full-loop refusal ends the consumer route. The E3 lab stress-probed
loop does not exercise runtime damage/repair; that limitation remains explicit.

## Sources for first-stage measurement

- data/grid_genome/operative_mutation_stage0.json.
- .development/x6/science/candidates.jsonl.gz; .development/x6/g1-review.json.
- .development/x6/operator/handoff.json; .development/x6/science/g0.json.

## Actual focused RED/GREEN evidence (2026-10-06)

All commands used the authoritative repository Python 3.13.9 with `-B`.
The rows below are separate runs, not a summed test count. Retained first-failure
logs and independent reviews supplement these focused checks; local closure still
requires the full sweep.

| Scope | Command | Actual result | Retained log |
| --- | --- | --- | --- |
| operator RED | `.venv/Scripts/python.exe -B -m unittest discover -s labs/grid_genome -p test_operative_permissions.py` | missing operative_permissions module | `.development/x6/operator/red.log` |
| operator RED | `.venv/Scripts/python.exe -B -m unittest discover -s packages/mecha_engine/tests -p test_operative_permissions_contract.py` | 3 failures; missing mutation_arm keyword | `.development/x6/operator/package-red.log` |
| operator RED | `.venv/Scripts/python.exe -B -m unittest discover -s labs/grid_genome -p test_operative_permissions.py -k zero_rates` | 1 failure; suppressed opportunities miscounted as proposals (0 != 36) | `.development/x6/operator/counter-red.log` |
| operator GREEN | `.venv/Scripts/python.exe -B -m unittest discover -s labs/grid_genome -p test_operative*.py` | 27 tests passed (includes separately owned scientific gate tests) | `.development/x6/operator/lab-green-03.log` |
| operator GREEN | `.venv/Scripts/python.exe -B -m unittest discover -s packages/mecha_engine/tests -p test_operative_permissions_contract.py` | 3 tests passed | `.development/x6/operator/package-green-02.log` |
| operator GREEN | `.venv/Scripts/python.exe -B -m unittest discover -s packages/mecha_engine/tests -p test_generation_contract.py` | 34 tests passed | `.development/x6/operator/legacy-contract-green.log` |
| operator GREEN | `.venv/Scripts/python.exe -B -m unittest discover -s labs/grid_genome -p test_package_generation_parity.py` | 5 tests passed | `.development/x6/operator/legacy-parity-green.log` |
| evolution plumbing RED | `.venv/Scripts/python.exe -B -m unittest discover -s labs/map_elites_archive -p test_operative_evolution_arm.py` | 5 missing mutation_arm keyword errors | `.development/x6/evolution-engine/red.log` |
| evolution plumbing GREEN | `PYTHONPATH=labs/map_elites_archive;labs/wfc_grid .venv/Scripts/python.exe -B -m unittest test_operative_evolution_arm test_evaluation_loop_scale test_generation_arm_evolution test_generation_refusal_causes test_slip_admission_arms test_wfc_population_throughput` | 96 tests passed in 58.526s (7 new X6 tests) | `.development/x6/evolution-engine/green-02.log` |
| scientific gate RED | `.venv/Scripts/python.exe -B -m unittest discover -s labs/grid_genome -p test_operative_mutation_gate.py` | expected ImportError missing all_open_inputs | `.development/x6/science/red.log` |
| scientific gate GREEN | `.venv/Scripts/python.exe -B -m unittest discover -s labs/grid_genome -p test_operative_mutation_gate.py` | 19 tests passed, including stale-review binding refusal | `.development/x6/science/review-binding-green.log` |

The E3 pre-measurement review corrected a proposed numeric rule before any run:
rounding a mean loss to six decimals can erase a positive cost when the legacy
spread is zero. Comparisons instead use exact decimal means of the recorded
six-decimal per-seed values, rounding only display values. The retained gate
preregistration records the correction; a one-seed 0.000001 loss with zero spread
must refuse even though the three-seed mean loss displays as 0.000000.
This clarifies the declared zero allowance and does not loosen any criterion.

## Full-evolution readiness review (2026-10-06)

Before the first timed run, independent review passed 13 gate tests and 7
parity/observation seam tests. The reviewed harness hash is
7f894701a17ebfc7db2c5b86b75592d46f25568572bf301e225376bbf782ed21.
The complete conservative inventory binds 235 non-test lab/package sources and
declared inputs. This includes the lazily imported invariant_scaling dependency,
which an import-only snapshot originally omitted. All six snapshots must match
each other and the final current files, not merely each run's own before/after.
The mixed-source false-pass diagnostic now refuses; the retained RED/GREEN is
in .development/x6/evolution-science/. No scientific workload or threshold changed.

Sources: .development/x6/e3-review.json;
labs/map_elites_archive/operative_evolution_gate.py;
labs/map_elites_archive/test_operative_evolution_gate.py.

## Full legacy instrument reproduction (2026-10-06)

The fresh first DR0052 seed, 20260709, exactly reproduced the DR0056
headline: 451 occupied niches, coverage 0.880859, QD 411.738214.
It completed 20,480 scored evaluations and 60,672 generation attempts,
with zero failures/refusals and zero invalid/illegal elites in 383.923s.
All 235 bound source/input hashes remained unchanged. The preserved complete
returned result is `.development/x6/evolution-science/runs/legacy-20260709.result.json.gz`;
compressed SHA256 `8f1e28c5d9d915b8a04ef021065d8b8afc0f64995d97cf6ef1a61142b3e2e496`.
This instrument pass authorizes the remaining five preregistered runs; it is
not a result for the operative arm.

An optional default-sandbox Win32_Process diagnostic was denied access during
measurement. It was not retried or bypassed; the approved foreground measurement
session continued normally. This is not a scientific execution blocker.

## Parent-requested bounded handoff (2026-10-06)

Implementation checkpoint: 10 existing source/document files changed and 15 added
relative to X5, no deletions. Named operator and parity-pinned evolution seam are
implemented; product consumers and default remain legacy. The second fresh legacy
seed 21260712 completed 20,480 scored evaluations, 426 niches, coverage 0.832031,
QD 386.123450, zero failures/refusals/illegal/invalid elites in 424.260s.

Session 31977 remains active with the third legacy seed followed by three
operative runs. The science delegate's turn has ended and monitoring is handed
to the parent/integration lead. Continue the existing session with write_stdin;
do not launch another --finish, interrupt it, run competing timed verification,
or change any of its 235 bound source/input files. Its exact current state is in
.development/x6/evolution-science/resume.json and finish.log. Final evolution
verdict and full local sweep remain pending. No product completion is claimed.

The complete implementation/measurement handoff is
.development/x6/integration-checkpoint.json. X7/X8 read-only design audits are
.development/x6/dependency-audit.json; neither milestone was preregistered or
implemented in this slice. Current HEAD remains d4b4337d0dacbdfa816d990297c03a5da2d0cdca
on phase-l-gate, and both live-save hashes match the original X6 baseline.

## Continuation correction: unavailable execution session (2026-10-06)

On the parent's explicit request to resume, both the integration and original
science delegate contexts returned `Unknown process id31977` from write_stdin.
The prior handoff's active-session statement was based on the earlier tool state
and saved run marker; it is not proof that the OS process survived the handoff.
As of the retained follow-up observation, finish.log is unchanged at 399 bytes,
two full legacy results exist, and the marker still names legacy seed22260715.
No third legacy result, operative result or final evolution artifact exists.
All235 bound source/input hashes still match. All4321 inventoried source files
and actual Git status matched the prior handoff before this documentation update.

No run was restarted or interrupted, no bound source changed, no competing sweep
started, and the denied optional process lookup was neither retried nor replaced
by another process-lookup route. Underlying process existence is unresolved.
This is an INCOMPLETE measurement with an execution-state blocker, not evidence
that the operative arm passes or scientifically fails. Product promotion remains
unqualified. The execution environment must recover the original process/session
or establish termination before missing runs can safely resume. Evidence and
exact next action: .development/x6/monitoring-loss.json and resume.json.

## Recovery and first full operative result (2026-10-06)

The parent authorized a narrowly scoped require_escalated CIM read for the
matching --finish process. It succeeded with zero matching workers; there was
no approval rejection. Original exit cause remains unknown. The interrupted
marker/log and prior handoffs were preserved in
.development/x6/evolution-science/recovery-01/ before resuming only missing runs.
The first two completed controls were reused through the unchanged hash-verifying
loader. Root owns resumed session70186 and remains attached through completion;
its wrapper will record an explicit exit receipt. No process was terminated and
no security setting changed.

The resumed third legacy seed22260715 returned coverage0.828125 and QD384.290746
in337.132s, completing20,480 evaluations with zero failures/refusals/illegal elites.
The three fresh legacy spreads are coverage0.052734 and QD27.447468.

The first operative seed20260709 completed20,480 evaluations with318 niches,
coverage0.621094, QD285.053747, and zero candidate failures/refusals or
invalid/illegal elites. All235 bound source/input hashes remained unchanged.
Its measured elapsed1966.830335s **FAILS the registered1,200s/run gate**.
Product promotion is therefore refused by a required per-run condition, regardless
of later seed outcomes. The remaining two operative runs are still pending; no
complete-cohort quality mean or final six-run artifact is claimed at this point.
The criteria, seeds and workload remain unchanged.

Of60,672 returned pool candidates before novelty selection,
11,932 changed net phenotype and48,740 were parent copies
(80.333597%). Accepted operations were13,380, versus
34,662 actual proposals and21,282 rejections.
All60,672 rate and protected-payload comparisons matched. Accepted edit events
are not the same as net changed descendants. These measurements establish operator
permission fidelity in this lab loop, not runtime damage/repair retention, and
show substantial copy/diversity and runtime costs rather than generic benefits.
The earlier72%/70% copy findings remain valid for their separate8x8 candidate cohorts.

Complete returned result:
.development/x6/evolution-science/runs/operative_permissions_v1-20260709.result.json.gz
Compressed SHA256:f77de14896ba88b727d72d1681a09596cbfc20958ff1d2861eb906c199e5788b.

## Local verification closure (2026-10-06)

The supported repository front door completed full run `20261006T054033-39ee58d3` with
**3,039 tests across 24 suites passed**, 2 documented DR0034 zlib skips,
and successful artifact validation. The runner recorded zero changed source/evidence
files, no verification problems and a clean tracked/staged diff check. Exact JSON
artifact totals and suite timings are retained in
`.development/runs/20261006T054033-39ee58d3/summary.json`; its `result.json` is the verification
receipt. This local result does not complete the interrupted scientific cohort,
qualify product promotion or establish published-SHA Windows/Ubuntu CI.

Actual command (repository Python 3.13.9, same authoritative directory):

```powershell
$env:PYTHONPATH=(Resolve-Path tools\mechas_cli\src).Path
$env:PYTHONIOENCODING='utf-8'
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full *> .development\x6\full-invocation-01.log
```

The timed study command was `.venv/Scripts/python.exe -B
labs/map_elites_archive/operative_evolution_gate.py --finish`. It was operationally
stopped after the already decisive measured runtime failure, with process exit -1;
it is not listed as a completed GREEN scientific command. The independent audit
recomputed all four completed summaries, verified compressed/decompressed hashes
and 235 common source/input hashes, and independently validated final elites.
Pool-level checks are retained observer aggregates rather than an archive of every
discarded candidate. Accepted-operation descendants (11,937) differ from net changed
descendants (11,932), because later accepted edits can reverse earlier edits.
The runtime measurement includes the named arm's observation code; it qualifies
this measured loop and does not isolate mutation cost from recording cost.

The metric JSON records local verification as pending at its measurement checkpoint;
this section and the current runner are the later local verification authority.
`.development/x6/e3-completed-review.json` retains the independent review.
`.development/x6/preservation-final.json` and `source-final.json` retain the final
baseline-relative file audit, owner/live-save preservation and source snapshot.
No X6 native binary was built: the retained X5 release is unchanged and does not
contain this experimental source arm. OS keyboard and exact published-SHA CI remain
unverified. X7/X8 implementation has not started; source-backed dependency audits
are `.development/x6/dependency-audit.json` and `contract-review-followup.json`.


## Retained-trace diagnosis for a future reopener (2026-10-06)

This analysis uses the completed first operative run and previously recorded
candidate cohorts only. No additional cohort, profiling experiment or source change
was run. The acceptance criteria and REFUSE are unchanged.

- Of 2,184,192 operator opportunities, 2,131,273 (97.577%) did not pass the inherited
  rate draw. This is expected probability behavior, distinct from candidate failure.
- Of 21,282 rejected nonempty proposals, 19,433 (91.312%) were refused by symmetry
  permission; 1,663 were invalid and 186 unaligned. There were also 11,096 organ
  overlap suppressions and 6,575 palette opportunities without an alternative.
  The 13,380 accepted operations comprise 11,982 cell edits and 1,398 organ shifts;
  no palette edit was accepted in this run.
- The separate 8x8 all-open cohorts had zero parent copies versus 72%/70% at
  ordinary inherited rates. This demonstrates limited-cohort capacity under
  different permissions, not evidence for raising authored rates or overriding
  locks. A future named proposal arm could investigate symmetry-preserving edits
  and eligible rigid-motion choices under the same permission contract. It needs
  independent preregistration and controls; it is not a rescue of this candidate.

Source inspection identifies performance candidates, not measured hotspots:
`operative_permissions.py:154,165` deep-copies full grids for alternative cell
choices before selecting one, including parent trace metadata replaced later.
The loop constructs a seeded RNG and event for every opportunity, including the
97.577% rate-not-selected outcomes; proposed and accepted deltas duplicate full
before/after payloads. The named observer validates every returned pool candidate.
A future bounded profiling/optimization study can isolate redundant copying and
observation costs while preserving outputs, event truth and permission guarantees.
The retained runtime includes all of these costs and does not attribute the failure
to any one of them. Detailed counts and source locations are in
`.development/x6/retained-trace-diagnosis.json`.

X7 is dependency-ready through care-context evaluation/selection independent of
the refused mutation mechanism. It still needs an exact observed-history window,
founder-occurrence ancestry association, immutable context/policy inputs and actual
descendant/welfare controls; current-life thought must reject stale adopted logs.
The product-compatible learning comparison retains R3's >=5% bar against both
comparators and the prior refusal. X8 needs a living breeder pool distinct from
the historical archive, explicit empty continuation versus new bootstrap, and
versioned regime/weather/role authority plus actual extinction evidence. These are
source-backed design findings, not implemented or scientifically qualified features.
The next implementation should start in a fresh context from
`.development/x6/resume.json` and `contract-review-followup.json`.
