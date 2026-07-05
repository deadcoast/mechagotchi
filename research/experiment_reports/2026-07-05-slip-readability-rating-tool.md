# Experiment Report: SLIP Readability Rating Tool

Date: 2026-07-05

## Objective

The manual readability calibration (the project's highest-value open
blocker) requires three humans to rate 21 sample grids on five 1–5
questions — but the samples existed only as grid-genome JSON, so the
protocol was not actually executable by a reviewer: there was nothing to
look at. This lab closes the tooling gap without touching the calibration
evidence itself.

## What changed

- `labs/readability_benchmark/rating_tool_builder.py` generates
  `data/readability/slip_readability_calibration_rating_tool.html`: a
  self-contained page (no network, no dependencies) that renders each of
  the 21 samples as pixel art on its native palette, collects the five
  ratings per sample per reviewer, supports the three independent
  reviewer passes (progress persisted in the browser, duplicate reviewer
  ids rejected), and exports a CSV whose header matches the reviewer
  template byte-for-byte, destined for
  `data/readability/slip_readability_calibration_ratings.csv`.
- The sample payload comes from the calibration gate's own loader:
  `build_slip_long_horizon_readability_benchmark` gained an optional
  `grid_collector` parameter (default `None`, report unchanged) so the
  tool renders exactly the grid set the gate scores, in template order.
- Bias controls are part of the contract and pinned by tests: the payload
  contains no proxy readability scores (the protocol requires rating
  before seeing them) and no role/organ/anchor annotations — reviewers
  judge raw pixels only.
- The gate's generated reviewer packet and folder README now point
  reviewers at the tool (template kept as the canonical column contract).

## Verification

RED (test file for a module that does not exist):

```powershell
python -B -m unittest discover -s labs/readability_benchmark -p "test_rating_tool_builder.py"
```

```txt
Ran 1 test in 0.000s
FAILED (errors=1)
```

RED (packet must reference the tool):

```txt
FAIL: test_write_artifacts_creates_report_template_packet_and_readme (...)
Ran 6 tests in 0.065s
FAILED (failures=1)
```

GREEN (full lab suite after implementation):

```powershell
python -B -m unittest discover -s labs/readability_benchmark -p "test_*.py"
```

```txt
Ran 20 tests in 0.140s
OK
```

Lab commands:

```powershell
python -B .\labs\readability_benchmark\rating_tool_builder.py
# {"sample_count": 21, "tool_file": "data/readability/slip_readability_calibration_rating_tool.html", ...}
python -B .\labs\readability_benchmark\slip_readability_calibration_gate.py
# regenerates packet/README; gate stage0 byte-identical (ratings_collected still false)
```

## Findings

1. Tests pin: sample order equals the reviewer template CSV row order; all
   21 samples render payloads with cells and palettes; the exported CSV
   header equals the template header; the payload leaks no proxy scores;
   generation is deterministic.
2. The calibration state is unchanged and honest: 0 of 63 rows collected,
   `manual_readability_calibration_ready: false`. This lab makes the
   protocol executable by humans; it does not and must not substitute for
   them.

## Decision

Status: `rating_tool_available`. The blocker
`manual_readability_calibration_absent` stands until three reviewer passes
produce `data/readability/slip_readability_calibration_ratings.csv` and
the calibration gate accepts it.

## Sources

- `labs/readability_benchmark/rating_tool_builder.py`
- `labs/readability_benchmark/test_rating_tool_builder.py`
- `labs/readability_benchmark/slip_readability_calibration_gate.py`
- `labs/readability_benchmark/test_slip_readability_calibration_gate.py`
- `data/readability/slip_readability_calibration_rating_tool.html`
- `data/readability/slip_readability_rating_tool_stage0.json`
- `data/readability/slip_readability_calibration_reviewer_packet.md`
- `data/readability/slip_readability_calibration_template.csv`
- `data/readability/slip_readability_calibration_README.md`
