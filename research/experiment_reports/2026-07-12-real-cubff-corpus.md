# Experiment Report: The Real CuBFF Corpus — the Standing Blocker Closes (Cycle 17 · SHARED · G2)

Date: 2026-07-12

## WHY

The oldest honest blocker in the ledger: the semantic-transducer
track was gated on REAL CuBFF soup/checkpoint snapshots
(`awaiting_real_cubff_snapshots`), because the upstream audit found
checkpoint-writing code but no committed data, and the owner ruled
real ingest REQUIRED (2026-07-07) with fabrication forbidden. Phase G
is its named late stage.

## WHAT

**The attempt path, recorded**: no C++ toolchain exists on the
Windows host (no cmake/MSVC/gcc/clang — checked); upstream publishes
no data assets, no wheels (checked against the live repo). The
machine's **WSL2 Ubuntu 24.04** carries the documented Debian build
path (g++ 13.3, make, libbrotli with headers) — so the upstream study
code was built and run FOR REAL, with no system changes:

- **Clone at the AUDITED commit** `f212e84…` — the exact commit the
  ingest record's upstream audit examined; `make CUDA=0` (OpenMP CPU
  path) builds clean.
- **One genuine run**: `bff_noheads --seed 0 --num 8192
  --max_epochs 16384 --save_interval 2048` (~seconds on 16 threads;
  256 epochs measured at 0.27 s) → **nine `.dat` checkpoints**
  (epochs 0…16384), each byte-exact to the documented writer format
  (24-byte header + 8192 × 64 soup bytes = 524,312), plus the run's
  own `metrics.csv` committed as provenance.
- **The gate flipped on the engine's own judgment**: rerunning
  `labs/cubff_transducer/real_snapshot_ingest.py` over the corpus —
  `status: ingested_real_cubff_snapshots`, **9 ingested / 0 rejected
  files / 0 rejected records**, decision
  `ready_for_real_transducer_comparison`. The transducer suite (17
  tests) stays green; the gate README regenerated itself.

**Honest observations, recorded not embellished**: over this window
the soup stays EARLY-PHASE (brotli ≈ 482k of 524k raw at the final
epoch — no compression collapse/takeover at this soup size);
replication scores are absent because the checkpoint format does not
store them (the documented writer limitation, not an omission).
Longer/larger runs for emergent states belong to G3's documented
protocol (20 runs / 400 curated states), never retrofitted here.

## Verification

```powershell
PS> wsl -e bash -lc "cd ~/cubff_g2 && git log --oneline -1 && make CUDA=0 -j4"
f212e84 Fix paper name (#45)          # the audited commit; builds clean
PS> wsl -e bash -lc "bin/main --lang bff_noheads --seed 0 --num 8192 --max_epochs 16384 --save_interval 2048 --checkpoint_dir ... --log .../metrics.csv"
# nine .dat checkpoints, each 524,312 bytes
PS> python -B labs/cubff_transducer/real_snapshot_ingest.py --source-commit f212e849027c98fcf4b242eccfb5fed435223e23 --seed 0
PS> # data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json:
#   status ingested_real_cubff_snapshots · 9 ingested · 0 rejected
PS> python -B -m unittest discover -s labs/cubff_transducer -p "test_*.py"
Ran 17 tests ... OK
```

## HONEST REMAINDER

1. **Adoption stays undecided by design** — the gate's own decision:
   `still_no_core_dependency_decision`; the comparison against the
   transducer baseline is G3's study.
2. **This corpus is one seed at one small soup size** — G3's
   documented protocol (20 runs / 400 curated states, the keep gates)
   chooses its own scales and budgets; the build path is now proven
   and seconds-cheap.
3. **The run machine is WSL2 on this host** — the corpus files are
   committed evidence; reproducing them needs the documented Debian
   build path (recorded in the corpus README), not this machine.
4. **G4 (real weather in the game) can now proceed** — real snapshots
   exist for the weather seam's zero-change promise to be verified
   against.

## Sources

- `audits/TODO.md` (cycle 17 G2), the owner ruling of 2026-07-07 (real ingest REQUIRED; never fabricate)
- `labs/cubff_transducer/real_snapshot_ingest.py` (+ its 17-test suite)
- `data/cubff_real_ingest/` (the flipped gate report + the committed corpus + provenance READMEs)
- `https://github.com/paradigms-of-intelligence/cubff` @ `f212e84` (the audited upstream), arXiv:2406.19108
