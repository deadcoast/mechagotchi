# Local development cycle

Date: 2026-10-04. Decision: DR 0062. Repair baseline: `7a48886`.

## Purpose and operating boundary

Run one cohesive, researched slice through REVIEW -> REPAIR -> ENHANCE ->
POLISH, preserving a restartable record in the actual Mechagotchi repository.
The agent makes the implementation decisions; this command captures scope,
executes verification, and refuses unsupported completion claims. It does not
invent features, spawn another agent, install dependencies, commit, or publish.

Current resume (2026-10-04): Q1-Q5 are locally complete. Read the existing
`q5-consolidation` state and Phase-Q report to resume from verified closure.
A fresh session alone is not a reason to repeat a current passing gate. Do not
replace completed evidence or treat an admitted task as verified. Cycle 28 is
planned in `sunsetted/TODO.md` and
`docs/development/cycle-28-learning-consumer.md`; it must wait for Q5 review.
Q1 eligibility remains separate from Q-table promotion. The latest recovery
delegation reserves commit/sync/push to the user.

## Preregistered workflow contract

1. `mechas develop --start local-workflow` records the repository path, HEAD,
   branch, dirty-file inventory, reviewed contract, and source fingerprints.
   A second start cannot discard unfinished state. Starting the next slice is
   allowed after local completion even if publication is blocked.
2. REVIEW reads CLAUDE.md, ONBOARDING.md, the queue, relevant decision records,
   consumers, and tests. Record the concrete failure/remaining requirement with
   `--checkpoint`. Scope must exist in `docs/development/workflow.json`, with
   a committed or reviewable specification before code and RED tests.
3. `--advance repair --note ...` enters REPAIR. Reproduce the relevant failure,
   repair its cause, preserve controls and historical observations, then run
   `--verify focused`. A failed check returns the phase to REPAIR. The runner
   captures actual output, never treats an empty discovery as a pass, and
   never restores files that a test changed.
4. `--advance enhance --note ...` requires a current passing check. Implement
   only the selected source-informed slice. Carry code, contract, tests,
   experiment report, decision/card, and ledger together. No new module-level
   approval stops are introduced. Scientific adoption gates stay explicit.
5. `--advance polish --note ...` requires another current passing check.
   Review the diff and documentation, then `--verify full` runs every lab,
   package, CLI, game, workshop, and CI-instrument test plus artifact parsing.
   It also checks tracked/untracked source bytes for test side effects and
   runs `git diff --check`. A green local result means local completion only.
6. Each verification gets a new `.development/runs/` directory containing
   stdout, stderr, the sweep summary, and the result. `.development/state.json`
   is replaced atomically. Checkpoints retain phase, fingerprints, and the next
   action. `--status` resumes by reading state and comparing current source;
   stale verification cannot authorize a transition or local completion.
7. Every status keeps native Windows and Ubuntu CI on the published commit
   explicitly **unmet**. This local command cannot mark that gate green.
   The agent must separately observe terminal Actions results for the exact
   pushed SHA when publishing becomes available. No alternate push route is
   part of the workflow.

## Verification and preservation semantics

The focused suite list is explicit per slice. Full means the existing sweep
without quick/filter flags. All dependency groups must be available in the
chosen interpreter; missing dependencies cannot be hidden behind skips.
DR 0034's named platform-dependent zlib skips remain valid observations.

Verification fingerprints include code, data, tests, schemas, configuration,
and untracked source. Markdown outside `data/` and the preregistered `docs/development/` contracts is separately recorded, so
adding measured results to a report does not require another expensive sweep;
polish still reviews that documentation. A current full pass also satisfies a
preceding focused transition, avoiding duplicate executions after evidence is
recorded. Each run compares *all* inventoried
file bytes before and after. Any mutation fails and is left for inspection.
Ignored runtime outputs are outside the source inventory. Nothing is reset,
stashed, or silently restored. Existing dirty files are recorded on start.

One agent/operator owns the cycle at a time. A killed verification leaves its
running record and partial logs; `--status` never calls it passed. Rerun the
verification to recover. No process continues after the invoking command ends.
Commands execute a fixed local sweep, not arbitrary commands from notes/specs.
No background service, credentials, or schedule is installed.

## Commands and resume

Reuse the authoritative repository and its existing Python 3.13.9 environment.
The normal command is `mechas develop`; the exact read-only source resume is:

```powershell
Set-Location -LiteralPath 'C:\Users\ryanf\github\_shelved\mechagotchi'
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --status
```

For Q5, expect `phase=polish`, `full_current=true`, `local_complete=true`, and
`running=null`. Read the latest checkpoint and
`research/experiment_reports/2026-10-04-phase-q-gate.md`; do not reopen or rerun
Q5 when that evidence is current. If a verification is running, inspect its run
logs. If source, data, configuration or a preregistered contract has changed,
follow the recorded phase and reverify as required; never relabel stale evidence.
Report-only updates outside the fingerprint do not require a fresh sweep.

R1 is planned but **not registered** in `docs/development/workflow.json`; no R1
start command is runnable yet. After Q5 review, the next legitimate preparation
is to preregister that existing bounded package producer/consumer parity scope,
its defaults-off controls and suite selection in the same workflow. Registration
and next-task execution are not performed by this Q5 resume example. Do not begin
the next task's RED before committing the previous completed task. This preserves
the AGENTS rule without barring reading or preregistration before that commit.
Commits, sync and pushes remain the user's actions.

`--python` selects an already provisioned interpreter explicitly. The output
always names the actual root, HEAD and branch so an isolated checkout cannot
be mistaken for the user's requested repository. `--status` is read-only.
Failed checks and invalid transitions exit nonzero. Use the existing full
sweep directly for independent diagnosis; its `--suite NAME` filter is local
focused verification, never a full-sweep claim.

## Go/no-go pins before implementation

- A real failing subprocess remains failed with complete diagnostics.
- Tests that mutate source fail even with exit code zero, without restoration.
- Editing executable source makes prior verification stale; report-only
  Markdown updates do not. A failed later check revokes earlier success.
- Incomplete/empty/mismatched sweep results and missing dependencies fail.
- Restarted status reproduces phase/checkpoints and the unmet cloud gate.
- Invalid transitions, missing specs and unfinished-state replacement fail.
- Starting Q2 after local completion preserves the prior cycle's history.

## Sources

- `CLAUDE.md`, `ONBOARDING.md`, `sunsetted/TODO.md`
- `docs/development/workflow.json`, `docs/development/q5-consolidation.md`
- `docs/development/cycle-28-learning-consumer.md`
- `research/decision_records/0061-portable-provenance-and-ci-evidence.md`
- `research/decision_records/0062-local-development-cycle.md`
- `tools/ci/run_sweep.py`, `tools/mechas_cli/src/mechas_cli/development.py`
