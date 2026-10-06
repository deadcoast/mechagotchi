# Cycle 38 X6: operative mutation permissions

Preregistered 2026-10-06 before RED, in the authoritative phase-l-gate checkout
at d4b4337d0dacbdfa816d990297c03a5da2d0cdca. X5 is locally complete;
.development/x6/baseline.json records all 4,306 source files and 172 incoming
dirty identities, matching X5 exactly. Commits/sync/push remain the owner's.

## Question and authority

Can faithful authored permissions control actual descendant operations without
unacceptable quality or reliability loss? Existing schema types locks but did
not specify germline inheritance. This is a NEW contract, not a finding that
legacy violated an old promise. TODO X6, DR0042/0047/0052/0056 and the package
generation contract govern the experiment. Default learning REFUSE, original
recordings, historical generation evidence and all live saves survive.

## Explicit operator contract

`mutation_arm="operative_permissions_v1"` is experimental. Omitted or `"legacy"`
uses the incumbent without extra RNG consumption or output/trace changes.
Parent and profile must already validate and align; never clamp or repair an
inadmissible parent. Begin with a deep copy, including rich unknown payload.
The parent mutation vector is inherited unchanged, not jittered output attributes.
Its four values are Bernoulli probabilities at the opportunities defined below;
SLIP maxima are ceilings on those input probabilities, not promised observed
acceptance rates. Zero probability means no corresponding operation.

Twelve rounds (existing proposal budget; the existing explicit temperature may
scale it) independently offer cell mutation, organ shift, and palette shift in
that fixed order. Successful rate draws permit a proposal, not forced change.
Structural proposals that lower the existing role-aware horizontal symmetry
statistic additionally require a Bernoulli draw under symmetry_break_rate.
Symmetry permission never authorizes an edit without its cell/organ permission.
No unconditional anchor reposition, rate jitter, forced variation or fallback
reconstruction is allowed. All rejection/no-op outcomes are retained.

Cell operations select unlocked positive-weight occupied sources proportionally
to mutation_weight; replace/delete there or grow into a cardinal empty neighbor
using learned local token constraints. No positive eligible weight means no
proposal, never uniform fallback. Growth inherits source permission/extra fields,
sets stress/damage to zero, and has no animation anchor. In-place changes retain
extra fields and anchor; learned A cannot add an anchor. Organ shift selects an
eligible organ by summed positive member weights and translates the complete
organ by one cardinal cell; overlap/out-of-bounds/zero-weight/protected members
prevent the proposal. The anchor travels with its member. Palette change samples
an allowed alternative and recolors by palette position; it is a global operation,
not controlled by cell-selection weights, but cannot alter protected cells.

In this named arm cell.locked protects the entire original cell payload and
coordinate throughout generation. organ.mutation_locked protects the complete
original organ, membership and constituent cell payloads; incoming edits cannot
bypass it. These flags and weights are inherited. The existing editor's authoring
lock remains distinct from this newly opted-in germline meaning. Each proposal
must pass exact protected-payload checks, genome validation and SLIP alignment,
or is rejected atomically. Zero-rate and all-locked controls may be exact phenotype
copies; only identity, ancestry and generation evidence differ. Trace includes
opportunity/rate gate, eligible weights, selected source, proposal outcome and
actual before/after delta. Lineage change events describe accepted nonempty edits,
never attempts or an invented anchor move. Inputs are immutable.

Locks govern descendant operators, not damage immunity. Runtime damage and repair
currently reconstruct cells and discard permissions. Consumer qualification must
therefore also demonstrate a separate inherited permission carrier through those
steps, reattaching flags/weights to surviving or repaired coordinates and preserving
protected empty loci without inventing undamaged cells. No end-to-end inheritance
claim or campaign exposure is allowed before that consumer gate passes.

## Registered qualification gates and fixed protocol

This is qualification for a named opt-in capability, not evidence of generic
fitness benefit or permission to change the legacy default. All gates are ANDed.

G0: reproduce the committed formal 8x8 instrument first, using its own 30/10/10
split, seed 20260706, 100 outputs/arm and 1,000 bootstrap resamples. Compare every
deterministic metric of the legacy package row to generation_bakeoff_formal_stage0;
record runtime separately. Historical artifact bytes must remain untouched.

G1: exact omitted/explicit-legacy behavior and input immutability; unchanged legacy
lab/package controls; byte-identical private operative lab/package implementation
and paired outputs. Deterministic tests cover zero/all-locked/organ-locked/zero-weight,
each rate independently disabled, caps, multi-generation inheritance, invalid
inputs, weighted source selection (before validity filtering), and trace delta truth.

G2: use the unchanged formal holdout parents/model and LCD profile, same parent/seed
pairs at seed blocks 20260706 and 20260707, 100 outputs per block per arm. Every
requested candidate must return valid/aligned, with no swallowed exceptions or
silent drops. Record rejected/no-op proposals separately from candidate failures.

G3: measure ordinary inherited-rate and all-open cohorts separately. The all-open
cohort explicitly uses rates/caps=1, unlocked cells/organs and equal existing
positive weights; other genome/profile/model inputs are unchanged. For each cohort
and both seed blocks compare legacy and operative: existing learned readability,
role-aware morphology novelty to holdout, silhouette entropy, parent-copy fraction,
validity/alignment and actual operator counts. Ordinary-rate mean readability loss
must not exceed abs(legacy block A - legacy block B). For all-open capacity, mean
novelty and silhouette entropy must be >= the worse legacy block; parent-copy
fraction must be <= the worse legacy block. Intentional zero/locked controls are
excluded from variation qualification and reported separately. No-op/clone control
must fail the all-open variation clause, random ungated control must fail reliability.
These are declared between-seed sampling controls, not numeric uncertainty estimates.
Normal-rate diversity tradeoffs are reported without claiming them as improvements.

Any G0-G3 failure yields REFUSE consumer promotion, keeps the experimental seam,
and records the precise reopening evidence. No higher-level study is run to rescue
failure and no threshold is retuned after seeing outcomes.

Only after G0-G3 pass, qualify through the consumer: permission-carrier retention
through actual damage/repair; paired adopted evolution at population 256, 20,480
scored evaluations, 24 lifecycle ticks and the three existing DR0052 seed values,
novelty-first selection and explicit slip_admission="insertion". Reproduce DR0056's
first-seed adopted result before trusting the comparison. Zero candidate failures
and illegal elites on every seed; mean coverage/QD costs no greater than measured
legacy three-seed spreads (DR0052 pattern). Zero spread permits zero cost, not an
invented tolerance. Record all attempts, refusals, actual changed descendants,
quality and elapsed runtime against the existing 1,200s/run bound.

After all gates pass, expose explicit named selection coherently through faithful
Workshop preview, hatch, succession and era generation; record it in versioned X5
immutable config/provenance and reproduce from the saved inputs. Legacy saves and
omitted configurations stay legacy. Demonstrate same permission-bearing draft in
preview/hatch/era descendants and accurate trace. No default flip is authorized.

## Pre-measurement clarification (2026-10-06)

Before any scientific run, metric definitions are fixed explicitly: G3 tests each
operative seed block separately; pooling cannot rescue a failed block. Silhouette
entropy is corpus diversity in bits using generation_bakeoff16._entropy_bits over
its silhouette_signature, not the different per-grid readability feature also
called silhouette_entropy. Parent-copy comparison excludes identity, lineage,
trace, rates and permission annotations, while retaining grid size, palette,
structural/rendered cell payload and organ structure. Optional extra diagnostics
cannot affect the registered verdict. This clarification precedes all measurements.

## Execution, verification and bounded outcome

REVIEW -> REPAIR -> ENHANCE -> POLISH; root is sole integration/runner owner.
Disjoint delegation: operator lab/private package seam and tests; scientific gate
harness/tests; root contract/triad/ledger/measurement integration and preservation.
Preregister module rules before measurement, RED before implementation. Focused
iteration does not close the slice. Full sweep, artifact validation, preservation
and diff review are required. A measured REFUSE completes the experiment, leaves
X6 product outcome explicitly open, and permits dependency-ready X7/X8 work with
independent preregistration. Do not replace the queue with cosmetic scope.

## Sources

- AGENTS.md; ONBOARDING.md; CLAUDE.md; sunsetted/TODO.md X6-X8.
- research/reports/2026-10-05-product-design-implementation-checkpoint.md.
- research/package_specs/mecha_engine_generation_contract_gate.md.
- research/decision_records/0042-generation-layer-loop-revisit.md; 0047-slip-admission-arms.md; 0052-slip-admission-default-insertion.md; 0056-adopted-default-headline-restatement.md.
- labs/grid_genome/{constrained_generator,generation_bakeoff_formal}.py.
- packages/mecha_engine/src/mecha_engine/{generation/generate,runtime/evolve,runtime/_damage,repair/wound}.py.
- docs/development/cycle-38-immutable-era-inputs.md; .development/x5/resume.json.

## Bounded execution disposition (2026-10-06)

The registered 1,200-second value is a qualification criterion, not an implemented
execution timeout. No pre-measurement early-stop rule exists. After the first
completed operative run measured 1,966.830335 seconds and therefore definitively
failed that mandatory condition, the parent directed bounded continuation. The
active second operative seed was operationally interrupted; the third was not
started. Four completed runs and two explicitly missing rows are preserved in
`data/archives/operative_evolution_stage0.json`, status `incomplete`. This operational
stop changes no scientific threshold and supplies no missing quality measurements.
Product promotion remains REFUSE, full-cohort quality judgment remains incomplete,
and further measurement is not automatically authorized by this checkpoint.
