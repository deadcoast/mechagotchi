# Experiment Report: Lineage Tracking Baseline

Date: 2026-05-12

## Objective

Continue the proposed research sequence by adding lineage tracking after the
first MAP-Elites archive baseline.

## Source Basis

Digital-evolution systems such as Avida emphasize controlled experimental
settings, measurement tools, and post-processing of evolutionary data. For
Mechagotchi, that means lineage records must be generated alongside archive
results rather than reconstructed later from screenshots or summaries.

Sources:

- https://pubmed.ncbi.nlm.nih.gov/15107231/
- https://www.nature.com/articles/s41597-023-02514-3

## Scope

Included:

- parent identity in constrained generated children
- lineage graph builder under `labs/grid_genome/lineage_tracker.py`
- generation, ancestor, mutation-event, and elite-membership records
- lineage artifact at `data/lineage/lineage_stage0.json`
- 200 lineage-aware generated candidates under
  `data/generated_grids/lineage_constrained/`

Not included:

- multi-generation reproduction
- lifecycle simulation
- survival age
- death/reset cause
- mutation survival rate
- archive emitter loop

## Verification

Command:

```powershell
python -m unittest discover -s labs\grid_genome -p 'test_*.py'
```

Result:

```txt
Ran 31 tests in 0.404s
OK
```

Lineage command:

```powershell
python labs\grid_genome\lineage_tracker.py --count 200 --rng-seed 818 --archive data\archives\map_elites_stage0.json --generated-dir data\generated_grids\lineage_constrained --output data\lineage\lineage_stage0.json
```

## Metrics

```json
{
  "node_count": 250,
  "edge_count": 200,
  "orphan_count": 0,
  "max_generation": 1,
  "generation_counts": {
    "0": 50,
    "1": 200
  },
  "founder_count": 50,
  "candidate_count": 200,
  "distinct_parent_count": 50,
  "dominant_parent_id": "mg_seed_002",
  "dominant_lineage_children": 9,
  "dominant_lineage_share": 0.045,
  "elite_count": 24,
  "elite_parent_count": 17
}
```

## Findings

The first lineage graph has no orphaned children and all 50 seed founders are
represented as parents. Archive elites are distributed across 17 parent
lineages, so the first archive is not collapsing into one founder family.

The graph is still shallow. It only proves seed-to-child tracking. The next
research step needs a lifecycle simulation and reproduction loop so lineage
depth, survival age, death/reset cause, and mutation survival rate become real
metrics.

## Decision

Keep lineage tracking as a required data artifact for all future generator and
archive experiments. Do not advance `mecha_darwin` beyond a mechanics proof
until lifecycle outcomes can be attached to lineage records.

