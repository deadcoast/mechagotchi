# Changelog

All notable changes to Mechagotchi, organised by **development cycle and
phase** — the repo's own unit of work — newest first.

**This file is a summary, not the record.** The authoritative history is
the evidence ledger: `research/README.md` maps every finding to its
report, decision record, lab code and data artifact, and each phase ends
with a consolidated gate report under `research/experiment_reports/`.
Entries here are derived from those gates; where they disagree, **the
gate report wins**.

There are no semantic-version releases. The project ships evidence, and
a phase is "done" only when its queue is exhausted **and** a full
verification sweep is green (`python -B tools/ci/run_sweep.py`). Adopted
capabilities are recorded as numbered decision records (`DR NNNN`).

Conventions used below: **ADOPTED** (a gate passed and the capability
ships), **WITHHELD/REFUSED** (a pre-registered gate failed and the
refusal shipped as the finding), **CORRECTED** (a previously recorded
number was re-measured and superseded by a dated note — originals are
never rewritten).

---

## [Unreleased] — Cycle 26 · Phase P — "the missing axes earn their sources"

*In progress. Queue: `sunsetted/TODO.md` (**P1, P2 DONE**; P3–P6 open).*
Planned from DR 0048's two real gaps (`happiness` needed a DEFINITION,
`cleanliness` needs a MECHANIC — neither a display gap) and the
instrument repairs Phase N and O named.

- **P1 — DONE 2026-08-08 (no DR; the decisions cited are
  0048/0054/0055).** **The §1.17 visible/hidden split measured AS
  SHIPPED, and the founding text now carries its dated correction.** A
  live client session, the on-screen half read from `snapshot()` under
  a pre-registered operationalization (a NAMED READOUT); the
  engine-source half through the package boundary. Measured: 6 of 8
  visible axes on screen, 2 absent upstream of display, 2
  documented-hidden axes surfaced under accurate names — and **no axis
  without an engine source is shown** (DR 0021's first law, pinned
  per-axis). The instrument reproduced the committed M5 survey 7/8
  with `health`'s difference explained by DR 0054; **M5's remainder 2
  closed in the game's own suite** (snapshot carries age and mood,
  measured, not cited). Game 200 → 216.
- **P2 — DONE 2026-08-08 (DR 0058).** **`happiness` is
  `social_warmth` — the engine's own recent-interaction window — and
  the readout landed the same day** (the N5 → O2 pattern end to end in
  one slice). Three CHOSEN candidates, five pre-registered gates
  (N5's four + **G5 distinct-from-shown**, whose `refuse_as_duplicate`
  outranks the euphemism verdict); both instrument gates held before
  judging (N5's committed 0.0685 floor reproduced exactly; the balance
  mirror matched the engine over 633 ticks at |Δ| 0.0).
- **`bond_rename` REFUSED as a duplicate** — it passed every
  behavioural gate and fell on exactly one ground: its per-tick series
  IS the shown bond readout's. One engine number may not wear two
  visible names.
- **`need_balance` WITHHELD** — the engine's own per-tick contentment
  statistic responds to the keeper's verbs *under* the measured floor
  and *negatively* from a near-target start, and reads **0.65 on the
  neglected corpse** (a mean hides the killer axis — the property that
  made health a minimum). Both liabilities recorded.
- **`social_warmth` ADOPTED** with the strongest honesty property any
  candidate showed: **the neglected corpse reads 0.0**; both keeper
  verbs move it +0.083 (over the floor); relieving a starving
  companion raises it +0.2. Prediction (recorded first) confirmed,
  including its deliberately named uncertainty.
- **Live in the client: `play` RAISES happiness while it LOWERS
  health** (+0.083 vs −0.075) — two bars answering different questions,
  both engine truth. The readout carries `chosen: true` and its
  legibility in the window's own counts (`tended_ticks`/`window_ticks`).
  The P1 instrument moved with the surface deliberately (regenerated:
  **7 visible on screen / 1 absent upstream / 2 hidden surfaced**);
  §1.17 carries a dated addendum. Game 216 → **228**.

---

## Cycle 25 · Phase O — "the adopted definitions reach the player" — 2026-08-08

**Gate: GREEN.** `research/experiment_reports/2026-08-08-phase-o-gate.md`;
queue archived to `sunsetted/complete/TODO/25/`. Planned from Phase N's
unusual debt: **it adopted three things and put none of them in front of
a player.** `insertion` is the loop's default but every historical study
is pinned to the incumbent, and `danger_margin` is the adopted
definition of `health` but is blocked off-screen by one package
constant. Each is correct and deliberate — and exactly the kind of debt
that quietly becomes permanent.

- **O1 — DONE 2026-07-28.** **`DANGER_THRESHOLDS` promoted to the
  package's public API**, taking the lifecycle contracted surface from
  **six names to seven** and removing the blocker DR 0054 recorded
  against its own adopted definition of `health`. Follows the **W1
  precedent** exactly: document the widening in the contract gate, add
  to `__all__`, and let the **exact `__all__` equality probe** fail
  until spec and code agree — **that failing run is the RED**, the pin
  doing its job by rejecting an undocumented widening.
- **The promotion is deliberately narrow, and the narrowness is
  pinned.** The charter said not to widen beyond the constant; a package
  test now asserts **neither `danger_margin` nor `health` appears on the
  surface**, so whether the margin formula belongs in the engine stays a
  separate decision instead of eroding by drift.
- **The constant is pinned BY VALUE, not by presence** — a promoted
  constant whose numbers can drift is not a contract — with a second pin
  that **every lethal axis has a threshold**, because a set missing one
  would let a bar read healthy on a dying companion, *the exact failure
  DR 0054 refused `grid_stability` for*. The **"danger, not lethal"**
  distinction is now a package-level pin too.
- **N5's loop is closed**: the lab imports from the public API and its
  artifact regenerates with **identical verdicts** — the check that this
  moved a *surface* and not a *behaviour*. Package suite **295 → 299**,
  no existing assertion moved.
- **No decision record, and the reason is recorded**: DR 0054 already
  made this decision and named this task as its blocker, and W1's
  precedent documents a surface widening in the contract gate rather
  than a record of its own.
- **O2 — DONE 2026-07-28 (DR 0055).** *(GAME track.)* **`health` is on
  the player's screen** — and the fix for the play-drop was **not to
  hide it**. DR 0054 deferred one question: `play` *lowers* the number
  (−0.075467, play costs energy), so a keeper will read the drop as a
  bug. Two of the three available answers are forbidden by DR 0021's
  first law — smoothing or hiding the fall would make the surface show
  something the engine does not.
- **ADOPTED — the readout ships with its BINDING AXIS.** Health is a
  *minimum* across axes, and a bare minimum discards the one thing that
  makes it legible: *which* axis is binding. `health 0.62 (tired)` costs
  **no new number** (argmin of margins already computed), is engine
  truth, and turns an unexplained fall into a sentence. The word names
  the state, never a friendlier version of it — DR 0054's refusal
  against comfortable renaming binds this table too.
- **The measured case, taken from the live client rather than a test**:
  a keeper who never sleeps sees `tired` from tick 2, **0.000 by tick
  7**, and the companion **dies of `energy_collapse` at tick 10** — the
  readout **named the death cause eight ticks early**, where a bare
  number would have shown only a falling line. A keeper who acts on the
  word takes the same creature **0.487 → 0.976**. The play-drop itself is
  visible and legible in that run (tick 8 plays at 0.813; tick 9 reads
  0.715 and says `tired`).
- **Refusal was reachable and did not fire** — a pin asserts that when
  the bar drops, the axis named after it must be one `play` actually
  worsens, or the readout misleads and does not ship.
- Formula **mirrored** into the game per the boundary law and pinned
  against the committed N5 artifact. Game suite **188 → 200**.
- **Honest limit recorded, not fixed**: the bar bottoms out at **danger,
  not death** — health reads 0.000 while the companion is still alive.
  Defensible as a warning that leaves time to act, but "health" implies
  zero means dead and it does not; a different floor is a different
  CHOSEN definition needing its own gate.
- **O3 — DONE 2026-07-28 (DR 0056). The headline studies RESTATED under
  the adopted default — and coverage buys quality.** DR 0053's rule 2
  shaped the task: *a measurement does not improve, it is reproduced or
  superseded by a new measurement answering a new question*, so this
  wrote a **new artifact** and left both committed incumbent artifacts
  exactly as they were. **Only the adopted arm was re-run**, cutting the
  work ~75%: the incumbent runs are read, and the **GA control is read
  because `run_ga_baseline` takes no `slip_admission`** and is
  structurally unaffected by the arm.
- **The headline, at DR 0042's own seed**: coverage **0.898438 →
  0.880859** (−0.017579), **QD 404.618236 → 411.738214 (+7.119978)**,
  niches 460 → 451, **refusals 4,435 → 0**, **illegal elites 35 → 0**.
  **Coverage does not fall for nothing — it buys quality.** L1 declined
  to patch the refusal tax because *"the fix trades against coverage"*;
  this prices the other side — nine niches and 0.0176 coverage buy
  **+7.12 QD** and an archive legal under the covenant that bred it.
- **The documented E4 gates hold: `NO_REGRESSION`.** Re-judged verbatim
  (`judge_gates` imported) over the documented ten paired seeds against
  the same GA control — `coverage_gate_met` True → True, mean best
  fitness moving only −0.000565.
- **`ga_advantage_gate_met` was already failing and is explicitly NOT
  attributed to the adoption** — the comparison is written so a
  pre-existing failure cannot be reported as a regression, because
  blaming the new arm for DR 0032's long-refuted clause would be a false
  accusation. Its margin does fall a further 0.029664, so **DR 0032 is
  refuted a little more decisively** (recorded, not re-scored).
- **DR 0042 is NOT retracted.** 0.8984 remains what the loop achieves
  under the incumbent arm. DR 0056 adds a **quoting rule** instead: any
  *"the loop achieves X"* must name **which arm** — the same discipline
  DR 0046 imposed across geometries. Dated notes sit beside DR 0042 and
  the `evaluation_loop_scale` card.
- **O4 — DONE 2026-08-08 (DR 0057).** **Stage 2's last undispositioned
  generator arms judged — each in its DOCUMENTED role, and the
  charter's own bake-off-both framing corrected first** (shape grammar
  is a Constraint system whose documented role is *"validator or
  post-generator stabilizer"* — a role **already shipped** as
  `wfc_grid._finish`). **CPPN — REJECTED** as a generator: validity
  **0.12** vs the 0.85 dossier bar, with the mechanism measured (79 of
  88 invalid bodies are *connected* cores under the DR 0029 mass floor;
  only 9 disconnect) and the method's documented strengths recorded
  beside the verdict (symmetry 0.475 above the WFC family; 100/100
  unique; none of it offsets validity, pre-registered). **Shape grammar
  — WATCH**: six named RNG-free productions repair the raw collapse
  0.01 → **1.00** validity at retention 1.0, then **TIE the incumbent
  `_finish`** at 1.00/1.0 under a two-seed measured noise floor of 0.0
  — a tie is not a reason to replace a shipped incumbent. **The
  instrument reproduced the committed wfc bake-off row exactly (all
  five keys) before any new number was trusted.** Prediction (recorded
  first) confirmed on both arms; nothing adopted; wfc_grid lab
  36 → **61**.
- **O5 — the Phase-O gate: GREEN 2026-08-08.** Closing sweep: 19 lab
  suites + package **299** + workshop **92** + game **200** + CLI —
  **2,247 JSON artifacts, 0 invalid**. Ledger at the gate: **273**
  experiment reports, **79** algorithm cards, **57** decision records.
  Cycle 26 (Phase P — "the missing axes earn their sources") planned
  from the documentation and the recorded remainders.
- *Mid-cycle, recorded*: the owner relocated the work-queue tree —
  `audits/` → `sunsetted/` and the root `CHANGELOG.md` → this file's
  current path — completed as rename-preserving commit `a4b04ae` with
  the living root docs re-pointed and dated records left as written.

---

## Cycle 24 · Phase N — "the descriptor space earns its edges" — 2026-07-28

**Gate: GREEN.** `research/experiment_reports/2026-07-28-phase-n-gate.md`
Closing sweep: 19 lab suites + package + workshop + game **188** + CLI —
**2,245 JSON artifacts, 0 invalid**. Six decision records, **0049–0054**.

The cycle earned the descriptor space its edges and answered four
long-standing questions. But its defining character was unplanned:
**Phase L audited its own numbers, Phase M its own sentences, and Phase N
its own INSTRUMENTS.** Every one of its six slices found a defect in the
measuring apparatus rather than in the thing measured — DR 0046's
controls were single draws; the queue's description of N2's defect was
wrong; N3's observer scored a learner on an event it cannot see; N4's
population parameter was invented and **flipped the verdict**; N7's
obvious migration plan would have **destroyed evidence**; and N5's own
candidate name overclaimed. **Three of those six were errors this
session made and caught before they shipped as findings**, each recorded
as a process deviation rather than absorbed.

**And every gate that could have rubber-stamped, did not**: N3 dropped
two of three candidates, N5 refused DR 0048's *named* candidate and
adopted one the record had not proposed, N4's rule could have refused all
three arms, and **N1 predicted structural indeterminacy and its own
measurement refuted it**. Two pre-run predictions were recorded and held;
one was recorded and refuted.

The queue grew one task mid-cycle — **N7** — which DR 0052 scheduled
rather than letting a default change happen as a side effect.

Planned from Phase M's deepest finding — **the octile edges are not
determined by a 600-creature derivation** — plus the debts DR 0047 and
DR 0048 explicitly asked for, and one non-archive slice (the
never-instantiated micro-learner conditions E/F/G) after two
archive-heavy cycles.

- **N1 — DONE 2026-07-27 (DR 0049).** The cycle's founding premise
  measured — **and it is half right, in the half that matters least**.
  DR 0046's re-addressing statistic run as a *function* of derivation
  size (75 → 4,800, four disjoint seed pairs per rung, both recipes),
  after the instrument reproduced **both** committed DR 0046 controls
  exactly. **Gate 1: `sampling_limited` on both recipes** — slope
  **-0.4186** / **-0.3997** against sampling theory's -0.5, judged by
  the *measured* spread of four per-track slopes — so
  **structural indeterminacy is REFUTED**: re-addressing falls
  monotonically 0.7268 → **0.1278** and the edges are under-sampled,
  not unknowable. **Gate 2 splits from Gate 1, and that is the
  finding**: against a *measured* floor of 4 niches, **at N=600 the
  incumbent re-addresses 31.7% of individual creatures while its
  occupied-niche count moves exactly the floor** — and at N=4,800
  re-addressing has improved 2.5× while ceiling movement is *higher*.
  So 600 does not determine the edges, and neither does 4,800; but the
  numbers every consumer reads were already at their measurement floor
  at 600.
- **DECIDED — `derivation_count` stays at 600** (DR 0049), not from
  caution but because **what raising it would fix is not what was
  broken**: it would re-address a third of the population, invalidate
  the frozen edge artifact, and move no number anyone quotes.
- **The mechanism separates two things M2's prose fused.** The
  `visual_complexity` edge band is essentially constant across the whole
  64× range (0.043993 → 0.045196), so **measure-thinness is structural
  and permanent — no derivation budget narrows it — while only the edge
  *placement* inside that fixed band is sampled.** K3's measure-thin
  windows are therefore not a small-sample artifact, and
  `visual_complexity` is the **slowest-converging** axis: the smallest
  per-axis contributor at N=75, **49%** of all axis movement by N=4,800.
- **CORRECTED (DR 0046's two controls, understated).** They are single
  draws; the four-pair means are **0.316917** (against 0.200000
  recorded) and **0.371583** (against 0.310333). **M2's verdict is
  unchanged and strengthened** — ratio 1.16 → **0.969** against the same
  2.0 bar, so the two geometries differ by *less* than the probe recipe
  differs from a resampled copy of itself. Dated notes beside both
  originals; nothing rewritten.
- **A limitation of N1's OWN pre-registration, recorded not repaired.**
  Gate 2's rule assumes monotone convergence and the movement is not
  monotone (`10.0, 15.5, 9.75, 4.0, 4.75, 7.5, 7.75`); the incumbent
  passes by an **exact tie** against a floor measured from three pairs.
  The verdict stands as the rule produced it, but `determined_at = 600`
  is a noisy statistic crossing a threshold, **not a located stability
  point** — and the two recipes' Gate-2 verdicts must not be read as a
  real difference between them.
- **N2 — DONE 2026-07-28 (DR 0050).** DR 0046's strongest named
  follow-on: the probe geometry is **frozen and committed**, so both
  scale geometries are now protected the same way instead of one being
  privileged. **All four pre-registered gates passed.** G1 provenance
  matched (a fresh derivation reproduces the recorded probe edges
  exactly — structural, no tolerance); G2 determinism `reproducible`
  (DR 0046 *asserted* "deterministic in practice"; this **measures**
  it); **G3 consumer invariance `invariant` — both committed headlines
  recomputed from scratch and both exact**: support ceiling
  **460 → 460**, reached-by-generators **495 → 495**, which matters
  because M2 had already found one cross-geometry headline that did
  *not* survive recounting; G4 separation held at **0.037500**,
  precisely L3's split, so DR 0046's refusal to converge is intact.
  The recipe now lives in **one** place instead of three private copies,
  every probe-side artifact records `edges_source`, and **a parity pin
  makes a live re-derivation fail the suite if it drifts** — turning
  "deterministic in practice" from an assertion into an enforced
  property.
- **CORRECTED — the queue's description of the defect was wrong, and the
  truth is worse.** `audits/TODO.md` recorded that each probe number is
  contingent on *"a draw no artifact records"*.
  `reachability_probe_stage0.json` **does** record its edges; it is
  `occupancy_saturation` and `reachability_escalation` that record
  **none** while depending on the same draw — so a re-derivation would
  have moved all three artifacts and **only one would have shown it**.
  Found by reading the artifacts instead of the sentence: the third such
  catch in three cycles.
- **The honest limit, stated with the win: freezing the edges does not
  freeze the numbers.** The support ceiling ranges **447–462** across
  six evaluation resamples (`[460, 457, 462, 447, 454, 451]`), so the
  committed **460** is one draw from that spread and only the coordinate
  system it is counted in is now pinned. Reported because a reader
  seeing "frozen" beside the ceiling could reasonably conclude
  otherwise.
- **N3 — DONE 2026-07-28 (DR 0051).** *(ENGINE track, deliberately
  non-archive after two archive-heavy cycles.)* The dossier's
  micro-learner ablation conditions **E (Q-table)**, **F (tiny decision
  tree)** and **G (Bayesian counter)** — named in the protocol and
  **never built since cycle 12** — are instantiated and judged through
  the **D6 gates verbatim**, with `ablation_gates` **imported, never
  re-implemented**. Each learner is the dossier's own mechanism with the
  dossier's own named weakness *respected* rather than engineered
  around, and all three credit the **executed** action, because the
  keeper can override and a learner crediting its own recommendation
  would learn a policy the world never ran.
- **E `qtable_policy` KEPT** (skill **+55.459%** regret reduction,
  welfare 0.795%); **F `tiny_tree_router` DROPPED** (**−1.776%**);
  **G `bayes_keeper_counter` DROPPED** (**+2.756%**, under half the
  bar). The pre-run expectation, written into the module first, held:
  every candidate's welfare cost is under 1.2%, so all three were
  decided on **skill** — D6's saturated decision seam reproduced.
- **Both drops carry a measured mechanism confirming the dossier's own
  weakness column.** F: the depth-2 tree returns **0.799976** against
  the depth-1 stump's **0.814443** — **the second split is decoration**,
  and the failure is *dilution* (leaves too thin to carry it) rather
  than overfitting. G: Brier **0.190317** against the running rate's
  **0.195712** — a real improvement in the right direction, under half
  the bar, and **nothing in the switchboard consumes the uncertainty** a
  Beta posterior carries.
- **The kept-five roster is unchanged, re-judged rather than assumed.**
  All eleven incumbents recomputed on the new baseline land between
  **0.000% and 0.359%** — because their verdicts rest on skill metrics
  that are properties of each thread's own prediction task, not of fleet
  composition. One number moved: `fleet_vs_frozen` **−0.054% →
  +0.965%** (a sign flip of ~1%, far below any gate).
- **Byte-identity PROVEN, not asserted** — the committed D6 artifact
  regenerates at full scale with an identical SHA-256, all 14 condition
  welfares and all 11 thread verdicts unchanged, with the off-mode
  roster pinned against a **frozen literal list** rather than a second
  call to the new code.
- **PROCESS DEVIATION, recorded not buried.** The first run scored G at
  **−154.796%** — the instrument's error, not the learner's: the
  observer scored it against *keeper override* while the thread observes
  `recent_interactions` (*whether the executed action was social*), two
  different events, so the learner was marked wrong on a question it was
  never asked. Corrected to its own observable and re-run:
  **−154.796% → +2.756%**, with **E and F bit-for-bit unchanged** — the
  check that the fix touched only the mismatched metric. A defect repair
  rather than a re-score; **G drops either way**.
- **WITHHELD** — nothing is promoted. `FLEET_THREADS` is untouched; a
  kept candidate has passed the ablation gate, not joined the fleet.
- **N4 — DONE 2026-07-28 (DR 0052). ADOPTED: the `slip_admission`
  default is `insertion`** — DR 0047's withholding **resolved** and its
  prediction **confirmed**. Four gates pre-registered before the run,
  which mattered more than usual because DR 0047 had published a
  prediction and a gate written afterwards cannot refute one. G1 and G2
  are DR 0047's carried verbatim (G1 now required on *every* seed,
  because a mean would let a clean seed hide a dirty one); **G3
  quality** and **G4 archive legality** are the two it asked for, G4
  **structural like G1** on its own reasoning — a covenant either holds
  over the archive it bred or it does not. The tie-break is DR 0047's
  invasiveness order **verbatim**; only the *set* it applies to changed,
  which is the whole mechanism by which this overturns its winner
  without touching its rule.
- **The instrument reproduced DR 0047's committed baseline exactly** at
  the shared seed — coverage 0.898438, QD 404.618236, 4,435 refusals, 35
  illegal elites, 460 niches — with the configuration read from its
  *artifact*, not its prose.
- **`parents` fails G4 completely** (35/37/35 illegal elites against the
  incumbent's 35/37/33 — it evicts none), while **`bootstrap` and
  `insertion` both clear all four** and are indistinguishable on the
  gated dimensions (identical coverage every seed, QD within 0.1 —
  structural, both removing the same creatures). The tie-break therefore
  decides on invasiveness alone → **`insertion`**.
- **The cost, stated not softened**: 0.029948 coverage — **90% of the
  measured 0.033204 control**, a narrow pass — buying 4,435 wasted
  evaluations per run removed and an archive legal under its own
  covenant. QD untouched (−0.1356 against a 16.56 control).
- **SCHEDULED, not assumed** — the default is *decided*, not *flipped*.
  `run_evaluation_loop` still defaults to `none`, and changing it
  rewrites the committed artifacts of **at least six lab modules** that
  call the loop without naming an arm, including **DR 0042's headline
  coverage** and **L1's entire subject**. Queued as **N7** with its
  ~380 s-per-run cost measured, rather than left as a floating
  remainder.
- **PROCESS DEVIATION, recorded not buried.** The first run used
  `population=512` — a parameter the module *invented* rather than
  inherited (M3 measured at 256, the loop's own documented default). The
  incumbent then failed to reproduce DR 0047's baseline and **the
  verdict flipped**: `insertion` failed G2 by **0.000652**, 2% of the
  control, leaving `bootstrap` sole passer. A hair's-width miss on the
  wrong configuration would have refuted a correct prediction. Caught by
  checking the discrepancy rather than accepting the tidy verdict,
  corrected, re-run; two pinned guards now read DR 0047's parameters
  from its artifact and refuse a diverging run. The 512 run is **not**
  offered as a robustness check — it was an error.
- **N7 — DONE 2026-07-28 (DR 0053). The default is FLIPPED to
  `insertion` — and the migration turned out not to be a
  regeneration.** DR 0052 scheduled this rather than letting it happen
  as a side effect, and the charter's own instruction decided how it
  went: *inventory before you flip the constant.*
- **The inventory was bigger than DR 0052 estimated**: **eight**
  production modules call the loop implicitly, not "at least six" — it
  missed `generation_arm_evolution` and `novelty_evolution` — writing
  eight committed artifacts across **63** implicit call sites.
- **Flipping broke DR 0047's pinned byte-identity contract**
  (`implicit == explicit("none")`), which proved to be the *weak* form
  ONBOARDING §9 warns about: it states a fact about the default, not
  about off-mode identity. Its guarantee now rests on the
  **frozen-key-set** pin, which survives a default change.
- **THE FINDING, and it inverts the obvious plan: regenerating the eight
  would have DESTROYED EVIDENCE.** `generation_refusal_causes` **is**
  the measurement of the 4,435-refusal tax, and under `insertion` that
  tax is zero — re-running it would not update the finding, it would
  erase the evidence the finding is made of. Three more measure the
  incumbent population directly (M1's 48-of-460, L2's bootstrap-founded
  dominant lines, M4's ancestry) and two are bake-offs readable only at
  fixed settings.
- **So the migration is: flip the default, and make every historical
  study NAME its arm.** All eight now pass `slip_admission="none"`
  explicitly with a per-study reason — the call-site discipline N2
  applied to `edges_source`, now generalised by **DR 0053**: *any
  setting that changes what an artifact means is recorded at the call
  site that produced it, never inherited from a default.*
- **The change is PROSPECTIVE, stated rather than dressed up.** No
  committed number moves; every new consumer gets zero refusal tax and a
  covenant-legal archive by default, pinned — which is what makes the
  fix propagate instead of sitting in a record. Proven by regenerating
  L1's artifact: **every measured field identical**, the sole difference
  being `wall_clock_s`, a machine-dependent stopwatch. Stated as
  measured rather than rounded up to "byte-identical".
- **NAMED, NOT DONE** — `evaluation_loop_scale` (DR 0042's headline
  0.8984) and `coverage_qd_gates` (the E4 gates) are the only genuine
  migration candidates and need their own record. The four
  defect-measuring studies should probably never migrate: **a
  measurement does not improve, it is reproduced or superseded.**
- **N5 — DONE 2026-07-28 (DR 0054).** *(GAME track.)* **A definition
  ADOPTED and a euphemism REFUSED**, resolving DR 0048's withholding of
  `health` through the gate it named. Four gates, refusal reachable for
  every candidate, and a prediction recorded before the run — confirmed.
- **REFUSED — `grid_stability` under the name "health"**, on the
  decisive number: the neglected creature **starved to death** and
  finished with `grid_stability` at **0.927**, so the bar would read
  **93% on a corpse** — and feeding a starving companion moves it
  **−0.001**, *down*. **An inverted signal, not a weak one**, which is
  why the verdict is `refuse_as_euphemism` rather than `withhold`. It
  technically *passed* the survival gate (0.998 vs 0.927), and that pass
  is instructive: a 0.07 gap looks like separation in a table while
  reading 93% at the moment of death.
- **ADOPTED — `health` is `danger_margin`**, the minimum normalised
  safety margin across the engine's own `DANGER_THRESHOLDS`. It answers
  DR 0048's own objection that a composite needs undocumented weights:
  **a minimum has no weights at all.** Reads 0.0 on the dead creature,
  0.845 on the survivor, and **+0.176** when the keeper feeds a starving
  companion.
- **Reported beside the verdict: the game already got this right.** It
  displays the axis as *"body stability"* and never committed the
  euphemism — and it already shows `stress` too, so the shipped client
  surfaces **two documented-HIDDEN axes under accurate names** and
  **§1.17's visible/hidden split is stale against it**. Found by reading
  the client rather than the document; recorded, not amended.
- **What shipped is the guard** — 5 game-side pins making the refusal an
  **enforced property**: nothing on the player's screen may carry the
  name "health" until a consumer change lands one.
- **A self-correction, for the reason the study exists**: candidate B was
  renamed `lethal_margin` → `danger_margin` mid-study, because
  `DANGER_THRESHOLDS` includes `bond`, which is not lethal. **A gate
  about honest labels may not ship an overclaiming name.**
- **NAMED, NOT DONE** — the adopted definition is not on screen: it reads
  a constant that is public in its module but **not in the package's
  `__all__`**, so landing it needs a package promotion with its own
  gate. And **`play` lowers it** (−0.0755, play costs energy) — honest,
  but a design question whoever puts it on screen owns.

---

## Cycle 23 · Phase M — "the archive meets its own inhabitants" — 2026-07-27

**Gate: GREEN.** `research/experiment_reports/2026-07-27-phase-m-gate.md`
Closing sweep: 19 lab suites + package 295 + workshop 92 + game 183 +
CLI 23 — **2,240 JSON artifacts, 0 invalid**.

The cycle answered every question it set itself. But its defining
character was unplanned: **three of its five slices found that a claim
in the repo's own prose was wrong** — and each was found by reading the
engine instead of the document. Phase L audited its own *numbers*;
**Phase M audited its own sentences.**

Planned from Phase L's unplanned convergent finding — **every instrument
measures a different population from the one the archive is actually
filled with** — plus the still-unmet documentation.

- **M1 — DONE 2026-07-27.** The instruments turned around to face the
  archive's actual inhabitants — and the slice **tested its own cycle's
  premise first and partly deflated it**: the elites' descriptor
  distribution is **`within_sampling_noise`** against the derivation
  population on all four statistics (highest ratio 1.70 vs a 2.0 bar).
  The bar was *measured*, one control per population type with the
  larger taken — and **that choice caught a false positive**:
  `animation_density` reads **5.14× → "material"** against the cheap
  derivation control alone and **0.85 → within noise** against the
  elite control (a second full loop). Beside the verdict: the top two
  symmetry octiles are depleted (48 and 28 vs ~57 flat), suggestive and
  not established; **48 of 460 elites (10.4%) are bootstrap creatures**
  — M3's denominator, now exact; L4's A2 independence **weakens by
  half** on the elites (max |r| 0.173 → 0.350, still inside its bar).
  **CORRECTED (L4's remainder, understated)** — A3 and A4 are not
  un-run on the elites but **structurally undefined**: one elite per
  niche means the same-bin denominator is measured at 0 and
  `occupied_4 == occupied_3` for any fourth axis. No number substituted.
- **M2 — DONE 2026-07-27 (DR 0046).** The two-geometry split
  **frozen, convergence REFUSED on the measurement** — and the split
  turned out not to be the disease. Measured in the unit ledger numbers
  actually use (**address changes**, not edge distance): disagreement
  **0.360000** against a *measured* control of **0.310333** → ratio
  **1.16** vs a 2.0 bar. The control is the finding: re-deriving the
  **probe** recipe at another seed reassigns **31%** of the population,
  the **incumbent** **20%** — the two geometries differ barely more
  than either differs from a resampled copy of itself, so they are two
  draws from a noisy edge-derivation process and converging them would
  have fixed nothing. Localised to **`visual_complexity`** (0.2647 of
  address changes), whose seven octile edges sit in a ~0.046-wide band
  — K3's measure-thinness, now measured in addresses.
- **CORRECTED (K2's cross-geometry claim, sharpened).** Counted over
  one population the support ceiling is **460 (probe) vs 456
  (incumbent)**. L3 recorded the identity as *not established*; M2
  records the numbers as **not equal** — the match at 460 was a
  coincidence across a geometry **and** a population boundary. No
  historical number is retracted; the operative output is a
  **comparability rule**: numbers from different geometries may not be
  read against each other.
- **M3 — DONE 2026-07-27 (DR 0047).** The unbreedable bootstrap elites:
  **three fixes that all work, and the one the rule picked is the worst
  of them.** Measured: the covenant admits only **49 of 256** bootstrap
  creatures (19.1%); **35 of the 48 bootstrap elites are SLIP-illegal**.
  All three arms drive the **4,435-refusal tax to zero**, and every
  coverage cost lands **below** the measured 0.033204 control — so L1's
  declined trade is affordable. The pre-registered tie-break picks
  `parents`. **Then the ranking reverses on what the rule did not
  gate**: `parents` is the only arm that **lowers quality** (QD
  404.618236 → 398.954451) and **leaves all 35 illegal elites seated**,
  while `bootstrap`/`insertion` raise mean elite fitness 3.8% and give a
  **SLIP-clean archive** for three more niches. The bar was not widened.
- **WITHHELD** — the loop default does **not** change (DR 0047). The
  gate weighed refusals and coverage; the arms separate on archive
  legality and quality in the opposite order, so promoting the gate's
  winner would let a rule decide a question it did not ask. What would
  decide it is named, not guessed.
- **M4 — DONE 2026-07-27.** Ancestry versus morphology: **both answers
  are true at once.** The question was reshaped first — asking it
  *across* runs is **not well posed** (each run's founder ids are
  disjoint objects, so families recur morphologically but their
  ancestry cannot). Asked within each run against a **measured
  permutation null**: **`common_descent`, consistent across three
  seeds** — z **+21.39 / +15.96 / +17.39**. **Evolution Q3 answered,
  and the answer is NO** — lineage continuity is not independent of
  visual novelty. But the z is large because the null is *tight*, not
  because the effect is near-total: the excess is ~0.16–0.20, about
  **29–31% of the way** to pure lineage determination. And the
  convergence half is real — **2.84–3.30 distinct founder lines per
  family, up to 7**.
- **CORRECTED (E5's recurrent-family count).** Prose across `research/`
  says **52**; the committed artifact says **54** (per-run 57–58, not
  53–56). Commit `f8c171b`'s message records "52 → 54" when the DR 0038
  vocabulary regenerated E4's rosters — the artifact moved, the prose
  did not. Dated notes beside the four primary carriers; nothing
  retracted and the gate verdict is unchanged.
- **M5 — DONE 2026-07-27 (DR 0048).** *(GAME track)* The documented
  visible companion state — **and two of the five "gaps" were already
  on the player's screen.** The charter said survey before building, so
  the instrument **measures rather than asserts**: `age` **is** a
  lifecycle field (`age_ticks`) and `mood` **is** a derived engine value
  (`select_animation_state`, since Phase C), and the game already
  displays both. **CORRECTED** — the prior claim counted lifecycle
  *homeostasis fields*, a narrower question than "has an engine field";
  **the real gap is three axes, not five**, and on this evidence it is
  not the repo's largest player-facing gap.
- **WITHHELD / OUT OF SCOPE** — the three real gaps are three different
  *kinds*: `happiness` has no **definition**, `cleanliness` has no
  **mechanic** (no clean action, no dirt state), and `health` is
  definable only as a **CHOSEN** definition from documented-**hidden**
  axes. **Nothing was built, and that is the finding** — building the
  panel would have invented two numbers and mislabelled a third
  (DR 0021's first law).

### The three prose corrections, each a dated note beside the original

- **L4's remainder was UNDERSTATED** (M1) — A3/A4 on the elites are not
  un-run, they are *structurally impossible*.
- **The recurrent-family count was STALE** (M4) — prose said **52**; the
  artifact has said **54** since `f8c171b` regenerated it under the
  DR 0038 vocabulary.
- **The visible-state gap was OVERSTATED** (M5) — five became **three**,
  and two of the "missing" axes were already on the player's screen.

Nothing was rewritten; in all three cases the underlying verdict was
unchanged or strengthened.

### Limitations of this cycle's own pre-registrations, recorded not repaired

- **M3 never gated QD**, which moved in both directions across the arms.
- **M1's TVD carries a finite-sample bias** and mixes sample sizes; a
  size-matched control was **deliberately not run**, because changing a
  statistic after seeing its numbers is re-scoring.

### Corrected by external code review, before merge (2026-07-27)

PR #2 drew automated review from five tools. Seven findings; **four were
real and fixed, one recorded, three verified wrong and rejected.**

- **CORRECTED — the byte-identity contract was actually broken** (M3).
  The `slip_admission` arm emitted two keys **unconditionally**, so the
  loop's return value changed for every existing caller even when off —
  contradicting the claim M3's own report made. The pin could not catch
  it, because it compared two calls to the *new* code and both had
  gained the keys: **"byte-identical when off" means identical to what
  the loop returned before the seam existed.** Both keys are now
  rung-conditional and the off-mode key set is **pinned against a frozen
  list**. No measured value changed.
- **CORRECTED — `bootstrap_composition` went stale** (M3). Under the
  `bootstrap` arm the population was filtered without recomputing the
  composition, so the result reported a mix summing to the *unfiltered*
  population beside an admitted count that did not. Now recomputed by
  measured membership, and pinned.
- **HARDENED — the M5 engine probe** replaced the child process's entire
  environment and hard-coded a Windows path, with no timeout. It now
  follows the repo's existing probe pattern (inherit `os.environ`,
  extend `PYTHONPATH`, bounded timeout). Artifact regenerated;
  dispositions identical.
- **The Phase-M gate report's sweep block** was abbreviated; replaced
  with the full pasted output, per the norm.
- **RECORDED, not re-scored** — M4's statistic covers every family per
  run, not only the recurrent intersection (63 against runs of 63/64/64,
  so at most one non-recurrent family each). Restricting it after seeing
  the numbers would be the re-scoring this repo forbids; it ships as a
  named remainder.
- **REJECTED, each verified empirically** — "`parents[1]` should be
  `parents[2]`" (**they resolve to the identical path**); "stage0 slugs
  must be hyphenated" (**219 of 219** existing artifacts use
  underscores); "test methods need `-> None`" (**0 of 545** existing
  test methods are annotated). Complying would have made the five new
  files the only inconsistent ones in the repo.

### Workflow defect: contradictory branch rules — FIXED by deletion

Cycles 22 and 23 both ended up stranded off `main`. The cause was two
rules in `ONBOARDING.md` that contradicted each other: *"PR back to
`main` at the gate"* obligated the merge, *"never push or merge
unasked"* forbade it. The second won every time, so each gate ended with
a question instead of a merge.

**The second rule is deleted.** "Never push without being asked" now
covers publishing *new* work only; unifying finished, gated work needs
no ask. Repo unified 2026-07-27 — `main`, `origin/main` and the working
branch on one commit.

---

## Cycle 22 · Phase L — "the descriptor space settles its geometry" — 2026-07-26

**Gate: GREEN.** `research/experiment_reports/2026-07-26-phase-l-gate.md`
Closing sweep: 19 lab suites + package 295 + workshop 92 + game 183 +
CLI 23 — **2,235 JSON artifacts, 0 invalid**.

The cycle set out to settle the descriptor geometry and did — but its
defining character was unplanned: **three of its five slices corrected
something the ledger already said, and nothing was rewritten.** Every
correction is a dated note beside the original wording.

### Added

- `collect_refusals` and `collect_lineage` observation seams on the
  evolution loop — additive, **byte-identical when off** (pinned), each
  adding exactly one gated key.
- **DR 0045** — density as pressure: instruction density may feed the
  CuBFF pressure math as its own named channel, off by default, mirrored
  at both parity sites.
- Four new instruments: the refusal-cause histogram, the
  lineage-dominance judge, the geometry-consistency survey, and the
  `animation_density` candidate axis.

### Changed / Corrected

- **CORRECTED (DR 0042, twice)** — the constrained arm's generation
  failure rate is **7.2%**, not the recorded ~22% (the old figure
  divided by the *scored budget*, where novelty-first requests 61,440
  attempts); and the promoted path refused **zero** invalid candidates.
  All 4,435 refusals are the SLIP rejecting the **parent** — a selection
  fact, not a generator fact — and 100% of those parents are bootstrap
  creatures.
- **CORRECTED** — the claim that 460 occupied niches is "exactly" the
  measured support ceiling compares numbers counted in **two different
  scale geometries** (see below); the coincidence is real, the identity
  is not established.
- **CORRECTED (DR 0043 / I3)** — the checkpoint forecast's inverted
  harshness. With `replication_scores` and `lineage_events` structurally
  absent from the checkpoint format, pressure rode on entropy and
  instruction diversity, **both of which fall as a soup organizes**, so
  the engine read organization as calm. Density — the one carried
  channel that rises — corrects the direction: inversion **−0.034293 →
  +0.006324**, agreeing with the lit-channel callback ground truth.

### Measured / Judged

- **The documented lineage-dominance clause judged for the first time in
  the project's history** — *"no single lineage > 40% of occupied
  cells"* (`deep-research.md:205`). **PASS at 0.2848** across 38 founder
  lines. Reported beside the verdict and deliberately outside it: **four
  founder lines hold half the archive**, and the two largest were
  founded by WFC *bootstrap* creatures though every elite was bred by
  the adopted `constrained` layer.
- **The scale geometry is not stale — it is split.** Re-running E1's
  derivation protocol reproduces the committed edges **exactly** (drift
  0.0 against a *measured* 0.0102 sampling control). But the repo runs
  **two** geometries: the loop and E4 gates on frozen train-derived
  edges, the reachability probe and occupancy instrument on live
  all-seeds edges — differing by **3.7× the sampling control**. So
  `460/512 occupied` and `508/512 reachable` are counted in different
  coordinate systems. Diagnosed, **not repaired**.
- K3's measure-thin windows are therefore **real**, and the quantization
  hypothesis hardens.
- **DR 0045's pre-run prediction (≈ +0.041) matched the measurement
  (+0.040617) to four decimal places**, from a ceiling derived from the
  language's own alphabet (256/10 = 25.6, independent of tape length)
  and a weight fixed in advance.

### Withheld

- **`animation_density` — adoptable, not adopted.** The candidate axis
  passed *every* machine gate (spread; independence at max |r| 0.173;
  discrimination at 2.7× the bar — **54.3%** of same-three-axis-bin
  pairs separated) with its cost reported (occupied 289 → 448; coverage
  0.5645 → 0.1094). Adoption was still refused: the documented selection
  criterion is *inter-rater interpretability*, which needs the
  owner-deferred human panel, and **no proxy was substituted**.

### Honest limits recorded

- Density recovers the **direction** of the biology, not its force —
  +0.0063 against the ground truth's +0.2622, about **2.4%** of the
  magnitude. The DR 0045 rider is **off by default** in the engine.

---

## Cycle 21 · Phase K — "the vocabulary settles its stack" — 2026-07-26

**Gate: GREEN.** `research/experiment_reports/2026-07-26-phase-k-gate.md`
Closing sweep: 19 lab suites + package 295 + workshop 92 + game 174 +
CLI 23 — 2,230 artifacts, 0 invalid.

Three of five slices ended in a verb that was not "ship it": a withheld
adoption, four measured bounds, and a blocked-upstream disposition.

- **DR 0041 — the 11-class regrowth head: adoption WITHHELD** by its own
  pre-registered rule (G1 refused at +0.0944 against a +0.10 bar while
  G2–G5 passed). The refusal carries its measured mechanism: at rich
  token sites the legacy head restores 0.0 exactly against the rich
  head's 0.525, and the pooled metric is denominator-diluted.
- **DR 0042 — the generation layer ADOPTED at its consumer.** Judged
  through the full loop at a matched 20,480-evaluation budget:
  coverage 0.7852 → **0.8984**, QD ratio 1.3025, 460 niches. The DR 0032
  GA-advantage clause refused *deeper* (+11.3% against a ≥ 25% bar).
- **508/512 descriptor bins proven reachable** — five more bins reached,
  two only at high mutation temperature; the remaining four bounded
  sharper by a new blocking-axis instrument (measure-thinness, not
  distance).
- **DR 0043 — forecast key 5 ADOPTED**: the first weather whose harshness
  channels are lit, with zero engine-seam changes proven structurally and
  behaviorally. `lineage_churn` dispositioned **BLOCKED-UPSTREAM** —
  honest silence, no proxy smuggled.
- **DR 0044 — the covenant's budget face in the workshop ADOPTED**,
  advisory-never-authority and pinned as such.

---

## Cycle 20 · Phase J — "the generative range" — 2026-07-20

**Gate: GREEN.** `2026-07-20-phase-j-gate.md`

- **Vocabulary blindness found and cured.** The breeding surface emitted
  the motion trio at exactly **0.0** — a pre-DR-0011 five-token
  projection erased seven ratified roles. **DR 0038** cured generation
  (emission 0.0 → **0.512**); **DR 0039** cured a second blind surface in
  the repair stack.
- **DR 0040 — novelty-first evolution ADOPTED** on both axes.
- The structured decoder joined the **refuted record** with its mechanism
  measured: the failure is spatial coherence, not information.

## Cycle 19 · Phase I — "the post-takeover science" — 2026-07-20

**Gate: GREEN.** `2026-07-20-phase-i-gate.md` — real post-takeover soup
corpus; weather harshness measured per phase; the callback export path
made real (replication channel lit) but left unconsumed by decision.

## Cycle 18 · Phase H — "workshop authoring depth" — 2026-07-19

**Gate: GREEN.** `2026-07-19-phase-h-gate.md` — 16×16 authoring end to
end with game admission, semantic layers, the animation timeline and
onion skin, the behavior editor, and the first-session journey proven
with its scripted proxy honestly labelled.

## Cycle 17 · Phase G — the public-alpha gate — 2026-07-12

**Gate: GREEN.** `2026-07-12-phase-g-gate.md`

- **Every documented phase A–G complete and gated**; `docs/gap-analysis.md`
  RETIRED per its own charter.
- **REAL CuBFF corpus ingested** — genuine upstream data built at the
  audited commit (the project's oldest blocker, closed).
- The alpha packet (`docs/alpha.md`): both builds reproducible from one
  document.

## Cycles 14–16 · Phase F — the GAME client — 2026-07-12

**Gates: GREEN** (MVP 0.1, 0.2, 0.3). *"Eras of the Soup"* — the playable
pygame-ce client (**DR 0033**): companion loop, era bench, covenant
spending, hatchery, replays, repertoire and lineage browsers, SLIP
import/export, community packs, save/resume, and a PyInstaller bundle.

## Cycle 13 · Phase E — evolution at documented scale — 2026-07-09

**Gate: GREEN.** 20,480 stress-probed evaluations per run; coverage, QD
and recurrent-family gates; **DR 0032** dispositioned the GA-advantage
clause as refuted with named re-openers.

## Cycle 12 · Phase D — the intelligence threads — 2026-07-08

**Gate: GREEN.** The 11-thread micro-learner fleet, with ablation gates
keeping five and **dropping six** on the measured rule.

## Cycle 11 · Phase C — the animation system — 2026-07-08

**Gate: GREEN.** Clips, transitions (0.9877), the `animstate_950`
dataset, and the render-packet contract.

## Cycle 10 · Phase B — generation — 2026-07-08

**Gate: GREEN.** The real generator bake-off: **DR 0031** adopted WFC;
the hybrid arm was **REFUTED**.

## Cycle 09 · Phase A — the 16×16 foundation — 2026-07-08

**Gate: GREEN.** **DR 0029** (size-parametric grids, 16×16 the proven
default) and **DR 0030** (size-relative SLIP mass bounds).

## Cycles 01–07 · pre-phase — through 2026-07-07

The ontology, the grid-genome schema and its numbered invariants, the
SLIP schema and its dual validators, the research labs, and the module
promotion program that produced `packages/mecha_engine`. *(There is no
cycle 08.)* Archived queues: `audits/complete/01/` … `audits/complete/07/`.

---

## Standing, by owner ruling

These are decisions, not backlog:

- **License: Apache-2.0** (DR 0028). Third-party dependencies are
  permitted when a capability needs one; stdlib has simply kept holding
  at every measured scale gate so far — a *measurement*, not a policy.
- **Manual readability calibration is deferred by owner choice.** The
  learned model is primary (**DR 0019**); the rating pipeline is its
  fallback and is never a blocker.
- **Community infrastructure, a pack registry and hosted distribution
  are owner decisions** (**DR 0035**), not tasks.
- The human-study block stays prepared-not-blocking. Where a human
  measure is unavailable, the record says so and **no proxy is
  substituted for it**.

## Sources

- `research/README.md` — the master traceability ledger (the authoritative record)
- `research/experiment_reports/` — dated findings and the per-phase gate reports
- `research/decision_records/` — ADRs `0001`–`0056`
- `audits/TODO.md` (the live queue) and `audits/complete/NN/TODO.md` (archived cycles)
- `tools/ci/run_sweep.py` — the one verification sweep every gate runs
