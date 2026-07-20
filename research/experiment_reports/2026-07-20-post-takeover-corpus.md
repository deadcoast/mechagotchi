# Experiment Report: The Post-Takeover Corpus — the G-Phase Science Un-Saturates at Its Source (Cycle 19 · SHARED · I1)

Date: 2026-07-20

## WHY

Phase G closed at a floor it named honestly: the real-CuBFF
instruments saturated on EARLY-PHASE soup. G3's transducer study ran
its 400 curated states and found the discrimination DEGENERATE (the
direct arm 0/400 valid, readability flat — "post-takeover states
would un-saturate the comparison"); G4 measured real weather MILD for
the same reason ("harsh real weather awaits post-takeover soup").
Cycle 19 opens with the corpus that both remainders wait on: REAL
CuBFF states from past the takeover transition, labeled, committed
with the G2 discipline.

The GAME is why the phase label matters and not just the bytes: the
weather system feeds the engine's `cubff_pressure_source` seam from
this corpus (the pressure the player's creatures live under), and the
transducer readability axis is a sprite-legibility axis — the same
grids that are the engine's genomes are the game's pixel assets. An
early-phase-only corpus caps both at "mild"; the post-takeover states
are where real weather can turn harsh and where readability can
actually discriminate.

## WHAT

**The takeover, measured not assumed.** The G2 build path (upstream
`f212e84…`, `make CUDA=0`, WSL2 Ubuntu 24.04) reruns for real at the
paper-scale soup — the upstream default `--num 131072` — because the
G2/G3 soup size never takes over: the NEGATIVE CONTROL
(`run_seed0_num8192_long`, 16× the G2 window at the G2 soup size)
never crosses the takeover ratio — minimum compression ratio
**0.675** at epoch 250,369, final 0.939 at epoch 262,145, all 4,096
metrics rows committed (a 2026-07-19 probe of the same parameters
agreed on the headline). At 131,072 programs the collapse is sharp
and early: the run's own metrics cross compression ratio 0.5 between
epochs **2753 and 2817** (0.708 → 0.388 in one 64-epoch window),
with `higher_entropy` rising from ≈0.26 (epoch 2049) to ≈4.93 (epoch
4097), and the late state (epoch 32,769) settled at ratio 0.195 /
entropy 5.94. Soup AGE and soup PHASE are different axes — the
committed corpus deliberately carries a late-epoch early-phase state
(the negative control's final save) alongside the post-takeover
states.

**The corpus layout: one directory per real run.** Each run directory
under `data/cubff_real_ingest/source_snapshots/` carries its `.dat`
checkpoints, the run's own `metrics.csv`, and a `run.json` manifest
recording the exact reproduction parameters:

- `run_seed0_num8192/` — the cycle 17 G2 run, moved (git mv) intact
  (nine checkpoints, all `early_phase`).
- `run_seed0_num131072/` — the new run through takeover: curated
  checkpoints epoch 1 (ratio 1.000), 2049 (0.943 — the last early
  save), 4097 (0.175 — the first post-takeover save), 32769 (0.195 —
  the late state); the thirteen uncommitted intermediate saves are
  NAMED in `run.json` (curation is a size decision, never a truth
  decision).
- `run_seed0_num8192_long/` — the negative control (final checkpoint
  + all 4,096 metrics rows): the small soup NEVER crosses the
  takeover ratio.

**The gate rerun over the two-phase corpus:** status
`ingested_real_cubff_snapshots`, **14 ingested / 0 rejected files /
0 rejected records**, `phase_summary` 12 early_phase · 2
post_takeover · 0 unmeasured, `corpus_truth`
**`early_and_post_takeover`** — the I1 charter's corpus truth, judged
by the lab. Checkpoint ids are disambiguated by the manifest's
`run_id` (`run_seed0_num131072/0000004096`) because runs reuse
checkpoint filenames — and the game's five real-weather tests pass
UNCHANGED over the regenerated report (the seam consumes the corpus
verbatim; DR 0021's zero-seam-change promise holds through the
corpus growth), with the full game suite at 153.

**Phase labels come from the run's own instruments.** The ingest lab
(`labs/cubff_transducer/real_snapshot_ingest.py`) joins each
checkpoint's HEADER epoch to the sibling `metrics.csv` row for that
epoch — the G3-observed filename+1 rule honored: file
`0000002048.dat` carries header epoch 2049, and 2049 is the row the
log writes. A state is `post_takeover` iff its measured
`brotli_size / raw_soup_bytes < 0.5` (`TAKEOVER_COMPRESSION_RATIO`,
the pre-registered midpoint between the two observed modes: ≈0.85–1.0
early, ≈0.18 post). Python callback states use their in-record
`brotli_size` the same way. A state with no measured row stays
`unmeasured` — nothing is recomputed, interpolated, or fabricated.
`run.json` rides every snapshot as
`provenance.run_parameters`; the report gains `phase_summary` and
`corpus_truth` (`early_and_post_takeover` only when both phases are
really present).

## Verification

RED first — the pins demanded the labeling vocabulary before it
existed:

```powershell
PS> python -B -m unittest discover -s labs/cubff_transducer -p "test_real_snapshot_ingest.py"
ImportError: cannot import name 'TAKEOVER_COMPRESSION_RATIO' from 'real_snapshot_ingest'
FAILED (errors=1)
```

A second RED mid-slice — the id-collision defect surfaced by survey
(runs reuse checkpoint filenames) and pinned before the fix:

```powershell
PS> python -B -m unittest discover -s labs/cubff_transducer -p "test_real_snapshot_ingest.py"
AssertionError: Lists differ: ['run_a/0000002048', 'run_b/0000002048'] != ['0000002048', '0000002048']
FAILED (failures=1)
```

GREEN — the full lab suite with the nine new phase pins (metrics
parse + malformed-row skip, the epoch+1 join, both labels at the
threshold, the honest `unmeasured` path, `run.json` as provenance
never a snapshot, run_id-disambiguated ids, `phase_summary` +
`corpus_truth` both-phases and single-phase):

```powershell
PS> python -B -m unittest discover -s labs/cubff_transducer -p "test_*.py"
Ran 29 tests ... OK
```

Lab — the gate rerun over the curated two-phase corpus:

```powershell
PS> python -B labs/cubff_transducer/real_snapshot_ingest.py --source-commit f212e849027c98fcf4b242eccfb5fed435223e23 --seed 0
# ingested_real_cubff_snapshots | snapshots: 14 | rejected: 0 0
# phase_summary: {'early_phase': 12, 'post_takeover': 2, 'unmeasured': 0}
# corpus_truth: early_and_post_takeover
```

## HONEST REMAINDER

1. **The comparison itself is I2's study** — this report commits the
   corpus and its labels; whether post-takeover states break G3's
   degeneracy (direct arm leaving 0-valid, readability leaving flat)
   is judged there, falsifiable both ways.
2. **Real weather harshness is I3's measurement** — the corpus makes
   late soup available to the untouched seam; the multiplier
   direction is measured there, never tuned here.
3. **Replication scores stay absent from checkpoints** (the
   documented writer limitation); the silent weather channels still
   await the named Python-callback export path (I3).
4. **One seed at each scale** — the takeover epoch window is this
   run's measurement, not a distribution; I2's protocol chooses its
   own seeds and budgets on the proven build path. Reproducibility is
   PROTOCOL-level, not byte-level: the OpenMP build's interaction
   scheduling varies run to run (the 2026-07-19 probe and the
   committed negative control traced different trajectories from the
   same parameters while agreeing on the headline), which is why the
   corpus commits the states themselves, not just the recipe.
5. **The threshold is a midpoint, not a theory** — 0.5 cleanly
   separates the two observed modes (≈0.85–1.0 vs ≈0.18); a corpus
   that ever lands near it deserves a sharper instrument, and the
   constant is named so a future record can revisit it.

## Sources

- `audits/TODO.md` (cycle 19 I1)
- `research/experiment_reports/2026-07-12-real-cubff-corpus.md` (G2 — the build path this run extends)
- `research/experiment_reports/2026-07-12-real-transducer-study.md` (G3 — the saturation this corpus un-saturates)
- `research/experiment_reports/2026-07-12-real-weather.md` (G4 — the mildness finding waiting on late soup)
- `labs/cubff_transducer/real_snapshot_ingest.py` (+ `test_real_snapshot_ingest.py`)
- `data/cubff_real_ingest/` (the gate report + the per-run corpus + `run.json` manifests)
- `https://github.com/paradigms-of-intelligence/cubff` @ `f212e84` (the audited upstream), arXiv:2406.19108
