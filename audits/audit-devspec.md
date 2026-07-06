# Development-Spec Audit: Original Design vs Current Source

Date: 2026-07-05. Commissioned by the owner (DESIGN-CORRECTION [00]–[3]):
review the depreciated first-version documents — `.depreciated/01-design.md`,
`.depreciated/01-formatted.md`, `.depreciated/01-research.md` — and confirm
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
  01-design.md [1]'s disclaimer verbatim in spirit: the engine generating
  its own mechagotchi from survival ancestry "IS THE MAIN AND CORE
  FUNCTION"; the editor exists "TO CREATE CUSTOM ASSETS FOR THE ENGINE,
  NOT THE CORE ENGINE ITSELF."
- **The missing wire (the real correction):** 01-design.md [1] defines
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
| Hybrid stack, no single algorithmic center (01-formatted §12/§13) | Markov generation + constraint validation + CA/NCA repair + MAP-Elites + micro-learners + SLIP + switchboard, each its own module/lab |
| "External novelty mediated through a semantic compiler" (01-research) | `labs/cubff_transducer/` implements exactly the tape→features→traits→grid pipeline; direct tape→pixels rejected per the og decision rule |
| Two-build model | Engine = `packages/mecha_engine`; workshop = `workshop/` app tree. **DIVERGED (documented)**: og placed the workshop under `packages/mecha_workshop/` with TS+React; DR 0010 chose dependency-free served pages first, TS+React recorded as the DR-gated scale-up path |

### 2.2 Research infrastructure — PRESERVED

01-formatted's research tree (`questions.md`, `literature_map.md`,
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
  24×24, 32×32?" and 01-research's sketch was 16×16. Everything shipped
  is 8×8; no decision record answers the size question. (TODO T6)
- **PARTIAL — species/animation fields**: 01-research's starter grid
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
not run. `slip_zoo` target was 100 profiles (01-research dataset table);
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

01-research's bridge diagram names three consumers: runtime renderer,
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

- `.depreciated/01-design.md`, `.depreciated/01-formatted.md`, `.depreciated/01-research.md`
- `README.md`, `docs/00-agent_onboarding.md`, `docs/workshop/mecha-workshop-design.md`
- `research/grid_genome/grid_genome.schema.json`, `research/slip/slip.schema.json`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `labs/cubff_transducer/`, `labs/ctm_ticks/`, `labs/grid_genome/`, `labs/workshop_editor/`
- `data/seed_grids/`, `data/invalid_grids/`, `data/generated_grids/`, `data/slips/`, `data/asset_provenance/`
- `research/decision_records/0010-start-mecha-workshop-build-track.md`
- `audits/TODO.md`

---

# Addendum (2026-07-05): RUN TWO documents — `.depreciated/02-design.md`, `.depreciated/02-research.md`

Second pass of the same audit workflow, per the owner's follow-up. The
02 files are the "Deep Research Program — RUN TWO": a second-generation
research plan with concrete starter schemas, statistical protocols, and
a recommended stack. Verdicts as before; every claim below was checked
against the current tree.

## A0. Document-integrity findings (the "corrupt injection" question)

- **`02-design.md` and `02-research.md` are byte-identical** (verified
  with a file diff). One document exists twice under two names — likely
  the artifact of a copy step during the original research runs. No
  content conflict *between* the two; the conflict is between RUN TWO
  and RUN ONE.
- **The RUN ONE / RUN TWO design fork is real, and it was never
  reconciled.** The two runs propose *different* SLIP shapes: RUN ONE
  (01-formatted, Layer 7) constrains palettes, body mass, and organ
  roles; RUN TWO's starter SLIP constrains grid **sizes** and
  **allowed roles**, requires `species_class`, and adds a whole
  `render` block (effects enum: lcd_ghosting/scanline/crt_bloom/glitch;
  `animation_vocab`), `mischief`/`sociability` behaviors, and
  `limb_growth`/`max_edit_fraction` mutation knobs. The shipped
  `slip.schema.json` follows **RUN ONE's shape** and takes none of RUN
  TWO's additions — a silent fork resolution with no decision record.
  This is the "conflict and confusion" the owner sensed: two competing
  specs in the historical record, one adopted implicitly. (TODO T14
  reconciles it explicitly.)

## A1. Grid genome schema — RUN TWO largely PRESERVED, but **dormant**
(refines finding 2.4 of the main audit)

Direct schema inspection corrects the first audit's impression: the
shipped `grid_genome.schema.json` DID adopt RUN TWO's expressiveness —
role enum `empty/body/shell/sensor/eye/mouth/joint/limb/antenna/
decoration/effect/anchor`, extended materials
(`void/soft/hard/glass/joint/light/signal`), organs as an open map (any
organ ids, `minProperties: 1`), and `grid_size` bounded 8-64 exactly as
RUN TWO specified. **However, the entire ecosystem exercises only the
narrow subset**: every corpus, generator, validator invariant, workshop
tool, and test uses body/eye/mouth roles, three fixed organs
(core/sensors/expression), and 8x8. The rich vocabulary is legal but
has zero coverage, zero invariants, zero rendering rules, and zero
workshop affordances — dormant spec, silently divergent from practice.
(TODO T15.) Two deliberate-looking divergences worth recording: shipped
materials differ from RUN TWO's proposal (`metal/gel/wire/organic` ->
`soft/hard/glass/joint/light/signal`) and shipped cells carry `visual`
hex colors instead of RUN TWO's `value` byte channel — both fine, both
undocumented as decisions.

## A2. Render packet — PARTIAL, now precisely scoped

BOTH runs specify the packet carries `animation`, `mood`, and `effects`
(RUN TWO adds `frame_id` and `ui_hints` such as `needs_attention`). The
promoted `render_packet_from_grid` emits `grid_id/grid_size/palette/
cells/state`, where `state` is an opaque caller passthrough — no
animation, mood, effects, or ui_hints contract exists anywhere. The
first audit caught the animation-vocabulary gap (T4); RUN TWO sharpens
it into a full packet-contract v2 requirement. (TODO T16.)

## A3. Experimental protocols — methods adopted, RUN TWO gates never run

- **Generator bake-off**: the arms exist and ran
  (`data/generated_grids/`: random_mutation_baseline, markov_local,
  constrained_wfc_style, lineage_constrained, slip-constrained) — but at
  Stage-0 scale. RUN TWO's protocol (120-seed corpus split 72/24/24,
  16x16 AND 24x24, 18,000 candidates/arm, 720-sample human panel,
  bootstrap CIs, Bradley-Terry preference model, gates: >=95% validity,
  >=3.5/5 readability, <=15% novelty loss, <250 ms) was never executed.
  The generator choice is evidence-based but not RUN-TWO-rigorous.
  (TODO T17; couples to the grid-size DR T6, since the protocol demands
  the larger sizes.)
- **MAP-Elites comparator study**: RUN TWO's keep-gate requires beating
  a GA baseline (pop 256) and a novelty-search baseline at 50k evals x
  10 seeds (>=25% coverage advantage, best-fitness within 10%). No GA
  or novelty-search comparator exists anywhere in the repo — MAP-Elites
  was adopted without its specified comparison. The archive works and
  is contract-tested, but the og-claimed superiority is unmeasured.
  (TODO T18.)
- **Micro-learner remove-one ablation**: RUN TWO specifies 5 synthetic
  user models (attentive/neglectful/erratic/punitive/exploratory) x 500
  lifecycles x remove-one-learner conditions, keep-gate = removal costs
  >=5% on a target metric. Never run (the shipped ablation work was
  repair-context, a different question). (TODO T19.)
- **Statistical/protocol standards**: fixed seeds — met repo-wide;
  train/dev/holdout splits — absent; "threats to validity" notes —
  absent; blind **pairwise** human judgments with Bradley-Terry —
  absent (the shipped rating tool is a 1-5 rubric — consistent with the
  bake-off's rubric metric, but RUN TWO's preferred pairwise-preference
  protocol has no tooling). (TODO T17/T20.) RUN TWO's ADR verb set
  (adopt/defer/watch/reject) differs cosmetically from the shipped card
  verbs (reject/watch/prototype/adopt) — no action needed.

## A4. Dataset program (RUN TWO table) — PARTIAL

| RUN TWO dataset | Status |
| --- | --- |
| Seed Grid Corpus v1 (120, split 72/24/24) | 50 exist, no split (RUN ONE's 50 was met; RUN TWO raised the bar) |
| Holdout Grid Corpus (24 hidden) | absent — no holdout discipline anywhere (T17) |
| SLIP Corpus (8 defaults + adversarial) | 3 valid + failure cases (T3.6 covers growth) |
| Lineage Log Lake (JSONL/Parquet) | PARTIAL — `data/lineage/` artifacts exist; no accumulating log-lake convention (T11) |
| Human Readability Panel (pairwise) | tool shipped (1-5 rubric); pairwise protocol absent (T20); data owner-deferred |
| CuBFF Snapshot Corpus | present — `data/cubff_real_ingest/` + transducer corpora |
| Asset Provenance Ledger | present — ledger + SPDX + attribution manifest + CI report |

## A5. Stack recommendations — mostly deliberate divergence, three silent

Documented/deliberate: stdlib-first instead of NumPy/Pydantic-everywhere
(DR 0005 scopes the lab dependency exceptions), unittest instead of
pytest (CLAUDE.md convention), served dependency-free workshop instead
of TS+React (DR 0010), storage (SQLite/Parquet) deferred with the
`storage` module. Silent (no decision recorded): **z3/SMT constraint
solving** — both runs list SAT/SMT/ASP as the hard-validity track; the
shipped validator is stdlib BFS + rules, and the solver track was never
opened or formally rejected (fold into T14's reconciliation verdicts);
**REUSE repository structure** — SPDX identifiers exist in the ledger,
but the REUSE `LICENSES/` directory convention RUN TWO specifies is
absent (TODO T21); **Jupyter experiment notebooks** — never adopted,
arguably superseded by the executable-lab convention (record as
superseded in T14).

## A6. Addendum summary

RUN TWO's biggest contributions were (a) concrete starter schemas and
(b) rigorous statistical protocols. The schemas were **partially
adopted silently** (grid: yes but dormant; SLIP: no — RUN ONE's shape
won without a record). The protocols were **downscaled without a
record** (bake-off) or **skipped** (MAP-Elites comparators, learner
ablation, holdout discipline, pairwise studies). None of this
invalidates shipped evidence — every shipped claim is honestly scoped —
but the fork and the rigor gaps now have names and tasks. The corrective
pattern is one decision record (T14) that walks RUN TWO's deltas and
issues an explicit adopt/defer/reject verdict for each, so no future
session rediscovers this fork.

## Addendum sources

- `.depreciated/02-design.md`, `.depreciated/02-research.md` (verified identical)
- `research/grid_genome/grid_genome.schema.json`, `research/slip/slip.schema.json`
- `packages/mecha_engine/src/mecha_engine/genome/render.py`
- `data/generated_grids/`, `data/slips/`, `data/lineage/`, `data/cubff_real_ingest/`, `data/asset_provenance/`
- `labs/map_elites_archive/`, `labs/readability_benchmark/`
- `research/decision_records/0005-lab-dependency-exceptions.md`, `research/decision_records/0010-start-mecha-workshop-build-track.md`
