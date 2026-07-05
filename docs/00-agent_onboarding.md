# Agent Onboarding — Mechagotchi

Written 2026-07-04 for the next Fable 5 session. This file orients you; it
does not replace the living documents. **State described here may be stale —
re-verify against `git log` and the gate artifacts before relying on it.**

## 1. What this project is

A grid-based artificial-life companion platform, built research-first. Two
builds (see `docs/01-brainstorming.md`): **mecha_engine** (the creature
engine: genome grids, generation, lifecycle, MAP-Elites archive, provenance)
and **mecha_workshop** (the authoring editor: PNG/APNG/Aseprite
interoperability, SLIP profile authoring). SLIP = Synthetic Learning
Intelligence Profile, the user-authored constraint profile that governs
generation and behavior (`research/glossary.md`).

The defining property of this repo: **the documentation is the deliverable
and the governance.** Nothing is claimed without executable evidence;
nothing is promoted without passing a documented gate.

**Standing identity constraint (2026-07-05, anti-drift — root `README.md`):
this repository is NOT a CLI application.** The `mechas` CLI (`tools/`) is
a supportive layer only. The application is, and remains, the researched
grid-based artificial-life companion engine — the Mechagotchi
Computational Life Engine — inspired by the CuBFF study and source code
behind *Computational Life* (arXiv:2406.19108, local copy at
`assets/pdf/2406.19108v2.pdf`). No supporting surface (CLI, tooling, docs,
UI) may quietly become the project; researched, mathematical, provable
practices govern every addition. MIVIM.dev flagship — the developer's name
is attached; hold every change to the established standards.

## 2. The prime directive

**Seek knowledge locally first, from the documents, for every request.**
The documentation is extensive and current. Working from memory or general
knowledge instead of the repo's own documents causes drift — the one failure
mode this system is designed to prevent.

Authoritative chain, in order:
1. `docs/02-research_plan.md` — the plan (stages, evaluation framework)
2. `research/decision_records/0001-0005+` — ADRs; check for newer ones
3. `research/package_specs/*` — package contracts, gates, the
   **contract traceability matrix** (fixes module promotion order)
4. `research/README.md` — the master traceability ledger (triads)
5. `data/**/**_stage0.json` — gate artifacts = current machine-readable state
6. `research/reports/mechagotchi_research_report_v0_N.md` — consolidated
   waves; read the newest first for "what happened lately"

When docs conflict, the more specific gate/spec wins; decision records win
over plans; and executed artifacts win over prose claims.

## 3. State snapshot (2026-07-05, report v0.10)

- **Research phase complete** (v0.1–v0.5), full 2026-07-04 code-review
  remediation complete (v0.6–v0.8: every H/M/L finding resolved —
  `docs/03-code_review/2026-07-04-code_review.md` is the annotated ledger).
- **Package phase underway** (v0.9+): `packages/mecha_engine` exists
  (src layout, DR 0004). Seven modules promoted with contract tests +
  lab-parity pins: `genome`, `generation`, `lifecycle`, `archive`,
  `provenance` (all 2026-07-04), `repair` (2026-07-05, DR 0006 —
  wound-site learned repair; observability contract: damage events report
  destroyed positions, never tokens, never a template), `runtime`
  (2026-07-05, DR 0008 — `live_cycle` + `evolve`), and `learning`
  (2026-07-05, DR 0009 — feedback micro-switchboard; bounded claim:
  wellbeing at zero survival cost, NO survival claim — survival is
  morphology-decided). Statuses tracked by
  `labs/package_promotion/package_promotion_gate.py`.
- **Tests**: ~13 labs + ~217 package tests + ~15 CLI tests, all green
  (run the sweep for exact counts). Runnable from any cwd (paths are
  ROOT-anchored).
- **Supportive layer**: the `mechas` CLI (tools/, DR 0007) standardizes
  user workflows; the rating loop is `mechas rate --creatures
  [--autoexport] [--reviewer <name>]`. It is NOT the application
  (identity constraint, root README).
- **Deliberately open** (v0.10 manifest `next_sequence`):
  1. **Manual readability calibration — HUMAN ONLY, and DEFERRED by owner
     decision (2026-07-05).** The owner will not provide survey data until
     development is further along (the 21-sample set may change), so this
     is NOT a blocker to chase — do not treat it as the highest-value
     unblock. The pipeline stays ready and verified:
     `mechas rate --creatures --autoexport` runs the whole loop (63 rows =
     21 samples × 3 reviewers). It still gates the evaluation module,
     descriptor threshold locks, and profile-weighted evolution claims —
     those stay honestly blocked until real data arrives. Never fabricate.
  2. **Learning module DR (0009 candidate) is now proposable** — the
     stress survival regime (2026-07-05) broke the saturation:
     `--mode evolution --regime stress_probe` runs episodes on the
     archive's contracted morphology probe (10/48 deaths, survival
     0.79-0.90, archive 25 niches). The learning claim to beat is the
     frozen switchboard's measured survival under this regime — a
     falsifiable bar at last. Other engine follow-ups: longer-horizon
     selection studies (incl. fitness-weighted vs uniform parenting as an
     explicit comparison), lineage counter accumulation through repair
     (parity-reviewed), package `runtime.evolve` regime parameter once
     lab evidence settles.
  3. Learning module — PROMOTED (DR 0009, 2026-07-05) with the bounded
     wellbeing claim. Future survival-relevant learners need new evidence
     through the stress learning benchmark harness. (The owner's only
     standing deferral remains the manual readability survey data; never
     extend it to anything else — owner correction, 2026-07-05.)
  4. The `mecha_workshop` build track: SLICES 1-4 SHIPPED (2026-07-05,
     DR 0010; build order owner-approved). `mechas workshop --editor` =
     grid editor (live engine validation); `--slip` = SLIP profile
     creator (Stage 0 authority live, authored profiles join the
     editor's chips); `--preview` = engine-truth preview (render
     packets verbatim, runtime.live_cycle day-in-the-life,
     generation-module offspring; alignment errors ARE the preview on
     mismatch; read-only). Slice 4 (complete): the editor's SHARE
     panel — self-contained PNG and Aseprite exports (embedded semantic
     sidecar, engine-strict, profile-bound), animated APNG, spritesheet
     pair (sheet PNG + sidecar JSON), and imports of all three formats
     through each codec's own integrity checks. Strict saves under
     data/workshop/. Charter: `docs/workshop/mecha-workshop-design.md`.
     Next: slice 5 (genome inspector + lineage browser) — owner said
     wait for the go. Windows note: ports are OS-reserved in shifting ranges —
     servers default to port 0 and announce their URL.
  5. mechas CLI roadmap (`docs/cli/mechas-cli.md`) — supportive layer
     only; never outranks engine work.

## 4. The document development format (non-negotiable)

Documents are living files: **every code or data change updates its
documents in the same change.**

- **Triad convention**: each finding = dated experiment report
  (`research/experiment_reports/YYYY-MM-DD-kebab-slug.md`) + algorithm
  card/spec (`snake_case`, same stem) + lab code + `data/<lab>/<slug>_stage0.json`
  artifact — all ledgered in `research/README.md`.
- Experiment reports carry **RED/GREEN verification blocks** with exact
  commands and pasted output, and a `## Sources` footer of repo paths.
- Artifacts carry `status` / `closed_states` / `blocked_states` /
  `decision`. Keep blocked states explicit; never silently drop one.
- Consolidated reports (v0_N + manifest) group waves; they link, never
  replace. Every manifest path must resolve — verify before writing.
- Completion checklist (also in CLAUDE.md): run the changed lab's tests →
  validate changed JSON with `python -m json.tool` → update triad docs →
  sweep for stale blocker wording.

## 5. Honesty norms (learned and enforced this session)

- **Gates derive from evidence, never constants.** A probe that cannot fail
  is a bug (see M-09's history). If a gate would flip on weak evidence,
  harden its derivation instead.
- **Record negative results.** "The blocker stands, measured at X vs bar Y"
  and "the flagged mismatch was latent — numbers unchanged" are first-class
  outcomes (see the M-12 and repair-bar reports).
- **Never pin environment observations in tests** (H-01's lesson): assert
  the policy/decision; record availability (`jsonschema_available` etc.) as
  per-run observations.
- **Parity before promotion.** Package ports keep lab semantics verbatim
  (error strings included) and pin it with a lab-side parity test over the
  full fixture corpora. Spec wins over raw port only where the gate says so
  — and then you document the divergence.
- **Regenerate artifacts you invalidate**, and explain each delta in the
  commit. Revert pure-noise regenerations (zip timestamps in
  `third_party_project_decoder` are known-non-deterministic).

## 6. Working cadence that worked

- Work in **batches mapped to finding/gate IDs**; one commit per batch with
  a message naming the IDs, evidence, and doc updates. Push after each.
- **Delegate heavy implementation to sub-agents with spec-first briefs**
  ("read these spec files FIRST; they override this brief"), keep
  verification, triad docs, gate reruns, and commits in the orchestrator.
  Give agents disjoint file zones; never let two agents share a lab.
- Sub-agents must report deviations and honest failures, not paper over
  them — the best finds this session (a wrong-pixels bug, a regression from
  a concurrent commit) came from agents empowered to say "this is broken".
- Rerun the **full 12-lab sweep + package suite** before every commit:
  suites are fast (<30 s total).

## 7. Environment and commands

```powershell
# One lab suite (stdlib unittest; no pytest; run from anywhere)
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
# Package suite
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
# Regenerate a lab's artifacts (argparse defaults point into data/)
python -B labs/package_promotion/package_promotion_gate.py
# Validate changed JSON
python -m json.tool data/<path>.json
```

- `python` resolves to system CPython 3.14; user site-packages leak into it
  (hence the H-01 rule). Lab extras (`pydantic`, `jsonschema`) are declared
  in the root `pyproject.toml` `lab` dependency group (DR 0005);
  `uv sync --group lab` provisions. All five package modules are
  stdlib-only; the **package** dependency policy is deliberately blocked.
- Always `python -B` — `__pycache__` dirs are tracked (pre-existing hazard).
- Git: LF→CRLF warnings on commit are normal noise. Commit messages end
  with the Claude co-author line. Push after committing (standing user
  instruction: keep docs committed and pushed).
- Package tests locate `mecha_engine` via a subprocess with PYTHONPATH at
  `packages/mecha_engine/src` — no `sys.path` text may appear anywhere in
  the package tree (the boundary scan greps for it). Package code/tests
  import `mecha_engine`, never `labs`; labs may import the package (that's
  how parity tests work).

## 8. Traps

- The grid validator enforces the full schema surface (64-char `grid_id`
  cap included) — generated IDs must stay schema-conformant (a
  multigeneration offspring-id overflow once broke this; ids are now
  hash-compressed).
- `descriptor_bin_spread` must be ≥ 2 before claiming a new archive axis
  contributes niches.
- The lifecycle sim is bistable (stress ≤0.94 stabilizes, ≥0.95 collapses
  ~tick 12–14) — survival variance needs the morphology stress probe, not
  longer horizons.
- The user's explicit authorization is required for scope-expanding steps
  the decision records gate (creating deferred package targets, license
  decisions, publishing). When a doc says "only when the user explicitly
  starts X" — ask, with a recommendation.

## 9. First moves for a fresh session

1. `git log --oneline -15` — what happened since this file was written.
2. Read the newest `research/reports/mechagotchi_research_report_v0_N.md`
   and its manifest's `next_sequence`.
3. `python -B labs/package_promotion/package_promotion_gate.py` — current
   candidate statuses are the truth, not this file.
4. Check whether
   `data/readability/slip_readability_calibration_ratings.csv` exists —
   calibration is deferred by owner decision, so its absence is expected;
   if it EXISTS with real rows, the owner resumed calibration: run
   `mechas rate --status` and the calibration gate.
5. Then continue whatever `next_sequence` names, batch-by-batch, docs
   first. Engine work outranks supportive-layer work (identity
   constraint).
