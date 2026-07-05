# Development-Spec Audit: Original Design vs Current Source

Date: 2026-07-05. Commissioned by the owner (DESIGN-CORRECTION [00]–[3]):
review the depreciated first-version documents — `.depreciated/og-design.md`,
`.depreciated/og-formatted.md`, `.depreciated/og-research.md` — and confirm
their design details are not minimized, stripped, or removed in the current
source integrations. Findings feed `audits/TODO.md` (same directory).

Method: every og design element was checked against the current tree by
direct inspection (paths cited per finding). Verdicts: **PRESERVED**
(intact or exceeded), **PARTIAL** (subset shipped, remainder needs a
tracked path), **MISSING** (not present, no tracked path), **DIVERGED**
(deliberate documented change).

---

## 1. The [00] question first: did the workshop become THE ecosystem?

**Verdict: the identity is intact; one load-bearing wire is missing.**

- The subordination IS recorded, in binding documents, in the og's own
  words. `docs/workshop/mecha-workshop-design.md` §1 quotes the founding
  law — "the workshop creates compatible profiles, but the engine remains
  autonomous" — and §7 states "Not the engine, and never upstream of it."
  The root `README.md` identity constraint predates the workshop build.
  The onboarding doc ledgers the engine as the application. This matches
  og-design.md [1]'s disclaimer verbatim in spirit: the engine generating
  its own mechagotchi from survival ancestry "IS THE MAIN AND CORE
  FUNCTION"; the editor exists "TO CREATE CUSTOM ASSETS FOR THE ENGINE,
  NOT THE CORE ENGINE ITSELF."
- **The missing wire (the real correction):** og-design.md [1] defines
  the link `engine <-> SLIP <-> workshop`, with workshop creations
  becoming assets the engine USES. Today that flow is one-directional
  and dead-ends: workshop creatures save to `data/workshop/grids/` and
  can be previewed singly (`live_cycle`), but **the ecosystem
  simulations never consume them** —
  `labs/runtime_integration/mecha_engine_runtime_loop.py` builds its
  parent pools exclusively from `build_seed_grids()` (lines 183, 528),
  and `mecha_engine.runtime.evolve` receives whatever seeds the caller
  passes, which no surface ever populates from the workshop. A creator
  can draw a creature but cannot release it into the world. That is the
  concrete gap behind the owner's correction, and it is task T1 in the
  TODO.
- Context for scale: the workshop slices landed in one intensive day
  (2026-07-05) on top of ~2 months of engine research and eight promoted
  engine modules. The center of gravity in the codebase remains the
  engine (`packages/mecha_engine`, 235 contract tests; labs ≈570 tests
  vs workshop 27).

## 2. Element-by-element verification

### 2.1 Core identity and architecture — PRESERVED

| og element | Current evidence |
| --- | --- |
| Predictive-algorithm core; creatures generated, complexifying via survival of ancestors (og-design [1] disclaimer) | `mecha_engine.generation` (Markov-style model), `lifecycle`, `archive` (MAP-Elites), `runtime.evolve` (multi-generation selection); stress-regime evidence of a selection signal (`2026-07-05-stress-regime-evolution.md`) |
| `engine <-> SLIP <-> workshop` triangle | SLIP schema + alignment authority both sides; workshop validates via engine surfaces. **Except the asset-return path — see §1** |
| Hybrid stack, no single algorithmic center (og-formatted §12/§13) | Markov generation + constraint validation + CA/NCA repair + MAP-Elites + micro-learners + SLIP + switchboard, each its own module/lab |
| "External novelty mediated through a semantic compiler" (og-research) | `labs/cubff_transducer/` implements exactly the tape→features→traits→grid pipeline; direct tape→pixels rejected per the og decision rule |
| Two-build model | Engine = `packages/mecha_engine`; workshop = `workshop/` app tree. **DIVERGED (documented)**: og placed the workshop under `packages/mecha_workshop/` with TS+React; DR 0010 chose dependency-free served pages first, TS+React recorded as the DR-gated scale-up path |

### 2.2 Research infrastructure — PRESERVED

og-formatted's research tree (`questions.md`, `literature_map.md`,
`algorithm_cards/`, `experiment_reports/`, `decision_records/`,
`failed_approaches/`, `glossary.md`, `source_notes/`,
`asset_provenance/`) exists 1:1 under `research/`. The algorithm-card
template matches field-for-field. The research loop and decision
standard ("Inspiration is not adoption… Evolution must be measurable")
are enforced by the gates.

### 2.3 The og lab roster — PRESERVED (names consolidated)

All suggested labs exist: `grid_genome` (markov_grid + grid_grammar +
micro_learners consolidated), `cellular_automata` (incl. NCA),
`cubff_transducer` (plus a real-snapshot ingest beyond og scope),
`ctm_ticks`, `map_elites_archive`, `slip_validator`, `asset_pipeline`,
`workshop_editor`, plus later additions (`lifecycle_sim`,
`readability_benchmark`, `architecture`, `package_promotion`,
`runtime_integration`). WFC lives as the constrained/WFC-style
generator inside `grid_genome` (`constrained_generator.py`;
`data/generated_grids/constrained_wfc_style/`). The Stage 2 bake-off ran
(three generator families in `data/generated_grids/`: markov_local,
constrained_wfc_style, lineage_constrained).

### 2.4 Grid genome — PRESERVED with two PARTIALs

- Formal genome G=(C,A,N,O,M,P): schema + numbered invariants + validator
  all shipped and promoted. Cell attributes carry the full og list
  (x, y, visual, role, material, mutation weight, anchor, organ,
  damage/stress state) — `research/grid_genome/grid_genome.schema.json`.
- **PARTIAL — grid size**: og research question 2 asked "8×8, 16×16,
  24×24, 32×32?" and og-research's sketch was 16×16. Everything shipped
  is 8×8; no decision record answers the size question. (TODO T6)
- **PARTIAL — species/animation fields**: og-research's starter grid
  schema carried `species_class`; og required animation-state vocabulary
  (idle/blink/sleep/beg/ill) and the `animstate_300` dataset. Current
  schema has a single animation anchor, no species_class, no state
  vocabulary. (TODO T4, T7)

### 2.5 SLIP profile — PARTIAL (the largest scope narrowing)

og SLIP scope: visual grammar, allowed materials, organ requirements,
palette constraints, behavior tendencies, mutation permissions, survival
weights, **learning switches, animation vocabulary, risk tolerances,
lineage preferences, forbidden traits, species class**.

Current `research/slip/slip.schema.json` (v0.1.0): palettes, body-mass
bounds, organ roles, 4 mutation caps, 3 behavior weights, 3 survival
weights. The narrowing is *honestly recorded* — the compatibility tests
and the constraint-baseline report both state that "animation vocabulary,
forbidden traits…" remain open — but there is **no concrete roadmap**
taking the schema from v0.1.0 toward the og scope, and the og's own
gates (20-archetype expressiveness test, fuzz pack, creator pilot) have
not run. `slip_zoo` target was 100 profiles (og-research dataset table);
15 exist. (TODO T3)

### 2.6 Micro-learning threads — PARTIAL

og listed ~11 predictors (hunger, sleep, boredom, attention, animation
preference, interaction timing, mood transition, mutation stability,
visual readability, SLIP compatibility, lineage survival).
`labs/grid_genome/micro_switchboard.py` implements a subset (hunger,
sleep, attention, grid/mutation stability among them) and the promoted
`mecha_engine.learning` carries the feedback loop with its measured
bounded claim. No census document maps og-thread → status. (TODO T5)

### 2.7 CTM track — PRESERVED as scoped; integration unverified

og's rule: "CTM is a conceptual research influence first… should not
become a core dependency until smaller micro-learning systems fail."
`labs/ctm_ticks/` + card + experiment report exist. Whether
confidence-gated extra switchboard cycles ("if confidence > 0.85 act;
else deliberate") ever reached the lifecycle/switchboard runtime is not
established by this audit. (TODO T8 verifies and decides)

### 2.8 CUBFF track — PRESERVED

The og hypothesis (tape → statistics → traits → SLIP-constrained grid,
never tape → pixels) is implemented in `labs/cubff_transducer/` with an
additional real-snapshot ingest lab and algorithm cards. This directly
addresses the owner's original CUBFF failure ("could not get the CUBFF
output to make any sense visually").

### 2.9 Workshop og responsibilities — PARTIAL by plan (slices)

| og responsibility | Status |
| --- | --- |
| Pixel art grid editor | Shipped (slice 1, live engine validation) |
| SLIP profile creator | Shipped (slice 2, authority + fit counts) |
| Behavior profile editor | Shipped within slice 2 (behavior/survival sliders) |
| Animation/state previewer | PARTIAL — render packets + live_cycle day (slice 3); no animation-state vocabulary to preview yet (blocked on T4) |
| Genome inspector | Planned (slice 5, owner-held) |
| Lineage browser | Planned (slice 5, owner-held) |
| Trait editor | MISSING as a named surface — cell roles/organs are editable, but og's trait-level editing (materials, mutation weights per cell) is not exposed (TODO T9) |
| Export/import tool | Shipped (slice 4: PNG/APNG/Aseprite/spritesheet over the proven codecs) |
| Community asset/profile system | Deferred behind a storage DR (documented) |
| og "semantic pixel editor, not a drawing tool" | Preserved — tools paint roles/organs; validation is semantic |

### 2.10 Evaluation framework — PARTIAL

Visual, evolution, and behavior metric families: implemented across the
readability benchmark, archive, and lifecycle labs. **Workshop
evaluation metrics** (authoring time, validator clarity, schema error
rate, custom-profile survival rate, first-session usability) and og's
human studies (semantic-vs-plain editor test, creator pilot) are not
instrumented — consistent with the owner's standing deferral of manual
survey data, but they need a tracked place. (TODO T10)

### 2.11 Datasets — PARTIAL

| og dataset | Status |
| --- | --- |
| mechaseed_50 | ✔ 50 seed grids |
| grid_invalid_200 | ✔ exactly 200 invalid cases |
| generated test grids (100+) | ✔ three generator families under `data/generated_grids/` |
| mechaseed_200 | ✗ (TODO T11) |
| mutationbench_5000 | ✗ as a named corpus (mutation evaluation exists in labs) (T11) |
| animstate_300 | ✗ — blocked on the animation vocabulary (T4) |
| slip_zoo_100 | PARTIAL — 15 profiles (T3) |
| replay_100k_ticks | ✗ as a corpus; runtime artifacts are smaller (T11) |
| humanratings_v1 | Pipeline shipped; data owner-deferred (documented) |
| asset_ledger_v1 | ✔ ledger + attribution manifest + CI report, SPDX ids |

### 2.12 Render bridge — PARTIAL

og-research's bridge diagram names three consumers: runtime renderer,
workshop preview, **recorded replay**. The packet contract is promoted
and the workshop preview consumes it; a replay recorder/consumer does
not exist. (TODO T12)

### 2.13 Asset sourcing/provenance — PRESERVED

Tiered sourcing policy, provenance ledger with SPDX identifiers,
attribution manifest, and a provenance CI gate all exist
(`data/asset_provenance/`, promoted `mecha_engine.provenance`). The
Piskel/Pixelorama/LibreSprite UX study happened
(`research/source_notes/2026-05-12-primary-source-review.md`,
literature map) and og's recommendation — study, don't embed; build
native; support standard formats — is exactly what shipped.

---

## 3. Audit summary

- **No foundational design error.** The engine is the application in
  code, tests, documents, and governance; the workshop is chartered as
  subordinate in the og's own words.
- **One structural correction required (T1):** workshop-authored
  creatures must become usable assets *inside* the ecosystem simulations
  — the og triangle's return path. This is the owner's [00] made
  concrete.
- **Largest scope narrowing:** SLIP v0.1.0 vs the og SLIP (learning
  switches, animation vocabulary, risk tolerances, lineage preferences,
  forbidden traits, species class) — honestly labeled, never roadmapped.
  Now roadmapped (T3/T4).
- Everything else og-specified is present, consolidated under different
  lab names, staged behind documented gates, or explicitly owner-deferred
  — with the PARTIALs enumerated above and tasked in `audits/TODO.md`.

## Sources

- `.depreciated/og-design.md`, `.depreciated/og-formatted.md`, `.depreciated/og-research.md`
- `README.md`, `docs/00-agent_onboarding.md`, `docs/workshop/mecha-workshop-design.md`
- `research/grid_genome/grid_genome.schema.json`, `research/slip/slip.schema.json`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `labs/cubff_transducer/`, `labs/ctm_ticks/`, `labs/grid_genome/`, `labs/workshop_editor/`
- `data/seed_grids/`, `data/invalid_grids/`, `data/generated_grids/`, `data/slips/`, `data/asset_provenance/`
- `research/decision_records/0010-start-mecha-workshop-build-track.md`
- `audits/TODO.md`
