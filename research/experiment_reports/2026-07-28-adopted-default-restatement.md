# Experiment Report: The Headline Studies Restated Under the Adopted Default — Coverage Buys Quality, and No Documented Gate Regressed (Cycle 25 · SHARED · O3)

Date: 2026-07-28

## WHY

DR 0052 adopted `insertion` as the `slip_admission` default and DR 0053
flipped it **prospectively** — all eight historical callers pinned to
the incumbent, no committed number moved. DR 0053 then named the only
two whose migration is a real question rather than an
evidence-destroying regeneration:

- **`evaluation_loop_scale`** — the source of **DR 0042's headline
  coverage 0.8984**, quoted across decision records, gate reports and
  ONBOARDING;
- **`coverage_qd_gates`** — the documented **E4 gates**.

O3 restates both.

## WHAT

**This restates; it never overwrites.** DR 0053's rule 2 is the shape of
the task: *a measurement does not improve — it is reproduced, or
superseded by a new measurement answering a new question.* "What does
the loop achieve under the adopted default" **is** a new question, so it
gets a new artifact and both committed incumbent artifacts stay exactly
as they are.

**Only the adopted arm was re-run**, and that shrank the work by roughly
three quarters:

| what | how it was obtained | why |
| --- | --- | --- |
| adopted MAP-Elites runs, 10 documented seeds | **re-run** | the new measurement |
| incumbent E4 runs | **read** from the committed artifact | DR 0053 rule 2 forbids re-running them |
| GA control, 10 runs | **read** | `run_ga_baseline` takes **no** `slip_admission` — structurally unaffected by the arm, so re-running would reproduce numbers that cannot move |
| DR 0042's headline, both sides | **read** | the incumbent from its own artifact; the adopted side from N4, which already measured `insertion` at that seed |

The documented E4 gates were re-judged **verbatim** — `judge_gates`
imported from `coverage_qd_gates`, never re-implemented, because a
second copy could score the adopted arm by a rule the incumbent was
never held to — and against the **same GA control** the incumbent was
judged against.

**The gate that could fail**: a documented gate that **passed** under
the incumbent and **fails** under the adopted default is a regression
and a blocking finding. A gate that was *already* failing is explicitly
not one — DR 0032's GA-advantage clause has been refuted repeatedly, and
blaming the new arm for it would be a false accusation.

## FINDINGS

### DR 0042's headline, restated — and the trade is not what "coverage fell" implies

At DR 0042's own seed (20260709), same population, same budget:

| | incumbent (`none`) | adopted (`insertion`) | delta |
| --- | --- | --- | --- |
| coverage | 0.898438 | **0.880859** | **−0.017579** |
| **QD** | 404.618236 | **411.738214** | **+7.119978** |
| occupied niches | 460 | 451 | −9 |
| **refusals** | 4,435 | **0** | **−4,435** |
| **SLIP-illegal elites** | 35 | **0** | **−35** |

> **Coverage does not fall for nothing — it buys quality.** L1 refused
> to patch the refusal tax because *"the fix trades against coverage"*.
> It does, and the restatement prices the other side of that trade:
> **nine niches and 0.0176 coverage buy +7.12 QD, the elimination of
> 4,435 wasted evaluations per run, and an archive that is legal under
> the covenant that bred it.**

The incumbent side reproduced N4's measurement exactly (`True`), so the
two artifacts agree and the restatement compares the same loop.

### The documented E4 gates hold — `NO_REGRESSION`

Re-judged over the documented ten paired seeds:

| gate | incumbent | adopted | |
| --- | --- | --- | --- |
| `coverage_gate_met` | **True** | **True** | held |
| `ga_advantage_gate_met` | False | False | **already failing — not a regression** |

| statistic | delta |
| --- | --- |
| `map_elites_coverage_mean` | −0.023633 |
| `map_elites_best_fitness_mean` | **−0.000565** |
| `coverage_advantage_over_ga` | −0.029664 |

**No documented gate that passed now fails.** Mean best fitness is
essentially untouched (−0.000565), and the coverage gate clears its
documented bar with enormous margin either way.

### DR 0032's GA-advantage clause, refuted again — and slightly deeper

`ga_advantage_gate_met` was already `False` under the incumbent and
stays `False`. **This is not a consequence of the adoption**, and the
gate is written so it cannot be reported as one. What the adoption does
change is the margin: `coverage_advantage_over_ga` falls a further
**0.029664**, so the clause is refuted a little more decisively than
before. Recorded, not re-scored — DR 0032's own re-openers are
untriggered and this changes none of them.

## HONEST REMAINDERS

1. **Both committed incumbent artifacts are untouched.**
   `evaluation_loop_scale_stage0.json` and `coverage_qd_gates_stage0.json`
   remain the measurements they were. DR 0042's 0.8984 is **not
   retracted** — it is what the loop achieves under the incumbent, and
   it stays true of that configuration.
2. **The other six loop callers stay pinned**, and four of them
   *measure the defect* and must never migrate (DR 0053).
3. **DR 0046's comparability rule applies**: every coverage and QD
   number here is an **incumbent-geometry** number. The restatement
   changes the admission arm, not the geometry.
4. **One SLIP profile** (`slip_lcd_seed`) — DR 0047's inherited limit. A
   wider palette rejects fewer bootstrap creatures and would move every
   number here.
5. **The GA control was read, not re-run.** That is sound because the
   arm cannot reach it structurally, but it does mean the GA side of the
   comparison carries the incumbent run's own seed noise unchanged.

## Verification

RED — the pins, written before the module existed:

```powershell
PS> python -B -m unittest test_adopted_default_restatement   # (from labs/map_elites_archive)
ModuleNotFoundError: No module named 'adopted_default_restatement'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN:

```powershell
PS> python -B -m unittest test_adopted_default_restatement
----------------------------------------------------------------------
Ran 17 tests in 0.239s

OK
```

The lab invocation that produced the artifact:

```powershell
PS> python -B labs/map_elites_archive/adopted_default_restatement.py
DR 0042 headline (seed 20260709): coverage 0.898438 -> 0.880859 (delta -0.017579); QD 404.618236 -> 411.738214 (+7.119978); niches 460 -> 451 (-9)
  incumbent headline reproduced from N4: True; refusals under the adopted default: 0; illegal elites: 0

E4 gates, re-judged verbatim over the documented ten seeds:
  map_elites_coverage_mean: delta -0.023633
  map_elites_best_fitness_mean: delta -0.000565
  coverage_advantage_over_ga: delta -0.029664
  coverage_gate_met: True -> True
  ga_advantage_gate_met: False -> False

NO_REGRESSION
  already failing (not a regression): ['ga_advantage_gate_met']
  computed 10, replayed 0, 2594.122 s
wrote data/archives/adopted_default_restatement_stage0.json
```

Wall clock **2594.122 s** for ten documented-budget runs — a quarter of
the naive forty-run cost, because the incumbent runs and the GA control
were read rather than re-measured.

## Sources

- `audits/TODO.md` (cycle 25 O3) · `research/decision_records/0056-adopted-default-headline-restatement.md` (the record this study produced)
- `research/decision_records/0053-admission-policy-belongs-at-the-call-site.md` (rules 2 and 3, which scoped this task), `0052-slip-admission-default-insertion.md`, `0042-generation-layer-loop-revisit.md` (the headline restated here, not retracted), `0032-map-elites-ga-gate-disposition.md`, `0046-two-geometry-split.md` (comparability)
- `labs/map_elites_archive/adopted_default_restatement.py` (+ `test_adopted_default_restatement.py`, 17 pins) · `data/archives/adopted_default_restatement_stage0.json`
- `labs/map_elites_archive/coverage_qd_gates.py` (`judge_gates`, imported never re-implemented) · `evaluation_loop_scale.py`
- `data/archives/coverage_qd_gates_stage0.json`, `evaluation_loop_scale_stage0.json`, `slip_admission_default_stage0.json` (all read, none overwritten)
