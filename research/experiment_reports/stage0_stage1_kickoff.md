# Experiment Report: Stage 0 and Stage 1 Kickoff

Date: 2026-05-12

## Objective

Begin the research phase defined by `docs/02-research_plan.md` by establishing
the active research structure, ontology, source map, first grid contract, and
algorithm cards.

## Work Performed

1. Reviewed `docs/01-brainstorming.md`.
2. Reviewed `docs/02-research_plan.md`.
3. Inventoried the existing shelved deep research report and source list.
4. Checked project state with Git; existing modified file:
   `docs/01-notes/01-prompts.md`.
5. Queried Serena project memory; no project memory existed.
6. Queried durable memory; no Mechagotchi hits existed.
7. Ran targeted web source review.
8. Queried Context7 for Pydantic schema/validation documentation.
9. Created initial `/research` evidence artifacts.

## Outputs Created

- `research/README.md`
- `research/questions.md`
- `research/glossary.md`
- `research/literature_map.md`
- `research/grid_genome/grid_genome.schema.json`
- `research/grid_genome/grid_invariants.md`
- `research/algorithm_cards/*.md`
- `research/source_notes/2026-05-12-primary-source-review.md`
- `research/decision_records/0001-research-ontology-and-first-sequence.md`
- `research/asset_provenance/ledger.schema.md`

## Findings

The existing project docs already converge on the right research stance:
Mechagotchi should be a semantic grid-genome companion engine, not a virtual-pet
clone or a procedural sprite toy.

The first measurable dependency is the grid genome and validator. Without that,
Markov, WFC, MAP-Elites, CUBFF, CTM, NCA, and workshop authoring cannot be
compared fairly.

## Open Work

1. Create 50 hand-authored seed grids. Done in `data/seed_grids/`.
2. Create 200 invalid counterexample grids. Done in `data/invalid_grids/`.
3. Implement the first validator lab. Done in `labs/grid_genome/validator.py`.
4. Emit a first validation report. Done in
   `research/experiment_reports/2026-05-12-grid-validator-baseline.md`.
5. Build the random mutation baseline. Done in
   `research/experiment_reports/2026-05-12-random-mutation-baseline.md`.
6. Build Markov and WFC generator labs. Raw Markov prototype is done in
   `research/experiment_reports/2026-05-12-markov-local-generator.md`;
   constrained WFC-style stabilization is done in
   `research/experiment_reports/2026-05-12-constrained-wfc-style-generator.md`.
7. Add SLIP constraints. First profile-constrained generation baseline is done
   in `research/experiment_reports/2026-05-12-slip-constraint-baseline.md`.
8. Build first MAP-Elites archive. First CPU archive baseline is done in
   `research/experiment_reports/2026-05-12-map-elites-archive-baseline.md`.
9. Add lineage tracking. First lineage graph baseline is done in
   `research/experiment_reports/2026-05-12-lineage-tracking-baseline.md`.
10. Build micro-learning switchboard. First interpretable switchboard baseline
    is done in
    `research/experiment_reports/2026-05-12-micro-switchboard-baseline.md`.
11. Run CUBFF semantic transducer lab. First synthetic CUBFF-style transducer
    baseline is done in
    `research/experiment_reports/2026-05-12-cubff-semantic-transducer-baseline.md`.
12. Build minimal workshop editor. First semantic workshop editor baseline is
    done in
    `research/experiment_reports/2026-05-12-workshop-editor-baseline.md`.

## Decision

Proceed to the seed grid corpus and validator baseline before any advanced lab
track.
