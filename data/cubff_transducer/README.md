# CUBFF Semantic Transducer Stage 0

Synthetic CUBFF-style snapshots were used to test the Mechagotchi semantic transducer contract without requiring a CUDA CuBFF run.

Key results:

- Direct visual validity: 0/12
- Hybrid semantic validity: 12/12
- Hybrid SLIP alignment: 12/12
- Decision: watch_synthetic_only

## The REAL study (cycle 17 G3, 2026-07-12)

- `real_states_curated.json` - the 400 curated states from 20 REAL
  runs (bff_noheads, seeds 0-19, 8192 programs, 19,456 epochs,
  checkpoints every 1024 on the G2 build path): tapes + soup sha256s
  + provenance, curation = every checkpoint in epoch order (no
  cherry-picking). The raw ~100 MB fleet is reproducible from these
  parameters and is not committed.
- `real_transducer_study_stage0.json` - the documented gates over
  those states: preference 400/400 (>60% MET), semantic invalid
  0/400 (<10% MET) -> KEEP. The honest mechanism recorded: the
  discrimination is DEGENERATE on early-phase soup (direct arm
  0/400 valid, readability flat 0.0; semantic arm flat 1.0 - both
  instruments saturated); the result reads "the semantic transducer
  is the only viable path from real early-phase soup to a
  displayable creature," not a graded preference. Produced by
  `labs/cubff_transducer/real_transducer_study.py`.
