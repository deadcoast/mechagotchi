# Primary Source Review - 2026-05-12

## Method

Reviewed the current planning docs, existing shelved research dossier, and
primary web sources. Used Serena for project context and Context7 for Pydantic
schema documentation. Context7 did not resolve QDax, so QDax was checked
through official web docs and paper sources.

## Confirmed Source Facts

- The PCG Book is the correct taxonomy source for constructive generation,
  search-based generation, grammars, ASP, mixed-initiative creation, and
  generator evaluation.
- WFC preserves local NxN patterns from inputs, runs observation plus
  propagation, can contradict, supports constraints, and has an MIT-licensed
  reference implementation with sample assets called out separately.
- MAP-Elites is a quality-diversity archive method that stores diverse
  high-performing solutions over user-chosen dimensions.
- QDax uses a modular MAP-Elites framing around container, emitter, and scoring
  function, which maps cleanly onto Mechagotchi archive architecture.
- CUBFF is an Apache-2.0, optionally CUDA-based implementation for
  self-modifying program soups used by the Computational Life experiments.
- CTM's reusable concept is internal time and synchronization, not a required
  dependency for the core engine.
- Avida is a free, open-source scientific platform for experiments with
  self-replicating and evolving computer programs.
- Piskel is Apache-2.0 and useful as a web sprite-editor UX reference.
- Pixelorama is MIT licensed and useful for import/export, metadata, extension,
  and command-line workflow research.
- SPDX provides standardized license identifiers and canonical license URLs.
- REUSE provides a file-level licensing practice for humans and machines.
- JSON Schema Draft 2020-12 is the schema dialect used by the first
  `grid_genome.schema.json` contract.
- Python `unittest` is sufficient for the first lab validator because the repo
  has no package-level test dependency yet.

## Active Interpretation

The research should not adopt an exotic center of gravity. The center should be:

```txt
grid genome -> validator -> generator bake-off -> life simulation
-> micro-learning switchboard -> MAP-Elites archive -> SLIP/workshop tooling
```

CUBFF, CTM, and NCA stay as lab tracks until the baseline can measure them.
