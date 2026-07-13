# Experiment Report: CI + Reproducibility — the Sweep Leaves This Machine (Cycle 17 · SHARED · G1)

Date: 2026-07-12

## WHY

Phase G's charter: "CI + reproducibility." The full sweep (19 lab
suites + package + workshop + CLI + game) has been the standing
verification since cycle 09, but it lived in session discipline and
one machine's interpreter quirks. One measured sensitivity blocked
honest portability: the foreign-fixture BYTE pins fail 10 subtests
under any classic-zlib interpreter (recorded in the F1 report) —
because deflate output is zlib-build-specific, not because anything
is wrong.

## WHAT

**DR 0034** separates what the byte pins protect (regression of the
spec-writer's exact output UNDER THE GENERATING BUILD) from what
protects correctness under EVERY build (the committed files'
recorded-hash integrity; every fixture × decoder expectation over
freshly built fixtures). The two byte pins became build-conditional —
they run under the fixture-generating `zlib-ng` family and SKIP with
a named reason citing the DR elsewhere (an H-01 environment
observation, never a pinned assumption); everything content-level
stays unconditional. The corpus README now records its build
provenance, and `FIXTURE_ZLIB_BUILD` is the single declared constant
to update with any future regeneration.

**Measured — the conversion of yesterday's honest failure:**

```text
system CPython 3.14 (zlib-ng):  Ran 40 tests ... OK            (pins RUN)
uv CPython 3.13 (classic zlib): Ran 40 tests ... OK (skipped=2) (pins SKIP, named)
# before this change the second line read: FAILED (failures=10)
```

**`tools/ci/run_sweep.py`** — the sweep as ONE stdlib runner, the
same locally and in CI: lab discovery, the four fixed suites, and
JSON validation over every committed data artifact; pygame suites
headless via SDL dummy; `--quick` (local convenience) skips the
~2-minute workshop suite. **Verified locally under the classic-zlib
venv interpreter — the strongest portability check available on this
machine**: 19 labs + package + CLI + game green, `workshop_editor OK
(skipped=2)` visible in-line, **2208 JSON artifacts valid**, SWEEP
GREEN. The full (non-quick) run including the workshop suite is
green in the same configuration.

**`.github/workflows/ci.yml`** — two runners on purpose:
`windows-latest` + CPython 3.14 (the fixture-generating build family;
the pins RUN) and `ubuntu-latest` (classic zlib; the skip path is
exercised on every push). The venv is built FROM the runner's set-up
interpreter (`UV_PYTHON`), never uv's managed build, and a provenance
step prints the run's `zlib.ZLIB_RUNTIME_VERSION` so every log states
which regime it verified. Concurrency-deduped, 30-minute timeout.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/workshop_editor -p "test_foreign_fixture_conformance*.py"
Ran 40 tests ... OK                # zlib-ng: the pins run
PS> uv run python -B -m unittest discover -s labs/workshop_editor -p "test_foreign_fixture_conformance*.py"
Ran 40 tests ... OK (skipped=2)    # classic zlib: named skips (was FAILED f=10)
PS> uv run python -B tools/ci/run_sweep.py
# 19 labs OK · package OK · cli OK · game OK · workshop OK ·
# 2208 JSON artifacts valid · SWEEP GREEN
```

## HONEST REMAINDER

1. **The first green CLOUD run awaits a push** — commits are never
   pushed unasked (standing law). The workflow is authored and the
   sweep script it calls is verified locally; the YAML itself cannot
   be executed on this machine.
2. **The windows-runner zlib expectation is an informed prediction,
   not a measurement** — setup-python's Windows 3.14 is expected to
   carry zlib-ng like the local build family; the provenance step
   prints the truth on the first run, and the conditional pins are
   correct under EITHER outcome.
3. **The evidence harness is not a CI job yet** — session-scale regen
   is minutes of evolve runs; wiring it as a scheduled (not per-push)
   job is a G6 alpha-packet decision.

## Sources

- `research/decision_records/0034-ci-and-zlib-conditional-pins.md` (this rung's authority)
- `research/experiment_reports/2026-07-12-front-end-client-skeleton.md` (the recorded sensitivity)
- `labs/workshop_editor/test_foreign_fixture_conformance.py`, `data/foreign_fixtures/README.md` (provenance)
- `tools/ci/run_sweep.py`, `.github/workflows/ci.yml`
- `audits/TODO.md` (cycle 17 G1)
