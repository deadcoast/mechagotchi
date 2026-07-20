# Experiment Report: The Transducer Study Over Post-Takeover States — the Pre-Registered Break REFUTED (Cycle 19 · SHARED · I2)

Date: 2026-07-20

## WHY

G3 ran the documented study (20 runs / 400 curated states) and found
the discrimination DEGENERATE on early-phase soup: the direct arm
0/400 valid, readability flat — both instruments saturated — with the
honest remainder "post-takeover states would un-saturate the
comparison." I1 built the post-takeover corpus and proved the
takeover scale. I2 re-runs the documented study over a fleet that
CROSSES takeover, with the expectation to break pre-registered and
falsifiable both ways.

## WHAT

**The fleet**: 20 REAL runs (`bff_noheads`, seeds 0–19) at the
PROVEN takeover scale — 131,072 programs (the upstream default; I1's
negative control showed the G3-era 8192 soup never takes over) — to
6,144 epochs with saves every 320: the fixed curation grid = **400
states**, every checkpoint of every run, no cherry-picking, each
state phase-labeled by its own run's metrics through the I1 ingest.

**Takeover onset, measured as a distribution** (the G3 "one seed"
remainder answered): only **4 of 20 seeds cross by epoch 6,144** —
crossings at epochs ~2785 (seed 0), ~3553 (seed 8), ~5409 (seed 16),
~5921 (seed 15); the other sixteen hold early-phase (final ratios
≈0.93). Onset is heavily stochastic; the 6,144 horizon (2.2× seed 0's
crossing) was calibrated on the luckiest seed. The corpus truth:
**386 early_phase · 14 post_takeover · 0 unmeasured**.

**The study, verbatim arms** (`real_transducer_study.py`, extended
with phase carriage and `judge_degeneracy`; G3's committed artifact
stays FROZEN under its own id — the I2 rerun writes
`real_transducer_study_i2_stage0.json` + `real_states_curated_i2.json`):

| Gate | Documented | Measured | Verdict |
| --- | --- | --- | --- |
| Preference | > 60% | 400/400 = 100% | MET |
| Semantic invalid | < 10% | 0/400 = 0% | MET |
| Keep decision | both | | **KEEP** (unchanged) |

**THE PRE-REGISTERED BREAK: REFUTED.** Over the 14 post-takeover
states: direct arm **0 valid**, direct readability **flat 0.0**
(min = max = 0), semantic flat 1.0 — `degeneracy_broken: false` by
the judgment's own arithmetic. Post-takeover soup is dominated by
self-replicators — repetitive tape structure — and a replicator tape
projected raw to pixels STILL never forms a connected, organ-bearing,
validator-grade body. **The saturation is a property of the ARMS,
not the soup's phase**: G3's honest reading gets stronger, not
weaker — the semantic transducer is the only viable path from real
CuBFF soup, early OR post-takeover, to a displayable creature. For
the game this is a load-bearing fact: the sprites the player sees can
only come through the validator-gated semantic path; there is no
"raw soup to screen" shortcut in any phase.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/cubff_transducer -p "test_real_transducer_study.py"
ImportError: cannot import name 'judge_degeneracy' from 'real_transducer_study'
FAILED (errors=1)                     # RED: the judgment absent
# after implementation (degeneracy falsifiable both ways, phase carriage,
# artifact identity divergence so G3 stays frozen):
Ran 36 tests ... OK                   # the full cubff_transducer suite
PS> wsl -e bash -lc 'for s in $(seq 0 19); do ... bin/main --lang bff_noheads --seed $s --num 131072 --max_epochs 6144 --save_interval 320 ...; done'
# FLEET_DONE:0 — 20 runs x 20 checkpoints
PS> python -B labs/cubff_transducer/real_transducer_study.py --fleet-dir <fleet> --artifact-id real_transducer_study_i2_stage0 --date 2026-07-20 --curated-filename real_states_curated_i2.json
# state_count 400 · preference 1.0 MET · invalid 0.0 MET · keep
# degeneracy: post_takeover_state_count 14 · direct_valid_count 0 ·
#   direct readability min 0 max 0 · degeneracy_broken FALSE
```

## HONEST REMAINDER

1. **The sharper remainder replaces the old one**: un-saturating this
   comparison is no longer a soup question — it needs a DIFFERENT
   direct arm (a structured decoder from tape to grid), which is a
   new study design with its own record, not more epochs.
2. **14 post-takeover states from 4 seeds** — the refutation is clean
   (every one 0-valid, flat) but the subset is small; the takeover-
   onset distribution says more post states cost real compute (longer
   horizons per seed), justified only if remainder 1's new arm exists.
3. **The raw 3.4 GB fleet is not committed** — the curated records
   (tapes + soup hashes + phases + provenance) are, and the recorded
   parameters reproduce the protocol (protocol-level, per I1's
   OpenMP observation).
4. **"Keep" still keeps the transducer, never a core dependency** —
   the adoption note stands unchanged.

## Sources

- `audits/TODO.md` (cycle 19 I2)
- `research/experiment_reports/2026-07-12-real-transducer-study.md` (G3 — frozen, its remainder now answered)
- `research/experiment_reports/2026-07-20-post-takeover-corpus.md` (I1 — the scale proof and the ingest labeling)
- `labs/cubff_transducer/real_transducer_study.py` (+ tests), `cubff_transducer.py` (the verbatim arms)
- `data/cubff_transducer/real_transducer_study_i2_stage0.json`, `real_states_curated_i2.json`
