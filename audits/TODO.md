# Development TODO — from the 2026-07-05 Dev-Spec Audit

Source of every task: `audits/audit-devspec.md` (og-doc reviews per the
owner's DESIGN-CORRECTION). Tasks follow repo governance: research-first,
labs before packages, triad docs with every change, decision records for
scope, gates before promotion. Priorities: **P0** = the owner's correction,
**P1** = og-scope restorations with engine value, **P2** = og program
completions, **P3** = owner-gated human studies (queued, never chased).

---

## P0 — The [00] correction: workshop creatures enter the ecosystem

- [ ] **T1 · Workshop→engine asset wire.** Workshop-authored creatures
  (`data/workshop/grids/`) become first-class simulation assets:
  - [ ] T1.1 Lab experiment (`labs/runtime_integration`): evolution run
        whose parent pool = corpus seeds + SLIP-aligned workshop grids;
        measure the workshop lineage's survival/archive entry vs corpus
        lineages (the og promise: user assets influence evolution).
        Regime-conditional keys; sheltered parity untouched.
  - [ ] T1.2 Provenance: workshop creatures already carry
        `metadata.source = workshop_grid_editor`; assert lineage
        traceability of workshop ancestry through generations
        (`ancestor_ids` chain) in the lab's tests.
  - [ ] T1.3 Surface: `mechas workshop` gains the release flow (e.g.
        `--release <creature>` or an editor "release into the ecosystem"
        action) that validates strictly, then registers the creature as
        simulation seed input. UX per the CLI charter.
  - [ ] T1.4 Docs: experiment report + runtime card update + workshop
        reference ("the creature you draw can live and breed in the
        engine's world") + og-triangle diagram restored in the charter.
  - [ ] T1.5 If the lab proves value and the owner accepts: DR for the
        `runtime.evolve` seed-source contract extension (promoted-module
        change; parity implications documented).

## P1 — og-scope restorations

- [ ] **T3 · SLIP schema ladder v0.1.0 → og scope.** One DR proposing the
  extension sequence, then per-field triads (schema + both validators +
  pydantic mirror + fixtures + workshop slip-creator controls):
  - [ ] T3.1 `forbidden_traits` (validator-enforceable now)
  - [ ] T3.2 `risk_tolerances` (consumed by lifecycle/switchboard)
  - [ ] T3.3 `learning_switches` (consumed by `mecha_engine.learning` —
        og's "learning toggles"; the bounded-claim evidence gives these
        real semantics)
  - [ ] T3.4 `lineage_preferences` (consumed by archive/evolve parenting)
  - [ ] T3.5 `species_class` + allowed `materials` + `visual_grammar`
        (blocked on T4 for animation vocabulary)
  - [ ] T3.6 og gates: 20-archetype expressiveness test, invalid-profile
        fuzz pack (false pass ≤ 1%), profile zoo growth 15 → 100
        (`slip_zoo_100`)
- [ ] **T4 · Animation-state vocabulary.** og: idle/blink/sleep/beg/ill
  states, animation anchors per state, `animstate_300` dataset.
  Research-first: lab defining state semantics on the grid genome
  (extends the single-anchor invariant), then schema, then render-packet
  animation selection, then workshop preview/editing. Feeds T3.5, T7,
  and slice-3 preview's "animation/state previewer" og responsibility.
- [ ] **T5 · Micro-learner thread census + gap plan.** Document mapping
  each og predictor (hunger, sleep, boredom, attention, animation
  preference, interaction timing, mood transition, mutation stability,
  visual readability, SLIP compatibility, lineage survival) →
  implemented thread / covered-elsewhere / missing, with evidence paths.
  Missing threads get og's required proof shape (input, output,
  confidence, explanation, effect on action, effect on survival) and the
  go/no-go: improve one measurable outcome without destabilizing.
- [ ] **T6 · Grid-size decision record.** Answer og research question 2
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
- [ ] **T9 · Workshop trait editor (og responsibility).** Expose
  per-cell material and mutation-weight editing in the grid editor
  (semantic overlay already carries both), with live engine validation
  as always. Small slice; charter pillars apply.
- [ ] **T11 · og dataset program completion**: `mechaseed_200` (curated
  variants of the 50), `mutationbench_5000` (generated offspring under
  fixed configs — the labs' mutation machinery makes this cheap),
  `replay_100k_ticks` (runtime episode logs; also feeds T12), and
  `animstate_300` (after T4). Each with a README + ledger entry.
- [ ] **T12 · Recorded replay consumer for the render bridge.** og named
  three packet consumers; replay is missing. Lab: record per-tick render
  packets from a `live_cycle`/episode run into a replay artifact; the
  workshop preview gains a replay scrubber (engine truth, recorded).
- [ ] **T13 · Workshop slice 5 (genome inspector + lineage browser)** —
  already owner-held; on go, design against og's inspector/browser
  responsibilities and T1's workshop-lineage traceability.

## P3 — Owner-gated human studies (queued; never chased as blockers)

- [ ] **T10 · Workshop evaluation instrumentation** (og metrics:
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
- `.depreciated/og-design.md`, `.depreciated/og-formatted.md`, `.depreciated/og-research.md`
