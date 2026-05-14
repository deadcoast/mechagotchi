# Decision Record 0001: Research Ontology and First Sequence

Date: 2026-05-12

## Status

Accepted.

## Context

`docs/02-research_plan.md` requires research to start with a living evidence
base, algorithm cards, decision records, source review, and staged experiments.
The proposed first research sequence starts with the grid genome schema, seed
creatures, validator, random mutation baseline, Markov generator, WFC
generator, and comparative bake-off.

## Decision

The active research program will start with:

1. Stage 0 ontology and glossary.
2. Stage 1 literature/source map.
3. Grid genome schema draft.
4. Grid invariants.
5. Algorithm cards for the first candidate systems.
6. Asset provenance ledger skeleton.

The first implementation research task after this pass is not CTM, CUBFF, NCA,
or workshop polish. It is the seed grid corpus and validator baseline required
to make all later experiments measurable.

## Consequences

- Algorithm novelty is gated by validation and measurable output.
- CUBFF and CTM remain research influences until the baseline exists.
- The workshop remains secondary until SLIP and grid contracts are real.
- The project gets a reproducible evidence trail before code enters
  `packages/`.

## Sources

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `docs/01-notes/01-shelved/03-reports/03-deep_research_report.md`
- `research/literature_map.md`
