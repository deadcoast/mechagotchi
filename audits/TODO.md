# Development TODO — Cycle 09: Phase A — the 16×16 foundation

Source: `docs/gap-analysis.md` (2026-07-07) — the measured gap between
the documented application and the implementation. The documents name
16×16 as the PRIMARY grid target (validity-research §1.34: the first
implementation target that "proves the entire thesis"; deep-research:
16×16 bake-off scale, SLIP ranges 12×12–32×32); everything ever proven
here was proven at 8×8 with ~13-cell bodies. Phase A moves the
foundation to documented scale so every downstream phase (WFC bake-off,
animation system, intelligence threads, evolution at scale, MVP 0.1)
builds on real ground. Third-party dependencies are permitted where the
scale needs them (DR 0028). The triad discipline and engine-truth law
are unchanged.

- [ ] **A1 · 16×16 invariants and schema ratification.** Re-derive the
  hard/soft invariants at 16×16 (body-mass bounds, connectivity,
  organ-count expectations, symmetry ranges — the 8×8 numbers do NOT
  scale linearly; measure, don't assume), ratify in
  `research/grid_genome/grid_invariants.md` + the schema (which already
  permits 8–64), and record the scaling decisions in a decision record.
  The 8×8 corpus remains valid input (SLIP grid ranges span sizes);
  16×16 becomes the default the engine is PROVEN at.
- [ ] **A2 · The 16×16 seed corpus.** The documented deliverable is
  hand-authored-quality seeds at the primary scale: extend
  `corpus_builder` to emit a 16×16 corpus (≥50 creatures across the
  five palettes with real morphological variety — multi-organ bodies,
  limbs, antennae, shells from the DR 0015 vocabulary, not upscaled
  8×8 blobs), plus the invalid corpus at the same scale. Workshop
  editor gains the 16×16 canvas (the grid is the hero surface).
- [ ] **A3 · Generator, validator, repair, lifecycle at 16×16.**
  Re-prove the promoted pipeline at the new scale: generation trained
  on the 16×16 corpus, validator invariants from A1, repair models
  (wound-site semantics unchanged; retrain + re-gate the stability
  bar at scale), lifecycle body-mass/stability derivations re-measured.
  NumPy enters HERE if the scale demands it (repair training and
  generation stats are the likely spots — justify in the DR either
  way). Every standing gate reruns green at 16×16 without breaking the
  8×8 pins (size-parametric, not size-replacing).
- [ ] **A4 · Evolution + game surfaces at 16×16.** `evolve`, the
  archive descriptors (bins re-derived for the larger trait ranges),
  the Keeper session, replays, and the companion all run at 16×16
  defaults; the session's engine parameters step up from the toy
  config (population and generations meaningfully raised — measure
  what wall-clock allows and record it; this is the bridge toward
  Phase E's documented scale, not its endpoint). Demo artifacts
  regenerated; every suite green.
- [ ] **A5 · Phase-A gate + report.** One consolidated experiment
  report: the 16×16 foundation — invariant table, corpus stats,
  re-run gate results at scale, before/after generation quality, and
  the honest list of what still runs at 8×8 and why. Gap-analysis
  Phase A checked off only when this gate is green.

## Standing note

`docs/gap-analysis.md` governs cycle planning until retired (Phase G
alpha). The engine-truth law (DR 0021), the identity constraint, and
the triad discipline are unchanged. CuBFF real ingest is REQUIRED
late-stage (Phase G). Apache-2.0; dependencies permitted with
justification (DR 0028).

## Sources

- `docs/gap-analysis.md` (Phase A)
- `docs/project-research/validity-research.md` (§1.34)
- `docs/project-research/deep-research/01/deep-research.md` (bake-off scale, SLIP ranges)
- `research/grid_genome/grid_invariants.md`
- `research/decision_records/0028-license-and-dependency-policy.md`
