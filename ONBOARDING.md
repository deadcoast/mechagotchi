# ONBOARDING.md — start here, next session

Written **2026-07-21** by the outgoing session and completed
**2026-07-26**, at the owner's direction. Read this file completely
before touching anything.

**How to trust this file:** §1 (the frame), §2 (owner rulings), §6 (the
format), and §7 (honesty norms) are *durable* — they are owner rulings
and established discipline; they do not expire. §3 (state) and §4
(what's next) are a **snapshot** — re-verify them against `git log`,
`audits/TODO.md`, and the gate artifacts before relying on them.

Related files: `FABLE5.md` is the previous onboarding handoff (its §1–2
and §6 remain valid law; its §3/§5 state sections are stale — this file
supersedes them). `AGENTS.md` is the current agent operating brief;
`CLAUDE.md` remains the Claude-specific brief.
`docs/agent-standards.md` is an older orientation doc, largely
superseded. Where they conflict: **this file and the decision records
win.**

---

## 1. THE FRAME — we are building TWO things

The owner has had to repeat this to the point of exhaustion. Do not
make them say it again.

1. **THE ENGINE** — the *Mechagotchi Computational Life Engine*.
   Grid genomes, generation, validation, lifecycle, repair, evolution
   archives, micro-learning threads, SLIP interpretation, the render
   bridge. Lives in `packages/mecha_engine` (ten promoted modules) and
   is proven through `labs/` + `research/` + `data/`. Inspired by the
   CuBFF study behind *Computational Life: How Well-formed,
   Self-replicating Programs Emerge from Simple Interaction*
   (arXiv:2406.19108; local copy `assets/pdf/2406.19108v2.pdf`).
2. **THE GAME** — *"Eras of the Soup"* (DR 0021): a Keeper stewards a
   bloodline through eras of a computational-life soup. It is a
   **separate build with its own playable front end** — a client a
   player launches and plays. It lives at `game/` (pygame-ce, DR 0033)
   and its MVP ladder 0.1 → 0.2 → 0.3 is built and gated.

They sell each other, so both must be high quality and creative or
neither matters. **The engine is built before the game.** The
`workshop/` (authoring layer) and the `mechas` CLI (`tools/`) are
**supporting surfaces — never the application.**

### Why we build it this way

The defining property of this repo: **the documentation is the
deliverable AND the governance.** Roughly 300k words of research
documents define the scope; the code is the part of it that has been
proven so far. Nothing is claimed without executable evidence; nothing
is promoted without passing a documented gate. This exists because the
project's one real failure mode is *drift* — a session working from
memory or momentum instead of the repo's own documents, overdeveloping
whatever is under its cursor, and calling a fraction "the application."

**The anti-periscope rule:** before deepening any feature, ask — does
the bigger picture need MORE of this, or am I periscoping? Every cycle
plan names its build track (ENGINE / GAME / SHARED) and its phase.

**The engine-truth law (DR 0021, first law):** everything any surface
shows a player is engine truth — a report field, an artifact, or a
recorded replay. No invented numbers. Uncalibrated things are shown as
uncalibrated.

**The North Star (DR 0017):** the ENGINE+GAME duality — deep
integrations over breadth. The manual rating system is a FALLBACK,
never a blocker.

---

## 2. Owner rulings that are LAW (do not re-litigate, do not undo)

- **Never declare the project "complete," "finished," or the queue
  "empty."** A prior session did this twice, measuring against its own
  invented queues instead of the documentation. The documentation
  defines the scope; the implementation is a fraction of it.
- **When a queue exhausts, THE DEVELOPER plans the next cycle** from
  the still-unmet documentation and keeps developing. **Never stop to
  ask "which direction?"** — a prior session did and was forcefully
  corrected. Asking for direction is a failure.
- **License: Apache-2.0** (DR 0028; root `LICENSE`; pyproject declares
  it; a test pins the declaration).
- **Third-party dependencies are PERMITTED** when a capability needs
  one (DR 0028), declared in the pyproject and justified in the
  feature's decision record. The old stdlib-only policy is retired —
  never present minimalism as a virtue that shrinks the documented
  scope. In practice stdlib has kept holding at every measured scale
  gate so far; that is a *measurement*, not a policy.
- **CuBFF real-export ingest was REQUIRED and is DONE** (cycle 17 G2 —
  real upstream data, built in WSL2 at the audited commit). Never
  fabricate "real" data; never resurface ingest as an open question.
- **Manual readability calibration** (browser survey via `mechas rate
  --creatures`, 0/63 rows) is deferred by owner choice. The LEARNED
  model is primary (DR 0019;
  `data/readability_benchmark/adopted_readability_model.json`); the
  rating pipeline is its fallback. **Never treat calibration as a
  blocker.**
- **`.depreciated/` is the owner's personal archive** — ignore unless
  explicitly linked.
- **Never push without being asked.** Commit per completed task. Note:
  the owner's IDE tooling can commit the working tree mid-session —
  check `git log` before committing and stage by explicit path.
- **Community infrastructure, a pack registry, and hosted
  distribution are OWNER decisions** (DR 0035), not tasks.
- Talk to the owner in **plain language**: explain what things ARE,
  not just what changed; lead with outcomes; never over-promise
  (describing 10% as if it were the vision destroyed trust once).

---

## 3. WHERE WE ARE RIGHT NOW (2026-07-21 — verify against `git log`)

### The headline

**Every documented phase A–G is COMPLETE and GATED.**
`docs/gap-analysis.md` — the roadmap that governed cycles 09–17 — is
**RETIRED per its own charter** (the Phase-G alpha gate went green
2026-07-12). It remains as the measured history of the gap and how it
closed. Since then, cycles plan from the **still-unmet documentation**
and from the named remainders each cycle's own records leave behind.

### The cycle ladder so far

| Cycle | Phase | What it delivered |
| --- | --- | --- |
| 01–07 | pre-phase | ontology, schemas, validators, labs, the module program (no cycle 08) |
| 09 | A | the 16×16 foundation (DR 0029/0030) |
| 10 | B | WFC generation + the real bake-off (WFC ships, DR 0031; hybrid REFUTED) |
| 11 | C | the animation system (clips, transitions 0.9877, `animstate_950`, packet contract) |
| 12 | D | the intelligence threads (fleet 11/11; ablation gates: 5 kept / 6 dropped) |
| 13 | E | evolution at documented scale (20,480 evals/run; coverage/QD/family gates) |
| 14–16 | F | the GAME client: MVP 0.1 → 0.2 → 0.3 (pygame-ce, DR 0033) |
| 17 | G | the late-stage requireds → **the public-alpha gate GREEN**; REAL CuBFF corpus ingested |
| 18 | H | workshop authoring depth |
| 19 | I | the post-takeover science |
| 20 | J | the generative range (vocabulary blindness found and cured) |
| **21** | **K** | **the vocabulary settles its stack ← WE ARE HERE** |

Archived queues live in `audits/complete/NN/TODO.md`.

### Cycle 21 · Phase K — current status

`audits/TODO.md` is the live queue: **K1–K5 are DONE; K6 is the only
task left.**

- **K1 — the 11-class regrowth head** (DR 0041): implemented at both
  head sites as a model-level vocabulary. **Adoption WITHHELD by its
  own pre-registered rule** — G1 refused at +0.0944 vs the +0.10 bar
  while G2–G5 passed. The refusal carries its own measured mechanism
  (rich-token sites 0.0 → 0.525; the pooled metric is
  denominator-diluted). A refused gate delivered as a first-class
  finding.
- **K2 — the DR 0031 generation-layer revisit** (DR 0042, **ADOPTED**):
  judged at the consumer through the full loop. Constrained wins
  coverage 0.7852 → **0.8984** and QD ratio 1.3025; 460 niches = the
  measured support ceiling. The E4 gates re-ran symmetrically; the
  DR 0032 GA-advantage clause refused *deeper* (+11.3% vs ≥25%).
- **K3 — the last nine bins**: the reachability probe escalated —
  **five reached (508/512 proven)**, four bounded sharper by a new
  blocking-axis instrument: the remaining emptiness is
  MEASURE-THINNESS, not distance (one bin misses by 0.0014; one is
  suspected *quantization* emptiness).
- **K4 — the real forecast** (DR 0043): the game adopts forecast key 5
  — the committed I3 callback records verbatim, the first weather
  whose harshness channels are LIT — with **zero engine-seam changes**
  proven structurally and behaviorally. `lineage_churn` dispositioned
  BLOCKED-UPSTREAM (honest silence, no proxy smuggled).
- **K5 — the covenant's budget face in the workshop** (DR 0044,
  **ADOPTED, boundary pinned**): the slip creator shows the campaign's
  earned caps beside the sliders that author them. **Advisory, never
  authority** — an over-budget schema-legal profile still validates and
  saves; the game's `apply_covenant_change` stays the only spender.
- **K6 — the Phase-K gate** ← **THE NEXT TASK.** One consolidated gate
  report; cycle 21 archived to `audits/complete/21/`; cycle 22 planned
  from the documentation.

### ⚠ UNCOMMITTED WORK IN THE TREE

**K5 is complete but NOT COMMITTED.** At handoff `git status` shows:

```text
 M audits/TODO.md                              (K5 checked off)
 M research/README.md                          (K5 ledger entry)
 M labs/game_loop/session_runner.py            (state_covenant_budget)
 M labs/game_loop/test_session_runner.py
 M workshop/server/workshop_server.py          (the read-only endpoint)
 M workshop/slip_creator/slip_creator.html     (the advisory strip)
 M workshop/tests/test_workshop_server.py
 M .serena/project.yml                         (tooling noise)
?? research/decision_records/0044-covenant-budget-workshop-face.md
?? research/experiment_reports/2026-07-21-covenant-budget-face.md
```

**First act of the next session: verify these are still uncommitted
(the owner's IDE may have committed them), confirm the suites are
green, and commit K5 before starting K6.** Last commit at handoff:
`c452b86` (K4).

### What exists and is genuinely good

- **`packages/mecha_engine`** — ten promoted modules: `genome`,
  `generation`, `lifecycle`, `archive`, `provenance`, `repair`,
  `runtime`, `learning`, `storage`, `slip`. (`render` is
  DISPOSITIONED, not promoted — DR 0026, rejected-until-consumer.)
  Each backed by contract tests and lab-side parity pins.
- **`game/`** — the playable client (pygame-ce). Companion loop, era
  bench, covenant spending, hatchery, Contribute bridge, replays,
  repertoire/lineage browsers, SLIP import/export, community packs,
  save/resume, a PyInstaller bundle. ~174 tests.
- **`workshop/`** — grid editor, SLIP creator, preview/scrubber,
  inspector, Keeper session page. ~92 tests.
- **`labs/`** — 19 research labs; every algorithm is proven here first.
- **`research/`** — the evidence ledger: 249 experiment reports,
  algorithm cards, 44 decision records, package specs.
- **`data/`** — 2,230 JSON evidence artifacts, all valid.

**Verified at handoff (2026-07-21):** `python -B tools/ci/run_sweep.py`
→ **SWEEP GREEN** — all 19 lab suites, package, CLI, game, and
workshop OK; `data artifacts OK — 2230 JSON artifacts valid`. This was
run **with the uncommitted K5 work in the tree**, so that work is
verified green, not merely finished. (Slowest: workshop 165 s,
runtime_integration 73 s, cellular_automata 35 s, map_elites 33 s.)
- Real CuBFF data is ingested; 16×16 is the proven grid scale;
  novelty-first evolution and the constrained generation layer are
  adopted; the vocabulary is ratified end to end.

### Standing named remainders (not tasks until a record charters them)

The undiluted rich-site regrowth instrument (K1's named re-opener);
the ~22% constrained generation-failure cause; an analytical emptiness
argument for the quantization bin; density-as-pressure (DR 0043 clause
2); richer callback export states; SLIP-shaped caps only in the
workshop budget strip; the ≤45-min HUMAN first-session pass (H5,
prepared-not-blocking); per-clip choreography (an engine DR when a
consumer asks); the scale-geometry seam; DR 0032's re-openers
(untriggered, refutation deepening).

---

## 4. WHAT TO DO NEXT

1. **Commit K5** (see the warning above) — verify green first.
2. **K6 · the Phase-K gate**: one consolidated gate report in
   `research/experiment_reports/2026-07-21-phase-k-gate.md` following
   the pattern of `2026-07-20-phase-j-gate.md` — the consolidated
   ladder K1→K5 with each verdict, the closing full sweep, and the
   **honest remainder list** (which becomes cycle 22's plan).
3. **Archive** `audits/TODO.md` → `audits/complete/21/TODO.md`.
4. **Plan cycle 22 FROM THE DOCUMENTATION** and the remainders Phase K
   recorded — then keep developing. Do not ask which direction.

---

## 5. The map — what each directory IS

```text
packages/mecha_engine/   THE ENGINE (src layout, promoted modules)
game/                    THE GAME (pygame-ce client, src layout)
workshop/                authoring layer (server + HTML pages)  — support
tools/mechas_cli/        the `mechas` CLI                        — support
tools/ci/run_sweep.py    the ONE verification sweep runner
labs/                    19 research labs — algorithms proven here FIRST
research/                the evidence ledger (the deliverable)
  ├─ experiment_reports/ dated findings (YYYY-MM-DD-kebab-slug.md)
  ├─ algorithm_cards/    fixed-template cards (snake_case, same stem)
  ├─ decision_records/   ADRs, NNNN-slug.md (through 0044)
  ├─ package_specs/      contracts + the traceability matrix
  └─ README.md           THE MASTER TRACEABILITY LEDGER
data/                    JSON evidence artifacts + fixture corpora
docs/                    the vision + roadmap documents
audits/TODO.md           THE ACTIVE CYCLE QUEUE
audits/complete/NN/      archived cycles
keeper/, game/dist/      live play state / builds — GITIGNORED, not evidence
```

**Boundary law (enforced by a scan):** no `sys.path` text anywhere in
`packages/` or `game/src/`. Package and game code import
`mecha_engine`, **never** `labs`. Labs *may* import the package — that
is exactly how parity pins work. The workshop may import both. Private
files are **mirrored verbatim, never imported across boundaries**, and
a lab-side parity test pins the mirror so drift fails the suite.

### The working vocabulary (you will meet these constantly)

`research/glossary.md` defines the companion-domain terms. These are
the *working* terms the reports, commit messages, and artifacts use —
they are not written down elsewhere:

- **SLIP** — Synthetic Learning Intelligence Profile: the user-authored
  constraint profile (palettes, mass bounds, organ roles, mutation
  caps, behavior weights, visual grammar) that governs generation and
  behavior. The *covenant* is the game's name for the player's SLIP.
- **The covenant / unlock facts / spending** — the game earns
  falsifiable "unlock facts" from eras and *spends* them to widen the
  covenant (thinking depth, palette, population). `apply_covenant_change`
  is the only spender.
- **Era / the Keeper** — one era = one `evolve` run under a weather
  forecast; the Keeper is the player, stewarding a bloodline across
  eras.
- **Niches / elites / coverage / QD** — MAP-Elites vocabulary. The
  descriptor space is binned (the 8×8×8 = 512-bin octile geometry);
  an *elite* is the best creature in a bin; *coverage* is the fraction
  of bins occupied; *QD* is quality-diversity (summed elite fitness).
- **Seam** — an additive extension point. The law: a new seam is
  **byte-identical when off**, proven by test, never a rewrite.
- **Parity pin** — a lab-side test asserting the promoted package
  reproduces lab semantics *verbatim* (error strings included). Private
  files are **mirrored, never imported** across boundaries; the pin is
  what makes drift fail the suite.
- **stage0 artifact** — a `data/<lab>/<slug>_stage0.json` evidence
  file. "Stage 0" is the evidence maturity level, not a version.
- **Gate / pre-registered gate / `withhold_adoption`** — a decision
  rule written down *before* the run, with adopt / withhold / refuse
  all first-class outcomes.
- **The fleet / threads** — the 11 micro-learner threads (cycle 12);
  five were kept by the D6 ablation, six dropped.
- **The soup / takeover / post-takeover** — CuBFF terms: the soup is
  the population of interacting programs; *takeover* is the moment
  self-replicators dominate. Early-phase soup behaves very differently
  from post-takeover soup, and reports are careful about which they
  measured.
- **Weather / harshness / forecast keys** — the game's environmental
  pressure, sourced from real CuBFF records; forecast keys 1–5 select
  the source in the client.
- **The triad** — report + card + code + artifact for one finding.
- **Engine truth** — DR 0021's first law (see §1).

### The documents that define the application

1. `docs/project-research/validity-research.md` — the founding vision
   and the MVP ladder (§1.34 names the first target).
2. `docs/project-research/deep-research/01/deep-research.md` — the
   research dossier: scale figures, thresholds, stages, the method
   matrices, the ablation protocols. (Two concatenated reports; both
   matter.)
3. `docs/project-research/research.md` — the research plan.
4. `docs/gap-analysis.md` — RETIRED but the measured history.
5. `research/decision_records/` — 0017 (North Star), 0021 (the game),
   0028 (license/deps), 0029 (size-parametric), 0031/0042 (generation),
   0032, 0033 (pygame-ce), 0035 (community = owner), 0038–0044 (recent).
6. `research/README.md` — the traceability ledger.
7. `docs/alpha.md` — the public-alpha packet.

---

## 6. THE FORMAT we develop in (non-negotiable)

### The triad convention

Every finding exists as linked files sharing one slug:

```text
research/experiment_reports/2026-07-21-covenant-budget-face.md   ← dated report
research/algorithm_cards/<same_stem>.md                          ← card (when an algorithm)
labs/<lab>/<module>.py  (+ test_<module>.py)                     ← code
data/<lab>/<slug>_stage0.json                                    ← evidence
```

…all registered in `research/README.md`. **Every code or data change
updates its documents in the SAME change.** Every research document
ends with a `## Sources` footer of relative repo paths.

### Experiment reports

WHY / WHAT / FINDINGS / **Verification** / Sources. The verification
block contains the exact PowerShell commands with **pasted real
output** — the RED run that failed, the GREEN run that passed, and the
lab invocation that produced the artifact.

### Artifacts

Every `*_stage0.json` carries `artifact_id`, `status`, `date`,
`purpose`, `source_artifacts`, metrics, `closed_states`,
`blocked_states`, `decision`, `next_research_step`. **Keep blocked
states explicit — never silently drop an unproven surface.** Paths in
artifacts are repo-relative POSIX strings, never absolute.

### The lab module pattern

`foo.py` + sibling `test_foo.py`, flat imports, `ROOT =
Path(__file__).resolve().parents[2]`, a `build_*_report()` returning
the report dict, a `write_*_artifacts(output_dir, report)`, and an
`if __name__ == "__main__":` main with argparse defaults into `data/`.
Modern union syntax, frozen dataclasses, explicit annotations,
deterministic tests using `tempfile.TemporaryDirectory`.

### The gate discipline (the strongest recent norm)

**PRE-REGISTER the decision rule in the module BEFORE the run.** Write
the gates, the bars, and the adopt/withhold verbs *first*; then run;
then record whatever the numbers say. Nothing is re-scored after the
fact. K1 refused its own adoption at +0.0944 vs a +0.10 bar and that
refusal shipped as the finding. **A gate that cannot fail is a bug.**

New engine seams are **additive and byte-identical when off** —
proven, not asserted. Adoption never deletes the incumbent: it stays
runnable and parity-pinned.

### The cycle rule

Work `audits/TODO.md` task by task; one commit per completed task
naming the task ID, the evidence, and the doc updates. A cycle ends
only when the queue is exhausted AND a full sweep is green — then
archive to `audits/complete/NN/` and plan the next cycle from the
documentation and the recorded remainders.

---

## 7. Honesty norms (learned the hard way; enforced)

- **Negative results and refuted hypotheses are first-class
  findings.** The refuted record is a real, valued part of this repo.
  A refusal that carries its own measured mechanism is worth more than
  a pass.
- **Gates derive from evidence, never constants.**
- **Record process deviations, don't hide them.** K3 recorded that it
  ran implementation-first, inverting RED-first. K2 recorded that a
  draft briefly carried invented numbers, caught and stripped before
  the artifact existed. Do this.
- **Never fabricate data**, and never present a proxy as the real
  thing. When a channel is silent upstream, pin the silence honestly
  (`lineage_events: []`) and name the re-openers.
- **Beware the statistic, not just the data** — reconstruct the
  engine's exact statistic before comparing outcomes (a survivorship
  bias once ranked the switchboard dead last).
- **A faithful replay reproduces the INPUTS exactly**
  (`founder_grids=None` ≠ `[]` — a real DR 0016 distinction).
- **Never pin environment observations in tests**; assert the policy,
  record availability as a per-run observation.
- **Regenerate artifacts you invalidate** and explain every delta.
  Never let a live surface overwrite committed evidence.

---

## 8. Commands and environment

```powershell
# The FULL sweep — every lab, package, workshop, CLI, game + JSON validation
python -B tools/ci/run_sweep.py            # --quick skips the ~2-min workshop suite

# Individual suites
python -B -m unittest discover -s labs/<lab> -p "test_*.py"
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
python -B -m unittest discover -s workshop/tests -p "test_*.py"
uv run python -B -m unittest discover -s game/tests -p "test_*.py"

# Gates and validation
python -B labs/package_promotion/package_promotion_gate.py
python -m json.tool data/<path>.json

# Play surfaces
uv run python -B game/run_game.py [--ticks N]
mechas session --open
```

- **Always `python -B`** (tree hygiene — tracked bytecode was a real
  past hazard).
- **Run labs with the system `python -B`, not `uv run`** —
  `workshop_editor`'s foreign-fixture byte pins are zlib-BUILD
  sensitive (system 3.14 uses zlib-ng; uv's 3.13 uses classic zlib and
  fails 10 of them; DR 0034 made those pins conditional). The uv venv
  is for the dependency-group suites: `uv sync --group lab --group cli
  --group game` (syncing one group alone EVICTS the others).
- Git: LF→CRLF warnings are normal noise. Commit messages end with the
  co-author line.

---

## 9. Traps that have bitten before

- **The 64-char `grid_id` cap** — reassign ids per cycle; never
  accumulate suffixes. This has bitten TWICE (once a study harness
  measured its own bug as biology).
- **Lifecycle bistability** — stress ≤0.94 stabilizes, ≥0.95 collapses
  around tick 12–14; idle creatures starve by ~tick 11. Mind
  survivorship bias in any per-tick aggregate.
- **`deliberation.max_ticks` has an authority floor of 2.**
- **Rung-conditional keys exist only when their feature ran** —
  `None` ≠ `[]` ≠ absent.
- **Complex one-liners fail PowerShell parsing** — write a script file
  to the scratchpad instead. The Bash tool's `cd` persists between
  calls; prefer absolute paths.
- **Servers must bind port 0** (OS-reserved ranges shift).
- Two `data/slips` pydantic-version observation artifacts get rewritten
  by `slip_validator` sweeps — `git checkout` them, never commit.

---

## 10. First moves for a fresh session

1. `git log --oneline -10` and `git status --short` — what happened,
   and is K5 still uncommitted?
2. Read `audits/TODO.md` — the live queue and its standing note.
3. `python -B tools/ci/run_sweep.py --quick` — confirm the tree is
   green before changing anything.
4. Read the most recent experiment reports in
   `research/experiment_reports/` (2026-07-21-*) for the immediate
   context of the last work.
5. Then work the queue — task by task, RED first, triad docs in the
   same change, one commit per task. When the queue exhausts, plan the
   next cycle yourself from the documentation.

## Sources

- `audits/TODO.md` (cycle 21 · Phase K), `audits/complete/*/TODO.md`
- `FABLE5.md` (the prior handoff; §1–2, §6 remain law)
- `AGENTS.md`, `CLAUDE.md`, `docs/agent-standards.md`
- `docs/gap-analysis.md` (retired; the measured history)
- `docs/project-research/` (the vision documents)
- `research/README.md` (the master ledger)
- `research/decision_records/0017`, `0021`, `0026`–`0044`
- `research/experiment_reports/2026-07-12-phase-g-gate.md`,
  `2026-07-20-phase-j-gate.md`, `2026-07-21-*.md`
- `tools/ci/run_sweep.py`
