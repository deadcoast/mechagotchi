# Lineage Data

This directory contains research lineage artifacts for Mechagotchi.

Current artifact:

- `lineage_stage0.json`: first seed-to-child lineage graph over 50 seed grids
  and 200 constrained generated children.

The Stage 0 lineage graph tracks:

- node type
- parent grid ID
- generation
- ancestor IDs
- mutation events
- archive elite membership
- orphan children

This is a one-generation graph. Deeper lineage requires reproduction from
archive elites and lifecycle/survival data.
