# Repo Root Path Anchoring

Date: 2026-07-04

Status: `research_repo_root_path_anchoring_no_package_code`

## Purpose

Fix review finding L-08 from `docs/03-code_review/2026-07-04-code_review.md`:
every lab module and test used cwd-relative `Path("data/...")` /
`Path("research/...")` literals, so suites and module `main()`s only worked
when invoked from the repo root.

## What changed

143 files under `labs/` (workshop_editor 97, grid_genome 20, slip_validator
9, cubff_transducer 5, readability_benchmark 4, asset_pipeline 2, one each in
the remaining labs):

1. Every cwd-relative path literal — module constants, argparse defaults,
   glob roots, keyword defaults, test fixture paths — is anchored on
   `ROOT = Path(__file__).resolve().parents[2]` (the pattern ~64 modules
   already used for `sys.path`). Non-prefix cwd dependencies fixed too:
   `Path(".")` repo-root defaults and `Path("packages").exists()`-style
   repo-state probes.
2. Artifact-recorded path *strings* stay repo-relative: the workshop_editor
   `_portable` helpers and the slip_validator/benchmark/ingest `source_path`
   fields record `path.relative_to(ROOT).as_posix()`, so no machine-specific
   absolute path leaks into committed JSON.
3. Inverse case: `slip_readability_calibration_gate.py` *consumes*
   repo-relative strings recorded in the committed long-horizon artifact;
   those reads are anchored with `ROOT / ...`.

## Result

- Full sweep from the repo root: 455 tests across 12 labs, OK.
- Full sweep from a different cwd with absolute `-s` paths: OK; no stray
  `data/` directories created outside the repo.
- Artifact byte-stability: representative `main()`s re-run for every touched
  lab; `git status -- data/ research/` clean afterward. Skipped known
  non-deterministic or externally-dependent mains
  (`third_party_project_decoder` zip timestamps, `real_snapshot_ingest`
  external checkout).
- Pre-existing (not path-related, left alone): three `data/*/README.md`
  files diverge from what their untouched generator functions emit
  (committed copies were extended by hand or came from a different `--mode`
  run) — the accompanying JSON artifacts regenerate byte-identically.

## Decision

The ROOT-anchoring two-liner is the required pattern for new lab code, and
artifact path strings must be recorded repo-relative
(`relative_to(ROOT).as_posix()`). Recorded in CLAUDE.md. Known residual
hazard, pre-existing: tracked `__pycache__/*.pyc` files mean a non-`-B` test
run dirties the tree.

## Verification

```powershell
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"      # from repo root
cd $env:USERPROFILE; python -B -m unittest discover -s C:\Users\ryanf\github\_new\mechagotchi\labs\grid_genome -p "test_*.py"
python -B labs/slip_validator/slip_validator.py; git status -- data/  # clean
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `labs/` (all twelve lab directories)
- `CLAUDE.md`
