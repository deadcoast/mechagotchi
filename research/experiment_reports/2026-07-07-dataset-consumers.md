# Experiment Report: The Datasets Become ML Fuel (E3) — Two Consumers, Two Findings

Date: 2026-07-07

## WHY

R6 delivered `mechaseed_200`, `mutationbench_5000`, and
`replay_100k_ticks` as "the ML tracks' fuel" — and nothing consumed
them. E3 wires the first two real consumers, each answering a question
the corpora were built for, with the verdicts being the numbers.

## WHAT

`labs/datasets/dataset_consumers.py` (+ `test_dataset_consumers.py`, 10
tests; artifact `data/datasets/dataset_consumers_stage0.json`).

**(a) Learned readability on REAL mutations.** R3's model was trained
on physics-verified SYNTHETIC degradation pairs; does it rank REAL
mutation outcomes? Method: R3's own admission rule transplanted — each
`mutationbench_5000` case is regenerated deterministically (every one
of 5,000 candidates matched its stored `grid_signature` — dataset
integrity re-proven in passing) and physics-labeled from the four
verified metrics (palette contrast, organ detectability, inverse
component count, anchor coverage): *degraded* only when monotone-down
with at least one strict move, mirrored for *improved*, else honestly
*unlabeled*.

**(b) Behaviour evaluation from stored ticks.** The `replay_100k_ticks`
corpus consumed AS DATA — per-policy outcomes streamed from the gzip
with zero simulation, using the ENGINE-FAITHFUL episode statistic
(`run_episode`'s own rule: need balance over the full requested horizon
with post-death ticks as 0.0).

## FINDING 1 — R3 generalizes to real mutations: 0.94

On 2,880 physics-labeled REAL pairs (57.6% coverage of 5,000 — real
mutations are rarely monotone; the 2,120 unlabeled are reported, not
hidden): **pairwise accuracy 0.9406**, zero score ties. By direction:
**0.983** on degraded pairs (1,973) vs **0.849** on improved (907) — the
model is better at recognizing damage than improvement, exactly what
training exclusively on degradations predicts, and honestly recorded.
The synthetic-pairs model carries to the real mutation distribution.

## FINDING 2 — survivorship bias, caught by the engine's own statistic

The first pass ranked policies by mean balance over LIVED ticks and got
**switchboard LAST**. The engine-faithful statistic flips it — and the
per-policy detail shows why the naive number lies:

| Policy | Episode need balance (engine rule) | Lived-tick mean | Survival | Mean ticks |
| --- | --- | --- | --- | --- |
| switchboard | **0.789** | 0.789 | **1.00** | 72.0 |
| random | 0.416 | 0.811 | 0.16 | 37.0 |
| idle | 0.121 | 0.792 | 0.00 | 11.0 |

Idle creatures ALL starve by tick ~11 — but their few lived ticks are
early, well-balanced ones, so the naive mean looks fine (0.792).
`run_episode`'s docstring says the quiet part: "early death can never
inflate the score by shortening the horizon." Reconstructed exactly
(sum of balances / requested horizon per episode), the switchboard
doesn't just lead — it is the ONLY policy that keeps every creature
alive across all 100,004 stored ticks. Both statistics are reported in
the artifact; the crafted-corpus unit test pins the padding math with
hand-computed expectations so the bias can never silently return.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/datasets -p "test_*.py"
Ran 22 tests in 2.131s
OK    # physics labeling falsifiable both ways + unlabeled-not-guessed;
      # signature verification; determinism; the survivorship-bias pin
      # with hand-computed expectations; full-scale artifact shape

PS> python -B labs/datasets/dataset_consumers.py
{
  "pairwise_accuracy": 0.940625, "labeled": 2880, "coverage": 0.576,
  "signature_mismatches": 0,
  "replay_ranking": ["switchboard", "random", "idle"],
  "switchboard_first": true
}
```

## Decision

`datasets_are_live_fuel` / adopt — E3 developed to its description: the
fuel burns, and both consumers returned real findings (the model
generalizes; the corpus independently confirms the switchboard's value
at scale once the honest statistic is used). If the 0.849
improved-direction accuracy is ever judged low, the bench's
physics-labeled pairs are a ready fine-tuning corpus for the R3
trainer — recorded as the natural follow-up, not queued.

## Sources

- `research/experiment_reports/2026-07-07-dataset-program.md` (R6, the fuel)
- `research/decision_records/0019-learned-readability.md` (R3, the model and the admission rule)
- `labs/datasets/dataset_consumers.py` (+ `test_dataset_consumers.py`)
- `data/datasets/dataset_consumers_stage0.json`
- `data/datasets/mutationbench_5000/mutationbench_5000.jsonl`
- `data/datasets/replay_100k_ticks/replay_100k_ticks.jsonl.gz`
- `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py` (the horizon rule)
