# Experiment Report: MAP-Elites Comparator Study (T18)

Date: 2026-07-06

## Objective

RUN TWO's unrun keep-gate: MAP-Elites was adopted without its specified
comparison. This lab runs it — GA truncation selection and novelty
search versus the shipped archive, at matched budgets over IDENTICAL
candidate streams (same generated creatures, same order, per seed; only
the selection strategy differs).

## Protocol (Stage 0, honestly scaled)

150 evaluations x 3 rng seeds per comparator; population 32 for
GA/novelty; kNN k=5 descriptor novelty; full engine evaluation per
candidate (generation -> lifecycle episode -> archive scoring). RUN
TWO's 256-population / 50k-evaluation / 10-seed protocol recorded as
the scale-up.

## Verification

RED (module absent) -> GREEN `Ran 4 tests OK` (gate derivation,
matched-budget structure, determinism, artifacts); full lab run:

```txt
                 coverage   qd_score   best     mean
ga_truncation      19.67      18.69    0.9644   0.9489
novelty_search     30.67      28.06    0.9601   0.9145
map_elites         76.00      69.46    0.9644   0.9140
gate: coverage advantage 2.864 (bar 0.25); best-fitness gap 0.0 (bar 0.10)
decision: map_elites_confirmed
```

## Findings

1. **The og claim is measured fact**: at identical budgets on identical
   streams, MAP-Elites preserves ~3.9x the niches of truncation
   selection (76 vs 19.7) and ~2.5x novelty search — while giving up
   ZERO best fitness (gap 0.0: the archive keeps the global best the GA
   keeps, plus 56 more niches of diversity).
2. Novelty search lands between the two, as theory predicts: diversity
   without fitness pressure per niche.
3. GA's mean fitness is highest (0.949) — truncation concentrates on
   the peak; that IS its failure mode for a companion ecosystem, which
   wants many viable species, not one optimum.

## Sources

- `labs/map_elites_archive/archive_comparators.py`, `labs/map_elites_archive/test_archive_comparators.py`
- `data/archives/archive_comparators_stage0.json`
- `.depreciated/02-design.md` (the protocol), `research/decision_records/0011-run-one-run-two-reconciliation.md` (verdict 11)
