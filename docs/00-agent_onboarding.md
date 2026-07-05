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

## 3. State snapshot (2026-07-04, report v0.9, commit `104cc67`)

- **Research phase complete** (v0.1–v0.5), full 2026-07-04 code-review
  remediation complete (v0.6–v0.8: every H/M/L finding resolved —
  `docs/03-code_review/2026-07-04-code_review.md` is the annotated ledger).
- **Package phase underway** (v0.9): `packages/mecha_engine` exists
  (src layout, DR 0004). Six modules promoted with contract tests +
  lab-parity pins: `genome`, `generation`, `lifecycle`, `archive`,
  `provenance` (all 2026-07-04), and `repair` (2026-07-05, DR 0006 —
  wound-site learned repair; observability contract: damage events report
  destroyed positions, never tokens, never a template). Statuses tracked
  by `labs/package_promotion/package_promotion_gate.py`.
- **Tests**: ~520 lab tests across 12 labs + ~163 package tests, all green.
  Runnable from any cwd (paths are ROOT-anchored).
- **Deliberately open** (v0.9 manifest `next_sequence`):
  1. **Manual readability calibration — HUMAN ONLY.** 63 reviewer rows
     (21 samples × 3 reviewers), packet at
     `data/readability/slip_readability_calibration_reviewer_packet.md`,
     filled CSV goes to `data/readability/manual_ratings.csv`. Blocks the
     evaluation module, final descriptor threshold locks, and any
     profile-weighted evolution claim. Ask the user; do not fabricate.
  2. Learned NCA repair — CLOSED. The wound-site arm (damage-event
     positions observed, tokens predicted, no template) meets all three
     0.9 bars (0.938462/0.938462/1.0 with the validity guard); the blind
     arm stays below the bar (0.8625, recorded honestly);
     retrieval-context conditioning was ablated and rejected. The user
     authorized DR 0006 (2026-07-05) and `repair` is now the sixth
     promoted package module with contract tests + a lab parity pin. See
     `research/experiment_reports/2026-07-05-mecha-engine-repair-promotion.md`.
  3. Learning module target: candidate is design-ready; creating the
     deferred `learning` package target is a scope decision — write a
     decision record first.
  4. The `mecha_workshop` build track (research done, no build).

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
4. Check whether `data/readability/manual_ratings.csv` exists — if the user
   supplied the 63 rows, running the intake lab
   (`labs/readability_benchmark/manual_rating_intake.py`) is almost
   certainly the highest-value next step.
5. Then continue whatever `next_sequence` names, batch-by-batch, docs first.
