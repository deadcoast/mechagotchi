# Literature Map

Reviewed on 2026-05-12 using the project docs, web search, Serena, and Context7.
Context7 resolved Pydantic documentation for schema generation. It did not
resolve QDax, so the official QDax docs and paper are used for that source.

## Source Priorities

| Track | Primary sources | Current stance |
| --- | --- | --- |
| PCG foundation | [PCG Book](https://www.pcgbook.com/) | Adopt as taxonomy for constructive, search-based, mixed-initiative, and evaluation work. |
| Grid local structure | [WaveFunctionCollapse](https://github.com/mxgmn/WaveFunctionCollapse) | Prototype as a local-pattern stabilizer, not the whole engine. |
| Evolution archive | [MAP-Elites paper](https://arxiv.org/abs/1504.04909), [QDax docs](https://qdax.readthedocs.io/en/latest/overview/), [QDax paper](https://arxiv.org/abs/2308.03665) | Prototype CPU MAP-Elites first; use QDax only after descriptors stabilize. |
| Digital evolution discipline | [Avida](https://avida.devosoft.org/) | Study for experiment controls, lineage data, and measurement discipline. Do not embed. |
| Morphogenesis | [Growing Neural Cellular Automata](https://distill.pub/2020/growing-ca/) | Watch/prototype after discrete grid validation is stable. |
| Artificial-life substrate | [Computational Life paper](https://arxiv.org/abs/2406.19108), [CUBFF repo](https://github.com/paradigms-of-intelligence/cubff) | Lab-only semantic transducer. Do not map raw tapes directly to pixels. |
| Internal time | [CTM repo](https://github.com/SakanaAI/continuous-thought-machines), [CTM report](https://pub.sakana.ai/ctm/) | Conceptual influence for ticks and confidence gates, not a dependency. |
| Schema validation | [Pydantic docs](https://docs.pydantic.dev/) via Context7 | Prototype Python contracts with `BaseModel.model_validate()` and `model_json_schema()`. |
| Workshop UX | [Piskel](https://github.com/piskelapp/piskel), [Pixelorama](https://github.com/Orama-Interactive/Pixelorama), [LibreSprite](https://github.com/LibreSprite/LibreSprite) | Study UX and metadata patterns; build Mechagotchi-native semantic editor. |
| Licensing | [SPDX License List](https://spdx.org/licenses/), [REUSE](https://reuse.software/) | Adopt SPDX IDs and REUSE-style file-level provenance early. |

## Evidence Extracts

### PCG Book

The PCG Book gives the project a practical taxonomy: constructive generation,
search-based generation, grammars, rules, ASP, mixed-initiative authoring, and
generator evaluation. Mechagotchi should use this as the frame for comparing
generators rather than treating one method as the whole system.

### Wave Function Collapse

The WFC reference implementation generates bitmaps that are locally similar to
an input by preserving observed NxN patterns and running an
observation-propagation cycle. It can hit contradictions, supports constraints,
and its overlapping model is related to higher-order Markov chains. This makes
it a strong candidate for local visual coherence and repair, but not for the
entire companion life loop.

### MAP-Elites and QDax

MAP-Elites is aligned with the Mechagotchi goal of many viable species types,
because it maps high-performing solutions across user-chosen behavior
dimensions. QDax documents the useful software decomposition: container,
emitter, and scoring function. This should influence the architecture even if
the first implementation is CPU-only and does not depend on JAX.

### Avida

Avida is a free, open-source platform for experiments with self-replicating and
evolving computer programs. Its main value for Mechagotchi is not code reuse;
it is the discipline around experimental settings, measurement tools, and
post-processing.

### Growing Neural Cellular Automata

Growing NCA shows that local update rules can grow, persist, and regenerate
patterns. It is relevant to Mechagotchi growth, repair, stress diffusion, and
sleep or damage states. It should stay behind the grid genome and validator
until discrete validation metrics are stable.

### CUBFF

CUBFF provides an optional CUDA implementation of a self-modifying program soup
used by the Computational Life experiments. The paper is valuable because it
studies emergence of self-replicators without an explicit fitness landscape.
For this project, CUBFF should produce hidden semantic traits such as mutation
pressure, instability, entropy, and lineage churn. It should not directly
generate companion pixels.

### Continuous Thought Machines

CTM contributes three useful ideas: an internal temporal axis, neuron-level
temporal processing, and synchronization as a representation. Mechagotchi can
adapt those ideas as internal ticks and confidence-gated switchboard cycles
without adopting CTM as a model dependency.

### Pydantic and JSON Schema

Pydantic supports runtime validation with `model_validate()` and JSON Schema
generation with `model_json_schema()`. That makes it appropriate for Python
research prototypes of grid genomes, SLIP profiles, render packets, and
experiment logs. JSON Schema should remain the interchange contract.

### Workshop UX

Piskel supports the browser-first editor direction, Pixelorama reinforces the
importance of metadata and export automation, and LibreSprite is useful for
animation workflow study. The Stage 0 workshop prototype therefore borrows UX
patterns only; it does not embed third-party editor code.

## Stage 1 Decisions

1. Use the PCG Book taxonomy as the method map.
2. Treat WFC, Markov variants, and validators as the first generator bake-off.
3. Treat MAP-Elites as the default archive hypothesis.
4. Keep CUBFF and CTM out of the core until baseline experiments prove value.
5. Use SPDX IDs and a provenance ledger before importing any external asset.
6. Keep the workshop editor Mechagotchi-native until licensing, metadata, and
   semantic-grid round trips are proven.
