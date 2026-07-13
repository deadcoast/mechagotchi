# Development TODO — Cycle 17: Phase G — the late-stage requireds (BOTH builds)

**Build track: SHARED** (per `docs/gap-analysis.md` §4: ENGINE A–E
complete; GAME Phase F complete — the MVP ladder 0.1→0.3 delivered
and gated, cycles 14–16). Phase G is the last documented phase; the
gap analysis retires only when this phase's alpha gate is green.

Source: `docs/gap-analysis.md` (Phase G): *"Real-CuBFF corpus + the
transducer study (20 runs / 400 states, the documented keep gates);
community asset/profile system; CI + reproducibility; the M7 public
alpha of BOTH builds."* CuBFF real ingest is REQUIRED (owner,
2026-07-07) — an additional feature, never an open question;
synthetic weather remains the interim source until real exports land,
and nothing "real" is ever fabricated.

- [x] **G1 · CI + reproducibility.** The full sweep as a checked-in
  CI workflow (labs + package + workshop + CLI + game; JSON artifact
  validation; the evidence harness as a regen check). The known
  environment sensitivities are handled HONESTLY, not hidden: the
  workshop_editor foreign-fixture byte pins are zlib-BUILD-sensitive
  (system zlib-ng generated them; classic-zlib interpreters fail 10
  of them — the F1 report's recorded observation) — the workflow
  pins a matching interpreter or marks those pins
  environment-conditional WITH a decision record; pygame suites run
  headless (SDL dummy, the suite's own convention).
- [ ] **G2 · The real-CuBFF corpus.** The REQUIRED ingest: obtain or
  build real CuBFF run exports (the upstream study's code) and land
  them through the EXISTING ingest seam
  (`awaiting_real_cubff_snapshots` — admission or verbatim
  rejection). If the upstream build is blocked on this machine,
  record the blocker honestly with what was attempted — never
  fabricate "real" data (standing law).
- [ ] **G3 · The transducer study at documented scale.** 20 runs /
  400 curated states against the documented keep gates (preference
  >60%, invalid <10%) over the REAL corpus from G2 — the study the
  docs specify; a blocked G2 blocks this honestly, not silently.
- [ ] **G4 · Real weather in the game.** Real snapshots drop into the
  weather seam with ZERO seam changes (the documented promise,
  verified end to end in the client: a real-weather era runs and its
  snapshot provenance shows).
- [ ] **G5 · Community distribution decisions.** A decision record
  for pack distribution (registry/sharing shape, provenance
  integrity/signing — the F16 remainder), scoped to what the alpha
  actually needs; implementation follows the DR, never precedes it.
- [ ] **G6 · The M7 public-alpha packet + the Phase-G gate.** The
  repo reproducible from its own docs (entry README path: install,
  run the suites, build the game, play); the alpha checklist of BOTH
  builds; one consolidated gate report. **If green, the gap analysis
  RETIRES** — and the next planning source is decided WITH the owner
  (the documentation still defines scope).

## Standing note

The engine-truth law (DR 0021), the identity constraint, the triad
discipline, and the mirror-never-import boundary are unchanged.
Apache-2.0; deps permitted with justification (DR 0028). Standing
engine remainders: DR 0032's re-openers; occupancy saturation ~55%;
behavior_neediness at 16×16; the unpromoted scale-geometry seam
(still undemanded); evolve's inner loop on WFC; the hybrid re-opener;
per-role limb/joint motion; clip-frame exports; dropped threads stay
out (D6). Phase-F remainders carried as facts: 16×16 workshop
authoring; the ledger-backed repertoire page; the cross-era family
lens; a WFC hatchery trace seam; per-elite clip playback; UI
key-surface polish; the model cache's id-keying.

## Sources

- `docs/gap-analysis.md` (Phase G; §4 the ladder)
- `research/experiment_reports/2026-07-12-phase-f-mvp03-gate.md` (the opener)
- `data/cubff_real_ingest/` (the honest blocker record + the ingest seam)
- `research/decision_records/0018`, `0020` (the weather seams), `0028` (deps/license)
- `labs/cubff_transducer/` (the study's lab), `data/workshop/released/`, `data/packs/` (G5's material)
