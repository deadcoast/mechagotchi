# Experiment Report: The `slip_admission` Default, Decided — `insertion`, Exactly as DR 0047 Predicted (Cycle 24 · SHARED · N4)

Date: 2026-07-28

## WHY

The engine breeds creatures by drawing parents from the archive. A
fraction of the archive's occupants are creatures the covenant (the
SLIP profile) says should not exist: they were built during bootstrap,
before the profile was applied, won niches on fitness, and are then
round-robined as parents forever. Every attempt to breed from one is
refused. L1 measured the tax at **4,435 refusals per run**, flat, and
it never improves.

M3 built three fixes. **All three take the tax to exactly zero.** So
"can it be fixed" was answered a cycle ago; the open question was
*which fix ships*.

M3's rule gated two things — refusals and coverage — and by that rule
the least invasive arm, `parents`, won. DR 0047 then **refused to
promote its own winner**, because `parents` is the worst of the three on
two dimensions the rule never asked about: it lowers quality, and it
leaves the illegal creatures sitting in the archive rather than clearing
them. It named its decider exactly:

> *"a re-run with **quality and archive legality pre-registered as
> gates alongside coverage**, over **multiple seeds**. On this evidence
> the likely winner is `insertion`, not `parents` — and that is exactly
> why it needs its own gate rather than a paragraph here."*

N4 is that re-run.

## WHAT

**Four gates, pre-registered before the run** — and the pre-registration
mattered more than usual here, because DR 0047 published a prediction. A
gate written after the numbers arrive cannot refute the prediction it
exists to test.

- **G1 — the cause is eliminated.** `refusals == 0`. DR 0047's gate
  unchanged, with one tightening: it must hold on **every seed**, not
  once. A mean would let a clean seed hide a dirty one.
- **G2 — coverage is preserved.** Cost must not exceed the **measured**
  seed-to-seed coverage control. DR 0047's gate unchanged in shape,
  wider in evidence. A coverage gain is never penalised.
- **G3 — quality is preserved** *(new — the first thing DR 0047 asked
  for)*. QD must not fall below the incumbent's by more than the
  **measured** seed-to-seed QD control. Same shape as G2, same refusal
  to use a constant, and a gain is never penalised.
- **G4 — the archive is covenant-legal** *(new — the second)*. Zero
  SLIP-illegal elites, on **every seed**. **Structural, exactly like
  G1**, on DR 0047's own reasoning for making G1 structural: a covenant
  either holds over the archive it bred or it does not, and a percentage
  bar would be a number nobody derived.

**The tie-break is DR 0047's, verbatim**: least invasive first
(`parents` < `insertion` < `bootstrap`). The *only* change is the set it
applies to — arms clearing all four gates. That single change is the
whole mechanism by which this study can overturn DR 0047's winner
without touching its rule.

**Refusing all three is reachable and pinned.** If nothing cleared all
four, the default would not move and DR 0047's withholding would stand.

Three seeds per configuration, four configurations (incumbent + three
arms) — twelve documented-budget loops.

### The instrument validates itself against the study it is deciding for

The first seed **is** DR 0047's seed, so the incumbent measured here
must reproduce its committed baseline exactly. It does, on every field:

| | DR 0047 committed | N4 measured |
| --- | --- | --- |
| coverage | 0.898438 | **0.898438** |
| QD | 404.618236 | **404.618236** |
| refusals | 4,435 | **4,435** |
| SLIP-illegal elites | 35 | **35** |
| occupied niches | 460 | **460** |

The configuration is **read from DR 0047's artifact**, not quoted from
its prose, and a mismatch is refused rather than silently run. That
check exists because it caught a real error — see the process deviation
below.

## FINDINGS

### The verdict: `ADOPT_DEFAULT → insertion`

Measured controls (the incumbent's own seed-to-seed spread): coverage
**0.033204**, QD **16.560333**. The coverage control lands on exactly
DR 0047's figure, because seeds 0 and 1 are the pair it used and seed 2
falls between them.

| arm | coverage | cost | QD | Δ QD | refusals | illegal elites | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| incumbent | 0.876953 | — | 394.186363 | — | 4435 / 4400 / 4543 | 35 / 37 / 33 | — |
| `bootstrap` | 0.847005 | +0.029948 | 394.1510 | −0.0353 | 0 / 0 / 0 | **0 / 0 / 0** | **ADOPTABLE** |
| `insertion` | 0.847005 | +0.029948 | 394.0508 | −0.1356 | 0 / 0 / 0 | **0 / 0 / 0** | **ADOPTABLE** |
| `parents` | 0.872396 | +0.004558 | 391.6805 | −2.5059 | 0 / 0 / 0 | **35 / 37 / 35** | **FAILS G4** |

**`parents` fails on archive legality, and it fails completely.** It
stops the tax without clearing a single illegal elite — 35, 37 and 35
across the three seeds, essentially unchanged from the incumbent's 35,
37 and 33. That is the arm behaving exactly as DR 0047 described: it
declines to *breed* the illegal creatures but evicts none of them.

**`bootstrap` and `insertion` both clear all four**, and the tie-break
picks the less invasive: **`insertion`**.

> **DR 0047's prediction is CONFIRMED.** It called `insertion` over its
> own rule's winner, said the call needed a gate rather than a
> paragraph, and the gate agrees.

### Why the two survivors are indistinguishable on coverage

`bootstrap` and `insertion` return **identical coverage on all three
seeds** (0.880859 / 0.832031 / 0.828125) and QD within 0.1. This is
structural, not coincidence, and DR 0047 already explained the
mechanism: both remove the same SLIP-illegal bootstrap creatures, and
the only difference is whether those creatures are *scored* before being
excluded. `insertion` scores them and drops them at the archive door;
`bootstrap` never builds them.

So the tie-break is doing real work here. On the four gated dimensions
these two arms are the same fix; invasiveness is the only thing that
separates them, and DR 0047 fixed that order before any of this was
measured.

### The cost, stated plainly

Adopting `insertion` costs **0.029948 coverage** — inside the measured
control of 0.033204, but only just: **90% of the control**. That is a
pass, not a comfortable one, and it should not be reported as though the
fix were free. What it buys is 4,435 wasted evaluations per run removed
and an archive that is legal under the covenant it was bred for.

QD is effectively untouched (−0.0353 for `bootstrap`, −0.1356 for
`insertion`, against a control of 16.56 — under 1% of it).

## PROCESS DEVIATION, RECORDED NOT BURIED

**The first full run of this study used `population=512`. That was
wrong, and it produced the wrong answer.**

M3 measured DR 0047's arms at **256**, which is also
`evaluation_loop_scale`'s own documented default. This module's first
draft set 512 — a parameter it *invented* rather than inherited. The
consequence was not cosmetic:

- the incumbent did not reproduce DR 0047's baseline (coverage 0.944661
  against the committed 0.898438; 4,070 refusals at DR 0047's own seed
  against the committed 4,435), so the arms were being judged against a
  different loop than the one DR 0047 withheld on;
- and **the verdict flipped**: at 512, `insertion` failed G2 by
  **0.000652** — 2% of the control — leaving `bootstrap` as the sole
  passing arm. A hair's-width miss on the wrong configuration would have
  refuted a correct prediction.

Caught by checking the discrepancy rather than accepting the tidy
verdict, corrected to 256, and re-run. Two guards now exist so it cannot
recur silently: `load_dr0047_baseline()` reads DR 0047's parameters
**from its artifact**, and `judge_configuration_match()` refuses a run
whose population, budget or first seed diverges from it. Both are
pinned.

The 512 run is **not** reported as a robustness check, because it was
not designed as one — it was an error, and its only evidentiary value is
the warning above.

## HONEST REMAINDERS

1. **This study decides; it does not migrate.** `run_evaluation_loop`'s
   default is still `slip_admission="none"`, and flipping it is a real
   piece of work with a measured blast radius: **at least six lab
   modules call the loop without naming an arm** —
   `evaluation_loop_scale`, `coverage_qd_gates`,
   `elite_population_measures`, `family_ancestry`,
   `generation_refusal_causes` and `lineage_dominance` — so every one of
   their committed artifacts changes, including **DR 0042's headline
   coverage 0.8984** and **L1's entire subject** (the 4,435 refusals
   become 0). That is a regeneration cascade with a delta to explain per
   artifact, at ~380 s per loop run. It is **queued as N7**, with this
   cost, rather than left as a floating remainder.
2. **The arms live in the lab evaluation loop.** `slip_admission`
   appears nowhere in `packages/` — promoting the fix into the promoted
   engine is a separate step with its own spec and gate, and is not
   claimed here.
3. **The coverage pass is narrow** (90% of the control). A wider control
   from more seeds could move it either way.
4. **One SLIP profile** (`slip_lcd_seed`) — DR 0047's own recorded
   limit, inherited unchanged. A wider palette rejects fewer bootstrap
   creatures and could move every cost here.
5. **No arm evicts an already-seated illegal elite.** DR 0047's fourth
   candidate remains unmeasured.
6. **DR 0046's comparability rule applies**: every coverage and QD
   number here is an incumbent-geometry number.

## Verification

RED — the pins, written before the module existed:

```powershell
PS> python -B -m unittest test_slip_admission_default   # (from labs/map_elites_archive)
    from slip_admission_default import (  # noqa: E402
    ...<9 lines>...
    )
ModuleNotFoundError: No module named 'slip_admission_default'


----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN:

```powershell
PS> python -B -m unittest test_slip_admission_default
----------------------------------------------------------------------
Ran 36 tests in 1.075s

OK
```

The lab invocation that produced the artifact:

```powershell
PS> python -B labs/map_elites_archive/slip_admission_default.py
incumbent  coverage 0.876953 QD 394.186363  refusals [4435, 4400, 4543]  illegal [35, 37, 33]
measured controls: coverage 0.033204, QD 16.560333

  bootstrap  cov 0.847005 (cost +0.029948)  QD 394.1510 (delta -0.0353)  refusals [0, 0, 0]  illegal [0, 0, 0]
             G1 True  G2 True  G3 True  G4 True  -> ADOPTABLE
  insertion  cov 0.847005 (cost +0.029948)  QD 394.0508 (delta -0.1356)  refusals [0, 0, 0]  illegal [0, 0, 0]
             G1 True  G2 True  G3 True  G4 True  -> ADOPTABLE
  parents    cov 0.872396 (cost +0.004558)  QD 391.6805 (delta -2.5059)  refusals [0, 0, 0]  illegal [35, 37, 35]
             G1 True  G2 True  G3 True  G4 False  -> FAILS G4_archive_legality

ADOPT_DEFAULT  default -> insertion
  passing arms: ['insertion', 'bootstrap']
  wall clock 3560.685 s (bound 14400.0 s, within True)
wrote data/archives/slip_admission_default_stage0.json
```

Wall clock **3560.685 s** against a bound of **14400 s** derived as
`4 configurations × 3 seeds × the loop's own registered bound`
(DR 0028), not picked.

The archive lab and the closing sweep:

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
----------------------------------------------------------------------
Ran 431 tests in 170.454s

OK

PS> python -B tools/ci/run_sweep.py
lab:animation_system             OK  OK  [11.7s]
lab:architecture                 OK  OK  [20.5s]
lab:asset_pipeline               OK  OK  [0.5s]
lab:cellular_automata            OK  OK  [40.8s]
lab:ctm_ticks                    OK  OK  [0.2s]
lab:cubff_transducer             OK  OK  [0.8s]
lab:datasets                     OK  OK  [3.3s]
lab:game_loop                    OK  OK  [7.3s]
lab:grid_genome                  OK  OK  [9.0s]
lab:lifecycle_sim                OK  OK  [0.5s]
lab:map_elites_archive           OK  OK  [169.3s]
lab:micro_threads                OK  OK  [9.1s]
lab:package_promotion            OK  OK  [0.2s]
lab:readability_benchmark        OK  OK  [3.1s]
lab:repair_boundary              OK  OK  [3.7s]
lab:runtime_integration          OK  OK  [87.9s]
lab:slip_validator               OK  OK  [0.7s]
lab:wfc_grid                     OK  OK  [7.0s]
lab:workshop_editor              OK  OK  [6.7s]
package                          OK  OK  [7.3s]
cli                              OK  OK (skipped=15)  [3.8s]
game                             OK  OK (skipped=5)  [14.1s]
workshop                         OK  <sys>:0: ResourceWarning: unclosed <socket.socket fd=1000, family=2, type=1, proto=0, laddr=('127.0.0.1', 14748)>  [188.2s]
data artifacts                   OK  2244 JSON artifacts valid  [8.4s]

SWEEP GREEN
```

Archive lab **395 → 431**, measured rather than carried forward.

**On the resume cache**: twelve documented-budget loops do not fit in
one sitting, so the module can resume from a default-off cache whose key
carries every parameter that changes a result. The loop is
deterministic, so a replay is the same measurement — verified rather
than assumed: regenerating the artifact entirely from cache returned
**every value identical** to the computed run. The artifact records how
many runs were computed versus replayed, so a 0.003 s replay can never
be mistaken for the study's cost.

## Sources

- `audits/TODO.md` (cycle 24 N4) · `research/decision_records/0052-slip-admission-default-insertion.md` (the record this study produced)
- `research/decision_records/0047-slip-admission-arms.md` (the record that withheld this default and named this decider), `0042-generation-layer-loop-revisit.md` (the coverage this trades against), `0046-two-geometry-split.md` (comparability), `0028-dependency-and-license-policy.md` (wall-clock-first)
- `research/experiment_reports/2026-07-27-slip-admission-arms.md` (M3), `2026-07-26-generation-refusal-causes.md` (L1 — the 4,435-refusal mechanism), `2026-07-27-elite-population-measures.md` (M1 — the 48-of-460 denominator)
- `labs/map_elites_archive/slip_admission_default.py` (+ `test_slip_admission_default.py`, 36 pins) · `data/archives/slip_admission_default_stage0.json`
- `labs/map_elites_archive/slip_admission_arms.py` (`_run` and the arms, IMPORTED never re-implemented) · `evaluation_loop_scale.py` (the loop and its `slip_admission` seam)
- `data/archives/slip_admission_arms_stage0.json` (DR 0047's committed baseline, reproduced exactly)
