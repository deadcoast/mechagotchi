# Decision Record 0062: Resumable local development with explicit publication evidence

Date: 2026-10-04

## Status and context

Adopt the local operating instrument after its regression and full-sweep gates.
The integrated DR 0061 repair is present in the requested repository at
`7a48886`. Publication is still blocked by the execution approval layer; no
native cloud pass has been observed for that commit. Independent local work
must remain useful and verifiable while that external gate is unmet.

The prior failure exposed three workflow hazards: a local result mistaken for
portable CI, tests changing committed observations, and a tested isolated
checkout mistaken for the user's actual directory. A generic feature-generation
loop addresses none of those hazards. The next work already exists: cycle 27
Q2-Q5, with Q2's validators/lifecycle/game persistence as one cohesive slice.

## Decision

Provide `mechas develop` as DR 0007's operational front door. The agent reads
the source, makes the decisions and implements the slice; the command records
REVIEW/REPAIR/ENHANCE/POLISH transitions, runs the existing sweep, and verifies
the evidence that justifies each transition. Specs and suite selections live
in `docs/development/`, not in an invented autonomous feature queue.

Store runtime state and per-run logs only in ignored `.development/`. Write
state atomically; preserve a completed cycle before starting another. Explicit
root/HEAD/branch output and before/after byte inventories prevent accidental
workspace substitution and evidence mutations from being hidden. A failed
later check invalidates earlier verification, even if focused recovery passes.
Code/data/schema/config changes make success stale. Research report Markdown
may record results without requiring duplicate expensive tests; preregistered
development contracts and data Markdown remain in the verification fingerprint.

The full sweep must report its entire expected suite set, real discovered
tests, complete status, successful JSON parsing and all dependency groups.
Focused selection is a new additive `--suite NAME` runner option and is labeled
in the summary. It never becomes a full-sweep claim. Test side effects are
reported, not restored. Timeout/interruption retains partial output and stops
only the process tree this invocation owns.

Native Windows plus Ubuntu CI on the published SHA is a separate, always-unmet
field in this local instrument. No local argument can claim it passed. The
agent must separately observe the external evidence before publication is
accepted. No push, credential, schedule, daemon or agent launcher is added.

## Consequences and limits

This is a reproducible active-agent workflow, not unattended model execution.
One operator owns a cycle at a time; concurrent invocations are unsupported.
A hard process kill can leave partial logs/running state; inspect and rerun the
verification. Specs and runtime records are reviewable evidence, not a security
boundary against a malicious person who edits both source and state.

Q2 is preregistered and ready for a resumed REVIEW. The new workflow does not
claim its mechanics feature implemented or mark Q2-Q5 complete. Historical
scientific results and default behavior are unchanged by this operating slice.

## Sources

- `docs/development/local-cycle.md`, `docs/development/q2-mechanics-rung.md`
- `docs/development/workflow.json`, `AGENTS.md`, `sunsetted/TODO.md`
- `tools/mechas_cli/src/mechas_cli/development.py`
- `tools/mechas_cli/src/mechas_cli/workflows/develop.py`
- `tools/mechas_cli/tests/test_development.py`, `tools/ci/run_sweep.py`
- `research/algorithm_cards/local_development_cycle.md`
- `research/experiment_reports/2026-10-04-local-development-cycle.md`
- `data/development/local_development_cycle_stage0.json`
