# Experiment Report: Flipping the `slip_admission` Default — and the Migration Turned Out Not To Be a Regeneration (Cycle 24 · SHARED · N7)

Date: 2026-07-28

## WHY

DR 0052 adopted `insertion` as the `slip_admission` default and
deliberately did **not** flip it, scheduling the migration as N7 with
its blast radius measured. N7 is that migration.

The task's own charter contained the instruction that decided how it
went:

> *Do not start it by flipping the constant — start it by listing every
> artifact and test that moves, because an unlisted one is a silent
> contradiction.*

## WHAT

### Step 1: the inventory, and it was bigger than DR 0052 estimated

DR 0052 said "at least six lab modules". Measured by walking every
`run_evaluation_loop(` call site and checking whether the call names an
arm:

| | count |
| --- | --- |
| production modules calling the loop **implicitly** | **8** |
| committed artifacts they write | **8** |
| implicit call sites in total (production + tests) | **63** |
| test files containing implicit call sites | **7** |
| call sites that already name an arm | 10 |

The two DR 0052 missed are **`generation_arm_evolution`** (DR 0031/0042's
generation bake-off) and **`novelty_evolution`** (DR 0040's selection
bake-off). "At least six" was honest but low; the number is eight.

### Step 2: flip, and let the suite say what breaks

Flipping the default produced **10 failures**, and the most informative
was `test_the_seam_is_byte_identical_when_off`, which asserted

```python
implicit = run_evaluation_loop(**TINY)
explicit = run_evaluation_loop(slip_admission="none", **TINY)
self.assertEqual(implicit, explicit)
```

That is **DR 0047's pinned contract** — *"the incumbent stays
byte-identical when `slip_admission='none'` (pinned)"* — and flipping the
default contradicts it by construction.

It also turned out to be the **weak form** of the pin that ONBOARDING §9
warns about: comparing the implicit call to the explicit one states a
fact about *the default*, not about off-mode identity. The guarantee it
was meant to carry now lives in
`test_the_OFF_result_carries_no_arm_key_at_all`, which pins the off-mode
key set against a **frozen literal** — the stronger form, and the one
that survives a default change.

## FINDINGS

### The migration is not a regeneration, and that is the finding

The obvious reading of "flip the default" is *regenerate all eight
artifacts under the new behaviour and explain the deltas*. Working
through the eight, that reading is **wrong for most of them**, and
wrong in a way that would have destroyed evidence.

**Several of these studies exist to measure the defect.** The clearest
case:

> `generation_refusal_causes` (L1) **is the measurement of the
> 4,435-refusal tax.** Under `insertion` that tax is zero. Regenerating
> it on the new default would not *update* the finding — it would
> **erase the evidence the finding is made of.**

The same applies with less force to three more:

- **`elite_population_measures` (M1)** measured *"48 of 460 elites are
  bootstrap creatures"* — a fact about the unfiltered archive.
  `insertion` prevents those creatures from ever reaching it.
- **`lineage_dominance` (L2)** judged the documented dominance clause
  and reported that the two largest founder lines were founded by WFC
  **bootstrap** creatures. `insertion` removes exactly those.
- **`family_ancestry` (M4)** measured common descent over the founder
  lines the unfiltered loop produces.

And two are **bake-offs**, which are only readable if every arm shares
every other setting with the run that decided them:

- **`generation_arm_evolution`** (DR 0031/0042, generation arms)
- **`novelty_evolution`** (DR 0040, selection arms)

Leaving two whose migration is a genuine documented decision rather than
a side effect:

- **`evaluation_loop_scale`** — E3's study and the source of **DR 0042's
  headline coverage 0.8984**, quoted in decision records, gate reports
  and ONBOARDING.
- **`coverage_qd_gates`** — the E4 gates, judged on the configuration
  they were documented under.

**So the correct migration is: flip the default, and make every
historical study NAME its arm.** Each of the eight now passes
`slip_admission="none"` explicitly, with a comment saying why *that
study* is pinned.

This is the same discipline N2 applied to the probe geometry's
`edges_source`: a study's admission policy is part of what it measured,
so it belongs at the call site where a reader can see it — not in a
default that can move underneath a committed artifact.

### What this means, stated plainly

**The change is prospective. No committed number moves.**

- Every existing study measures exactly what it measured before, and its
  artifact keeps its meaning.
- Every **new** consumer of the loop gets, by default, zero refusal tax
  and an archive that is legal under the covenant that bred it.
- The restated "what the loop achieves under the adopted default"
  numbers are not missing — they were measured by N4 and are committed
  in `data/archives/slip_admission_default_stage0.json` (coverage
  0.847005, QD 394.0508, 0 refusals, 0 illegal elites, over three
  seeds).

A reader who expected this task to improve a published number should
read that as the honest outcome rather than a hedge: **the eight
existing artifacts are records of measurements, and a measurement does
not improve — it is either reproduced or superseded by a new one.**

### The pins that hold it

- `test_the_loop_default_is_the_ADOPTED_arm` — a new caller gets
  `insertion`. This is what makes the fix propagate rather than sit in a
  record.
- `test_the_incumbent_is_still_reachable_and_unchanged` — `"none"` is
  named, reachable, and carries no arm key.
- `test_the_OFF_result_carries_no_arm_key_at_all` — the off-mode key set
  against a **frozen literal**, unchanged by this task and now the sole
  carrier of the off-mode guarantee.

## HONEST REMAINDERS

1. **Two studies are candidates for a real migration, and neither is
   done here**: `evaluation_loop_scale` (DR 0042's headline coverage)
   and `coverage_qd_gates` (the E4 gates). Migrating either means
   restating a number quoted across decision records, gate reports and
   ONBOARDING, with a delta explained at every site. That is a
   documented decision with its own record — **not** a side effect of a
   default change, which is precisely why this task refused to make it
   one.
2. **The four defect-measuring studies should probably never migrate.**
   Their subject is the incumbent's behaviour. If they are ever re-run
   on the new default, it should be as *new* artifacts answering a new
   question, never as regenerations of these.
3. **The promoted engine is untouched.** `slip_admission` still appears
   nowhere in `packages/`; reaching the engine is a separate step with
   its own spec and gate.
4. **DR 0047's byte-identity pin was re-expressed, not deleted.** Its
   guarantee moved to the frozen-key-set pin. A reader of DR 0047 should
   know its literal wording ("the incumbent stays byte-identical when
   `slip_admission='none'`") is still true — what changed is that the
   *implicit* call no longer means `"none"`.

## Verification

The full archive lab, after the flip and the pinning:

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
----------------------------------------------------------------------
Ran 432 tests in 128.738s

OK
```

Byte-identity of a committed artifact under the pinned caller —
`generation_refusal_causes`, chosen because it is the study whose
subject would vanish if the pinning were wrong:

```powershell
PS> python -B labs/map_elites_archive/generation_refusal_causes.py --output-dir <scratch>
PS> python -B <diff script>
committed    sha256: cd8475f59048b17da5038ab9fa2e33d56cd4e8c058c6cf3efc3a8a7e4fd1db9e
regenerated  sha256: 82adaeeff057fa9b56884dae0983cfe5efcc72618a27a93cbc4f71f6eb149d07
BYTE-IDENTICAL: False

--- differences ---
  .metrics.wall_clock_s: 273.776 -> 209.008

identical ignoring wall_clock_s: True
```

**Read that honestly: the hashes differ, and the reason is a stopwatch.**
The *only* differing field is `metrics.wall_clock_s` — a machine-dependent
timing value, which this repo's own convention keeps out of the
deterministic report body precisely because it is not a measurement of
the loop. Every measured field is identical, including
`generation_attempts_total`, the reason-class histogram, the refused-parent
families and the `k2_self_verification` block — the numbers this study
exists to carry.

The claim is therefore stated as what was measured rather than rounded
up to "byte-identical": **every measured field reproduces exactly; the
artifact is not bit-identical because it timestamps its own runtime.**
Had the pinning been wrong, `generation_attempts_total` and the whole
refusal histogram would have collapsed to zero — that is the failure
this check was built to catch, and it did not fire.

The closing sweep. **The artifact count is unchanged at 2,244**, which
is the point: this task regenerated nothing, because nothing needed
regenerating.

```powershell
PS> python -B tools/ci/run_sweep.py
lab:animation_system             OK  OK  [8.2s]
lab:architecture                 OK  OK  [14.2s]
lab:asset_pipeline               OK  OK  [0.3s]
lab:cellular_automata            OK  OK  [28.5s]
lab:ctm_ticks                    OK  OK  [0.1s]
lab:cubff_transducer             OK  OK  [0.5s]
lab:datasets                     OK  OK  [2.3s]
lab:game_loop                    OK  OK  [5.3s]
lab:grid_genome                  OK  OK  [6.7s]
lab:lifecycle_sim                OK  OK  [0.4s]
lab:map_elites_archive           OK  OK  [130.0s]
lab:micro_threads                OK  OK  [7.0s]
lab:package_promotion            OK  OK  [0.2s]
lab:readability_benchmark        OK  OK  [2.4s]
lab:repair_boundary              OK  OK  [2.7s]
lab:runtime_integration          OK  OK  [62.9s]
lab:slip_validator               OK  OK  [0.5s]
lab:wfc_grid                     OK  OK  [4.8s]
lab:workshop_editor              OK  OK  [4.7s]
package                          OK  OK  [5.4s]
cli                              OK  OK (skipped=15)  [3.7s]
game                             OK  OK (skipped=5)  [10.1s]
workshop                         OK  <sys>:0: ResourceWarning: unclosed <socket.socket fd=872, family=2, type=1, proto=0, laddr=('127.0.0.1', 3468)>  [146.6s]
data artifacts                   OK  2244 JSON artifacts valid  [5.8s]

SWEEP GREEN
```

## Sources

- `audits/TODO.md` (cycle 24 N7) · `research/decision_records/0053-admission-policy-belongs-at-the-call-site.md` (the record this study produced) · `research/decision_records/0052-slip-admission-default-insertion.md` (the record that scheduled this migration)
- `research/decision_records/0047-slip-admission-arms.md` (whose byte-identity pin this re-expresses), `0042-generation-layer-loop-revisit.md` (the headline coverage this deliberately does not restate), `0040-novelty-first-evolution-surface.md`, `0031-wfc-generation-adoption.md`
- `research/experiment_reports/2026-07-28-slip-admission-default.md` (N4 — the decision, and the committed numbers under the adopted default), `2026-07-26-generation-refusal-causes.md` (L1 — the defect this pins)
- `labs/map_elites_archive/evaluation_loop_scale.py` (the default, flipped) · `coverage_qd_gates.py`, `elite_population_measures.py`, `family_ancestry.py`, `generation_arm_evolution.py`, `generation_refusal_causes.py`, `lineage_dominance.py`, `novelty_evolution.py` (the eight callers, each pinned with its reason)
- `labs/map_elites_archive/test_slip_admission_arms.py`, `test_evaluation_loop_scale.py` (the re-expressed pins)
