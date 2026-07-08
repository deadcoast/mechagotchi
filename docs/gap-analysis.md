# Gap Analysis — The Documented Application vs What Exists (2026-07-07)

Commissioned by the owner's course correction: the implementation had
been measured against self-invented cycle queues instead of the
repository's own documentation. This document measures against the
documentation — `docs/project-research/validity-research.md` (the
founding vision + MVP staging), `docs/project-research/deep-research/01/
deep-research.md` (the research dossier and staged program),
`docs/project-research/research.md` (the research plan), and the
workshop/CLI charters. It is the source for every development cycle
until it is retired.

## 0. The two builds (the frame everything below sits in)

**We are building TWO things** (owner, 2026-07-07; validity-research
§1.5–1.7 says the same):

1. **THE ENGINE** — the Mechagotchi Computational Life Engine,
   inspired by CuBFF: genome grids, generation, validation, lifecycle,
   repair, evolution archives, micro-learning, SLIP interpretation,
   the render bridge. `packages/mecha_engine` and everything that
   proves it.
2. **THE GAME** — a showcase built ON the engine, with its own USER
   FRONT END: a playable client a person launches and plays. The
   Keeper/era design (DR 0021) is the game's DESIGN; the dev-served
   workshop HTML pages are NOT its front end — the playable layer does
   not exist yet and is a first-class build target, not an
   afterthought.

They sell each other, so both must be high quality and creative or
neither matters. **The engine is built before the game.** Every cycle
plan names which build it serves. The recurring failure mode this
document guards against: periscoping into one feature or module,
treating it as the whole application, overdeveloping it, and losing
the picture below.

The workshop is the third surface — the authoring layer serving both
(it feeds the engine creatures/profiles and gives the game its
creator loop) — and the CLI remains supportive tooling only.

## 1. What the application IS (the documents' own words)

> "Mechagotchi is an open-source digital companion engine where
> grid-based creatures are born from procedural genomes, guided by
> SLIP profiles, shaped by user interaction, and evolved through a
> lightweight Darwinian intelligence system composed of Markov
> prediction, micro-learning threads, and quality-diversity survival
> archives." (validity-research §1.35)

A living, 90s-retro LCD-device creature whose grid is simultaneously
"body, genome, memory surface, animation system, and evolutionary
substrate." Two builds: `mecha_engine` (life simulation, evolution,
prediction, companion logic — THE core) and `mecha_workshop` (the
semantic authoring layer). The user raises a creature with visible
needs; across lifecycles it dies, mutates, and produces children that
grow "more complex over time based on the survival of its ancestors";
users author species via SLIP and the workshop; the render bridge is
front-end agnostic (web, Godot, terminal, Pygame, desktop) with retro
effects (scanline, lcd_ghosting, crt_bloom, glitch).

## 2. The honest position

**The RESEARCH program (dossier Stages 0–6) is substantially executed.**
That is what the past cycles genuinely built: the ontology, the schema,
the validators, the labs, the promoted modules, the gates, the evidence
ledger. It is real and it is the repo's strength.

**The APPLICATION the documents specify is barely begun.** What exists
at the product layer is Stage-0-scale proofs wired into demo pages.
Nothing yet reaches even MVP 0.1's own named target (validity §1.34):
*"A 16×16 monochrome grid creature that is generated from a genome,
has hunger/energy/mood/age, changes expression by state, logs
interactions, mutates after death, produces a child using parent
traits, saves a lineage file. This proves the entire thesis."*

## 3. The gap, measured

| Surface | The documents specify | What exists | Gap |
| --- | --- | --- | --- |
| **Grid scale** | 16×16 primary target; SLIP ranges 12×12–32×32; schema to 64 | 8×8 grids, ~13 body cells | The foundational gap — everything downstream is proven only at toy scale |
| **Generation** | Hybrid architecture: Markov → **WFC/constraints** → mutation → validator → MAP-Elites; bake-off vs random/Markov/MRF/WFC/grammar/CA at ≥85–95% validity, ≤250 ms @16×16 | Markov-style generator + validator + repair. **No WFC lab exists at all** (`labs/wfc_grid/` was never created); no grammar, no MRF, no CPPN arms; bake-off ran without the documented field | The documented winning architecture is missing its constraint layer |
| **Evolution scale** | 8×8×8 ≈ 576 niches; populations ~256; 20k–50k evaluations; coverage ≥25%; ≥5 recurrent families; MAP-Elites ≥25% coverage over GA | population 4, 3 generations, 16 ticks, a handful of niches | ~3 orders of magnitude below the documented regime; none of the scale gates ever run |
| **Micro-learners** | ~11 named threads (hunger/sleep/boredom/attention predictors, animation-preference bandit, interaction timing, HMM mood, mutation stability, readability, SLIP compat, lineage survival) each streaming confidence into the switchboard; 5 synthetic user models; 100k-tick × 500-lifecycle benchmark; ablation gates (≥15% welfare; drop any learner whose removal costs <5%) | A frozen rule switchboard + one feedback learner + a 7-weight linear ranker | The "intelligence threads" thesis — the owner's core ML idea — is ~2 threads of 11, with no user models and no ablation harness |
| **Companion state** | Visible: hunger, happiness, energy, cleanliness, mood, age, health, bond; hidden: mutation pressure, lineage fitness, stress, novelty decay, attachment, response confidence, profile alignment, grid stability | hunger, energy, stress, bond, grid_stability, age | Missing visible axes (happiness, cleanliness, health) and most of the hidden layer |
| **Animation** | Animation CLIPS with frames, anchors, transition validity ≥80%, `animstate_300` dataset; packet carries clip/frame_index | Single state name + a pulse frame for APNG export; no clips, no frames, no transitions, no dataset | The animation SYSTEM does not exist — only a vocabulary gate |
| **Rendering** | Front-end-agnostic render bridge (web, Godot, terminal, Pygame, desktop); retro effects pipeline (scanline, lcd_ghosting, crt_bloom, glitch); ui_hints (need icons, attention ping) | One HTML canvas drawer; no effects; no second runtime; no ui_hints | The bridge contract is documented but only one consumer of a partial packet exists |
| **Tech stack** | Pydantic 2 data model; NumPy-first (Numba optional); optional JAX/QDax; z3-solver; Parquet/JSONL analytics; TS+React+Canvas/WebGL workshop path | stdlib dicts; zero NumPy; pydantic lab-side only; SQLite + JSON | Was BLOCKED by the stdlib-only policy — now unblocked (DR 0028); the scale work above genuinely needs NumPy |
| **Workshop** | Semantic pixel editor with layers, onion skin, animation timeline, behavior editor; community asset/profile system; ≤45-min first-session creature+SLIP | Single-page editors (grid/slip/preview/inspect — solid, engine-true, but single-layer, single-frame); community system deferred | Authoring depth: layers/onion-skin/timeline/behavior editor absent |
| **CuBFF** | Semantic transducer over REAL runs: 20 runs, 400 curated states; keep if preference >60%, invalid <10% | Transducer lab + synthetic snapshots; real ingest seam only | REQUIRED, late-stage (owner, 2026-07-07) — the corpus and the study remain |
| **Delivery** | Stage 7 / M7: vertical integration → PUBLIC ALPHA, reproducible from docs and CI; distributable app | No CI, no packaging, no installable app; surfaces run from a dev checkout | The product has no delivery form at all |
| **MVP ladder** | MVP 0.1 (companion loop @16×16) → 0.2 (+Markov gen, micro-threads, editor) → 0.3 (+archive, niches, import/export, lineage browser, community packs) | Pieces of each scattered across research surfaces; no single coherent product at ANY MVP rung | The ladder was never climbed as a product |

Aligned and genuinely done per the docs: the ontology/glossary, the
grid schema + validators (at 8×8), SLIP schema + zoo + authoring, the
CTM-inspired deliberation (internal ticks, confidence gating — exactly
the documented "conceptual influence, not the full model"), MAP-Elites
mechanics (at toy scale), provenance/SPDX/REUSE machinery, the
datasets program (mechaseed_200, mutationbench_5000, replay_100k_ticks
— documented data products, delivered), the rating pipeline, storage
(SQLite), and the workshop's engine-truth discipline.

## 4. The build program (derived from the documents' own sequencing)

The dossier's rule: "Formalize first, compare generators second, prove
diversity third, test exotic ideas fourth, build authoring tooling
fifth, integrate last." Research formalized; now the two builds climb
the documented ladder in order — **the ENGINE track completes before
the GAME track begins in earnest** — each phase at REAL scale:

### ENGINE track (Phases A–E)

- **Phase A — the 16×16 foundation.** Migrate the genome/corpus/
  validator/generator/repair/lifecycle to the documented primary grid
  scale (schema already permits it); re-derive invariants and re-run
  the standing gates at 16×16; NumPy enters where the scale demands it
  (DR 0028). **COMPLETE (cycle 09, 2026-07-08)** — gate report
  `research/experiment_reports/2026-07-08-phase-a-gate.md` (DR 0029/
  0030; NumPy measured NOT demanded at this scale; the honest
  8×8-remainder list lives in the gate report).
- **Phase B — the missing generation layer.** Build `labs/wfc_grid/`
  (the documented WFC/constraint generator), then run the REAL
  documented bake-off (random vs Markov vs WFC vs hybrid at 16×16,
  dossier thresholds) and adopt the winner into `generation`.
  **COMPLETE (cycle 10, 2026-07-08)** — gate report
  `research/experiment_reports/2026-07-08-phase-b-gate.md` (WFC won and
  ships in the engine, DR 0031; the documented hybrid was REFUTED by
  the pre-registered rule and the refutation recorded with its named
  re-opener; evolve's inner loop deliberately stays on the constrained
  path pending its own evidence).
- **Phase C — the animation system.** Clips, frames, anchors,
  transitions (≥80% transition validity), `animstate_300`, the packet's
  documented clip/frame_index contract, and the retro effects pipeline
  — the render BRIDGE contract the game's client will consume.
- **Phase D — the intelligence threads.** The named micro-learner
  fleet streaming confidences into the switchboard; the 5 synthetic
  user models; the 100k-tick × 500-lifecycle harness; the documented
  ablation gates.
- **Phase E — evolution at documented scale.** Hundreds of niches,
  populations in the hundreds, 20k+ evaluations, the coverage/QD/
  family gates (QDax path optional per the dossier).

### GAME track (Phase F) — the build the engine exists to showcase

- **Phase F — the playable game.** A REAL user front end: a game
  client a player launches and plays — not dev-served workshop pages.
  The Keeper/era design (DR 0021) and the companion loop are its
  DESIGN inputs; the client consumes the engine's render-packet
  bridge and the retro effects pipeline; the MVP ladder (0.1 → 0.2 →
  0.3, validity §1.21–1.24) is climbed as PRODUCT releases —
  installable, launchable, with save files. Front-end technology
  chosen by decision record when the phase opens (the docs name web /
  Godot / terminal / Pygame / desktop as bridge targets and TS+React
  as the documented workshop scale-path).

### Shared / late-stage (Phase G)

- **Phase G — the late-stage requireds.** Real-CuBFF corpus + the
  transducer study (20 runs / 400 states, the documented keep gates);
  community asset/profile system; CI + reproducibility; the M7 public
  alpha of BOTH builds.

Each phase decomposes into cycle TODOs; `audits/TODO.md` always names
its phase AND its build track. This document is retired only when
Phase G's alpha gate is green.

## Sources

- `docs/project-research/validity-research.md` (§1.3 core function, §1.9 life loop, §1.14–1.18, §1.21–1.34 MVP ladder and first target)
- `docs/project-research/deep-research/01/deep-research.md` (both concatenated reports: scale figures, thresholds, stages M0–M7)
- `docs/project-research/research.md` (stages, layers, evaluation framework)
- `docs/mecha-workshop/mecha-workshop-design.md`, `docs/cli/mechas-cli.md`
- `research/decision_records/0028-license-and-dependency-policy.md`
- owner course correction, 2026-07-07
