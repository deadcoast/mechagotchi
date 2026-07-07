# Algorithm Card: Dataset Program (deterministic corpus builders)

- **Name**: og dataset program — three deterministic corpus builders
  (`mechaseed_200`, `mutationbench_5000`, `replay_100k_ticks`) over
  promoted engine surfaces, with signature-based verifiability.
- **Purpose**: R6 (=T11) — complete the og research plan's dataset
  table; the ML tracks' fuel (learned-readability retraining,
  mutation-operator evaluation, switchboard/behaviour evaluation, R5
  replay tooling).
- **Mathematical basis**: determinism as the storage-compression
  theorem — a candidate grid is a pure function
  `generate_candidate(parent, model, profile, rng_seed)`, so a dataset
  row storing `(config, grid_signature)` carries the full grid's truth
  verifiably without storing it; curation is a deterministic greedy walk
  (fixed seed-offset enumeration, accept iff `validate_grid` ∧ novel
  signature); replay enumeration is a fixed product order over
  (corpus × policies × rng rounds) until the tick target is crossed.
- **Inputs**: `mechaseed_50` (`data/seed_grids/`), the package
  generation/lifecycle trainers, `slip_corpus_r6` (the fixture profile
  widened to admit the whole corpus — authority-valid, shipped
  alongside).
- **Outputs**: three versioned datasets, each with a README; a stage-0
  report carrying per-file sha256 checksums and coverage metrics.
- **Strengths**: every row engine truth; every stored or elided grid
  verifiable by `grid_signature`; byte-deterministic files (gzip
  `mtime=0`); corpus-wide palette/mass diversity preserved by the
  corpus profile.
- **Weaknesses**: variant diversity is bounded by the generation
  model's operator set (no hand-curated exotic body plans); one
  generation profile per dataset version.
- **Failure modes**: a signature collision or non-reproducible row
  would break the compression claim — pinned by regeneration tests;
  target-shortfall in the curation walk is bounded (offset cap) and
  would fail the count test loudly rather than pad silently.
- **Integration risk**: none to the engine (read-only consumers of
  public surfaces).
- **License status**: original stdlib implementation; data derived from
  the repo's own hand-authored corpus.
- **Prototype result**: 200/200 valid unique bodies (50 seeds + 150
  variants); 5,000 signature-verifiable mutation cases; 100,004
  verbatim lifecycle ticks across 3 policies; 12/12 tests; ~5.5 MB
  total on disk.
- **Decision**: adopt (the og dataset table is fully delivered);
  PNG-render companions deferred until a consumer exists (recorded
  blocked state).
- **Go-No-Go gate**: determinism (built twice, equal); every
  `mechaseed_200` entry valid + signature-unique + variant-reproducible;
  sampled `mutationbench` rows regenerate to their stored signatures;
  replay ticks contiguous per episode and gzip round-trips exactly;
  corpus profile authority-valid and admitting all 50 seeds.

## Sources

- `research/experiment_reports/2026-07-07-dataset-program.md`
- `labs/datasets/dataset_program.py` (+ `test_dataset_program.py`)
- `data/datasets/` (the three corpora + `slip_corpus_r6.json` + stage-0 manifest)
- `docs/project-research/deep-research/01/deep-research.md` (the og dataset table)
