# Grid Genome Helper Deduplication

Date: 2026-07-04

Status: `research_grid_genome_helper_dedup_no_package_code`

## Purpose

Fix review finding L-04 from `docs/03-code_review/2026-07-04-code_review.md`:
duplicated helpers across the grid_genome generator modules. Drift between
copies of shared logic is the failure class that produced finding H-02; this
change removes the remaining duplicate sites.

## What changed

New `labs/grid_genome/grid_helpers.py` holds the single implementations:

- `_cell` — the three copies (corpus_builder, markov_grid,
  constrained_generator) were byte-identical; unified directly.
- grid-from-matrix family — one implementation with the real divergences
  expressed as parameters: `strict_tokens` (corpus blueprints must *reject*
  unknown tokens; generators skip them — load-bearing, pinned by test),
  `rng_seed` metadata (omitted when `None`), per-module `source` labels, and
  lineage parentage (`parent_grid_id`/`mutation_events`).
- `run_baseline` — random_mutation and markov copies were identical;
  constrained's copy inserts `unique_signatures` between `validity_rate` and
  `error_counts` (key order matters in JSON-dumped reports); unified with an
  optional `signature` callable that preserves exact key order.
- `grid_signature` — identical duplicate in constrained_generator and
  slip_profile_benchmark; unified, aliased back.
- Bonus duplicate found during the diff: markov's `_sample` ==
  constrained's `_weighted_sample`; unified as `weighted_sample`.
- `PALETTES` moved into grid_helpers (avoids an import cycle) and re-exported
  from corpus_builder so all existing cross-lab imports are unchanged.

Deliberately left: random_mutation's `_add_body_cell` (intentionally
different `mutation_weight` 0.15 vs `_cell`'s 0.1) and the `_write_json`
duplicate (out of scope).

Also regenerated `data/generated_grids/constrained_wfc_style/` (100 grids):
the committed corpus predated `generate_constrained_grid` populating parent
lineage and carried stale `parent_grid_id: null` / `generation: 0` /
empty `ancestor_ids`. Regeneration is a catch-up to HEAD code discovered
during refactor verification, not an effect of the refactor.

## Result

Refactor verified byte-equivalent: `corpus_builder.py`, markov, and
random-mutation corpora regenerate byte-identical; the constrained corpus was
diffed against a pristine-HEAD worktree run and matches pre-refactor code
exactly (its committed files changed only due to the stale-lineage catch-up
above).

```powershell
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
# Ran 62 tests - OK  (was 53; 9 new pinning tests: helper identity at all
# former duplicate sites, strict-token divergence, report key order)
```

All cross-importing lab suites green (map_elites_archive, cellular_automata,
lifecycle_sim, readability_benchmark, ctm_ticks, cubff_transducer,
workshop_editor); full sweep 455 tests OK.

## Decision

`grid_helpers.py` is the single source for cell construction, matrix-to-grid
conversion, baseline reporting, signatures, and weighted sampling in the
grid_genome lab. New generator modules must import from it rather than
copying; incidental divergences go through parameters, deliberate ones stay
local with a comment naming the difference.

## Verification

```powershell
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
python -B labs/grid_genome/corpus_builder.py
git diff --stat data/seed_grids data/invalid_grids   # empty
python -m json.tool data/generated_grids/constrained_wfc_style/mg_constrained_000.json
```

## Sources

- `docs/03-code_review/2026-07-04-code_review.md`
- `labs/grid_genome/grid_helpers.py`
- `labs/grid_genome/test_grid_helpers.py`
- `labs/grid_genome/corpus_builder.py`
- `labs/grid_genome/markov_grid.py`
- `labs/grid_genome/constrained_generator.py`
- `labs/grid_genome/random_mutation.py`
- `labs/grid_genome/slip_profile_benchmark.py`
- `data/generated_grids/constrained_wfc_style/`
