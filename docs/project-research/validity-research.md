# 1. Brainstorming

<!-- vscode-markdown-toc -->
* 1. [1.1. DEVELOPMENT: BRAINSTORMING + RESEARCH, PLANNING](#DEVELOPMENT:BRAINSTORMINGRESEARCHPLANNING)
* 2. [1.2. CURRENT STEP: "BRAINSTORMING + RESEARCH"](#CURRENTSTEP:BRAINSTORMINGRESEARCH)
* 3. [1.3. [1] `mecha_engine` Back end Companion Logic](#mecha_engineBackendCompanionLogic)
* 4. [1.4. [2] `mecha_workshop`: Pixel Art Grid Editor, `SLIP` Profile Creator](#mecha_workshop:PixelArtGridEditorSLIPProfileCreator)
* 5. [1.5. The Two-Build Model](#TheTwo-BuildModel)
* 6. [1.6. `mecha_engine`](#mecha_engine)
* 7. [1.7. `mecha_workshop`](#mecha_workshop)
* 8. [1.8. Critical Design Reframe](#CriticalDesignReframe)
* 9. [1.9. The Core Loop](#TheCoreLoop)
* 10. [1.10. The Grid as Genome](#TheGridasGenome)
* 11. [1.11. Markov Grid Generation](#MarkovGridGeneration)
* 12. [1.12. `mecha_darwin`: Evolution Layer](#mecha_darwin:EvolutionLayer)
* 13. [1.13. Recommended Evolution Model](#RecommendedEvolutionModel)
* 14. [1.14. `SLIP`: Synthetic Learning Intelligence Profile](#SLIP:SyntheticLearningIntelligenceProfile)
* 15. [1.15. Micro Machine Learning Threads](#MicroMachineLearningThreads)
* 16. [1.16. The Switchboard](#TheSwitchboard)
* 17. [1.17. Companion State Model](#CompanionStateModel)
* 18. [1.18. Suggested Engine Architecture](#SuggestedEngineArchitecture)
* 19. [1.19. Visual Engine Contract](#VisualEngineContract)
* 20. [1.20. Recommended Tech Stack](#RecommendedTechStack)
* 21. [1.21. MVP Definition](#MVPDefinition)
* 22. [1.22. MVP 0.1](#MVP0.1)
* 23. [1.23. MVP 0.2](#MVP0.2)
* 24. [1.24. MVP 0.3](#MVP0.3)
* 25. [1.25. Core Algorithms to Build First](#CoreAlgorithmstoBuildFirst)
* 26. [1.26. Grid Markov Generator](#GridMarkovGenerator)
* 27. [1.27. Mutation Engine](#MutationEngine)
* 28. [1.28. Fitness Evaluator](#FitnessEvaluator)
* 29. [1.29. Lineage Archive](#LineageArchive)
* 30. [1.30. Switchboard](#Switchboard)
* 31. [1.31. Visual Style Direction](#VisualStyleDirection)
* 32. [1.32. Research Notes](#ResearchNotes)
* 33. [1.33. Naming the Internal Systems](#NamingtheInternalSystems)
* 34. [1.34. Recommended First Implementation Target](#RecommendedFirstImplementationTarget)
* 35. [1.35. Working Thesis](#WorkingThesis)

<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->
<!--
##  1. <a name='DEVELOPMENT:BRAINSTORMINGRESEARCHPLANNING'></a>1.1. DEVELOPMENT: BRAINSTORMING + RESEARCH, PLANNING
##  2. <a name='CURRENTSTEP:BRAINSTORMINGRESEARCH'></a>1.2. CURRENT STEP: "BRAINSTORMING + RESEARCH"
`Mechagotchi`: The open source digital-visual companion engine.
- *Inspired by retro-computing and life in the 90's.*
I want to create a tamagotchi style personal companion. I want to use a grid to create the graphic assets of the companions. Grids are consistent, simple, scalable and mathematic. Combined with the back end logic of a tamagotchi style companion, we can create a consistent, scalable and highly modular engine.
The project will operate on two comprehensive builds.[1],[2].

##  3. <a name='mecha_engineBackendCompanionLogic'></a>1.3. [1] `mecha_engine` Back end Companion Logic
**DISCLAIMER**: THE SYSTEM IN ITSELF, NEEDS TO RUN OFF OF A PREDICTIVE ALGORITHM LIKE MARKOV CHAINS FOR ITS GRID. AT ITS CORE, IT WILL GENERATE ITS MECHAGOTCHI AND OVER TIME, GENERATE MORE COMPLEX ONES BASED ON THE SURVIVAL OF ITS ANCESTORS. **THIS IS THE MAIN AND CORE FUNCTION OF THE PROJECT AND MECHA ENGINE. THE FEATURES BELOW ARE WHAT MAKES IT A COMPLETE EXPERIENCE BUT NOT THE CORE EXPERIENCE.
This logic must link to the visual engine and vice versa.
- mecha: `engine` <-> `SLIP` <-> `workshop`
  - THE SLIP PROFILES ARE USED FOR THE CORE `mecha_darwin` ALGORITHM THAT SHOULD CONTROL WHAT IS WEIGHTED AS IMPORTANT, OR 'OPTIMAL' FOR ITS NEXT EVOLUTION PASS.
  - THE `Pixel Art Grid Editor` EDITOR IN [2] ARE DESIGNED TO LINK WITH THE `SLIP` PROFILES IS TO CREATE CUSTOM ASSETS FOR THE ENGINE, NOT THE CORE ENGINE ITSELF
- the logic should incoperate real machine learning in an accelerated manner. We should be creative, and approach the machine learning as intelligence threads; we cannot utilize one broad machine learning logic because this format is too short in lifespan, the loop wont benefit from traditional ML.
  - Instead, we creat many micro machine learning threads that all link into something more concrete like a main logic switchboard. We can provide guidance to the ML where required, and have hundreds of smaller, isolated ML enviornments that, upon linking into the switchboard, would act in itself as 'automation'. Its providing a datastream back to the main engine, that hence can then translate that data and provide visual output to the user facing experience through[2].

##  4. <a name='mecha_workshop:PixelArtGridEditorSLIPProfileCreator'></a>1.4. [2] `mecha_workshop`: Pixel Art Grid Editor, `SLIP` Profile Creator
 Id like to include a simple pixel art based proprietary editor the users can add their own `SLIP`(Synthetic Learning Intelligence Profile) for.
- Pixel Art Grid Editor
- Pre set Profiles, the profile logic should robustly and thorougly designed modular. These `modular` style development and design system should be deeply rooted into the engines source code operation for futureproofing and easy modifications, additions, enhanvements.
- We should provide so be created in full so the users can create complete and workable profiles that link into the engine.
-->

`Mechagotchi` should not be “a Tamagotchi clone with generated sprites.”

It should be:

> **A living grid-based companion engine where visual form, behavior, memory, survival, mutation, and user-made profiles all influence future generations.**

The strongest idea in your concept is that the **grid is not just art**. The grid is the creature’s body, genome, memory surface, animation system, and evolutionary substrate.

That gives the project a unique identity.

---

##  5. <a name='TheTwo-BuildModel'></a>1.5. The Two-Build Model

---

##  6. <a name='mecha_engine'></a>1.6. `mecha_engine`

This is the **life simulation, evolution, prediction, and companion logic layer**.

Its responsibilities:

* Generate a companion from a grid genome.
* Simulate needs, moods, energy, risk, adaptation, decay, growth, memory, and survival.
* Run the `mecha_darwin` evolutionary algorithm.
* Interpret `SLIP` profiles as behavioral/visual/intelligence constraints.
* Feed output states to the visual layer.
* Receive user interaction and workshop-created profile data.
* Maintain lineage, ancestry, mutations, fitness history, and “species memory.”

The key research alignment here is **procedural content generation**, where game content is created algorithmically instead of fully by hand. Modern PCG research groups methods into search-based, learning-based, rule-based, noise-based, grammar-based, and hybrid approaches; your project should intentionally combine several instead of relying on one broad model. ([arXiv][1])

##  7. <a name='mecha_workshop'></a>1.7. `mecha_workshop`

This is the **creative authoring layer**.

Its responsibilities:

* Pixel art grid editor.
* `SLIP` profile creator.
* Trait editor.
* Behavior profile editor.
* Animation/state previewer.
* Genome inspector.
* Lineage browser.
* Export/import tool.
* Community asset/profile system.

This should not replace the core engine. It should be the way users **guide, constrain, remix, and author** compatible companion profiles.

---

##  8. <a name='CriticalDesignReframe'></a>1.8. Critical Design Reframe

Your disclaimer is correct and important:

> The core of the project is not user-made art.
> The core is predictive grid-based generation plus evolutionary survival.

So the system should be designed like this:

```txt
mecha_engine
  ├─ genome
  ├─ grid generator
  ├─ Markov predictor
  ├─ micro-learning threads
  ├─ survival simulation
  ├─ mecha_darwin
  ├─ SLIP interpreter
  └─ renderer bridge

mecha_workshop
  ├─ grid editor
  ├─ SLIP editor
  ├─ preview simulator
  ├─ profile validator
  └─ export/import tools
```

The workshop creates compatible profiles, but the engine remains autonomous.

---

##  9. <a name='TheCoreLoop'></a>1.9. The Core Loop

The engine should run on a repeating life cycle:

```txt
1. Generate initial genome
2. Render body from grid genome
3. Simulate companion needs and environment
4. Observe user interactions
5. Update behavior weights
6. Evaluate survival / comfort / novelty / coherence
7. Store lineage memory
8. Mutate or evolve next variant
9. Render evolved form
10. Repeat
```

This allows the companion to become more complex over time without needing a massive ML model.

---

##  10. <a name='TheGridasGenome'></a>1.10. The Grid as Genome

Every Mechagotchi should be represented by a structured grid.

Example:

```json
{
  "grid_size": [16, 16],
  "cells": [
    {
      "x": 0,
      "y": 0,
      "material": "empty",
      "role": "background",
      "energy": 0,
      "mutation_lock": false
    }
  ],
  "symmetry": "bilateral",
  "palette": "lcd_green",
  "organs": {
    "eye_left": [[5, 5], [5, 6]],
    "eye_right": [[10, 5], [10, 6]],
    "mouth": [[7, 10], [8, 10]]
  }
}
```

The grid should contain more than pixels. Each cell can have semantic meaning:

```txt
visual value
material value
organ role
animation role
mutation probability
survival relevance
behavioral association
```

This is what makes the grid mathematical, scalable, and evolvable.

---

##  11. <a name='MarkovGridGeneration'></a>1.11. Markov Grid Generation

A Markov chain is a good first-generation predictive system because it can learn local patterns and produce new sequences based on prior probabilities.

For Mechagotchi, Markov logic can operate at multiple levels:

```txt
cell-to-cell transition
row-to-row transition
organ placement transition
palette transition
animation frame transition
mood-to-pose transition
ancestor-to-child mutation transition
```

Research on Markov-chain-based PCG shows that Markov models have been used to generate game maps by learning local content transitions, and that PCG techniques often fall into search-based, learning-based, and tiling-style approaches. ([cdn.aaai.org][2])

For your engine, the Markov model should not generate “random sprites.” It should generate **probable body structures**.

Example:

```txt
If a cell is eye-left,
neighboring cells are more likely to be:
- eye-fill
- face-shell
- empty highlight
- expression anchor
```

This creates coherent grid creatures.

---

##  12. <a name='mecha_darwin:EvolutionLayer'></a>1.12. `mecha_darwin`: Evolution Layer

`mecha_darwin` should be the evolutionary judge.

It should ask:

```txt
Did this companion survive?
Did the user interact with it?
Did its form remain readable?
Did its behavior become stable?
Did its needs system stay balanced?
Did it become visually distinct?
Did it preserve useful traits from ancestors?
Did it avoid malformed grids?
```

A useful model here is **quality-diversity search**, especially MAP-Elites-style thinking. MAP-Elites divides a behavior space into niches/cells and stores the best individual in each niche, which fits your grid-based philosophy extremely well. ([members.loria.fr][3])

That means instead of evolving toward one “best” Mechagotchi, the engine can preserve many successful types:

```txt
best sleepy companion
best chaotic companion
best social companion
best low-maintenance companion
best visually symmetrical companion
best strange-but-survivable companion
best tiny-grid companion
best high-animation companion
```

This is better than a single fitness score.

Your evolution system should optimize for:

```txt
survival
readability
novelty
user attachment
behavioral coherence
visual coherence
profile compatibility
ancestral continuity
```

---

##  13. <a name='RecommendedEvolutionModel'></a>1.13. Recommended Evolution Model

Use a hybrid system:

```txt
Markov chain
  → generates probable grid structures

Mutation system
  → alters cells, organs, palettes, animation anchors

Fitness evaluator
  → scores survival, coherence, interaction, novelty

Quality-diversity archive
  → preserves multiple successful species types

SLIP weighting
  → nudges evolution toward profile-specific goals
```

In simple form:

```txt
child = mutate(markov_generate(parent_lineage))
score = evaluate(child, environment, user_history, SLIP)
archive.insert(child, niche, score)
```

---

##  14. <a name='SLIP:SyntheticLearningIntelligenceProfile'></a>1.14. `SLIP`: Synthetic Learning Intelligence Profile

`SLIP` should be the bridge between authored intent and autonomous evolution.

A `SLIP` profile should not be just “pet settings.”

It should define:

```txt
visual constraints
behavioral tendencies
learning preferences
mutation permissions
survival priorities
interaction rewards
emotional ranges
grid grammar rules
animation vocabulary
```

Example:

```json
{
  "slip_version": "0.1.0",
  "name": "Rusty Desktop Goblin",
  "species_class": "mecha_goblin",
  "grid": {
    "min_size": [12, 12],
    "max_size": [32, 32],
    "symmetry_bias": 0.65,
    "allowed_materials": ["shell", "eye", "joint", "antenna", "void"]
  },
  "behavior": {
    "curiosity": 0.8,
    "neediness": 0.4,
    "sleepiness": 0.6,
    "mischief": 0.7
  },
  "survival_weights": {
    "fed": 0.25,
    "rested": 0.2,
    "social": 0.2,
    "clean": 0.1,
    "novelty": 0.15,
    "stability": 0.1
  },
  "mutation": {
    "palette_shift": 0.1,
    "organ_shift": 0.05,
    "limb_growth": 0.08,
    "symmetry_break": 0.02
  }
}
```

The `SLIP` profile should be validated before use.

Invalid example:

```txt
No eyes
No body mass
Mutation rate too high
Behavior weights exceed limits
Animation anchors missing
Grid impossible to render
```

---

##  15. <a name='MicroMachineLearningThreads'></a>1.15. Micro Machine Learning Threads

Your idea of many small “intelligence threads” is very strong.

Do not build one general-purpose ML brain.

Build many tiny learners.

Each one should have a narrow job:

```txt
hunger predictor
sleep predictor
boredom predictor
interaction timing predictor
mood transition predictor
animation preference learner
grid mutation evaluator
user attachment estimator
visual coherence scorer
lineage stability scorer
SLIP compatibility scorer
```

Each thread can be simple:

```txt
Markov chain
exponential moving average
multi-armed bandit
tiny decision tree
Bayesian counter
Q-table
rule-weight learner
```

The point is not “big AI.” The point is **many small adaptive systems feeding a switchboard**.

---

##  16. <a name='TheSwitchboard'></a>1.16. The Switchboard

Create a central decision system:

```txt
mecha_switchboard
```

It receives signals from all micro-learners.

Example:

```json
{
  "hunger_predictor": 0.72,
  "sleep_predictor": 0.21,
  "boredom_predictor": 0.64,
  "user_attention_likelihood": 0.33,
  "mutation_stability": 0.81,
  "visual_readability": 0.9,
  "slip_alignment": 0.76
}
```

The switchboard chooses the next action:

```txt
idle
ask for food
sleep
animate
mutate slightly
reject mutation
evolve next generation
change expression
trigger event
```

This gives you “intelligence” without requiring an expensive neural network.

---

##  17. <a name='CompanionStateModel'></a>1.17. Companion State Model

Each Mechagotchi needs visible and hidden states.

Visible:

```txt
hunger
happiness
energy
cleanliness
mood
age
health
bond
```

Hidden:

```txt
mutation pressure
lineage fitness
stress
novelty decay
attachment score
user response confidence
profile alignment
grid stability
```

This creates a richer simulation while keeping the UI simple.

> **Dated correction, 2026-08-08 (cycle 26 P1).** The split above is the
> founding intent and stands as written; the SHIPPED state has moved,
> and is measured — not asserted — by
> `data/game_client/companion_axis_split_stage0.json` (a live client
> session; every §1.17 axis mapped to its engine source and its
> on-screen surface). What the measurement says:
>
> 1. **Six of the eight visible axes are on screen** (hunger, energy,
>    bond, age, mood, health). The two that are not — **happiness** and
>    **cleanliness** — are absent *upstream* of display: one has no
>    documented DEFINITION, the other no engine MECHANIC (DR 0048).
>    Neither is a display gap.
> 2. **`health` is shown under a CHOSEN definition, not a documented
>    one**: `danger_margin` (DR 0054, which refused `grid_stability`
>    under the name "health" as a euphemism), displayed with its
>    binding axis (DR 0055) and labelled *chosen* on the surface.
> 3. **Two hidden axes are deliberately surfaced under accurate
>    names**: `stress` as "stress" and `grid stability` as
>    "body stability" — engine truth shown honestly, not a euphemism
>    (DR 0021's first law).
>
> The six other hidden axes are not surfaced; their engine sources
> remain unsurveyed (M5's remainder 4,
> `research/experiment_reports/2026-07-27-companion-state-survey.md`).
> Earlier corrections to survey claims about this section: M5 / DR 0048
> (three real gaps, not five) and N5 / DR 0054 (the split measurably
> stale). This note supersedes neither — it is the measured state of
> the shipped client as of its date.
>
> **Dated addendum, 2026-08-08 (cycle 26 P2, DR 0058).** `happiness`
> is now VISIBLE under a CHOSEN definition: **`social_warmth`**, the
> mean of the engine's own `recent_interactions` window (feed/play,
> last 5 ticks), adopted through a five-gate study that refused
> `bond`-under-another-name as a duplicate and withheld the engine's
> `need_balance` under the measured responsiveness floor
> (`data/architecture/happiness_definition_gate_stage0.json`). The
> shipped split is now **seven of eight visible axes on screen**;
> `cleanliness` is the one remaining absence, and it needs a MECHANIC
> (DR 0048). The measuring artifact above was regenerated under the
> new surface the same day.
>
> **Dated addendum, 2026-08-09 (cycle 26 P3, DR 0059).** `cleanliness`
> now has its MECHANIC: an **opt-in** lifecycle seam (byte-identical
> when off; every parameter derived from the incumbent engine — a
> decay, a keeper `clean` verb, a bounded dirt→stress coupling that an
> attentive keeper's care absorbs entirely), adopted through a
> five-gate study
> (`data/lifecycle/cleanliness_mechanic_gate_stage0.json`) and landed
> in the client for opted-in covenants. The **default** covenant does
> not enable it — that is a product decision with its own future
> record — so the default shipped split stays seven of eight on
> screen, with the eighth an honest opt-in absence rather than a
> missing mechanic. No documented visible axis lacks an engine source
> any longer.

---

##  18. <a name='SuggestedEngineArchitecture'></a>1.18. Suggested Engine Architecture

```txt
mechagotchi/
  packages/
    mecha_engine/
      core/
        companion.py
        lifecycle.py
        state.py
        clock.py
      genome/
        grid_genome.py
        mutation.py
        lineage.py
        archive.py
      learning/
        markov_grid.py
        micro_threads.py
        switchboard.py
        evaluators.py
      slip/
        schema.py
        validator.py
        interpreter.py
      render_bridge/
        frame_packet.py
        animation_state.py
      storage/
        save_file.py
        event_log.py

    mecha_workshop/
      editor/
      slip_creator/
      previewer/
      exporters/

    mecha_shared/
      schemas/
      constants/
      test_fixtures/
```

---

##  19. <a name='VisualEngineContract'></a>1.19. Visual Engine Contract

The back end should not directly care whether the front end is web, Godot, terminal, Pygame, or desktop.

It should output render packets:

```json
{
  "companion_id": "mx-001",
  "frame": 1042,
  "grid_size": [16, 16],
  "cells": [
    {"x": 4, "y": 5, "color": "#2f3b24", "role": "eye"}
  ],
  "animation": "idle_blink",
  "mood": "curious",
  "effects": ["scanline", "lcd_ghosting"]
}
```

That makes the project modular and futureproof.

---

##  20. <a name='RecommendedTechStack'></a>1.20. Recommended Tech Stack

For an open-source modular prototype:

```txt
Core engine: Python
Workshop frontend: TypeScript + React
Rendering: Canvas/WebGL initially
Schema: JSON Schema / Pydantic
Storage: SQLite or local JSON saves
Testing: Pytest
Package structure: monorepo
```

Why Python first?

* Easy for procedural generation.
* Good for ML experiments.
* Easy testability.
* Friendly open-source contribution path.
* Later you can port the runtime core to Rust, TypeScript, or Godot if needed.

For visual/editor work, TypeScript + Canvas is likely the fastest path.

---

##  21. <a name='MVPDefinition'></a>1.21. MVP Definition

Do not start with the full dream.

Start with this:

##  22. <a name='MVP0.1'></a>1.22. MVP 0.1

```txt
Generate one companion from a grid genome.
Display it in a pixel grid.
Simulate hunger, energy, mood, age.
Allow feed/play/sleep interactions.
Log survival data.
Mutate next generation.
Save lineage.
Load one SLIP profile.
```

That is enough to prove the engine.

##  23. <a name='MVP0.2'></a>1.23. MVP 0.2

```txt
Add Markov grid generation.
Add micro-learning threads.
Add profile-weighted mutation.
Add visual editor.
Add preview simulation.
```

##  24. <a name='MVP0.3'></a>1.24. MVP 0.3

```txt
Add mecha_darwin archive.
Add species niches.
Add import/export SLIP files.
Add lineage browser.
Add community profile packs.
```

---

##  25. <a name='CoreAlgorithmstoBuildFirst'></a>1.25. Core Algorithms to Build First

##  26. <a name='GridMarkovGenerator'></a>1.26. Grid Markov Generator

Learns from parent grids and preset examples.

```txt
input: ancestor grids + SLIP constraints
output: probable child grid
```

##  27. <a name='MutationEngine'></a>1.27. Mutation Engine

Applies controlled changes.

```txt
cell mutation
palette mutation
organ shift
symmetry break
limb growth
animation anchor shift
```

##  28. <a name='FitnessEvaluator'></a>1.28. Fitness Evaluator

Scores the result.

```txt
survival score
visual score
behavior score
novelty score
SLIP score
user bond score
```

##  29. <a name='LineageArchive'></a>1.29. Lineage Archive

Stores ancestry.

```txt
parent_id
child_id
mutation_events
fitness_scores
death_cause
survival_age
user_interactions
```

##  30. <a name='Switchboard'></a>1.30. Switchboard

Turns all signals into action.

```txt
current_state + predictions + profile + environment → next action
```

---

##  31. <a name='VisualStyleDirection'></a>1.31. Visual Style Direction

The identity should be very specific:

```txt
90s LCD device
retro computing
grid creatures
scanlines
limited palettes
boot screens
terminal diagnostics
fake BIOS logs
low-resolution UI
toy-like companion behavior
machine-animal hybrids
```

Possible modes:

```txt
LCD green
Game Boy gray
Amber terminal
CRT blue
Pocket organizer monochrome
Early Windows 95 toy UI
```

---

##  32. <a name='ResearchNotes'></a>1.32. Research Notes

The current open-source landscape has many small Tamagotchi-style projects, including Python, Godot, JavaScript, ESP32, and GitHub-activity pets, but most appear to focus on standard virtual-pet mechanics rather than a reusable evolutionary grid-companion engine. GitHub topic listings show many small Tamagotchi-inspired projects, while projects like TamaFi explore modern virtual-pet behavior on ESP32 hardware. ([GitHub][4])

This gives `Mechagotchi` a good niche:

> **Not just a virtual pet. Not just a pixel editor. A procedural companion life engine.**

The strongest differentiator is the combination of:

```txt
grid genome
Markov prediction
micro-learning threads
quality-diversity evolution
SLIP profile authoring
retro visual companion layer
```

---

##  33. <a name='NamingtheInternalSystems'></a>1.33. Naming the Internal Systems

You already have strong names. I would formalize them like this:

```txt
mecha_engine        Core simulation/evolution engine
mecha_workshop      Editor and authoring environment
SLIP                Synthetic Learning Intelligence Profile
mecha_darwin        Evolution and selection system
mecha_switchboard   Signal-routing decision layer
mecha_genome        Grid/body representation
mecha_lineage       Ancestry and survival history
mecha_render        Visual output bridge
mecha_archive       Quality-diversity species archive
```

---

##  34. <a name='RecommendedFirstImplementationTarget'></a>1.34. Recommended First Implementation Target

Build this first:

```txt
A 16x16 monochrome grid creature that:
1. Is generated from a genome.
2. Has hunger, energy, mood, and age.
3. Changes expression based on state.
4. Logs user interactions.
5. Mutates after death or lifecycle completion.
6. Produces a child using parent traits.
7. Saves a lineage file.
```

This proves the entire thesis.

Everything else can grow from there.

---

##  35. <a name='WorkingThesis'></a>1.35. Working Thesis

The project can be summarized as:

> `Mechagotchi` is an open-source digital companion engine where grid-based creatures are born from procedural genomes, guided by `SLIP` profiles, shaped by user interaction, and evolved through a lightweight Darwinian intelligence system composed of Markov prediction, micro-learning threads, and quality-diversity survival archives.

That is the core.

And it is strong.

[1]: https://arxiv.org/html/2410.15644v1?utm_source=chatgpt.com "Procedural Content Generation in Games: A Survey ..."
[2]: https://cdn.aaai.org/ojs/12708/12708-52-16225-1-2-20201228.pdf?utm_source=chatgpt.com "Generating Maps Using Markov Chains"
[3]: https://members.loria.fr/jbmouret/qd.html?utm_source=chatgpt.com "Quality Diversity Algorithms"
[4]: https://github.com/topics/tamagotchi-game?o=asc&s=forks&utm_source=chatgpt.com "tamagotchi-game"

### 2026-10-04 addendum to section 1.17: hidden source survey

The complete P1 visible instrument reproduces. Mutation pressure, the opt-in
novelty/boredom signal, prediction-specific attention confidence and Boolean
profile alignment have bounded derived source candidates. Dedicated lineage
fitness and independent attachment definitions are absent from reviewed public
surfaces; candidate fitness and bond are not aliases. No hidden display or
canonical adoption follows. See DR 0065 and the six-row measured table in
`research/experiment_reports/2026-10-04-hidden-axis-sources-and-readable-controls.md`.
