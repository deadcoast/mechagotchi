# Mechagotchi — Computational Life Engine

**Mechagotchi is the ongoing, research-first development of a grid-based
artificial-life companion engine.** It is inspired by the CuBFF study and
source code behind the paper *Computational Life: How Well-formed,
Self-replicating Programs Emerge from Simple Interaction*
([arXiv:2406.19108](https://arxiv.org/abs/2406.19108); local copy at
`assets/pdf/2406.19108v2.pdf`; upstream code:
[paradigms-of-intelligence/cubff](https://github.com/paradigms-of-intelligence/cubff)).

## What this repository is — and is not

**This repository is NOT a CLI application.** It has a CLI *supportive
layer* (`mechas`, under `tools/`), and that layer exists only to serve the
application. The application is, and remains, the engine: genome grids,
constrained generation, lifecycle, repair, MAP-Elites archives,
provenance — the Mechagotchi Computational Life Engine. This distinction
is a standing constraint recorded to prevent drift of the end goal: no
supporting surface (CLI, tooling, docs, UI) may quietly become the
project.

The main goal requires researched, mathematical support and provable
practices. This repository was **not** created on assumptions, was not
rushed fastest-to-launch, and cuts no corners. It was designed from the
ground up with comprehensive foundations to build upon — deep research,
theories, methods, and functions derived from them. Nothing is claimed
without executable evidence; nothing is promoted without passing a
documented gate.

## The public alpha (M7)

Both builds are reproducible from one document: **`docs/alpha.md`** —
install, run the full verification sweep, play/build the game, share
covenant packs. The GAME build lives at `game/` (a pygame-ce client;
DR 0033) and the ENGINE at `packages/mecha_engine/`; the whole MVP
ladder (0.1 → 0.3) and Phase G's gates are recorded in
`research/experiment_reports/` with their evidence under `data/`.

## The supporting ecosystem

Every piece of source code and application surface is supported by the
same ecosystem, and changes to one must update the others in the same
change:

| Surface | Where |
| --- | --- |
| Research | `research/` — experiment reports, algorithm cards, decision records, the master ledger (`research/README.md`) |
| Documents | `docs/` — the research plan (`docs/project-research/research.md`, governing), agent standards, reports |
| Features / Designs / SPEC | `research/package_specs/`, `docs/cli/` and `docs/mecha-workshop/` design charters |
| TODO | `research/questions.md`, per-doc roadmaps, artifact `next_research_step` fields |
| Modules | `packages/mecha_engine/` — promoted engine modules, each gated by contract tests and lab parity |
| Labs | `labs/` — executable research prototypes, stdlib-first |
| CLI (supportive layer) | `tools/mechas_cli/` — the `mechas` command; design contract in `docs/cli/mechas-cli-design.md` |
| Tests | per-lab suites, package contract suites, CLI suites — all green before any commit |
| Evidence | `data/` — JSON artifacts and fixture corpora every claim traces to |

Authoritative chain when documents conflict: the research plan → decision
records → package specs/gates → the ledger → executed `data/` artifacts.
Executed artifacts win over prose claims.

## Provenance and standards

Mechagotchi is the flagship and first project of **MIVIM.dev** —
**M I V I M · Modular Innovations, Versatile Integration Methods**. The
developer's name is attached to it: everything created here represents
its author and is held to the strict, thorough development standards the
repository has established — research-first, evidence-gated,
honestly-reported (negative results are first-class), and documented as
living files.

MIVIM prides itself on design philosophy, user experience, and quality of
life throughout every aspect and stage of development. No matter the
detail, the ideology and execution always provide the best user
experience — not necessarily the most optimized or the fastest. MIVIM
products are known for finding creative implementations and developing
unique integrations for a one-of-a-kind user experience, built
foundationally from the ground up. In this repository that doctrine is
visible everywhere: the research-first engine foundations, the evidence
ecosystem around every surface, and the `mechas` supportive layer whose
design charter (`docs/cli/mechas-cli-design.md`) trades speed margins for
developed quality of life by explicit policy.

## Sources

- `assets/pdf/2406.19108v2.pdf` (Computational Life, arXiv:2406.19108)
- `docs/project-research/research.md`
- `docs/agent-standards.md`
- `research/README.md`
- `research/literature_map.md`
- `docs/cli/mechas-cli-design.md`
- `CLAUDE.md`
