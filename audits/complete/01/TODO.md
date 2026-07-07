# Development TODO — from the 2026-07-05 Dev-Spec Audit

Source of every task: `audits/audit-devspec.md` (og-doc reviews per the
owner's DESIGN-CORRECTION). Tasks follow repo governance: research-first,
labs before packages, triad docs with every change, decision records for
scope, gates before promotion. Priorities: **P0** = the owner's correction,
**P1** = og-scope restorations with engine value, **P2** = og program
completions, **P3** = owner-gated human studies (queued, never chased).

---

## P0 — The [00] correction: workshop creatures enter the ecosystem

- [x] **T1 · Workshop→engine asset wire.** (shipped 2026-07-05; T1.5 owner-gated) Workshop-authored creatures
  (`data/workshop/grids/`) become first-class simulation assets:
  - [x] T1.1 Lab experiment (`labs/runtime_integration`): evolution run
        whose parent pool = corpus seeds + SLIP-aligned workshop grids;
        measure the workshop lineage's survival/archive entry vs corpus
        lineages (the og promise: user assets influence evolution).
        Regime-conditional keys; sheltered parity untouched.
  - [x] T1.2 Provenance: workshop creatures already carry
        `metadata.source = workshop_grid_editor`; assert lineage
        traceability of workshop ancestry through generations
        (`ancestor_ids` chain) in the lab's tests.
  - [x] T1.3 Surface: `mechas workshop` gains the release flow (e.g.
        `--release <creature>` or an editor "release into the ecosystem"
        action) that validates strictly, then registers the creature as
        simulation seed input. UX per the CLI charter.
  - [x] T1.4 Docs: experiment report + runtime card update + workshop
        reference ("the creature you draw can live and breed in the
        engine's world") + og-triangle diagram restored in the charter.
  - [x] T1.5 (DR 0016, 2026-07-06 — owner authorized) runtime.evolve founder_grids contract shipped; formerly: If the owner accepts and the owner accepts: DR for the
        `runtime.evolve` seed-source contract extension (promoted-module
        change; parity implications documented).

## P1 — og-scope restorations

- [x] **T3 · SLIP schema ladder v0.1.0 → og scope.** COMPLETE (DR 0012 rungs 1-5 + DR 0013 package port + T3.6 gates met, 2026-07-06; remaining og fields sociability/render-effects stay deliberately queued per DR 0011) One DR proposing the
  extension sequence, then per-field triads (schema + both validators +
  pydantic mirror + fixtures + workshop slip-creator controls):
  - [x] T3.1 `forbidden_traits` (shipped 2026-07-05, DR 0012 rung 1)
  - [x] T3.2 `risk_tolerances` (shipped 2026-07-05; census-designed switchboard consumer)
  - [x] T3.3 `learning_switches` (shipped 2026-07-05; switchboard thread gates — also T19's profile-authored ablation harness)
  - [x] T3.4 `lineage_preferences` (shipped 2026-07-05; fitness_weighted parenting + the v01_projection package-boundary adapter)
  - [x] T3.5 `species_class` + `visual_grammar` (allowed_materials + animation_vocab) (shipped 2026-07-05; mirrors synced; full grammar UI rides T9)
  - [x] T3.6 og gates (2026-07-06, ladder_gates_met: 18/20 with zero unplanned gaps; fuzz 0.0 false-pass over 161 cases; slip_zoo_100 delivered)
- [ ] **T4 · Animation-state vocabulary.** (SEMANTICS + animstate_300 SHIPPED 2026-07-05 — states are deterministic genome projections, 300/300 valid; remaining: T16 packet selection, workshop previewer, T3.5 field) og: idle/blink/sleep/beg/ill
  states, animation anchors per state, `animstate_300` dataset.
  Research-first: lab defining state semantics on the grid genome
  (extends the single-anchor invariant), then schema, then render-packet
  animation selection, then workshop preview/editing. Feeds T3.5, T7,
  and slice-3 preview's "animation/state previewer" og responsibility.
- [x] **T5 · Micro-learner thread census + gap plan.** (research/micro_learners/thread_census.md, 2026-07-05) Document mapping
  each og predictor (hunger, sleep, boredom, attention, animation
  preference, interaction timing, mood transition, mutation stability,
  visual readability, SLIP compatibility, lineage survival) →
  implemented thread / covered-elsewhere / missing, with evidence paths.
  Missing threads get og's required proof shape (input, output,
  confidence, explanation, effect on action, effect on survival) and the
  go/no-go: improve one measurable outcome without destabilizing.
- [x] **T6 · Grid-size decision record.** (DR 0014, 2026-07-05: 8x8 committed on probe evidence; T17 re-opens) Answer og research question 2
  (8×8 vs 16×16 vs 24×24 vs 32×32) with evidence: generator validity,
  readability proxies, invariant scaling, render/edit ergonomics at each
  size. og's own sketch was 16×16; today's 8×8 is undecided policy, not
  a decision. DR either commits to 8×8 with reasons or plans the
  multi-size path (schema already carries `grid_size`).

## P2 — og program completions

- [ ] **T7 · Grid schema fields from the og starter schema**:
  `species_class` (with T3.5), animation-state fields (with T4).
  Schema version bump + validator + invariants doc + migration note for
  existing corpora.
- [ ] **T8 · CTM gating integration decision.** Verify whether
  `labs/ctm_ticks`' confidence-gated deliberation ("act if confident,
  else extra switchboard cycles") reached the runtime switchboard; if
  not, run the integration experiment (og research question: does
  internal deliberation make behavior feel more alive / improve
  decisions measurably?) and record adopt/watch/reject.
- [x] **T9 · Workshop trait editor (og responsibility).** (shipped 2026-07-06: Traits tool, full vocabulary, engine-judged overrides) Expose
  per-cell material and mutation-weight editing in the grid editor
  (semantic overlay already carries both), with live engine validation
  as always. Small slice; charter pillars apply.
- [ ] **T11 · og dataset program completion**: `mechaseed_200` (curated
  variants of the 50), `mutationbench_5000` (generated offspring under
  fixed configs — the labs' mutation machinery makes this cheap),
  `replay_100k_ticks` (runtime episode logs; also feeds T12); `animstate_300` DONE (2026-07-05, with T4). Each with a README + ledger entry.
- [ ] **T12 · Recorded replay consumer for the render bridge.** og named
  three packet consumers; replay is missing. Lab: record per-tick render
  packets from a `live_cycle`/episode run into a replay artifact; the
  workshop preview gains a replay scrubber (engine truth, recorded).
- [x] **T13 · Workshop slice 5 (genome inspector + lineage browser)** (2026-07-06, owner-authorized: mechas workshop --inspect — genome tables + lineage browser over released ancestry and the wire artifacts' workshop-lineage traces)

## P1 addition — RUN TWO reconciliation (from the audit addendum)

- [x] **T14 · RUN ONE / RUN TWO reconciliation decision record.** (DR 0011, 2026-07-05) One DR
  that walks every RUN TWO delta and issues an explicit
  adopt/defer/reject verdict, ending the silent fork: SLIP shape (RUN
  ONE's won implicitly — ratify or revise), RUN TWO SLIP additions
  (render block with effects enum + animation_vocab -> feeds T3/T4/T16;
  mischief/sociability behaviors; limb_growth/max_edit_fraction
  mutation knobs; species_class required), grid-cell `value` byte vs
  shipped `visual` hex, RUN TWO material vocabulary vs shipped, z3/SMT
  constraint-solver track (open or formally reject), Jupyter notebooks
  (record as superseded by executable labs). No future session should
  rediscover this fork.
- [x] **T15 · Dormant grid-schema vocabulary: cover or trim.** (DR 0015, 2026-07-05: COVER — exemplar corpus + drift-guard test; editor affordances -> T9; per-role animation -> future T4 increment) The
  schema legally admits roles shell/joint/limb/antenna/decoration/
  effect, open organ ids, materials light/signal, and grid sizes to
  64x64 — none exercised by any corpus, invariant, generator, renderer,
  or workshop tool. Decide per vocabulary item: give it coverage (seed
  exemplars + invariants + rendering + workshop affordance) or trim it
  from the schema with a migration note. Couples to T6 (size) and T9
  (trait editor).
- [ ] **T16 · Render packet contract v2.** (SHIPPED 2026-07-05 incl. the DR 0013 package port — genome.render_packet_v2 additive publics; effects wait on the SLIP render-block rung) Both og runs specify the
  packet carries animation, mood, and effects (RUN TWO adds frame_id +
  ui_hints like needs_attention). Today `state` is an opaque
  passthrough. Spec-first: packet v2 contract (animation from T4's
  vocabulary, mood from lifecycle state, effects from SLIP render
  block per T14/T3), then promoted-module change with parity notes,
  then the workshop preview consumes the new fields. Depends on T4;
  feeds T12 (replay).

## P2 additions — RUN TWO protocol completions

- [x] **T17 · Formal generator bake-off at RUN TWO protocol.** (8x8 slice 2026-07-06, bakeoff_gate_met: shipped hybrid confirmed 1.0/1.0 on holdout; constrained arm's evolution A/B RUN 2026-07-06: dead heat, shipped_hybrid_stands; multi-size arms + human panel stay blocked per DR 0014/T10) After T6
  (sizes) and the seed-corpus growth (T11): holdout-split corpus
  (train/dev/holdout discipline enters the repo here), multi-size arms,
  large candidate volumes, bootstrap CIs, and the published thresholds
  (>=95% validity, readability bar, novelty-loss cap, latency budget).
  The human-panel arm is owner-gated (T10/T20); all machine metrics can
  run now. Confirms or revises the shipped generator choice with
  RUN-TWO rigor.
- [x] **T18 · MAP-Elites comparator study.** (2026-07-06, map_elites_confirmed: coverage advantage 2.86 vs bar 0.25, best-fitness gap 0.0; RUN TWO full scale recorded as scale-up) The unrun keep-gate: GA
  baseline (population 256) and novelty-search baseline vs the shipped
  archive at matched evaluation budgets, >=3 seeds first pass (RUN TWO
  says 10; scale as compute allows). Measures coverage advantage,
  best-fitness gap, lineage depth, extinction frequency. Either the
  og-claimed superiority becomes measured fact or the archive design
  gets revisited — first-class result either way.
- [x] **T19 · Micro-learner remove-one ablation.** (Stage 0 2026-07-05 + scaled rerun 2026-07-06: verdicts replicate across all 8 creatures/240 episodes; mood estimator keep at 77-85% decline; dead_weight threads still not removed — RUN TWO's 500-lifecycle protocol recorded as the final arbiter) RUN TWO's design: 5
  synthetic user models (attentive/neglectful/erratic/punitive/
  exploratory) x lifecycles x remove-one conditions over the switchboard
  threads; keep-gate: removal costs >=5% on a target metric without
  buying more elsewhere. Also delivers the og "full switchboard beats
  rules-only" claim as a measured number. Builds on the T5 census.
- [x] **T21 · REUSE repository structure.** (2026-07-06: LICENSES/ + reuse_licenses_ok CI check in lab + promoted mirror; repo-wide license grant recorded as the owner's pending decision) SPDX ids exist in the
  provenance ledger; adopt the REUSE convention RUN TWO specifies
  (LICENSES/ directory keyed by SPDX id, file-level notices where
  practical) and add the check to the provenance CI gate.

## P3 addition

- [x] **T20 · Pairwise-preference study protocol.** (PIPELINE 2026-07-06: protocol doc + stdlib Bradley-Terry MM lab + CSV intake, tooling-validated on synthetic data; rating-tool pairwise collection mode lands with the first scheduled study) RUN TWO prefers
  blind pairwise forced-choice with Bradley-Terry/Elo analysis over
  rubric scoring for human judgments. Build the protocol + a pairwise
  mode for the rating tool (tooling may ship; data stays owner-gated
  like all human studies). Serves T17's human panel and the CUBFF
  transducer's preference gate.

## P3 — Owner-gated human studies (queued; never chased as blockers)

- [x] **T10 · Workshop evaluation instrumentation** (PIPELINE 2026-07-06: /api/metrics session instrumentation + flush artifacts + research/human_studies_protocol.md; the STUDIES still require humans — owner schedules) (og metrics:
  authoring time, validator clarity, schema error rate, import/export
  fidelity, custom-profile survival rate) and og's human studies:
  semantic-vs-plain editor test, first-session usability (≤ 45 min),
  SLIP creator pilot (≥ 90% validate within two edits). Requires owner
  participation/recruits — same standing rule as the readability
  ratings: pipeline may be built, data is never fabricated.

---

## Standing note

Nothing in this TODO overrides the identity constraint: the engine is
the application; every workshop task above exists to make the workshop a
better **asset creator for the engine's ecosystem**, per the owner's
DESIGN-CORRECTION and the og documents.

## Sources

- `audits/audit-devspec.md`
- `.depreciated/01-design.md`, `.depreciated/01-formatted.md`, `.depreciated/01-research.md`
- `.depreciated/02-design.md`, `.depreciated/02-research.md` (RUN TWO addendum)
