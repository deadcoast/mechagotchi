# Project Overview

Mechagotchi is a research-first grid-based artificial-life companion platform. The governing thesis in `docs/02-research_plan.md` is that creature visual grids, behavior, survival, memory, mutation, and user-authored SLIP profiles should participate in a coherent evolutionary system. The repo is currently a research/lab workspace, not a packaged app: `packages/` is intentionally absent until package gates are satisfied.

Important source-of-truth docs:
- `docs/01-brainstorming.md`: concept notes and original two-build model (`mecha_engine`, `mecha_workshop`).
- `docs/02-research_plan.md`: primary research plan and stage requirements.
- `research/README.md`, `research/slip/profile_compatibility_tests.md`, and `research/experiment_reports/stage0_stage1_kickoff.md`: current ledgers for completed/blocked research state.

Main code/data layout:
- `labs/`: executable research prototypes and unit tests.
- `data/`: generated evidence artifacts and fixture corpora.
- `research/`: algorithm cards, reports, package specs, source notes, SLIP docs.
- `docs/`: planning and archived source material.

Current work pattern is evidence-first: add or update lab tests, generate JSON/data artifacts, update research reports/ledgers, and keep blocked states explicit rather than promoting lab work prematurely.