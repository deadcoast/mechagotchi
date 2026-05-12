# Algorithm Card: Lineage Tracking

## Purpose

Track ancestry, mutation events, generation depth, and archive membership so
Mechagotchi evolution can be measured rather than described informally.

## Mathematical Basis

Directed parent-child graph with generation labels and aggregate lineage
statistics.

## Inputs

- Seed grid corpus
- Generated child grids
- Optional MAP-Elites archive elite IDs

## Outputs

- Lineage graph
- Parent-child edges
- Orphan list
- Generation counts
- Dominant lineage share
- Elite parent spread

## Strengths

- Makes ancestry explicit.
- Detects orphaned generated records.
- Supports future survival and mutation-history metrics.
- Provides the bridge between generator output and `mecha_darwin`.

## Weaknesses

- Current graph is only one generation deep.
- No lifecycle/death cause data yet.
- Parent selection is generator-defined, not evolved reproduction.

## Failure Modes

- Missing parent IDs
- Generated children without corresponding founder records
- One founder dominating the archive
- Mutation events recorded as vague labels

## Integration Risk

Low.

## License Status

Internal lab code.

## Prototype Result

First lineage prototype completed on 2026-05-12.

```txt
node_count: 250
edge_count: 200
orphan_count: 0
founder_count: 50
candidate_count: 200
max_generation: 1
distinct_parent_count: 50
dominant_lineage_share: 0.045
elite_count: 24
elite_parent_count: 17
```

## Decision

Keep lineage tracking as a required data product for every generator/archive
experiment. Next step is lifecycle simulation so lineage records can include
survival age, death/reset cause, and mutation survival rate.

