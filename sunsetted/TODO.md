# Development TODO — Cycle 25: SHARED track · Phase O — the adopted definitions reach the player

**Planned from the documentation and from cycle 24's own named
remainders** (the standing rule: the developer plans when a queue
exhausts).

Phase N earned the descriptor space its edges and answered four
long-standing questions. Its defining character was unplanned, and it
sets this cycle's discipline: **Phase L audited its own numbers, Phase M
its own sentences, and Phase N its own INSTRUMENTS** — every one of its
six slices found a defect in the measuring apparatus rather than in the
thing measured, and **three of those were errors the session made and
caught before they shipped as findings**.

Phase N also left a specific, unusual shape of debt: **it adopted three
things and put none of them in front of a player.**

- `insertion` is the adopted `slip_admission` default (DR 0052) and is
  the loop's default (DR 0053) — but every historical study is pinned
  to the incumbent, so **no number anyone reads has moved yet**.
- `danger_margin` is the adopted definition of `health` (DR 0054) — but
  it is **not on screen**, blocked on one package constant.

That is correct in each case and deliberate in each case. It is also
exactly the kind of debt that quietly becomes permanent. **Cycle 25 is
where the adopted things land**, and the two that can land are small and
concrete.

**The identity constraint and the anti-periscope rule both apply.** O1
and O2 are the GAME-facing landings Phase N earned; O3 is the SHARED
migration DR 0053 named and scoped; O4 is deliberately **non-archive and
non-loop**, from the still-unmet documentation, after a cycle that spent
four of six slices in the archive. Community infrastructure and a
registry stay owner decisions (DR 0035).

Sources: `research/experiment_reports/2026-07-28-phase-n-gate.md` (the
remainder list this cycle opens), `2026-07-28-health-definition-gate.md`
(O1/O2), `2026-07-28-slip-admission-migration.md` (O3),
`research/decision_records/0054-health-definition-danger-margin.md`,
`0053-admission-policy-belongs-at-the-call-site.md`,
`0052-slip-admission-default-insertion.md`, `0048-visible-companion-state-axes.md`,
`0021-game-loop.md` (engine truth), `0004-package-scaffold.md` (promotion),
`docs/project-research/validity-research.md` §1.17,
`docs/project-research/deep-research/01/deep-research.md`,
`docs/project-research/research.md`, `research/questions.md`.

- [x] **O1 · Promote `DANGER_THRESHOLDS` to the package's public API.**
  DONE 2026-07-28 (`2026-07-28-danger-thresholds-promotion.md`): the
  lifecycle surface widens **six names → seven**, following the **W1
  precedent** exactly (document the widening in the contract gate, add
  to `__all__`, let the **exact `__all__` equality probe** fail until
  spec and code agree — that failing run *is* the RED, the pin doing its
  job by rejecting an undocumented widening). **The promotion is
  deliberately narrow and the narrowness is PINNED**: the charter said
  do not widen beyond the constant, and a package test now asserts
  neither `danger_margin` nor `health` appears on the surface, so
  whether the margin formula belongs in the engine stays a separate
  decision rather than eroding by drift. **The constant is pinned BY
  VALUE, not by presence** — a promoted constant whose numbers can drift
  is not a contract — plus a coverage pin that **every lethal axis has a
  threshold**, because a set missing one would let a bar read healthy on
  a dying companion, *the exact failure DR 0054 refused `grid_stability`
  for*. The **"danger, not lethal"** distinction is now a package-level
  pin too (`bond` has a threshold and is not a death condition).
  **N5's loop is closed**: the lab imports from the public API and its
  artifact regenerates with **identical verdicts**, the check that this
  moved a surface and not a behaviour. Package suite **295 → 299**; no
  existing assertion moved. **No DR**: DR 0054 already made this
  decision and named this task as its blocker, and the W1 precedent
  documents a surface widening in the contract gate rather than a record
  of its own — writing one here would record the *execution* of a
  decision rather than a decision. Traceability matrix updated.
  *Original charter, kept because its last instruction is what shaped
  the task:* N5's named blocker, and the smallest real thing in this
  queue.
  `danger_margin` — the adopted definition of `health` — reads a
  constant that is a **public name in a public module but is not in
  `mecha_engine`'s `__all__`**, so any consumer depending on it depends
  on a surface the package has never promised. Promote it with the
  package discipline it deserves: a contract entry in
  `research/package_specs/`, a package test, and the traceability matrix
  updated. **Do not widen the promotion beyond the constant** — if the
  margin formula itself belongs in the engine, that is a separate
  decision, and this task must say which it did.
- [x] **O2 · Land the `health` readout in the game.** DONE 2026-07-28
  (`2026-07-28-health-readout.md`, **DR 0055**): **health is on the
  player's screen, and the play-drop is explained rather than hidden.**
  Three ways to handle a keeper verb that lowers the bar, and two are
  forbidden by DR 0021's first law — smoothing or hiding it would make
  the surface show something the engine does not. **The answer is to
  show the BINDING AXIS beside the number**: health is a *minimum*, and
  a bare minimum throws away the one thing that makes it legible, so
  `health 0.62 (tired)` costs no new number (argmin of margins already
  computed) and turns an unexplained fall into a sentence. **Refusal was
  reachable and did not fire** — a pin asserts that a drop must be
  explained by the axis named after it. **THE MEASURED CASE, from the
  live client**: a keeper who never sleeps sees `tired` from tick 2,
  0.000 by tick 7, and **dies of `energy_collapse` at tick 10** — the
  readout named the death cause **eight ticks early**; a keeper who acts
  on the word goes **0.487 → 0.976** on the same creature. The
  play-drop itself is visible and legible in that run (tick 8 plays at
  0.813, tick 9 reads 0.715 and says `tired`). Formula **MIRRORED** into
  the game per the boundary law and pinned against the committed N5
  artifact, so drift either way fails the suite. RED first; 12 pins;
  game 188 → **200**. **Honest limit recorded, not fixed**: the bar
  bottoms out at DANGER, not death, so health reads 0.000 while the
  companion is still alive — defensible as a warning, but "health"
  implies zero means dead and it does not; a different floor is a
  different CHOSEN definition needing its own gate.
  *Original charter (GAME track, depended on O1):* DR 0054 adopted `danger_margin` and shipped only a
  guard. Put it on screen — and **answer the design question DR 0054
  refused to answer for the consumer**: `play` LOWERS `danger_margin`
  (−0.075467, because play costs energy and adds hunger), so a keeper
  who sees "health" drop when they play with their pet will read it as a
  bug. Decide, and gate, whether that is shown as-is (honest, and the
  engine's truth), smoothed, or split into two readings. **DR 0021's
  first law binds**: whatever ships is engine truth or it does not ship.
  Refusing to display it after all is a legitimate verdict if the design
  question has no honest answer.
- [x] **O3 · Migrate the two headline studies onto the adopted
  default.** DONE 2026-07-28
  (`2026-07-28-adopted-default-restatement.md`, **DR 0056**):
  **restated, not overwritten — and coverage buys quality.** DR 0053's
  rule 2 shaped it: *a measurement does not improve, it is reproduced or
  superseded by a new measurement answering a new question*, so this is
  a **new artifact** and both committed incumbent artifacts stay exactly
  as they were. **Only the adopted arm was re-run**, which cut the work
  ~75%: the incumbent runs are read (rule 2 forbids re-running them) and
  the **GA control is read because `run_ga_baseline` takes no
  `slip_admission`** — structurally unaffected, so re-running it would
  reproduce numbers that cannot move. **THE HEADLINE, at DR 0042's own
  seed**: coverage **0.898438 → 0.880859** (−0.017579), **QD
  404.618236 → 411.738214 (+7.119978)**, niches 460 → 451, **refusals
  4,435 → 0**, **illegal elites 35 → 0**. **Coverage does not fall for
  nothing — nine niches and 0.0176 coverage buy +7.12 QD and an archive
  legal under the covenant that bred it**, which prices the other side
  of the trade L1 declined. **E4 gates re-judged VERBATIM** (`judge_gates`
  imported) over the documented ten seeds against the same GA control:
  **`NO_REGRESSION`** — `coverage_gate_met` holds, mean best fitness
  moves −0.000565, and `ga_advantage_gate_met` was **already failing**
  so it is explicitly not attributed to the adoption (DR 0032 refuted
  again, its margin falling a further 0.029664). **DR 0042 is NOT
  retracted**; DR 0056 adds a quoting rule instead — any *"the loop
  achieves X"* must name **which arm**. Dated notes beside DR 0042 and
  the `evaluation_loop_scale` card. Wall clock 2594.122 s for ten
  documented-budget runs. RED first; 17 pins.
  *Original charter:* DR 0053's rule 3, scoped there and unfinished by design:
  `evaluation_loop_scale` (the source of **DR 0042's headline coverage
  0.8984**) and `coverage_qd_gates` (the E4 gates) are the **only two**
  of the eight callers whose migration is a real question rather than an
  evidence-destroying regeneration. Restate both under
  `slip_admission="insertion"`, **explain the delta at every site that
  quotes the old number** (decision records, gate reports, ONBOARDING,
  CHANGELOG), and keep the incumbent artifacts as what they are — the
  measurements they were. **DR 0046's comparability rule applies
  throughout.** The other six callers stay pinned; DR 0053 says why, and
  re-opening that is not this task.
- [ ] **O4 · Stage 2's undispositioned generator arms.** *(Design done,
  not built. Two corrections found by reading the dossier and the engine
  BEFORE writing measurement code — they reshape the task, and the next
  session should start from them rather than from the charter below.)*

  **CORRECTION 1 — the charter's framing is wrong for one of the two.**
  It says *"judge them against the adopted generation layer on its own
  bake-off terms"*. Measured against the dossier: **CPPN** is *"Indirect
  encoding… optional late-stage"*, priority low-to-medium, integration
  risk **High**, stance *"keep as a late exploratory generator"* — a
  generator bake-off IS its documented role. But **shape grammar** is
  filed under **Constraint systems** with WFC and SAT/SMT, and the
  stance for that family is *"**use as validator or post-generator
  stabilizer**"*. It is **explicitly not** proposed as a primary
  generator, so a bake-off would test it at a job nobody gave it and a
  rejection earned that way would mean nothing. **Judge each in its
  documented role.**

  **CORRECTION 2 — shape grammar's documented role is ALREADY SHIPPED,
  and this is the bigger finding.** `wfc_grid._finish` (called inside
  `generate_wfc_grid`, line ~169) is documented in its own docstring as
  *"The documented post-generator stabilizer pass"* and quotes the
  dossier's *"use as validator or post-generator stabilizer"*
  recommendation verbatim. It applies exactly those constraint
  productions — keep the largest 8-connected core, cardinality
  constraints as restart conditions, anchor normalization — and it is
  part of the **adopted** WFC arm (DR 0031). So *"does a constraint
  stabilizer help?"* is answered and adopted. **The real open question
  is sharper: does a SHAPE-GRAMMAR stabilizer beat the incumbent
  `_finish`?** That is a genuine bake-off where rejection is a real
  outcome rather than a foregone one.

  **Process note for whoever picks this up**: the RED test written
  during this design (`labs/wfc_grid/test_stage2_generator_arms.py`) was
  committed prematurely by the owner's IDE mid-design and then removed,
  because a deliberately-failing test in a lab directory turns the
  closing sweep red for an unrelated task. **Do not write a RED into a
  lab directory until the previous task is committed.** The design and
  both corrections above survive; the file does not.
  *Original charter:* Deliberately
  **non-archive and non-loop** after a cycle that spent four of six
  slices in the archive — the anti-periscope rule's own instruction.
  `docs/project-research/deep-research/01/deep-research.md` names
  **shape grammar** and **CPPN** as generator candidates and neither has
  ever been dispositioned: no card, no prototype, no reject/watch verdict
  — the same class of documented-and-unmet debt N3 closed for the
  micro-learner conditions after twelve cycles. Build the smallest
  honest prototype of each, judge them against the **adopted** generation
  layer (DR 0031/0042) on its own bake-off terms, and **let the measured
  rule reject, watch or prototype each**. Rejecting both is first-class:
  DR 0031 already refuted the hybrid arm, and a second refutation with a
  measured mechanism is worth more than a third generator nobody asked
  for.
- [ ] **O5 · The Phase-O gate.** One consolidated report; cycle 25
  archived; cycle 26 planned from the documentation.

## Standing note

The engine-truth law (DR 0021), the identity constraint, the triad
discipline, the mirror-never-import boundary, Apache-2.0, and DR 0028
apply. Gates are PRE-REGISTERED before the run and a gate that cannot
fail is a bug; new seams are additive and byte-identical when off,
proven not asserted; adoption never deletes the incumbent. **DR 0046's
comparability rule is law**: numbers measured in different geometries
may not be read against each other. **DR 0053's rule is now law too**:
any setting that changes what an artifact means is recorded at the call
site that produced it, never inherited from a default — and **a study
that measures a defect is never migrated onto the fix.**

**Phase N's lesson rides along, and it is about instruments**: every one
of its six slices found the measuring apparatus wrong rather than the
thing measured, and three of those were the session's own errors. **Check
the instrument against a committed number before trusting what it
says** — N1, N2 and N4 each reproduced a predecessor's committed value
first, and N4's check is the only reason a wrong population parameter
did not silently overturn a correct prediction.

**Named, deliberately not tasked**: §1.17's visible/hidden split, now
measurably **stale against the shipped game** (N5 — the client already
surfaces `stress` and `grid_stability` under accurate names); whether
the **Q-table beats the incumbent reactive rule** rather than uniform
random (N3's weak baseline, named there); a **like-for-like online stump**
for N3's tree (its current baseline gets a full-sample oracle);
`occupancy_saturation` and `reachability_escalation` still not carrying
their edges in their **committed** bodies (N2); a floor fine enough to
**locate** N1's knee rather than bound it; the probe's two engine
move-set **descents**, not re-run because the edges were identical (N2);
**`happiness`** needing a DEFINITION and **`cleanliness`** a MECHANIC
(DR 0048 — neither is a display gap); `animation_density`'s adoption
awaiting the human panel (L4), whose A2 independence halves on the
elites (M1); the **576-vs-512** repertoire divergence (L2); the scored
candidate stream and a size-matched TVD control (M1); the unbuilt method
tracks (**MRF-lite**, **Lenia/Flow-Lenia**, **reaction–diffusion**, the
**MDP sandbox**, the **QDax shadow port**, **z3/SMT** at DR 0011's
WATCH); the **24×24 scale-up** (DR 0014's re-opener); the undiluted
rich-site regrowth instrument and the unexplained 0.525 ceiling
(DR 0041); an analytical emptiness argument for the quantization bin;
richer callback export states; which forecast keys enable the DR 0045
density rider in a shipped client.

The owner-deferred **human-study block** stays prepared-not-blocking:
the readability panel, the bake-off's readability clause, the
semantic-editor comparison, the SLIP-creator pilot, the ≤45-minute
HUMAN first-session pass, and live-browser click-testing. The transducer
study's "preference" number is a labelled **proxy** — never restate it
as human preference. DR 0032's re-openers stand. Per-clip choreography
stays an engine DR when a consumer asks; the workshop keeps its ratified
stack (DR 0010); community infrastructure, a pack registry, and hosted
distribution are owner decisions (DR 0035); the first green CLOUD CI run
awaits a push that is never made unasked.

## Sources

- `research/experiment_reports/2026-07-28-phase-n-gate.md` (the closed ladder + the remainder list this cycle opens)
- `research/experiment_reports/2026-07-27-derivation-size-stability.md`, `2026-07-28-probe-edge-freeze.md`, `2026-07-28-candidate-learner-ablation.md`, `2026-07-28-slip-admission-default.md`, `2026-07-28-slip-admission-migration.md`, `2026-07-28-health-definition-gate.md` (the Phase-N science this cycle extends)
- `research/decision_records/0049`–`0054`; `0021-game-loop.md`, `0028-dependency-and-license-policy.md`, `0031-wfc-generation-adoption.md`, `0042-generation-layer-loop-revisit.md`, `0046-two-geometry-split.md`, `0048-visible-companion-state-axes.md`
- `research/package_specs/` (O1's contract home) · `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py`
- `docs/project-research/validity-research.md` §1.17, `docs/project-research/deep-research/01/deep-research.md`, `docs/project-research/research.md`, `research/questions.md`
- `sunsetted/complete/TODO/24/TODO.md` (the archived cycle)
