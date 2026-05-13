# Experiment Report: Manual Readability Reviewer Packet

Date: 2026-05-12

## Objective

Continue the readability research path by preparing the human-review collection
packet required to unblock proxy calibration, without fabricating reviewer data.

## Source Basis

Internal sources:

- `data/readability/manual_rating_protocol.md`
- `data/readability/manual_rating_template.csv`
- `data/readability/manual_readability_rating_intake_stage0.json`
- `data/readability/manual_rating_recheck_stage0.json`
- `research/source_notes/2026-05-12-manual-readability-rating-source-review.md`

External sources:

- https://arxiv.org/abs/2107.02457
- https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-016-0200-9

## Scope

Included:

- reviewer-facing packet
- collection acceptance gate
- expected completed-row count
- exact intake rerun command
- explicit blocked status while `manual_ratings.csv` is absent

Not included:

- fabricated ratings
- proxy-weight calibration
- reviewer UI
- package promotion

## Method

The existing Stage 0 template contains 30 samples:

| Source | Rows |
| --- | ---: |
| `seed_holdout` | 10 |
| `constrained_holdout` | 10 |
| `markov_holdout` | 10 |

The collection gate requires at least three reviewers. Each reviewer fills all
30 sample rows, producing 90 expected completed rows in
`data/readability/manual_ratings.csv`.

The expected CSV header remains:

```txt
sample_id,grid_id,source,reviewer_id,silhouette,organ_clarity,palette_contrast,animation_readiness,companion_appeal,notes
```

## Outputs

Reviewer packet:

- `data/readability/manual_rating_reviewer_packet.md`

Machine-readable collection gate:

- `data/readability/manual_rating_collection_gate_stage0.json`

Status:

- `reviewer_packet_prepared_human_ratings_absent`

## Findings

The project now has enough operational detail to hand the rating packet to
reviewers without changing the benchmark. The blocker remains real: no completed
`data/readability/manual_ratings.csv` file exists, so human calibration still
cannot proceed.

## Verification

Verification commands for this research artifact:

```powershell
python -m json.tool .\data\readability\manual_rating_collection_gate_stage0.json > $null
Test-Path .\data\readability\manual_ratings.csv
python -B .\labs\readability_benchmark\test_manual_rating_intake.py
rg -n "manual_rating_reviewer_packet|manual_rating_collection_gate_stage0|reviewer_packet_prepared_human_ratings_absent" research data
git diff --check
```

## Decision

Keep readability calibration blocked until real reviewer rows exist. The next
action is to collect at least three complete reviewer passes into
`data/readability/manual_ratings.csv` and rerun the manual rating intake.

