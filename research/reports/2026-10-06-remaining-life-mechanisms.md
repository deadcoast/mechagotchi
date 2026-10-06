# Remaining life mechanisms: exact design authority and next boundary

2026-10-06, post-measurement handoff. This is a read-only design/source analysis,
not a new experiment contract or a measured physiology result.

Current owner direction is explicit: **keep food access unchanged in this
implementation**. The earlier unanswered food-access question selected nothing.
Do not add a deprivation switch to obtain extinction. The earned-preparation
stage0 metric retains its earlier pending-question state as dated study history;
this document and `.development/x8-v2/resume.json` give the current direction.

## What the existing design requires

| Requirement | Exact existing passage | Scope established |
| --- | --- | --- |
| Functional bodies | [Research plan, line 323](../../docs/project-research/research.md#L323): “genome → phenotype grid → renderable body → behavioral affordances → survival history → lineage” | The body must affect operation; a descriptor alone does not complete the chain. |
| Semantic organ meaning | [Validity analysis, lines 203–212](../../docs/project-research/validity-research.md#L203) lists “organ role,” “survival relevance,” and “behavioral association.” | Organ semantics are intended to have functional significance. No action-cost equation is specified. |
| Experience and form reach descendants | [Validity analysis, line 73](../../docs/project-research/validity-research.md#L73): “visual form, behavior, memory, survival, mutation, and user-made profiles all influence future generations.” | The care-to-descendant requirement is already designated. |
| Real failure and succession | [DR0021, lines 62–71](../decision_records/0021-game-loop.md#L62): “survival stakes are real engine dynamics, not scripted events”; “successor bloodline carrying only their unlocks.” | Genuine loss and explicit successor play are existing goals; famine is not prescribed. |
| Falsifiable variation | [Product checkpoint, lines 278–285](2026-10-05-product-design-implementation-checkpoint.md#L278) requires deciding species versus individual variation and a “justified falsifiable mechanism before adding it.” | Body differences need an implemented and measured law. Archive neediness cannot be relabeled personality. |
| Preserve evidence while establishing loss | [Product checkpoint, lines 320–324](2026-10-05-product-design-implementation-checkpoint.md#L320): “Preregister what live population/campaign failure means while preserving historical elites”; “Do not delete archive evidence or fabricate deaths.” | A new gate must keep the original criteria, controls and failures. |
| Operational extinction criterion | [X8 contract, line 139](../../docs/development/cycle-38-surviving-populations.md#L139): “Extinction requires real candidate lifecycle deaths in the recorded terminal generation and zero eligible breeders, without injected deaths or archive removal.” | The original 0/10 finding remains refused; fixture handling cannot satisfy it. |

The documents designate morphology-sensitive functioning and real population loss.
They do **not** specify a sensor effectiveness formula, a metabolism equation,
finite reproduction, or food scarcity. [DR0086, lines 50–51](../decision_records/0086-lived-care-context-and-visible-thought.md#L50)
expressly preserves covenant species priors and says “No new personality mechanism
is adopted.” The next mechanism must be declared as a game-design hypothesis,
with evidence before adoption; it is not a biological claim or a previously
specified equation merely waiting to be copied into code.

## What current mechanisms implement, and what they cannot establish

**Needs reset:** [X8 contract, line 17](../../docs/development/cycle-38-surviving-populations.md#L17)
acknowledges independent episodes. Lines 34–49 call v1 a designed generational
replacement mechanism and exclude continuous individual age. `lifecycle/simulate.py:420`
initializes an episode; `runtime/_survival_live.py:104–129` evaluates after repair,
and `_survival_population.py:487–493` starts a separate final episode. This implements
v1; it does not implement accumulated physiological exposure across those episodes.
Calling the reset a bug would contradict the registered semantics. A continuously
exposed candidate would require an explicit new version.

**Repair:** [Repair interface contract, lines 45–50](../package_specs/mecha_engine_repair_interface_spec.md#L45)
requires “never fewer (every site refilled with some live token)” and an original
position set restored exactly. Full positional recovery is an adopted guarantee.
`repair/_grids.py:235–236` creates restored cells with zero stress/damage;
`_survival_live.py:90–129` applies damage, repairs and then evaluates. Thus weather
causes actual damage and repair work, and can change reconstructed tokens. It does
not currently impose persistent injury or an energetic repair burden. Inventing
unhealed damage or weakening this guarantee solely to cause deaths is unsupported.

**Population refill:** `_survival_population.py:422–438` cycles through eligible
parents to create the requested candidate count. It is generational sampling,
not a census of persistent individuals or finite-resource reproduction. Death
does disqualify breeders (`_survival_live.py:163–173`); zero breeders ends evolution
(`_survival_population.py:650–655`). Those implemented paths correctly exclude
dead parents and preserve archives, but partial losses do not create vacant
population slots. A finite-reproduction ecosystem is a larger new model.

**Food:** [Validity analysis, lines 469–479](../../docs/project-research/validity-research.md#L469)
describes the companion action as “ask for food.” Native `game/src/mecha_game/session.py:418–425`
mediates autonomous feed into begging/idle, so the Keeper must supply food.
Population evaluation executes its established switchboard feed directly. The
two paths implement different existing contexts; population measurements do not
establish native care or scarce food. Keep both unchanged in this implementation.

**Body response:** [Lifecycle contract, line 93](../package_specs/mecha_engine_lifecycle_contract_gate.md#L93)
requires initialization from actual grid stress, damage and body mass. The source
reads/stores mass (`lifecycle/simulate.py:205–237`) but derives neediness, sleepiness
and curiosity from the covenant, then uses common drift/action effects at 311–339.
The morphology stress probe (`archive/_metrics.py:187–222`) explicitly leaves
transition and death arithmetic unchanged at 208–212. This is an implemented
starting-stress effect, not an ongoing body/action affordance. It can affect
survival monotonically while leaving fed/neglected candidate rankings unchanged.

The measured record supports these distinctions: original X8 had 152 real stress
deaths across episodes yet every stress trial retained breeders. The new six-era
role/density study had zero lifecycle deaths and 16 final breeders in every era.
Neither result establishes immortality, guaranteed extinction or balanced ecology.

## Smallest coherent next development slice

Preregister and lab-prove **one opt-in body-dependent action response**, shared by
native lifecycle, contextual care evaluation and population evaluation. A concrete
candidate is functional core/locomotion workload affecting the energy cost of
`play`, derived from actual semantic body cells and integrity. This makes an
existing action interact with a body property instead of adding another scalar
starting-stress penalty. Do not silently substitute archive `behavior_neediness`
for personality, or bundle a new sensory-observation model into the same slice.

The candidate equation, normalization, calibration basis, supported body sizes and
eligibility must be named before RED or holdout evaluation. Recompute the same
projection from actual damaged/repaired grids; do not fabricate residual injury,
deaths or repair costs. Preserve current food access, positional-repair guarantee,
death thresholds, independent-episode semantics and fixed-size sampling. Exact
legacy/v1 off-path parity, saved per-life model choice, cold newborns, restart and
immutable reproduction are required. This is a versioned proposed game mechanic,
not default promotion and not an inherited trained Q-table.

First require fixed causal contrasts showing body-by-action sensitivity. For
damage/repair sensitivity, require a response change when the evaluated repaired
body's functional projection changes, and an exact null when that projection is
restored. A transient damaged-body projection that no episode consumes does not
establish production sensitivity. Reject a merely uniform score offset or
unchanged complete rankings.
Only a demonstrated live mechanism justifies fresh, preregistered care descendant
holdouts and a bounded production survival protocol. Keep all v1/v2 refusals.
Extinction is an outcome to observe, never a guaranteed target to achieve by
retuning constants, adding deprivation or searching more seeds. A genuine native
loss → explicit successor → inherited unlocks → next-era demonstration may use
only an actual qualifying outcome under that future contract.

This first slice can proceed under the existing research/development mandate; the
undefined equation is a falsifiable engineering proposal to preregister and test.
No new owner-level food decision blocks it. Retaining explicit v1 sampling and
episode semantics also avoids opening the larger continuous-age or finite-
reproduction design choices. If those later become necessary, surface that
specific change with its gameplay consequences before treating it as adopted.

## Handoff

Finish the current slice from `.development/x8-v2/closing.json` and the runner.
No further scientific trial belongs to its closed 16-stage budget. The next active
integrator should review this boundary, register the single body/action contract,
then delegate non-overlapping lab, lifecycle/native integration and independent
review work. Numerical acceptance criteria and holdouts must be frozen before
measurement. Do not repeat the original refused cohorts or call current X8 complete.
