# Mechagotchi Research Report v0.1

Date: 2026-05-12

## Executive Summary

The first research sequence supports the central thesis: Mechagotchi is most
promising as a semantic grid-genome companion engine, not as a plain virtual pet
or sprite generator.

The completed labs show that:

- A compact 8x8 semantic grid can encode body, sensors, expression, mutation,
  animation anchor, palette, and lineage metadata.
- A semantic validator gives the project a measurable foundation.
- Raw Markov and random mutation are useful baselines but not sufficient.
- Constraint-guided generation plus validation is the strongest current visual
  generation path.
- SLIP can constrain generation without breaking validity.
- MAP-Elites improves repertoire coverage over scalar top-k selection.
- Lineage tracking, micro-learning, CUBFF transduction, workshop authoring, and
  provenance now have working Stage 0 prototypes.

The strongest current architecture is still a small cooperating system:

```txt
SLIP profile
  -> constrained grid generator
  -> validator
  -> companion genome
  -> micro-learning switchboard
  -> MAP-Elites archive
  -> lineage mutation
  -> workshop/export/provenance
```

## Research Scope

This report consolidates the first planned research sequence from
`docs/02-research_plan.md`:

1. Define grid genome schema.
2. Create 50 hand-authored seed creatures.
3. Build grid validator.
4. Build random mutation baseline.
5. Build Markov grid generator.
6. Build WFC grid generator.
7. Compare Markov vs WFC vs random.
8. Add SLIP constraints.
9. Build first MAP-Elites archive.
10. Add lineage tracking.
11. Build micro-learning switchboard.
12. Run CUBFF semantic transducer lab.
13. Build minimal workshop editor.
14. Add asset provenance ledger.
15. Publish research report v0.1.

## Primary Artifacts

| Area | Artifact |
| --- | --- |
| Ontology | `research/questions.md`, `research/glossary.md`, `research/literature_map.md` |
| Grid contract | `research/grid_genome/grid_genome.schema.json`, `research/grid_genome/grid_invariants.md` |
| Seed corpus | `data/seed_grids/`, `data/invalid_grids/` |
| Labs | `labs/grid_genome/`, `labs/cubff_transducer/`, `labs/workshop_editor/`, `labs/asset_pipeline/` |
| Archive | `data/archives/map_elites_stage0.json` |
| Lineage | `data/lineage/lineage_stage0.json` |
| Switchboard | `data/micro_learners/switchboard_stage0.json` |
| CUBFF transducer | `data/cubff_transducer/cubff_transducer_stage0_report.json` |
| Workshop | `data/workshop_editor/workshop_editor_stage0_report.json` |
| Provenance | `data/asset_provenance/ledger.json` |

## Experiment Results

| Experiment | Result | Decision |
| --- | ---: | --- |
| Validator | 50/50 valid seeds accepted; 200/200 invalid counterexamples rejected | Adopt as foundation |
| Random mutation | 42/100 valid | Keep as baseline |
| Raw Markov local generator | 13/100 valid | Watch; needs repair/constraints |
| Constrained WFC-style generator | 100/100 valid; 100 unique signatures | Prototype/adopt as stabilizer |
| SLIP constrained generation | 50/50 valid and aligned | Prototype |
| MAP-Elites archive | 24 occupied niches; coverage 0.192; best fitness 0.898214 | Prototype |
| Scalar top-k comparison | 7 occupied niches; coverage 0.056 | Reject as sole archive |
| Lineage tracker | 250 nodes; 200 edges; 0 orphans | Prototype |
| Micro-switchboard | 3 scenarios; feed/sleep/play selected as expected | Prototype |
| CUBFF direct visual baseline | 0/12 valid | Reject direct mapping |
| CUBFF semantic compiler | 12/12 valid and SLIP aligned | Watch; synthetic only |
| Workshop editor | Export valid and SLIP aligned | Prototype |
| Asset provenance ledger | 7 assets tracked; validation ok | Adopt for research artifacts |

## Decisions

### Adopt

- Semantic grid genome as the shared research substrate.
- Validator-gated generation as the baseline safety gate.
- Internal seed grids and invalid counterexamples as the first benchmark.
- Asset provenance ledger for committed research artifacts.

### Prototype

- Constrained WFC-style stabilizer.
- SLIP profile validation and aligned generation.
- CPU MAP-Elites archive.
- Lineage graph generation.
- Micro-learning switchboard.
- Minimal semantic workshop editor.

### Watch

- Raw Markov generation as a source of local probabilities.
- CUBFF semantic transduction, pending real CuBFF snapshot ingestion.
- CTM concepts as inspiration for internal ticks and confidence gates.
- NCA/CA morphogenesis until the discrete grid baseline matures.

### Reject For Core v0.1

- Direct CUBFF tape-to-pixel mapping.
- Scalar top-k as the only evolutionary selection strategy.
- Third-party editor embedding before semantic round trips are proven.
- External art in default/core paths without ledger approval.

## Interpretation

The main technical lesson is that novelty must be mediated through semantics.
Raw generative signals can be interesting but invalid. The project becomes
measurable only when every generator emits a grid genome that the validator,
SLIP profile, archive, lineage tracker, and workshop can all inspect.

The current best generator path is not pure WFC, Markov, CUBFF, or MAP-Elites.
It is a pipeline:

```txt
seed corpus
  -> local pattern constraints
  -> validator-gated mutation
  -> SLIP alignment
  -> archive scoring
  -> lineage recording
```

The strongest product implication is that Mechagotchi should expose semantic
authoring, not generic pixel editing. The workshop must let creators paint
meaningful organs and mutation surfaces, then export a valid genome.

## Risks

- The constrained generator currently starts from valid parents, so it may be
  conservative.
- Readability is still represented by proxy metrics, not human ratings.
- The CUBFF result is synthetic-only and must not be treated as adoption
  evidence.
- MAP-Elites descriptors are provisional and may not represent final species
  diversity.
- Provenance is not yet CI-enforced across the whole repository.

## Next Research Sequence

1. Add a lifecycle simulator to measure survival, need balance, and recovery.
2. Add a held-out readability benchmark and manual rating protocol.
3. Extend MAP-Elites descriptors beyond body mass, sensors, and symmetry.
4. Add import/export round trips to the workshop editor.
5. Ingest real CuBFF snapshots before revisiting CUBFF adoption.
6. Add provenance CI checks and SPDX expression parsing.
7. Start CA/NCA growth and repair labs only after lifecycle metrics exist.

## Publication Status

This is a research publication inside the repository, not a production release.
The report is versioned as v0.1 because it consolidates the first working
research baseline and identifies the next gates.
