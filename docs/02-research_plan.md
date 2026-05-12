# Mechagotchi Research Plan

## Core research thesis

`Mechagotchi` should be researched as a **grid-based artificial-life companion platform**, not merely a virtual pet, pixel editor, or procedural sprite toy.

The central question is:

> Can we build an operational companion engine where a creature’s visual grid, behavior, survival, memory, mutation, and user-authored `SLIP` profile all participate in a coherent evolutionary system?

The research should test this in layers: math, artificial life, grid generation, companion behavior, visual legibility, asset provenance, workshop authoring, and open-source sustainability.

Your two suggested references are useful, but they should be treated differently. **Continuous Thought Machines** are useful as inspiration for internal temporal processing, adaptive compute, and “thinking over ticks,” because CTM explicitly introduces a temporal axis, neuron-level processing, synchronization, and adaptive compute. ([arXiv][1]) **BFF / CUBFF** is better treated as artificial-life substrate research: the paper studies self-replicating programs emerging from simple computational substrates without an explicit fitness landscape, while the CuBFF repo provides the CUDA-capable implementation used for many of those experiments. ([arXiv][2])

---

## 1. Research constitution

## WHY

We are not trying to ship quickly. We are trying to answer whether `Mechagotchi` can become a **real modular artificial-life engine** with a defensible mathematical foundation.

The research must prove:

1. The grid can act as more than art.
2. The companion can evolve without becoming random noise.
3. The `SLIP` profile can guide evolution without killing autonomy.
4. User interaction can influence future generations without exploitative engagement loops.
5. Open-source assets and tools can support the project without degrading originality or legal clarity.

## WHAT

The research output should be a living body of evidence:

```txt
research/
  questions.md
  literature_map.md
  algorithm_cards/
  experiment_reports/
  datasets/
  asset_provenance/
  decision_records/
  failed_approaches/
  glossary.md
```

Every major algorithm should have an **Algorithm Card**:

```txt
Name
Purpose
Mathematical basis
Inputs
Outputs
Strengths
Weaknesses
Failure modes
Integration risk
License status
Prototype result
Decision: reject / watch / prototype / adopt
```

## WHO

Even if one person performs multiple roles at first, the research should be divided by role:

| Role                                | Responsibility                                                                                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Research Lead                       | Maintains the research map, priorities, experiment standards, and decision records.                           |
| Applied Math / Algorithm Researcher | Evaluates Markov chains, WFC, cellular automata, MAP-Elites, bandits, HMMs, RL, and constraint systems.       |
| Artificial Life Researcher          | Studies CUBFF, Avida, Lenia, NCA, open-endedness, self-replication, survival, lineage, and mutation dynamics. |
| Engine Architect                    | Converts research into modular engine interfaces.                                                             |
| Visual Systems Designer             | Defines grid grammar, pixel readability, animation semantics, palette rules, and asset constraints.           |
| Workshop / Tooling Designer         | Designs the pixel editor, `SLIP` creator, validator, previewer, and export flow.                              |
| Licensing / Provenance Maintainer   | Tracks asset/code licenses, attribution, SPDX identifiers, and reuse compatibility.                           |
| Evaluation Lead                     | Defines metrics, benchmarks, playtests, and failure reports.                                                  |

## HOW

Research should follow this loop:

```txt
1. Read / inspect source
2. Extract usable theory
3. Build smallest possible lab prototype
4. Measure output
5. Compare against baseline
6. Record failure modes
7. Decide whether to reject, watch, prototype, or adopt
```

The decision standard should be:

```txt
Inspiration is not adoption.
Aesthetic interest is not scientific value.
Working code is not enough.
Visual output must be human-legible.
Evolution must be measurable.
SLIP compatibility must be testable.
```

## WHERE

Research should happen in four places:

```txt
/docs
  Permanent project theory, architecture, design decisions.

/research
  Literature reviews, algorithm cards, source notes, experiment reports.

/labs
  Disposable prototypes and isolated experiments.

/packages
  Only code that survives research and becomes part of the platform.
```

Suggested lab structure:

```txt
labs/
  markov_grid/
  wfc_grid/
  grid_grammar/
  cellular_automata/
  neural_cellular_automata/
  cubff_transducer/
  map_elites_archive/
  micro_learners/
  slip_validator/
  asset_pipeline/
  workshop_editor/
```

---

## 2. Primary research tracks

## Track A — Grid genome theory

### WHY

The grid must become the mathematical center of the project.

The creature should not be:

```txt
sprite + stats
```

It should be:

```txt
genome → phenotype grid → renderable body → behavioral affordances → survival history → lineage
```

### WHAT to research

Research the grid as:

1. A tensor.
2. A graph.
3. A cellular automaton substrate.
4. A probabilistic field.
5. A symbolic genome.
6. A render packet.
7. A validation object.
8. A mutation surface.

### HOW

Define a formal grid genome:

```txt
G = (C, A, N, O, M, P)
```

Where:

```txt
C = cells
A = cell attributes
N = neighborhood topology
O = organs / semantic regions
M = mutation permissions
P = palette / rendering constraints
```

Each cell should carry at least:

```txt
x
y
visual value
semantic role
material type
mutation weight
animation anchor flag
organ membership
damage / stress state
```

### WHERE

Prototype in:

```txt
labs/grid_genome/
packages/mecha_engine/genome/
```

### Research questions

1. Can a grid represent body, animation, state, mutation, and heredity at once?
2. What grid size is expressive but still manageable: 8×8, 16×16, 24×24, 32×32?
3. Which invariants are required for a valid companion?
4. Can a validator reject malformed creatures without over-constraining novelty?

### Required outputs

```txt
grid_genome.schema.json
grid_invariants.md
grid_validation_report.md
50 hand-made seed grids
100 generated test grids
```

### Core invariants to test

```txt
connectedness
minimum body mass
maximum body mass
eye / sensor presence
animation anchor presence
palette validity
symmetry range
semantic cell validity
mutation bounds
renderability
```

---

## 3. Mathematics layers to explore

Procedural content generation already has mature categories worth mapping into `Mechagotchi`, including search-based methods, constructive generation, noise/fractals, grammars/L-systems, rules/mechanics, planning, answer set programming, mixed-initiative tools, and generator evaluation. ([PCG Book][3])

## Layer 1 — Local probability

### Candidate theories

```txt
Markov chains
n-gram models
Hidden Markov Models
Markov Random Fields
Bayesian transition models
```

### WHY

This is the foundation for predictable grid generation.

### WHAT to test

```txt
cell → neighboring cell probability
row → next row probability
organ → adjacent organ probability
mood → pose probability
ancestor pattern → child pattern probability
```

### HOW

Train small Markov models from seed grids and ancestor grids.

Example:

```txt
P(cell_role[x,y] | neighborhood[x,y])
P(next_frame | mood, energy, age)
P(child_trait | parent_trait, survival_score)
```

### Alternatives

| Method              | Use case                             | Risk                                             |
| ------------------- | ------------------------------------ | ------------------------------------------------ |
| Basic Markov chain  | Simple local transitions             | Can produce local coherence but global nonsense. |
| Higher-order Markov | Better pattern memory                | Larger state space.                              |
| HMM                 | Hidden mood / hidden state inference | More complex, but useful for behavior.           |
| Markov Random Field | Spatial image coherence              | Harder inference.                                |
| Bayesian model      | Uncertainty-aware generation         | Requires careful priors.                         |

### Go / no-go test

A Markov grid generator should beat random mutation on:

```txt
valid grid rate
visual coherence
organ placement
ancestor resemblance
SLIP compliance
```

---

## Layer 2 — Constraint-based generation

### Candidate theories

```txt
Wave Function Collapse
constraint satisfaction
answer set programming
tile adjacency grammars
SAT / SMT solving
```

### WHY

Markov generation alone may not enforce hard rules. Constraint systems can guarantee validity.

Wave Function Collapse is especially relevant because it reads patterns from an input bitmap, represents possibilities as a “wave,” chooses low-entropy cells, collapses them, and propagates constraints; its tilemap version is essentially adjacency constraint propagation. ([GitHub][4])

### WHAT to test

```txt
allowed neighbor roles
allowed organ layouts
allowed animation anchors
allowed palette relationships
symmetry requirements
minimum readable body structure
```

### HOW

Use WFC as a **grid pattern stabilizer**, not the whole creature engine.

Pipeline:

```txt
seed grids
  → extract local patterns
  → generate candidate grid
  → validate semantic organs
  → mutate
  → evaluate
```

### Alternatives

| Method        | Use case                         | Risk                             |
| ------------- | -------------------------------- | -------------------------------- |
| WFC           | Local pattern consistency        | Can overfit to samples.          |
| SAT / SMT     | Hard validity constraints        | May become too rigid.            |
| ASP           | High-level rule-based generation | Powerful but tooling-heavy.      |
| Shape grammar | Body plans and modular limbs     | Requires careful grammar design. |

### Go / no-go test

WFC should be adopted only if it creates better local visual coherence than Markov alone without collapsing variety.

---

## Layer 3 — Cellular automata and morphogenesis

### Candidate theories

```txt
classic cellular automata
continuous cellular automata
Lenia-style artificial life
Neural Cellular Automata
differentiable CA
reaction-diffusion systems
```

### WHY

A companion should feel like it grows, heals, decays, sleeps, glitches, and mutates. Cellular systems are strong candidates for local emergence.

Growing Neural Cellular Automata are directly relevant because they train local update rules for growth, persistence, and regeneration of patterns. ([Distill][5])

### WHAT to test

```txt
grid growth
grid healing
damage recovery
sleep-state animation
mood diffusion
cell stress spread
mutation propagation
```

### HOW

Build a small CA layer where each cell updates from neighbors:

```txt
cell_state[t+1] = update(cell_state[t], neighbors[t], global_mood, SLIP)
```

### Alternatives

| Method                   | Use case                    | Risk                                     |
| ------------------------ | --------------------------- | ---------------------------------------- |
| Classic CA               | Simple local life rules     | Can be hard to control.                  |
| Neural CA                | Learnable morphogenesis     | Requires ML infrastructure.              |
| Lenia-like continuous CA | Rich artificial life        | Less aligned with pixel-grid simplicity. |
| Reaction-diffusion       | Organic texture/mood spread | More aesthetic than behavioral.          |

### Go / no-go test

A CA layer should be adopted only if it improves perceived life, regeneration, animation, or mutation behavior without making the creature unreadable.

---

## Layer 4 — Evolution and quality-diversity

### Candidate theories

```txt
genetic algorithms
novelty search
MAP-Elites
quality-diversity optimization
multi-objective optimization
open-ended evolution
lineage graphs
```

### WHY

`mecha_darwin` should not select one “best” companion. It should preserve many successful companion types.

MAP-Elites is especially aligned with your project because it maps high-performing but diverse solutions across user-defined feature dimensions instead of returning only one optimum. ([arXiv][6]) QDax is also worth researching as an accelerated JAX implementation path for MAP-Elites-style experiments. ([GitHub][7])

### WHAT to test

Use a quality-diversity archive with niches such as:

```txt
visual complexity
symmetry
neediness
social behavior
mutation stability
survival length
novelty
user bond
energy efficiency
SLIP alignment
```

### HOW

Define candidate:

```txt
x = companion genome
```

Define behavior descriptor:

```txt
b(x) = [
  visual_complexity,
  symmetry_score,
  interaction_neediness,
  mutation_rate,
  animation_count
]
```

Define fitness:

```txt
f(x) = weighted survival + readability + bond + novelty + SLIP alignment
```

Archive rule:

```txt
If candidate enters niche and beats existing elite, replace elite.
```

### Alternatives

| Method                       | Use case                      | Risk                           |
| ---------------------------- | ----------------------------- | ------------------------------ |
| Basic genetic algorithm      | Simple parent-child evolution | Optimizes too narrowly.        |
| Novelty search               | Strange creatures             | Can ignore usefulness.         |
| MAP-Elites                   | Diverse successful species    | Requires good descriptors.     |
| Multi-objective optimization | Balances competing goals      | Harder to interpret for users. |

### Go / no-go test

`mecha_darwin` succeeds if it produces a stable archive of distinct companion families rather than converging into one boring optimum.

---

## Layer 5 — Artificial-life substrates

### Candidate systems

```txt
CUBFF / BFF
Avida
Tierra-inspired digital organisms
Core War-style systems
self-modifying program soups
```

### WHY

This is the deep research track for “life-like computation,” but it must not be confused with the visual engine.

Avida is relevant as a mature digital-evolution reference because it is an open-source platform for experiments with self-replicating and evolving computer programs, including measurement and post-processing tools. ([avida.devosoft.org][8])

### CUBFF interpretation

Your previous problem with CUBFF makes sense: raw computational life output is not naturally human-legible.

So the new rule should be:

> CUBFF output should not directly become pixels.
> CUBFF output should become **behavioral and structural signals** that pass through a grid phenotype compiler.

Bad pipeline:

```txt
BFF tape → raw pixels → unreadable image
```

Better pipeline:

```txt
BFF tape
  → replication / entropy / motif / locality features
  → semantic trait vector
  → SLIP-constrained grid genome
  → validator
  → renderable companion
```

### WHAT to extract from CUBFF

```txt
replication rate
instruction motif frequency
survivor token ancestry
tape entropy
copy-distance patterns
mutation scars
program length distribution
dominant lineage turnover
collapse events
```

### HOW to map to visuals

| CUBFF signal               | Mechagotchi visual / behavioral mapping            |
| -------------------------- | -------------------------------------------------- |
| High replication stability | Strong shell, calm behavior, longer life.          |
| High entropy               | Glitch patterns, unstable animation, chaotic mood. |
| Short replicators          | Minimal compact creature body.                     |
| Long replicators           | Complex body, appendages, layered animation.       |
| Dominant lineage collapse  | “Extinction scar” or corrupted descendant trait.   |
| Mutation survival          | Adaptive organs, unusual but valid structure.      |

### Go / no-go test

CUBFF is useful only if the semantic transducer produces creatures that are more interesting than baseline procedural evolution while remaining readable.

---

## Layer 6 — Companion behavior and micro-learning

### Candidate theories

```txt
Markov Decision Processes
contextual bandits
Q-learning
Hidden Markov Models
exponential moving averages
Bayesian counters
small decision trees
rule-weight learning
```

### WHY

The companion lifespan may be too short and too sparse for broad ML. Your “many intelligence threads” idea is correct: use many tiny learners, each with a narrow job.

Contextual bandits are worth researching for personalization because they can adapt action choices from context and feedback; one chatbot study used a contextual bandit to personalize conversation pacing and found it learned an effective policy with lower experimentation cost than a uniform randomized baseline. ([Springer][9])

### WHAT to build

```txt
hunger predictor
sleep predictor
boredom predictor
attention predictor
animation preference learner
interaction timing learner
mood transition model
mutation stability learner
visual readability learner
SLIP compatibility scorer
lineage survival predictor
```

### HOW

Do not create one giant “brain.” Create micro-learners:

```txt
micro learner → confidence signal → switchboard → action
```

Example switchboard input:

```json
{
  "hunger_risk": 0.74,
  "sleep_risk": 0.18,
  "boredom_risk": 0.62,
  "user_attention_likelihood": 0.31,
  "mutation_stability": 0.81,
  "visual_readability": 0.89,
  "slip_alignment": 0.76
}
```

Switchboard decision:

```txt
next_action = argmax utility(action | state, predictions, SLIP)
```

### Alternatives

| Method             | Use case                    | Risk                            |
| ------------------ | --------------------------- | ------------------------------- |
| Fixed rules        | Reliable baseline           | Boring, non-adaptive.           |
| Contextual bandits | Small personalization loops | Needs reward design.            |
| Q-learning         | Action policy learning      | Data sparse.                    |
| HMM                | Hidden mood inference       | Needs careful state definition. |
| Tiny neural model  | Pattern detection           | Harder to interpret.            |

### Go / no-go test

A micro-learning thread must improve one measurable outcome without destabilizing the companion.

---

## Layer 7 — `SLIP` as mathematical profile

### WHY

`SLIP` should not be a cosmetic preset. It should be a **profile of priors, constraints, weights, mutation rules, and behavioral tendencies**.

### WHAT

A `SLIP` should include:

```txt
visual grammar
allowed materials
organ requirements
palette constraints
behavior tendencies
mutation permissions
survival weights
learning switches
animation vocabulary
risk tolerances
lineage preferences
```

### HOW

Treat `SLIP` as:

```txt
SLIP = constraints + priors + weights + validators
```

Example scoring:

```txt
score = w_survival*S + w_readability*R + w_novelty*N + w_bond*B + w_profile*P
```

Where the profile contributes:

```txt
P = SLIP alignment score
```

### WHERE

```txt
packages/mecha_engine/slip/
packages/mecha_workshop/slip_creator/
```

### Required outputs

```txt
slip.schema.json
slip_validator.py
slip_examples/
slip_failure_cases.md
profile_compatibility_tests.md
```

---

## 4. Specific research stages

## Stage 0 — Define the research ontology

### WHO

Research Lead, Engine Architect, Applied Math Researcher.

### WHAT

Create the canonical vocabulary:

```txt
grid
cell
organ
trait
mutation
lineage
fitness
survival
mood
bond
SLIP
archive
species
generation
phenotype
genotype
render packet
```

### HOW

Every term receives:

```txt
definition
data shape
engine location
example
non-example
```

### WHY

Without shared definitions, the project will collapse into vague “AI pet” language.

### WHERE

```txt
research/glossary.md
docs/mechagotchi_ontology.md
```

---

## Stage 1 — Literature and source review

### WHO

Research Lead, Applied Math Researcher, Artificial Life Researcher.

### WHAT

Create a literature map across:

```txt
procedural content generation
Markov models
constraint generation
WFC
cellular automata
neural cellular automata
quality-diversity
MAP-Elites
open-ended evolution
digital organisms
virtual pet attachment
affective agents
interactive evolutionary computation
pixel-art tooling
open-source licensing
```

### HOW

Each paper/source gets:

```txt
summary
usable idea
non-usable idea
implementation difficulty
dependency risk
license status
Mechagotchi relevance
```

### WHERE

```txt
research/literature_map.md
research/source_notes/
research/algorithm_cards/
```

### WHY

The goal is to prevent novelty theater. Every theoretical claim should connect to a prototype or design decision.

---

## Stage 2 — Grid generation bake-off

### WHO

Applied Math Researcher, Visual Systems Designer, Engine Architect.

### WHAT

Compare several generation methods:

```txt
random mutation baseline
Markov grid generator
WFC grid generator
shape grammar generator
CPPN generator
cellular automata growth generator
hybrid generator
```

### HOW

Use the same seed set and compare outputs.

Metrics:

```txt
validity rate
connectedness
organ presence
silhouette readability
symmetry
novelty
ancestor resemblance
SLIP alignment
user-rated appeal
generation speed
```

### WHERE

```txt
labs/markov_grid/
labs/wfc_grid/
labs/grid_grammar/
labs/cellular_automata/
```

### WHY

This decides whether the core body generator should be Markov-first, WFC-first, grammar-first, CA-first, or hybrid.

### Expected outcome

The likely best architecture is hybrid:

```txt
Markov → candidate local patterns
WFC / constraints → structural validity
mutation engine → lineage variation
validator → reject malformed forms
MAP-Elites → preserve diverse winners
```

---

## Stage 3 — `mecha_darwin` archive research

### WHO

Artificial Life Researcher, Applied Math Researcher, Engine Architect.

### WHAT

Build the first evolutionary archive.

### HOW

Implement:

```txt
candidate generator
mutation operators
fitness evaluator
behavior descriptor extractor
archive insertion logic
lineage graph
extinction handling
```

### WHERE

```txt
labs/map_elites_archive/
packages/mecha_engine/darwin/
```

### WHY

This is where `Mechagotchi` becomes more than a pet simulator.

### Metrics

```txt
archive coverage
QD score
best fitness
species count
lineage depth
mutation survival rate
invalid offspring rate
visual diversity
profile diversity
```

---

## Stage 4 — CUBFF transducer experiment

### WHO

Artificial Life Researcher, Applied Math Researcher, Visual Systems Designer.

### WHAT

Research whether BFF/CUBFF dynamics can contribute useful hereditary signals.

### HOW

Build three pipelines:

```txt
Pipeline A: direct tape → pixels
Pipeline B: tape statistics → traits → grid
Pipeline C: lineage dynamics → mutation weights → grid
```

Compare:

```txt
visual legibility
novelty
behavioral interest
survival improvement
ancestor continuity
human preference
```

### WHERE

```txt
labs/cubff_transducer/
```

### WHY

This directly addresses your previous failure: CUBFF worked computationally, but not visually. The new research question is whether a **semantic grid compiler** can solve that.

### Decision rule

```txt
Adopt CUBFF only if semantic transduction beats direct visual mapping and baseline procedural mutation.
```

---

## Stage 5 — Micro-learning switchboard

### WHO

Engine Architect, Applied ML Researcher.

### WHAT

Build the first `mecha_switchboard`.

### HOW

Start with small models:

```txt
EWMA for recent interaction
bandit for animation preference
HMM-like model for hidden mood
rule-weight learner for action utility
logistic scorer for mutation risk
```

### WHERE

```txt
labs/micro_learners/
packages/mecha_engine/learning/
```

### WHY

This tests your “intelligence threads” theory.

### Required proof

Each thread must produce:

```txt
input
output
confidence
explanation
effect on action
effect on survival or experience
```

---

## Stage 6 — `SLIP` profile creator research

### WHO

Workshop Designer, Engine Architect, Visual Systems Designer.

### WHAT

Define the profile-authoring system.

### HOW

Research what users need to author:

```txt
species class
grid constraints
palette
animation states
behavior sliders
mutation permissions
survival priorities
personality tendencies
learning toggles
forbidden traits
```

### WHERE

```txt
labs/slip_validator/
packages/mecha_workshop/slip_creator/
```

### WHY

`SLIP` must be powerful enough for creators but strict enough to prevent invalid companions.

### Required proof

A user-created `SLIP` should be able to:

```txt
generate a valid creature
preview behavior
preview mutation
export profile
load into engine
survive validation
influence evolution
```

---

## Stage 7 — Workshop editor research

### WHO

Workshop Designer, Visual Systems Designer, Licensing Maintainer.

### WHAT

Research whether to build the editor from scratch, embed an existing editor, or borrow UX patterns.

### Candidate sources

Piskel is an Apache-2.0 web sprite editor built with JavaScript, HTML, and CSS. ([GitHub][10]) Pixelorama is MIT-licensed, open source, supports metadata, imports/exports, extensions, and command-line automation. ([GitHub][11]) LibreSprite is GPL-2.0 and useful to study for animation workflows, onion skinning, layers, frames, tiled drawing, and pixel-precise tools, but its GPL status means embedding code requires stronger license planning. ([GitHub][12])

### Recommendation

Use existing tools for research, not immediate embedding.

Best path:

```txt
1. Study Piskel / Pixelorama / LibreSprite UX.
2. Build a small Mechagotchi-native grid editor.
3. Support import/export to standard sprite formats.
4. Keep SLIP metadata proprietary to Mechagotchi schema, not locked to a third-party editor.
```

### WHY

A normal sprite editor cannot express mutation weights, organ roles, survival semantics, or SLIP constraints. The workshop must be a **semantic pixel editor**, not just a drawing tool.

---

## 5. Asset sourcing plan

## Principle

Assets must support originality, not replace it.

The default Mechagotchi visual identity should be generated and authored internally. Third-party assets should be used for:

```txt
research references
style benchmarking
palette exploration
editor testing
placeholder examples
community compatibility tests
```

## Asset source tiers

| Tier   | Source type                            | Use                                     |
| ------ | -------------------------------------- | --------------------------------------- |
| Tier 0 | Original Mechagotchi-generated assets  | Preferred core assets.                  |
| Tier 1 | Original hand-authored internal assets | Seed grids, examples, defaults.         |
| Tier 2 | CC0 / public domain assets             | Safe placeholder and test material.     |
| Tier 3 | Attribution-compatible open assets     | Usable with provenance tracking.        |
| Tier 4 | Copyleft assets                        | Use carefully; may affect distribution. |
| Tier 5 | Proprietary / commercial inspiration   | Moodboard only; never ship directly.    |

OpenGameArt accepts free/open asset licenses such as CC0, OGA-BY, CC-BY, CC-BY-SA, WTFPL, and public domain, but it also warns that derivative sharing requires explicit permission from contributors. ([OpenGameArt.org][13]) The Liberated Pixel Cup materials are stylistically useful but are dual-licensed under CC BY-SA 3.0 and GPLv3-or-later, so they should be handled as copyleft assets rather than casual defaults. ([Liberated Pixel Cup][14]) Lospec is useful for palette research because it provides a large downloadable pixel-art palette database, including hardware-inspired palettes and artist-created palettes. ([Lospec][15])

## Asset provenance ledger

Every external asset must have:

```yaml
asset_id:
title:
creator:
source:
source_url:
download_date:
license:
spdx_id:
cc_tool:
derivative_of:
modifications:
hash:
included_in_repo: true/false
attribution_text:
commercial_allowed:
redistribution_allowed:
share_alike_required:
notes:
```

Use SPDX identifiers for software/code licenses because SPDX provides standardized license identifiers, canonical URLs, and machine-readable license data. ([spdx.org][16]) Use REUSE-style file-level licensing practices because REUSE is designed to make licensing human-readable and machine-readable across project files. ([reuse.software][17]) Creative Commons’ own chooser confirms key distinctions such as CC0, CC BY, and CC BY-SA, and explicitly notes that CC licenses are generally for copyrightable works rather than software/hardware. ([Creative Commons][18])

## Asset research questions

```txt
Can generated assets replace most external assets?
Can users create complete SLIP profiles from original grids?
Which palettes feel 90s/retro without copying protected hardware identities?
Can all third-party assets be excluded from core builds by default?
Can the project ship with a clean attribution manifest?
```

---

## 6. Experimental open-source projects to research

## High-priority research candidates

| Project / source                 | Research use                                                             | Adoption stance                                              |
| -------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------ |
| Continuous Thought Machines      | Internal time axis, adaptive compute, temporal state reasoning.          | Inspiration first; prototype only after core engine works.   |
| CuBFF / BFF paper                | Computational-life substrate, self-replication, lineage signals.         | Lab-only until semantic transducer proves value.             |
| Avida                            | Digital evolution methodology, organism competition, measurement design. | Study deeply; do not necessarily embed.                      |
| MAP-Elites / QDax                | `mecha_darwin` archive, quality-diversity search, species niches.        | Strong candidate for research implementation.                |
| Wave Function Collapse           | Local grid pattern generation and constraint propagation.                | Strong candidate as visual coherence module.                 |
| Growing Neural Cellular Automata | Growth, repair, persistence, local update rules.                         | Medium-term candidate.                                       |
| Piskel                           | Web sprite editor UX and browser rendering model.                        | Study UX; possible code reference depending on architecture. |
| Pixelorama                       | Editor metadata, import/export, open-source workflow.                    | Study heavily; possible interoperability target.             |
| LibreSprite                      | Animation UX, layers, onion skinning.                                    | Study UX; avoid embedding unless GPL-compatible.             |

---

## 7. Specific CUBFF research plan

## Problem

Previous attempt:

```txt
CUBFF worked computationally
but visual output did not make human sense
```

## Hypothesis

CUBFF should not create the body directly. It should create **life-process signals**.

## Experiment design

### A. Raw visual baseline

```txt
BFF tape → byte values → grid pixels
```

Expected result:

```txt
High novelty, low readability.
```

### B. Statistical transducer

```txt
BFF tape
  → entropy
  → motif counts
  → replication rate
  → lineage dominance
  → trait vector
  → grid genome
```

Expected result:

```txt
Better readability, meaningful ancestry.
```

### C. Behavioral transducer

```txt
BFF dynamics
  → companion temperament
  → mutation pressure
  → survival bias
  → animation instability
```

Expected result:

```txt
CUBFF contributes behavior, not just visuals.
```

### D. Hybrid transducer

```txt
BFF traits + Markov grid + SLIP constraints + validator
```

Expected result:

```txt
Most likely usable path.
```

## Metrics

```txt
human readability score
grid validity score
ancestor resemblance
visual novelty
behavioral novelty
mutation stability
survival impact
SLIP alignment
```

## Decision

```txt
Adopt CUBFF only as a hidden artificial-life influence unless it reliably improves visual generation.
```

---

## 8. Specific CTM research plan

## Problem

A full CTM-like model may be excessive for a virtual companion engine.

## Useful concept

CTM’s useful idea is not “use a giant neural model.” The useful idea is:

```txt
thinking unfolds over internal time
```

## Mechagotchi adaptation

Use CTM-inspired principles in a lighter form:

```txt
internal ticks
adaptive compute
state synchronization
confidence-gated decisions
longer thought for uncertain actions
short thought for simple actions
```

Example:

```txt
if confidence(action) > 0.85:
    act immediately
else:
    run extra switchboard cycles
```

## Research questions

```txt
Does internal deliberation make behavior feel more alive?
Does adaptive compute improve decisions?
Can the companion visibly “think” without delaying interaction?
Can temporal synchronization help animation/mood coherence?
```

## Decision

```txt
CTM is a conceptual research influence first.
A CTM-like model should not become a core dependency until smaller micro-learning systems fail.
```

---

## 9. Evaluation framework

## Visual evaluation

Metrics:

```txt
connected components
body mass ratio
silhouette entropy
symmetry score
organ detectability
palette contrast
animation anchor coverage
human readability rating
```

## Evolution evaluation

Metrics:

```txt
survival age
offspring validity rate
archive coverage
QD score
lineage depth
trait persistence
mutation rejection rate
extinction frequency
species diversity
```

## Companion behavior evaluation

Metrics:

```txt
need balance
mood stability
interaction responsiveness
non-annoyance score
user bond rating
state predictability
surprise / novelty
recovery from neglect
```

## Workshop evaluation

Metrics:

```txt
profile creation success
validator clarity
import/export fidelity
preview accuracy
authoring time
schema error rate
custom profile survival rate
```

## Open-source evaluation

Metrics:

```txt
license clarity
attribution completeness
third-party dependency count
build reproducibility
documentation quality
contribution ease
```

---

## 10. Research data to collect

## Engine data

```txt
companion_id
generation_id
parent_id
grid_genome
SLIP profile
mutation events
fitness vector
behavior descriptor
survival age
death / reset cause
user interactions
archive niche
```

## Visual data

```txt
grid snapshots
animation frames
palette
semantic cell map
render packet
validator results
human ratings
```

## Learning data

```txt
micro-learner inputs
micro-learner outputs
confidence
selected action
reward signal
prediction error
switchboard decision
```

## Asset data

```txt
source
license
creator
hash
modifications
attribution
usage location
redistribution status
```

---

## 11. Proposed first research sequence

Do this in order:

```txt
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
```

This sequence is intentionally research-first. It proves the platform before polishing the product.

---

## 12. Recommended core architecture after research

The most plausible architecture is:

```txt
SLIP profile
   ↓
grid generator
   ↓
constraint validator
   ↓
companion genome
   ↓
life simulation
   ↓
micro-learning switchboard
   ↓
mecha_darwin archive
   ↓
lineage mutation
   ↓
render packet
   ↓
workshop / visual engine
```

CUBFF, CTM, NCA, WFC, Markov models, and MAP-Elites should not compete to be “the one engine.”

They should occupy different roles:

```txt
Markov          local probability
WFC             local visual constraint
CA / NCA        growth, repair, persistence
MAP-Elites      evolutionary archive
CUBFF           artificial-life signal substrate
CTM concepts    internal temporal reasoning
SLIP            user-authored constraints and priors
Switchboard     decision integration
```

---

## 13. Final research stance

The key innovation is not any one algorithm.

The strongest research direction is:

> A semantic grid-genome companion engine where multiple small mathematical systems cooperate: Markov prediction for local structure, constraints for validity, quality-diversity for evolution, micro-learners for behavior, `SLIP` for authorial intent, and artificial-life substrates like CUBFF as optional hidden sources of lineage pressure.

That is the path most likely to produce something novel, real, useful, and operational.

[1]: https://arxiv.org/abs/2505.05522 "[2505.05522] Continuous Thought Machines"
[2]: https://arxiv.org/abs/2406.19108 "[2406.19108] Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction"
[3]: https://www.pcgbook.com/ "Procedural Content Generation in Games book"
[4]: https://github.com/mxgmn/WaveFunctionCollapse "GitHub - mxgmn/WaveFunctionCollapse: Bitmap & tilemap generation from a single example with the help of ideas from quantum mechanics · GitHub"
[5]: https://distill.pub/2020/growing-ca "Growing Neural Cellular Automata"
[6]: https://arxiv.org/abs/1504.04909 "[1504.04909] Illuminating search spaces by mapping elites"
[7]: https://github.com/adaptive-intelligent-robotics/qdax "GitHub - adaptive-intelligent-robotics/QDax: Accelerated Quality-Diversity · GitHub"
[8]: https://avida.devosoft.org/ "Avida by devosoft"
[9]: https://link.springer.com/article/10.1007/s10994-021-05983-y "Bandit algorithms to personalize educational chatbots | Machine Learning | Springer Nature Link"
[10]: https://github.com/piskelapp/piskel "GitHub - piskelapp/piskel: A simple web-based tool for Spriting and Pixel art. · GitHub"
[11]: https://github.com/orama-interactive/pixelorama "GitHub - Orama-Interactive/Pixelorama: Unleash your creativity with Pixelorama, a powerful and accessible open-source pixel art multitool. Whether you want to create sprites, tiles, animations, or just express yourself in the language of pixel art, this software will realize your pixel-perfect dreams with a vast toolbox of features. Available on Windows, Linux, macOS and the Web! · GitHub"
[12]: https://github.com/LibreSprite/LibreSprite "GitHub - LibreSprite/LibreSprite: Animated sprite editor & pixel art tool -- Fork of the last GPLv2 commit of Aseprite · GitHub"
[13]: https://opengameart.org/ "OpenGameArt.org |"
[14]: https://lpc.opengameart.org/static/LPC-Style-Guide/build/index.html "Liberated Pixel Cup style guide, assets, and demo — Liberated Pixel Cup styleguide documentation"
[15]: https://lospec.com/palette-list "Palette List"
[16]: https://spdx.org/licenses/ "SPDX License List | Software Package Data Exchange (SPDX)"
[17]: https://reuse.software/ "REUSE - Make licensing easy for everyone"
[18]: https://creativecommons.org/chooser/ "Chooser - Creative Commons"
