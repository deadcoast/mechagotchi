# CI reproducibility repair specification

Date: 2026-10-04. Baseline: `19cc73d31f0781d5ab82dcdb625e76ade47d628e`.

## Problem and scope

Sweep #32 fails the same five suites on Windows and Ubuntu. The source
provenance ledger records mixed working-tree line endings and native path
ordering; a fresh checkout cannot reproduce it. Four CLI help assertions
mistake terminal styling for missing options. The sweep discards subprocess
tracebacks. Several SLIP writer tests overwrite committed observations.

This is one integrated repair. Engine behavior, scientific thresholds,
historical findings, Q-table promotion and the default covenant stay governed
by their existing records. No dependency upgrade is part of this repair.

## Decisions before implementation

1. Preserve the four original provenance artifacts under
   `data/asset_provenance/baselines/stage0-windows/`. The current baseline is
   explicitly restated on 2026-10-04, with raw SHA-256 bytes unchanged as the
   integrity contract. Pin the three included text-asset locations to LF in
   `.gitattributes`. Define directory ordering as case-sensitive lexical
   ordering of relative POSIX strings. Record old/new digests and the reason
   for each delta. Do not silently normalize arbitrary inputs while hashing.
2. Mirror the corrected algorithm in lab and package, and replace the native
   path ordering in the contract oracle. Add a fixed independently assembled
   mixed-case/nested filename corpus; retain mutation and stale-hash controls.
3. Decode captured CLI ANSI output before checking semantic text. Exercise
   help in fresh processes under both plain and GitHub-style terminal settings.
   Preserve every flag and exit-code assertion.
4. Retain stdout, stderr, counts, status, duration and timeout diagnostics per
   suite; emit failing traces and flushed progress. Write a machine-readable
   summary and interpreter/dependency provenance. Upload logs after failures.
   Test nonzero exit propagation and timeout retention with real subprocesses.
5. Give the three SLIP artifact writers explicit output paths with current
   defaults preserved for deliberate regeneration. Test writes in temporary
   directories and prove the committed targets remain byte-identical.

## Acceptance

- RED evidence comes from the isolated baseline reproduction and new regression
  pins before their implementation; no deliberately failing test is published.
- All focused tests and the full sweep pass with all dependency groups installed.
- The sweep leaves tracked source/evidence unchanged. New test logs are ignored.
- Fresh Windows and native Ubuntu GitHub jobs pass on the exact pushed commit.
  Local LF reproduction is supporting evidence, never a Linux pass claim.
- Original provenance records remain available, correction documents explain
  every digest delta, and no scientific acceptance threshold changes.
- Source and remote branch identities are checked before publishing; local
  synchronization preserves any work that appeared during the repair.

## Sources

- `.github/workflows/ci.yml`, `tools/ci/run_sweep.py`
- `labs/asset_pipeline/provenance_ledger.py`
- `packages/mecha_engine/src/mecha_engine/provenance/hashing.py`
- `tools/mechas_cli/tests/test_cli_surface.py`, `labs/slip_validator/`
- `research/decision_records/0034-ci-and-zlib-conditional-pins.md`
- https://github.com/deadcoast/mechagotchi/actions/runs/31311673414
- https://git-scm.com/docs/gitattributes
- https://docs.python.org/3/library/pathlib.html#general-properties
- https://rich.readthedocs.io/en/latest/console.html#environment-variables
