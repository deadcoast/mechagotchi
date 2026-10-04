# SLIP Examples

These Stage 0 examples satisfy the authored `../slip.schema.json` contract and
mirror the active valid profile corpus in `data/slips/valid/`.

- `slip_lcd_seed.json`
- `slip_gray_stable.json`
- `slip_amber_social.json`

They are research-facing examples only. The executable fixture corpus remains
under `data/slips/` so generation, workshop, lifecycle, and future package tests
can share one data location.

## 2026-10-04: Current mirror census

Five examples now mirror the five valid fixtures, including the v0.2
`slip_v2_no_shell.json` and new `slip_v2_cleanliness.json`. The new mechanics
example is byte-identical to its executable fixture; prior files are unchanged.
The earlier three-profile list describes the Stage 0 corpus.

## Sources

- `research/decision_records/0063-covenant-mechanics-authorship.md`
- `research/slip/README.md`
- `data/slips/valid/slip_v2_cleanliness.json`
