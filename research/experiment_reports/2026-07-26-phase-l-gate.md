# Experiment Report: THE PHASE-L GATE — the Cycle That Audited Its Own Ledger (Cycle 22 · SHARED · L6)

Date: 2026-07-26

## WHY

Cycle 22 opened on a survey finding rather than a remainder. The
Phase-K gate went looking through the still-unmet documentation and
found that the MAP-Elites evaluation gate has a second clause —
*"no single lineage > 40% of occupied cells"* — that **had never once
been judged in the project's history**. That was the sharpest unmet
item in the repo, and it set the cycle's shape: Phase L was to settle
the **descriptor space** — the geometry that decides what "coverage
0.8984" and "460 niches" actually *mean*.

It did that. It also did something the plan did not anticipate, which
turned out to be the more valuable half.

## THE LADDER

1. **L1 — the refusal-cause histogram** (`7a2c67d`). The cheapest
   instrument in the queue, and it **corrected DR 0042's reading of its
   own number twice**. The count reproduces exactly (4,435, matching
   both the committed artifact and the loop's independent counter), but
   the **rate is 7.2%, not ~22%** — the old figure divided by the
   *scored budget* where novelty-first requests 61,440 attempts — and
   the promoted path refused **zero** invalid candidates. All 4,435
   refusals are the SLIP rejecting the **parent**: a selection fact,
   not a generator fact. The mechanism closes on itself — origin 100%
   **bootstrap**, exactly as `_acceptable` guarantees, since it
   requires SLIP alignment to emit. Hence generation 1 refusing **73.8%**
   of its requests, decaying to a flat **38-per-generation tax unbroken
   for 40 generations**.

2. **L2 — the lineage-dominance clause, judged at last** (`5e9dff5`).
   The rule pre-registered before the run; **PASS at 0.2848** against
   the documented ≤ 0.40 bar, across 38 founder lines. Reported beside
   the verdict and deliberately outside it: **four founder lines hold
   half the archive** — a clause about one lineage cannot see a cartel
   of four — with the bar **not** widened to meet an interesting
   number. And the dominant lines were founded by the *losing*
   generator: the two largest (39.4% between them) are WFC **bootstrap**
   creatures, though every elite was bred by the adopted `constrained`
   layer. Generation layer and founder stock are independent facts,
   separated here for the first time.

3. **L3 — the geometry is not stale, it is SPLIT** (`029f468`). The
   task's own premise was tested first and **refuted**: E1's protocol
   re-run today reproduces the committed edges **exactly** (drift 0.0
   against a *measured* 0.0102 sampling control), because the frozen
   artifact was regenerated at the DR 0038 commit itself. So K3's
   measure-thin windows are real and the quantization hypothesis
   **hardens**. What the measurement surfaced instead had never been
   written down: **the repo runs two scale geometries.** The loop and
   the E4 gates consume frozen **train**-derived edges;
   `reachability_probe` and `occupancy_saturation` derive **live from
   all 50 seeds** — differing by 0.0375, **3.7× the control**. So
   `460/512 occupied` and `508/512 reachable` are counted in different
   coordinate systems, and have been read against each other in prose.

4. **L4 — `animation_density` earns its place and still cannot be
   adopted** (`513e3be`). The definition is declared **CHOSEN**: the
   documentation names the axis exactly once, in a JSON example, and
   never defines it. Every machine gate passes — spread, independence
   (max |r| **0.173**), and discrimination at **2.7× the bar** (of the
   656 pairs sharing the same three-axis bin, **54.3%** separate) —
   with the cost reported (occupied 289 → 448; coverage 0.5645 →
   0.1094). Verdict `adoptable_pending_blocked_clause`: the documented
   selection criterion needs the owner-deferred human panel, and **no
   proxy was substituted**.

5. **L5 — density as pressure** (`308910c`, **DR 0045 ADOPTED**). The
   checkpoint forecast stops lying about the biology. The defect's
   mechanism diagnosed exactly: with the replication and lineage
   channels structurally absent, pressure rides on entropy and
   diversity — **both of which fall as a soup organizes** — so the
   engine read organization as calm. Density is the one carried channel
   that rises. The signal is **derived, not calibrated** (a ceiling of
   256/10 = 25.6, independent of tape length, from the language's own
   alphabet), and **the DR's pre-run prediction of ≈ +0.041 matched the
   measured +0.040617 to four decimal places**. Inversion −0.034293 →
   **+0.006324**, agreeing with the lit-channel ground truth.

## WHAT PHASE L ACTUALLY SETTLED

**Three of the five slices corrected something the ledger already
said.** L1 corrected DR 0042 twice — a rate and a diagnosis. L3
refuted the cycle plan's own stated premise and found two geometries
being compared as though they were one. L5 corrected a defect I3 had
recorded honestly and could not fix at the time.

That is the cycle's real character: **Phase L is where the repo audited
its own recorded numbers and found several of them wanting.** And the
discipline held under that pressure — *nothing was rewritten*. Every
correction is a dated note beside the original wording, every
superseded claim still says what it said, and no artifact was edited to
look right in hindsight. A ledger that can correct itself without
erasing itself is worth more than one that was never wrong.

The gates also held in both directions. L2 passed and still refused to
widen its bar to capture a more interesting number. L4 passed every
machine gate and still refused to claim adoption, because the
documented criterion is a human measure and substituting a proxy is
precisely the error this project has already been burned by once. L5
adopted — and its adoption is credible *because* the prediction was
written down first and could have missed.

## WHAT PHASE L OPENED

One finding kept recurring without being planned, in four separate
slices, and it is the strongest thing this cycle produced:

> **Every instrument measures a different population from the one the
> archive is actually filled with.**

- **L1**: the elites that hold niches forever are SLIP-illegal
  **bootstrap** creatures.
- **L2**: the dominant founder lines are **bootstrap**-founded, not
  seed-corpus-founded.
- **L3**: the geometry is calibrated on `build_population`, while the
  archive is filled by `generate_candidate` — and the one attempt to
  measure that stream produced 120 of 600 requested, a bound only.
- **L4**: the candidate axis was judged on the derivation population,
  not on the loop's elites.

Four instruments, four different questions, one convergent answer. That
is cycle 23's spine, and the L2 lineage seam already exposes the elite
set, so it is cheap to act on.

## CLOSING SWEEP

The full sweep, workshop included, run at this gate before anything was
written:

```powershell
PS> python -B tools/ci/run_sweep.py
lab:animation_system             OK  OK  [11.8s]
lab:architecture                 OK  OK  [17.7s]
lab:asset_pipeline               OK  OK  [0.5s]
lab:cellular_automata            OK  OK  [40.1s]
lab:ctm_ticks                    OK  OK  [0.1s]
lab:cubff_transducer             OK  OK  [0.6s]
lab:datasets                     OK  OK  [3.0s]
lab:game_loop                    OK  OK  [7.8s]
lab:grid_genome                  OK  OK  [7.7s]
lab:lifecycle_sim                OK  OK  [0.5s]
lab:map_elites_archive           OK  OK  [51.5s]
lab:micro_threads                OK  OK  [8.5s]
lab:package_promotion            OK  OK  [0.1s]
lab:readability_benchmark        OK  OK  [2.7s]
lab:repair_boundary              OK  OK  [3.5s]
lab:runtime_integration          OK  OK  [85.0s]
lab:slip_validator               OK  OK  [0.5s]
lab:wfc_grid                     OK  OK  [5.7s]
lab:workshop_editor              OK  OK  [6.0s]
package                          OK  OK  [6.8s]
cli                              OK  OK (skipped=15)  [3.7s]
game                             OK  OK (skipped=5)  [12.8s]
workshop                         OK  <sys>:0: ResourceWarning: unclosed <socket...>  [174.9s]
data artifacts                   OK  2235 JSON artifacts valid  [0.6s]

SWEEP GREEN
```

**19 lab suites + package 295 + workshop 92 + game 183 + CLI 23 —
2,235 JSON artifacts, 0 invalid — SWEEP GREEN.**

Against the Phase-K close (game 174, 2,230 artifacts) the cycle added
**9 game pins** (L5's consumer contract) and **5 artifacts**. The
archive lab grew 142 → **219** across the cycle (L1's 22, L2's 17, L3's
17, L4's 21) and `cubff_transducer` 43 → **58** (L5's 15). Workshop 92
and CLI 23 are unchanged and verified so: `git diff --name-only
5c4bee3..308910c` matches no file under `workshop/` or `tools/`.

Two recorded environment facts, unchanged from the Phase-K gate: the
workshop suite's teardown `ResourceWarning` (a test artifact, not a
failure — the suite is OK), and the `slip_validator` sweep rewriting
the two `data/slips` pydantic-version observation artifacts, which are
per-run environment observations by design (review finding H-01) and
are restored with `git checkout`, never committed.

## HONEST REMAINDERS (the cycle 23 material)

**From Phase L's own records:**

1. **The archive has never been measured on its own inhabitants** (the
   convergent L1/L2/L3/L4 finding above). Every geometry, occupancy and
   axis number in the ledger is measured on a derivation or bootstrap
   population. The L2 lineage seam already exposes the elite set.
2. **The geometry split is diagnosed, NOT repaired** (L3). Making the
   surfaces agree means choosing one calibration population and
   re-deriving — which changes what every historical coverage number
   means. That is a gated record of its own, and it must state plainly
   that prior artifacts stay true under the edges they were measured
   with.
3. **The unbreedable bootstrap elites are unfixed by choice** (L1).
   Filtering the bootstrap, refusing SLIP-illegal elites at insertion,
   and restricting parent selection are three different changes, and at
   least one **trades against coverage** — a niche whose only occupant
   is SLIP-illegal goes empty. It needs a pre-registered gate, not a
   patch.
4. **A founder line is not an E5 recurrent family** (L2). One is
   ancestry, the other descriptor similarity. Whether the 52 recurrent
   families share ancestry or converge from different lines is a
   genuinely interesting question and has never been asked.
5. **`animation_density` waits on a human panel** (L4), and the
   576-vs-512 repertoire divergence (L2) stands declared but unresolved.
6. **Density recovers direction, not magnitude** (L5) — ~2.4% of the
   callback path's gap — and the rider is OFF by default in the engine;
   which forecast keys enable it in a shipped client is a client
   decision this record did not make.

**From the still-unmet documentation** (the Phase-K survey, re-verified
here for what cycle 22 closed):

7. **Five of the eight documented VISIBLE companion state axes have no
   field in the engine.** `validity-research.md` §1.17 names visible
   state as *hunger, happiness, energy, cleanliness, mood, age, health,
   bond*; the engine's lifecycle carries `hunger, energy, stress, bond,
   grid_stability`. **`happiness`, `cleanliness`, `mood`, `age` and
   `health` are absent** — and these are the *player-facing* ones. (Some
   documented *hidden* axes exist under other names on other surfaces —
   mutation pressure in the CuBFF traits, lineage fitness in the archive
   — so the hidden list needs a per-axis survey rather than a headline.)
   This is the largest documented GAME-facing gap in the repo.

   > **CORRECTED BY MEASUREMENT, 2026-07-27** (cycle 23 M5 —
   > `2026-07-27-companion-state-survey.md`, **DR 0048**): **the count
   > is three, not five, and this is not the largest player-facing gap
   > on the corrected evidence.** `age` **is** a lifecycle field
   > (`age_ticks`, set at construction and incremented every tick,
   > reported as `survival_ticks`), and `mood` **is** a derived engine
   > value (`select_animation_state` returns `(animation, mood)`, since
   > Phase C) — **both are engine truth and both are already displayed
   > by the game** (`app.py:316`, `session.py:149`/`156`). The claim
   > above counted lifecycle *homeostasis fields*, which is a narrower
   > question than "has an engine field". The real gap is `happiness`,
   > `cleanliness` and `health` — and they are three *different kinds*
   > of gap (no definition; no mechanic; a definition that would have to
   > be CHOSEN from documented-HIDDEN axes). The wording above stands as
   > what the Phase-K/L survey measured.
8. **Stage 2 remains partially met**: shape grammar and CPPN are named
   arms with no lab, no module and no record — still undispositioned.
9. **Unbuilt method tracks**, each with zero implementation hits:
   MRF-lite, Lenia/Flow-Lenia, reaction–diffusion, the MDP sandbox, the
   QDax shadow port, and z3/SMT (WATCH by DR 0011's own words).
10. **The micro-learner ablation conditions E/F/G** (Q-table, tiny
    decision tree, Bayesian counter) were never instantiated.

    > **Dated note, 2026-07-28 — CLOSED by cycle 24 N3 (DR 0051).** All
    > three built and judged through the D6 gates verbatim: **E
    > `qtable_policy` KEPT** (+55.459% skill), **F `tiny_tree_router`
    > DROPPED** (−1.776% — the depth-2 split is worse than a depth-1
    > stump), **G `bayes_keeper_counter` DROPPED** (+2.756%, under half
    > the bar). Every candidate's welfare cost is under 1.2%, so all
    > three were decided on skill, reproducing D6's saturated decision
    > seam. The kept-five roster is **unchanged**, and the committed D6
    > artifact regenerates **byte-identical**. Nothing is promoted. See
    > `research/experiment_reports/2026-07-28-candidate-learner-ablation.md`.
11. **The 24×24 scale-up** (DR 0014's re-opener) and the unpromoted
    **scale-geometry seam**.
12. **The human-study block** stays owner-deferred and
    prepared-not-blocking; the transducer study's "preference" number
    remains a labelled PROXY.
13. **Standing**: DR 0032's re-openers (untriggered), per-clip
    choreography, community/registry (DR 0035), and the first green
    CLOUD CI run, which awaits a push never made unasked.

## VERDICT

**Phase L is green.** The descriptor space was judged on the engine's
own numbers, with every rule pre-registered: a documented clause that
had never been measured now has an answer, a geometry suspected of
being stale was proven current *and* found to be doubled, a candidate
axis earned every machine gate without being allowed to claim adoption,
and a forecast that told players the opposite of its own biology was
corrected by a signal derived from the language's alphabet rather than
fitted to a wanted result.

The cycle's honest character is that it spent much of its effort
**auditing numbers the ledger already reported** — and corrected three
of them without erasing a single original.

Cycle 22 archives to `audits/complete/22/`. Cycle 23 (**Phase M — the
archive meets its own inhabitants**) is planned from the convergent
finding above and the documentation: the elite-population re-measure
(1), the geometry-split decision (2), the unbreedable-bootstrap gate
(3), the ancestry-vs-family question (4), and the documented visible
companion state axes (7) — the largest player-facing gap the survey
found, and the cycle's GAME-track balance after an archive-heavy
Phase L.

## Sources

- `audits/TODO.md` (cycle 22, L1–L6) → `audits/complete/22/TODO.md`
- `research/experiment_reports/2026-07-26-generation-refusal-causes.md` (L1), `2026-07-26-lineage-dominance.md` (L2), `2026-07-26-geometry-consistency.md` (L3), `2026-07-26-animation-density-axis.md` (L4), `2026-07-26-density-as-pressure.md` (L5)
- `research/decision_records/0045-density-as-pressure.md` (the cycle's one new record) · `0042-generation-layer-loop-revisit.md` and `0043-callback-forecast-adoption.md` (both carry dated corrections from this cycle)
- `research/experiment_reports/2026-07-26-phase-k-gate.md` (the survey that opened this cycle)
- `data/archives/generation_refusal_causes_stage0.json`, `lineage_dominance_stage0.json`, `geometry_consistency_stage0.json`, `animation_density_axis_stage0.json` · `data/game_client/density_pressure_stage0.json`
- `docs/project-research/validity-research.md` (§1.17 — the visible/hidden state axes), `docs/project-research/deep-research/01/deep-research.md` (the gate clause at 205; the four-axis descriptor at 526-532; the interpretability clause at 204), `docs/project-research/research.md`, `research/questions.md`
- `tools/ci/run_sweep.py` (the closing sweep)
