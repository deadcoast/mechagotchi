# Experiment Report: The og Dataset Program Completed (R6) — The ML Tracks' Fuel

Date: 2026-07-07

## WHY

R6 (=T11, carried from cycle 01): the og research plan's dataset table
named the corpora the ML tracks need; `mechaseed_50`, the 200-case
invalid corpus, `slip_zoo_100`, and `animstate_300` shipped earlier —
`mechaseed_200`, `mutationbench_5000`, and `replay_100k_ticks` remained.
Each must exist as a named, versioned dataset with a README and a ledger
entry, built deterministically from engine surfaces so the data is
engine truth, not synthesis.

## WHAT

`labs/datasets/dataset_program.py` (+ 12 tests) builds all three under
one generation config — `slip_corpus_r6`, the fixture profile widened to
admit the WHOLE seed corpus (all five palettes, full mass range;
authority-valid and alignment-verified against all 50 seeds by test) so
the body-plan datasets keep the corpus's diversity instead of one
covenant's slice. The profile ships alongside the datasets.

| Dataset | Contents | Format | Delivered |
| --- | --- | --- | --- |
| `mechaseed_200` | the 50 seeds + 150 engine-generated variants, curated by `validate_grid` + `grid_signature` novelty (deterministic seed-offset walk) | JSON (the `animstate_300` precedent) | 200/200, every entry valid, signatures unique, variants reproducible from their recorded `(parent, rng_seed)` |
| `mutationbench_5000` | 5,000 offspring cases (50 parents x 100 fixed rng seeds): config + outcome measurements (validity, alignment, lineage generation, cell diffs, mutation events) + the candidate's `grid_signature` | JSONL | 5,000 rows; candidates reproducible case-by-case, signature-verified (5,000 grids of truth without 5,000 stored grids) |
| `replay_100k_ticks` | per-tick lifecycle logs — the episode's own history entries VERBATIM — across 50 creatures x 3 policies x deterministic rng rounds | gzipped JSONL (stdlib `gzip`, `mtime=0` for byte determinism) + uncompressed sample | 100,004 ticks; contiguous per episode, balance-bounded, gzip round-trip pinned |

Every dataset file is sha256-checksummed in the stage-0 manifest
(`data/datasets/dataset_program_stage0.json`), so drift is detectable.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/datasets -p "test_*.py"
Ran 12 tests in 0.322s
OK

PS> python -B labs/datasets/dataset_program.py
{
  "artifact_id": "dataset_program_stage0",
  "decision": "dataset_program_complete",
  "mechaseed_200": 200,
  "mutationbench_5000": 5000,
  "replay_ticks": 100004,
  ...
}
```

Key falsifiable pins: a sampled `mutationbench` row's candidate is
regenerated from its config and must match its stored signature and
validity; a sampled `mechaseed` variant regenerates equal to its stored
grid; the replay gzip decompresses to exactly the built rows; both
builders are deterministic (built twice, equal).

## Honest scope

- The og table's PNG-render companion for `mechaseed_200` is deferred
  with a recorded blocked state (`mechaseed_200_png_renders_deferred_no_
  consumer`): the workshop export codecs produce renders on demand, and
  no consumer for 200 committed PNGs exists yet.
- `replay_100k_ticks` logs lifecycle ticks (the og "tick logs +
  interaction scripts"); full render-frame replays remain single-life
  artifacts (R5's recorder) — framing 100k ticks is a consumer decision,
  not a dataset obligation.

## Decision

`dataset_program_complete` / adopt as dataset evidence (R6 developed to
its description — the og dataset table is now fully delivered). Next:
R7 (grid-schema animation/species fields), the cycle's last open task.

## Sources

- `labs/datasets/dataset_program.py`
- `labs/datasets/test_dataset_program.py`
- `data/datasets/dataset_program_stage0.json`
- `data/datasets/slip_corpus_r6.json`
- `data/datasets/mechaseed_200/` (+ README)
- `data/datasets/mutationbench_5000/` (+ README)
- `data/datasets/replay_100k_ticks/` (+ README)
- `docs/project-research/deep-research/01/deep-research.md` (the og dataset table)
- `audits/complete/01/audit-devspec.md` (the dataset-status audit)
- `research/decision_records/0017-recalibration-engine-game-duality.md` (R6)
