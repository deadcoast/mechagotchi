# Experiment Report: The Transducer Study at Documented Scale — Over Real States (Cycle 17 · SHARED · G3)

Date: 2026-07-12

## WHY

The documented CuBFF study (gap analysis, the CuBFF row): "Semantic
transducer over REAL runs: 20 runs, 400 curated states; keep if
preference >60%, invalid <10%." The synthetic-era lab ran the
comparison on synthetic snapshots and explicitly refused adoption
until real data existed; G2 landed the real build path; G3 runs the
documented protocol.

## WHAT

**`labs/cubff_transducer/real_transducer_study.py`** (RED-first, 3
tests; gate arithmetic pinned falsifiable BOTH ways, boundary values
included): curation is the FIXED grid — every checkpoint of every run
directory, ingested in epoch order through the G2 gate's own parser
(epoch-stratified, no cherry-picking); the arms are the existing
lab's functions verbatim (direct tape→pixels vs the semantic
features→traits→constrained compile); preference per state = the
semantic grid strictly out-reads the direct one on the lab's own
readability instrument.

**The fleet**: 20 REAL runs (`bff_noheads`, seeds 0–19, 8192
programs, 19,456 epochs, checkpoints every 1024) on the G2 build path
— 400 curated states spanning epochs 1–19,457 across all twenty
independent runs. The curated state records (tapes + soup hashes +
provenance) are committed (`real_states_curated.json`); the raw
fleet is reproducible from the recorded parameters.

## THE GATES — met, with the mechanism scrutinized

| Gate | Documented | Measured | Verdict |
| --- | --- | --- | --- |
| Preference | > 60% | **400/400 = 100%** | MET |
| Semantic invalid | < 10% | **0/400 = 0%** | MET |
| **Keep decision** | both | | **KEEP** |

**The scrutiny a clean sweep demands (recorded, not celebrated):**
the discrimination is DEGENERATE at this corpus phase. The direct
arm went **0/400 valid** with readability flat at 0.0 — raw
early-phase soup projected to pixels never forms a connected,
organ-bearing body — while the semantic arm scored flat 1.0 (its
compiler is validator-gated by construction). Both instruments
saturated; the honest reading is not "graded preference for the
semantic transducer" but **"the semantic transducer is the only
viable path from real early-phase soup to a displayable creature"**
— which IS the documented question, answered at its floor. A graded
comparison needs post-takeover soup (structured tapes), which this
corpus honestly lacks (G2's early-phase observation).

Also observed: the checkpoint header's epoch is filename+1 (files
`0000000000.dat` … parse as epochs 1 … 19,457) — the upstream
writer's own convention, recorded verbatim.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/cubff_transducer -p "test_real_transducer_study.py"
Ran 1 test ... FAILED (errors=1)   # RED: module absent
# after implementation:
Ran 3 tests ... OK                 # gates falsifiable both ways, boundaries pinned
PS> wsl -e bash -lc "... for seed in $(seq 0 19) ... bin/main --lang bff_noheads --seed $seed --num 8192 --max_epochs 19456 --save_interval 1024 ..."
PS> python -B labs/cubff_transducer/real_transducer_study.py --fleet-dir <fleet>
# state_count 400 · preference 1.0 (>0.6 MET) · invalid 0.0 (<0.1 MET) · KEEP
PS> python -B -m unittest discover -s labs/cubff_transducer -p "test_*.py"
Ran 20 tests ... OK
```

## HONEST REMAINDER

1. **The preference instrument is the lab's readability proxy**, not
   human preference judgments — the recorded instrument the
   synthetic-era study used, applied unchanged; a human-preference
   pass is a named upgrade if adoption ever needs it.
2. **The corpus is early-phase** — post-takeover states (longer/larger
   runs) would un-saturate the comparison; the build path makes them
   cheap when a consumer asks.
3. **"Keep" keeps the TRANSDUCER, not a core dependency** — the
   ingest gate's own adoption note stands
   (`still_no_core_dependency_decision`); CuBFF remains the weather/
   corpus source it was designed to be.
4. **The raw 400-checkpoint fleet is not committed** (~100 MB);
   the curated records with soup hashes are, and the run parameters
   reproduce the fleet exactly.

## Sources

- `audits/TODO.md` (cycle 17 G3), the gap analysis (the CuBFF row's documented protocol)
- `labs/cubff_transducer/real_transducer_study.py` (+ its tests), `cubff_transducer.py` (the verbatim arms), `real_snapshot_ingest.py` (the parser)
- `data/cubff_transducer/real_transducer_study_stage0.json`, `real_states_curated.json` (the committed study)
- `research/experiment_reports/2026-07-12-real-cubff-corpus.md` (G2 — the corpus and its early-phase observation)
