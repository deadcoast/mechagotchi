# 1. MAP OF CONTENTS

**The navigational map of the Mechagotchi repository.** Every directory,
what it *is*, and which file to open for a given question.

Last refreshed **2026-08-08** (Phase-O gate green; cycle 26 · Phase P
open). Counts in §5 are measured, not quoted — re-measure before
relying on them.

<!-- vscode-markdown-toc -->
* 1. [1.1. START HERE](#STARTHERE)
* 2. [1.2. THE TWO BUILDS](#THETWOBUILDS)
* 3. [1.3. THE GOVERNING DOCUMENTS](#THEGOVERNINGDOCUMENTS)
* 4. [1.4. THE EVIDENCE LEDGER](#THEEVIDENCELEDGER)
* 5. [1.5. THE WORK: QUEUE AND HISTORY](#THEWORKQUEUEANDHISTORY)
* 6. [1.6. SUPPORTING SURFACES](#SUPPORTINGSURFACES)
* 7. [1.7. DICTIONARY](#DICTIONARY)
	* 7.1. [1.7.1. INDEXING](#INDEXING)

<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

---

##  1. <a name='STARTHERE'></a>1.1. START HERE

Five markdown files sit at the repo root (the changelog was relocated
into `sunsetted/` by the owner, 2026-08-08). This is what each one is for:

| file | what it is | read it when |
| --- | --- | --- |
| [`ONBOARDING.md`](ONBOARDING.md) | **the entry point** — the frame, the owner rulings that are LAW, the state snapshot, honesty norms, first moves | starting a fresh session |
| [`README.md`](README.md) | what the project **is**, and the anti-drift identity constraint | you need the identity or the pitch |
| [`CLAUDE.md`](CLAUDE.md) | the agent operating brief — commands, architecture, conventions, the completion checklist | you are about to change code |
| [`CHANGELOG.md`](sunsetted/complete/CHANGELOG/01/CHANGELOG.md) | cycle-by-cycle summary of what shipped, derived from the gate reports | you need the shape of the history fast |
| [`_MOC_.md`](_MOC_.md) | **this file** — the map of contents | you don't know where something lives |
| [`TOOLS.md`](TOOLS.md) | tooling notes | setting up the environment |

**Authority order when documents conflict:** the research plan →
decision records → package specs/gates → the ledger → executed `data/`
artifacts. **Executed artifacts win over prose claims.** `ONBOARDING.md`
and the decision records win over everything else at the root.

---

##  2. <a name='THETWOBUILDS'></a>1.2. THE TWO BUILDS

The project is **two separate builds**. Confusing them is the failure
mode `README.md`'s identity constraint exists to prevent.

| | THE ENGINE | THE GAME |
| --- | --- | --- |
| what | the Mechagotchi Computational Life Engine | *"Eras of the Soup"* (DR 0021) |
| where | [`packages/mecha_engine/`](packages/mecha_engine/) | [`game/`](game/) |
| stack | src layout, stdlib-only | pygame-ce (DR 0033) |
| modules | 10 promoted: `genome`, `generation`, `lifecycle`, `archive`, `provenance`, `repair`, `runtime`, `learning`, `storage`, `slip` | companion loop, era bench, covenant spending, hatchery, replays, browsers |
| contracts | [`research/package_specs/`](research/package_specs/) | DR 0021's engine-truth law |

`render` is **dispositioned, not promoted** (DR 0026,
rejected-until-consumer). **The engine is built before the game.**

**Everything else is a supporting surface, never the application:**

| surface | where | what it is |
| --- | --- | --- |
| authoring layer | [`workshop/`](workshop/) | grid editor, SLIP creator, preview/scrubber, inspector |
| CLI | [`tools/mechas_cli/`](tools/mechas_cli/) | the `mechas` command (Typer + Rich, DR 0007) |
| the sweep | [`tools/ci/run_sweep.py`](tools/ci/run_sweep.py) | **the ONE verification runner** every gate uses |

**Boundary law (enforced by a scan):** no `sys.path` text anywhere in
`packages/` or `game/src/`. Package and game code import `mecha_engine`,
**never** `labs`. Labs *may* import the package — that is exactly how
parity pins work. Private files are **mirrored verbatim, never
imported** across boundaries, and a lab-side parity test pins the mirror
so drift fails the suite.

---

##  3. <a name='THEGOVERNINGDOCUMENTS'></a>1.3. THE GOVERNING DOCUMENTS

**The documentation is the deliverable AND the governance** — roughly
300k words defining the scope; the code is the part proven so far.

### The vision and the plan

| document | what it is |
| --- | --- |
| [`docs/project-research/research.md`](docs/project-research/research.md) | **THE GOVERNING DOCUMENT** — thesis, math/ALife layers, Stages 0–7, the evaluation framework |
| [`docs/project-research/validity-research.md`](docs/project-research/validity-research.md) | the founding vision and the MVP ladder (§1.34 names the first target; §1.17 the visible/hidden companion axes) |
| [`docs/project-research/deep-research/01/deep-research.md`](docs/project-research/deep-research/01/deep-research.md) | **the research dossier** — scale figures, thresholds, stages, method matrices, ablation protocols. *Two concatenated reports; both matter.* |
| [`docs/project-research/deep-research/01/sources.md`](docs/project-research/deep-research/01/sources.md) | the dossier's citations |
| [`docs/alpha.md`](docs/alpha.md) | the public-alpha packet — both builds reproducible from one document |
| [`docs/gap-analysis.md`](docs/gap-analysis.md) | **RETIRED** per its own charter (Phase-G gate green 2026-07-12); kept as the measured history of the gap and how it closed |
| [`docs/agent-standards.md`](docs/agent-standards.md) | an older orientation doc, **largely superseded** by `ONBOARDING.md` |

### The upstream science

[`assets/pdf/2406.19108v2.pdf`](assets/pdf/) — *Computational Life: How
Well-formed, Self-replicating Programs Emerge from Simple Interaction*
(arXiv:2406.19108). Upstream code:
[paradigms-of-intelligence/cubff](https://github.com/paradigms-of-intelligence/cubff).
Real CuBFF export data **is ingested** (cycle 17 G2) — never resurface
ingest as an open question, and never fabricate "real" data.

### Design charters

| document | governs |
| --- | --- |
| [`docs/cli/mechas-cli-design.md`](docs/cli/mechas-cli-design.md) | the `mechas` CLI design contract |
| [`docs/cli/mechas-cli.md`](docs/cli/mechas-cli.md) · [`mechas-cli-audit.md`](docs/cli/mechas-cli-audit.md) | the CLI reference and its audit |
| [`docs/mecha-workshop/mecha-workshop-design.md`](docs/mecha-workshop/mecha-workshop-design.md) · [`mecha-workshop.md`](docs/mecha-workshop/mecha-workshop.md) | the workshop authoring layer |

---

##  4. <a name='THEEVIDENCELEDGER'></a>1.4. THE EVIDENCE LEDGER

[`research/`](research/) **is the deliverable.** Every claim traces from
the plan down through reports to lab code and JSON artifacts.

### The master index

**[`research/README.md`](research/README.md) — THE MASTER TRACEABILITY
LEDGER.** Start here for any "where is the evidence for X" question.

### The triad convention

Each finding exists as linked files sharing one slug:

```text
research/experiment_reports/YYYY-MM-DD-kebab-slug.md   ← dated report
research/algorithm_cards/same_stem.md                  ← card (when an algorithm)
labs/<lab>/<module>.py (+ test_<module>.py)            ← code
data/<lab>/<slug>_stage0.json                          ← evidence
```

All four are registered in `research/README.md`. **Every code or data
change updates its documents in the SAME change.**

### The ledger's directories

| directory | what it holds |
| --- | --- |
| [`research/experiment_reports/`](research/experiment_reports/) | dated findings + **the per-phase gate reports** (`YYYY-MM-DD-phase-N-gate.md`) |
| [`research/algorithm_cards/`](research/algorithm_cards/) | fixed-template cards (Name / Purpose / Mathematical basis / … / Decision / Go-No-Go gate) |
| [`research/decision_records/`](research/decision_records/) | **ADRs, `NNNN-slug.md`** — the decisions that are law |
| [`research/package_specs/`](research/package_specs/) | engine contracts + the **traceability matrix** |
| [`research/reports/`](research/reports/) | consolidated reports `v0_1`–`v1_0`, each with a `*_manifest.json` |
| [`research/failed_approaches/`](research/failed_approaches/) | **the refuted record — a valued, first-class part of this repo** |
| [`research/grid_genome/`](research/grid_genome/) | the genome schema + the numbered hard/soft **invariants** |
| [`research/slip/`](research/slip/) | the SLIP schema + its pydantic-generated mirror |
| [`research/micro_learners/`](research/micro_learners/) · [`asset_provenance/`](research/asset_provenance/) · [`source_notes/`](research/source_notes/) | per-domain notes |

### The reference documents inside the ledger

| document | what it answers |
| --- | --- |
| [`research/glossary.md`](research/glossary.md) | the companion-domain vocabulary |
| [`research/questions.md`](research/questions.md) | the research questions, numbered by stage — **the TODO of the science** |
| [`research/literature_map.md`](research/literature_map.md) | the surveyed literature |
| [`research/human_studies_protocol.md`](research/human_studies_protocol.md) | the owner-deferred human-study block (prepared, **not** blocking) |

### The decision records you will meet constantly

| DR | what it decided |
| --- | --- |
| **0017** | **the North Star** — the ENGINE+GAME duality; deep integrations over breadth |
| **0021** | **the game, and its FIRST LAW: everything shown a player is engine truth** |
| **0028** | Apache-2.0; third-party dependencies **permitted** when a capability needs one |
| 0029 / 0030 | size-parametric grids (16×16 proven); size-relative SLIP mass bounds |
| 0031 / 0042 | WFC generation adopted → the constrained layer adopted **at the loop** |
| 0033 | pygame-ce for the game client |
| 0035 | community infrastructure / registry / hosting are **OWNER decisions**, not tasks |
| 0046 | the two-geometry split — **and its comparability rule: numbers from different geometries may not be read against each other** |
| 0052 / 0053 | `slip_admission="insertion"` adopted → **a setting that changes what an artifact MEANS is recorded at the call site, never inherited from a default; a study that measures a defect is never migrated onto the fix** |
| 0054 / 0055 | `health` **is** `danger_margin` (a euphemism refused) → the readout ships **with its binding axis** |
| 0056 | DR 0042's headline **restated, not retracted** — any *"the loop achieves X"* must name **which arm** |
| 0057 | Stage 2's generator arms dispositioned **in their documented roles** — CPPN rejected, shape grammar watches, nothing adopted |

### The evidence itself

[`data/`](data/) — JSON artifacts and fixture corpora. Every
`*_stage0.json` carries `artifact_id`, `status`, `date`, `purpose`,
`source_artifacts`, metrics, `closed_states`, `blocked_states`,
`decision`, `next_research_step`. **Blocked states stay explicit — never
silently drop an unproven surface.** Paths inside artifacts are
repo-relative POSIX strings, never absolute.

> Two `data/slips` pydantic-version artifacts are rewritten by every
> `slip_validator` sweep. They are **per-run environment observations by
> design** — `git checkout` them, **never commit**.

---

##  5. <a name='THEWORKQUEUEANDHISTORY'></a>1.5. THE WORK: QUEUE AND HISTORY

| file | what it is |
| --- | --- |
| **[`sunsetted/TODO.md`](sunsetted/TODO.md)** | **THE LIVE CYCLE QUEUE** — the actual work list |
| [`sunsetted/complete/TODO/NN/TODO.md`](sunsetted/complete/TODO) | archived cycles (01–07, 09–25; **there is no cycle 08**) |
| [`CHANGELOG.md`](sunsetted/complete/CHANGELOG/01/CHANGELOG.md) | the cycle-by-cycle summary, derived from the gate reports |

**The cycle rule:** work the queue task by task, RED first, triad docs in
the same change, **one commit per task naming the task ID**. A cycle ends
only when the queue is exhausted **and** a full sweep is green — then
archive to `sunsetted/complete/TODO/NN/` and **plan the next cycle from
the documentation**. Never ask which direction.

### The phase ladder

| cycle | phase | delivered |
| --- | --- | --- |
| 01–07 | pre-phase | ontology, schemas, validators, labs, the module promotion program |
| 09–13 | A–E | 16×16 foundation → WFC generation → animation → the micro-learner fleet → evolution at documented scale |
| 14–17 | F–G | the GAME client (MVP 0.1→0.3) → **the public-alpha gate**, real CuBFF ingest |
| 18–21 | H–K | workshop depth → post-takeover science → the generative range → the vocabulary settles |
| 22 | L | the descriptor geometry — *and the cycle audits its own **numbers*** |
| 23 | M | the archive's own inhabitants — *and the cycle audits its own **sentences*** |
| 24 | N | the descriptor space earns its edges — *and the cycle audits its own **instruments*** |
| 25 | O | the adopted definitions reach the player — *landed without a committed number drifting* |
| **26** | **P** | **the missing axes earn their sources ← current** |

### The measured state

Verified **2026-08-08**, `python -B tools/ci/run_sweep.py` →
**SWEEP GREEN**:

| surface | count |
| --- | --- |
| lab suites | **19** |
| package | **299** tests |
| game | **200** tests |
| workshop | **92** tests |
| CLI | **23** tests |
| JSON artifacts | **2,247**, 0 invalid |
| experiment reports | **273** |
| algorithm cards | **79** |
| decision records | **57** (through DR 0057) |

---

##  6. <a name='SUPPORTINGSURFACES'></a>1.6. SUPPORTING SURFACES

### The labs — where every algorithm is proven FIRST

[`labs/`](labs/) — 19 research labs. **No algorithm graduates to the
package until it has an algorithm card, an experiment report, a metric
report, and a decision record.**

| lab | domain |
| --- | --- |
| `grid_genome` | the genome schema, the validator, SLIP interpretation |
| `wfc_grid` | wave-function-collapse generation + the generator bake-offs |
| `map_elites_archive` | the MAP-Elites archive, the evolution loop, coverage/QD gates *(the largest suite)* |
| `micro_threads` | the micro-learner fleet + the ablation gates |
| `lifecycle_sim` | homeostasis, death conditions, the danger thresholds |
| `cellular_automata` | growth/repair dynamics |
| `workshop_editor` | ~30 modules hand-encoding PNG/APNG/Aseprite with stdlib `struct`+`zlib` |
| `readability_benchmark` | the learned readability model (DR 0019) |
| `cubff_transducer` | the CuBFF bridge |
| `package_promotion` | **the promotion gate** — a module moves only when it says `promotion_ready` |
| `architecture`, `animation_system`, `asset_pipeline`, `ctm_ticks`, `datasets`, `game_loop`, `repair_boundary`, `runtime_integration`, `slip_validator` | the remainder |

**The lab module pattern** (preserve it): `foo.py` + sibling
`test_foo.py`, flat imports, `ROOT = Path(__file__).resolve().parents[2]`,
a `build_*_report()` returning the report dict, a
`write_*_artifacts(output_dir, report)`, and an `if __name__ ==
"__main__":` main with argparse defaults into `data/`.

### Not evidence

`keeper/` and `game/dist/` are live play state and builds — **gitignored,
never evidence**. [`.depreciated/`](.depreciated/) is the **owner's
personal archive — ignore unless explicitly linked.**

---

##  7. <a name='DICTIONARY'></a>1.7. DICTIONARY

###  7.1. <a name='INDEXING'></a>1.7.1. INDEXING

> *NUMERIC MEANING/CATEGORY IN THE INDEX*

* [0] = "Orientation and onboarding"
  * [ONBOARDING](ONBOARDING.md) ← **the entry point**
  * [AGENT-BRIEF](CLAUDE.md)
  * [AGENT-ONBOARDING](docs/agent-standards.md) *(older, superseded)*
* [1] = "Unformatted notes or rough ideas"
  * [BRAINSTORMING](docs/project-research/validity-research.md)
* [2] = "Research Plans"
  * [RESEARCH_PLANS](docs/project-research/research.md) ← **governing**
* [3] = "Formatted Reports created from [2]"
  * [DOSSIER](docs/project-research/deep-research/01/deep-research.md)
  * [CODE-REVIEW](sunsetted/complete/TODO/02/2026-07-04-code_review.md)
* [4] = "Sources and Citations"
  * [SOURCES](docs/project-research/deep-research/01/sources.md)
  * [LITERATURE](research/literature_map.md)
* [5] = "The evidence ledger"
  * [MASTER-LEDGER](research/README.md) ← **the traceability spine**
  * [EXPERIMENT-REPORTS](research/experiment_reports/)
  * [ALGORITHM-CARDS](research/algorithm_cards/)
  * [REFUTED-RECORD](research/failed_approaches/)
* [6] = "Decisions that are law"
  * [DECISION-RECORDS](research/decision_records/)
* [7] = "Contracts and specifications"
  * [PACKAGE-SPECS](research/package_specs/)
  * [TRACEABILITY-MATRIX](research/package_specs/mecha_engine_contract_traceability_matrix.md)
  * [GRID-INVARIANTS](research/grid_genome/grid_invariants.md)
* [8] = "The work"
  * [LIVE-QUEUE](sunsetted/TODO.md) ← **the actual work list**
  * [ARCHIVED-CYCLES](sunsetted/complete)
  * [CHANGELOG](sunsetted/complete/CHANGELOG/01/CHANGELOG.md)
* [9] = "The builds"
  * [ENGINE](packages/mecha_engine/)
  * [GAME](game/)
  * [ALPHA-PACKET](docs/alpha.md)

---

## Sources

* `ONBOARDING.md`, `README.md`, `CLAUDE.md`, `TOOLS.md`, `sunsetted/complete/CHANGELOG/01/CHANGELOG.md`
* `docs/project-research/research.md`, `validity-research.md`, `deep-research/01/deep-research.md`
* `research/README.md` (the master ledger), `research/glossary.md`, `research/questions.md`
* `research/decision_records/0017`, `0021`, `0028`, `0033`, `0035`, `0046`, `0052`–`0057`
* `sunsetted/TODO.md`, `sunsetted/complete/TODO/`
* `tools/ci/run_sweep.py` (the one verification sweep)
