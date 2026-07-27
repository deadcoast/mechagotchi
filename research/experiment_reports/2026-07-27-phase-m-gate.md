# Experiment Report: THE PHASE-M GATE — the Cycle That Went Looking for a Gap and Found Its Own Prose (Cycle 23 · SHARED · M6)

Date: 2026-07-27

## WHY

Cycle 23 was planned on Phase L's one unplanned finding, which had
arrived four separate times without anyone looking for it:

> **Every instrument measures a different population from the one the
> archive is actually filled with.**

Phase M was to turn the instruments around and face the creatures
actually in the archive. It did that. It also did something the plan did
not anticipate — and, as in Phase L, the unplanned half turned out to be
the more valuable one.

## THE LADDER

1. **M1 — the archive measured on its own inhabitants** (`ca82fc1`).
   The loop gained its third additive observation seam,
   `collect_elite_grids`. The verdict was
   **`within_sampling_noise` on all four statistics** (highest ratio
   1.70 against a 2.0 bar) — **which partly deflated the premise the
   cycle was planned on**, and is recorded as such. Its lasting result
   is methodological and measured rather than argued: pre-registering
   **two** controls, one per population type with the larger taken,
   **caught a false positive** — `animation_density` reads **5.14× →
   "material"** against the cheap derivation control alone and **0.85 →
   within noise** against the elite control. Also measured: **48 of 460
   elites (10.4%) are bootstrap creatures** (M3's denominator, exact),
   L4's A2 independence **halves** on the elites (max |r| 0.173 →
   0.350), and L4's A3/A4 are **structurally undefined** there — one
   elite per niche means the same-bin denominator is 0 and
   `occupied_4 == occupied_3` for *any* fourth axis. **L4's remainder,
   which called that measurement "cheap", was corrected as understated.**

2. **M2 — the geometry split decided, and the split was not the
   disease** (`3197cbc`, **DR 0046**). L3's statistic could not settle
   it: edge distance is not the unit any ledger number is expressed in.
   Measured in **addresses** instead — disagreement **0.360000** against
   a **measured** control of **0.310333**, ratio **1.16** →
   **`freeze_split`**. The control is the finding: re-deriving the
   **probe** recipe at another seed reassigns **31%** of the population,
   the incumbent **20%**. **The two geometries are two draws from a
   noisy edge-derivation process**, not two coordinate systems, so
   convergence was **refused on the measurement**. Localised to
   `visual_complexity` (0.2647 of address changes), whose seven octile
   edges sit in a **~0.046-wide band** — K3's measure-thinness, now in
   addresses. **K2's cross-geometry claim resolved**: the support
   ceiling is **460 (probe) vs 456 (incumbent)** — L3 said the identity
   was *not established*; M2 says the numbers are **not equal**.

3. **M3 — three fixes that all work, and the rule's winner is the worst
   of them** (`faab322`, **DR 0047**). The covenant admits only **49 of
   256** bootstrap creatures (19.1%); **35 of the 48 bootstrap elites
   are SLIP-illegal**. All three arms drive the **4,435-refusal tax to
   zero**, and every coverage cost lands **below** the measured control
   — so **L1's declined trade is affordable**. The tie-break picks
   `parents`; then the ranking **reverses** on what the rule never
   gated: `parents` is the only arm that **lowers quality** (QD
   404.618236 → 398.954451) and **leaves all 35 illegal elites seated**,
   while `bootstrap`/`insertion` raise mean elite fitness **3.8%** and
   give a **SLIP-clean archive** for three more niches. **The loop
   default was WITHHELD** — promoting the gate's winner would let a rule
   decide a question it did not ask.

4. **M4 — ancestry versus morphology: both answers are true at once**
   (`11dcfad`). The question was **reshaped first**: asking it *across*
   runs is **not well posed**, because each run's founder ids are
   disjoint objects — families recur morphologically, their ancestry
   cannot. Asked within each run against a **measured permutation
   null**: **`common_descent`, consistent across three seeds** (z
   **+21.39 / +15.96 / +17.39**). **Evolution Q3 has a measured answer
   and it is NO.** But **the z is large because the null is tight, not
   because the effect is near-total** — the excess is ~0.16–0.20, about
   **29–31%** of the way to pure lineage determination — and the
   convergence half is real: **2.84–3.30 distinct founder lines per
   family, up to 7**.

5. **M5 — two of the five "gaps" were already on the player's screen**
   (`0497088`, **DR 0048**). The charter said survey before building, so
   the instrument **measures rather than asserts**. **`age` is a
   lifecycle field** and **`mood` is a derived engine value** — both
   engine truth, both already displayed by the game. The prior claim had
   counted lifecycle *homeostasis fields*. **The real gap is three, not
   five**, and the three are three *different kinds*: no **definition**
   (`happiness`), no **mechanic** (`cleanliness`), and a definition that
   would have to be **CHOSEN** from documented-hidden axes (`health`).
   **Nothing was built, and that is the finding.**

## WHAT PHASE M ACTUALLY SETTLED

The cycle answered every question it set itself. But its character is
this:

> **Three of the five slices found that a claim in the repo's own prose
> was wrong — and each was found by reading the engine instead of the
> document.**

- **M1** found L4's remainder **understated**: A3/A4 on the elites are
  not un-run, they are *impossible*.
- **M4** found the recurrent-family count **stale**: prose says **52**,
  the artifact has said **54** since commit `f8c171b` regenerated it.
- **M5** found the visible-state gap **overstated**: five became
  **three**, and two of the "missing" axes were already on screen.

Phase L audited its own *numbers*. **Phase M audited its own
sentences** — and found that the gap between what the repo had measured
and what the repo had *written down* was wider than anyone had checked.

Every one of those corrections is a **dated note beside the original**.
Nothing was rewritten, no artifact was edited to look right in
hindsight, and in all three cases the underlying verdict was unchanged
or strengthened.

**The gates held in both directions, again.** M1's could have fired and
did not. M2 had convergence available and **refused it on the
measurement**. M3 found three adoptable arms and still **withheld the
default change**, because the arms separate on dimensions the gate never
weighed. M5 was chartered to build a player-facing feature and **built
nothing**, because building it would have invented two numbers and
mislabelled a third.

## THE HONEST ACCOUNTING

Two limitations of *this cycle's own* pre-registrations, recorded rather
than repaired after the fact:

- **M3 never gated QD**, and QD moved in both directions across the arms
  (+1.8% for two, −1.4% for the third). The gate answered the question
  it asked; it did not ask about quality.
- **M1's TVD statistic carries a finite-sample bias** and its
  derivation-vs-elite comparison mixes sample sizes. A size-matched
  control would separate bias from shape — **deliberately not done**,
  because changing a statistic after seeing its numbers is re-scoring.

Both are named for whoever runs them next rather than quietly fixed.

## CLOSING SWEEP

```powershell
PS> python -B tools/ci/run_sweep.py
lab:animation_system             OK  OK  [12.6s]
lab:architecture                 OK  OK  [18.9s]
lab:asset_pipeline               OK  OK  [0.8s]
lab:cellular_automata            OK  OK  [47.0s]
lab:ctm_ticks                    OK  OK  [0.1s]
lab:cubff_transducer             OK  OK  [0.7s]
lab:datasets                     OK  OK  [3.3s]
lab:game_loop                    OK  OK  [9.8s]
lab:grid_genome                  OK  OK  [8.7s]
lab:lifecycle_sim                OK  OK  [0.6s]
lab:map_elites_archive           OK  OK  [90.3s]
lab:micro_threads                OK  OK  [10.7s]
lab:package_promotion            OK  OK  [0.2s]
lab:readability_benchmark        OK  OK  [3.5s]
lab:repair_boundary              OK  OK  [5.5s]
lab:runtime_integration          OK  OK  [102.5s]
lab:slip_validator               OK  OK  [0.7s]
lab:wfc_grid                     OK  OK  [7.7s]
lab:workshop_editor              OK  OK  [9.6s]
package                          OK  OK  [8.6s]
cli                              OK  OK (skipped=15)  [3.7s]
game                             OK  OK (skipped=5)  [15.7s]
workshop                         OK  <sys>:0: ResourceWarning: unclosed <socket.socket fd=312, family=2, type=1, proto=0, laddr=('127.0.0.1', 8268)>  [228.8s]
data artifacts                   OK  2240 JSON artifacts valid  [0.7s]

SWEEP GREEN
```

*(A gate slice changes no code, so it carries no RED/GREEN pair of its
own — the closing sweep is its verification, following the Phase-K and
Phase-L gate precedent. The RED/GREEN blocks with pasted output live in
the five slice reports this one consolidates.)*

**19 lab suites + package 295 + workshop 92 + game 183 + CLI 23 —
2,240 JSON artifacts, 0 invalid — SWEEP GREEN.**

Against the Phase-L close (2,235 artifacts) the cycle added **5
artifacts**, one per slice. The archive lab grew **219 → 319** (M1's 36,
M2's 20, M3's 25, M4's 19) and `architecture` **14 → 27** (M5's 13).
Workshop, CLI and game are unchanged — M5 measured the engine and cited
the game by file reference rather than importing it, which the boundary
law requires.

The ledger now holds **261 experiment reports, 77 algorithm cards and 48
decision records** (through **DR 0048**).

Two recorded environment facts, unchanged since Phase K: the workshop
suite's teardown `ResourceWarning` (a test artifact, not a failure), and
the `slip_validator` sweep rewriting the two `data/slips`
pydantic-version observation artifacts, which are per-run environment
observations by design and are restored with `git checkout`, never
committed.

## HONEST REMAINDERS (the cycle 24 material)

**Named by this cycle's own records:**

1. **Do 600 creatures determine the octile edges at all?** (M2) The
   deepest thing this cycle found: `visual_complexity` reassigns **26%**
   of the population on a resample, and the edges sit in a 0.046-wide
   band. That is a defect **underneath every coverage number in the
   repo**, and it is a question about E1's derivation protocol rather
   than about which population feeds it.

   > **Dated note, 2026-07-27 — ANSWERED by cycle 24 N1 (DR 0049), and
   > the phrase "underneath every coverage number in the repo" is
   > OVERSTATED.** Both halves measured. (a) The protocol is
   > **`sampling_limited`, not structurally indeterminate** — slope
   > **-0.4186** against sampling theory's -0.5 inside a measured band,
   > re-addressing falling monotonically 0.7268 (N=75) → **0.1278**
   > (N=4800). So 600 does not determine the *addresses*, and neither
   > does 4,800 — but the edges are under-sampled, not unknowable.
   > (b) **The coverage numbers were already at their measurement
   > floor.** Against a measured floor of 4 niches, the incumbent's
   > occupied-niche count moves exactly 4 at N=600 while 31.7% of
   > individual creatures re-address — and at N=4800 re-addressing has
   > improved 2.5× while ceiling movement is *higher*. The instability
   > is real in addresses and **does not reach the aggregate every
   > coverage figure is counted in**. `derivation_count` therefore stays
   > at 600 (DR 0049). The 26% and the 0.046 band above are both
   > confirmed — and the band is now measured **constant across a 64×
   > size range**, so measure-thinness is structural and permanent while
   > only the edge placement inside it is sampled. See
   > `research/experiment_reports/2026-07-27-derivation-size-stability.md`.
2. **The probe's edges are not frozen** (M2 / DR 0046). The incumbent is
   protected from its own 20% instability by being committed once; the
   probe is re-derived live. No committed probe number is wrong, but
   each is contingent on a draw no artifact records.
3. **The `slip_admission` default is undecided** (M3 / DR 0047), and
   what would decide it is named: quality and archive legality
   pre-registered *alongside* coverage, multi-seed. On current evidence
   the likely winner is **`insertion`**, not the tie-break's `parents`.
4. **`health` is withheld, not refused** (M5 / DR 0048) — the one absent
   visible axis with a real engine source, needing a record that
   declares its definition CHOSEN and gates it, including on whether a
   player-facing "health" that is really grid-stability is honest
   labelling or a euphemism.
5. **The scored candidate stream** (M1) — what would answer L4's A3/A4
   on the population the archive is actually filled *from*, as opposed
   to the winners it ends up holding.
6. **`cleanliness` needs a MECHANIC** and **`happiness` needs a
   DEFINITION** (M5) — neither is a display gap.
7. **A size-matched TVD control** (M1); a **game-side snapshot pin** for
   age and mood (M5); the **documented HIDDEN axes**, still never
   surveyed per-axis.

**Standing, unchanged:** `animation_density`'s adoption (the
owner-deferred human panel); the 576-vs-512 repertoire divergence;
Stage 2's undispositioned arms (**shape grammar**, **CPPN**); the
unbuilt method tracks (MRF-lite, Lenia, reaction–diffusion, the MDP
sandbox, the QDax shadow port, z3/SMT); the micro-learner ablation
conditions **E/F/G**, never instantiated since cycle 12; the **24×24
scale-up**; the undiluted rich-site regrowth instrument and the 0.525
ceiling; the analytical emptiness argument; richer callback export
states; which forecast keys enable the DR 0045 density rider in a
shipped client; the owner-deferred human-study block; DR 0032's
re-openers; and the first green CLOUD CI run, which awaits a push never
made unasked.

## VERDICT

**Phase M is green.** The archive was measured on its own inhabitants
for the first time; the two-geometry split was decided by record and
the decision was *refusal*, on evidence; the unbreedable-bootstrap fix
was measured three ways and found affordable, with the default still
withheld; a documented ALife question was answered with both of its
halves reported; and a player-facing feature was chartered, surveyed,
and deliberately **not built**.

Its real character is that **it audited the repo's own prose against the
repo's own engine, and the prose lost three times.** A project whose
documentation is its deliverable has to be able to find that, and to
record it beside the original rather than over it.

Cycle 23 archives to `audits/complete/23/`. Cycle 24 (**Phase N — the
descriptor space earns its edges**) is planned from the remainders above
and the still-unmet documentation.

## Sources

- `audits/TODO.md` (cycle 23, M1–M6) → `audits/complete/23/TODO.md`
- `research/experiment_reports/2026-07-27-elite-population-measures.md` (M1), `2026-07-27-geometry-decision.md` (M2), `2026-07-27-slip-admission-arms.md` (M3), `2026-07-27-family-ancestry.md` (M4), `2026-07-27-companion-state-survey.md` (M5)
- `research/decision_records/0046-two-geometry-split.md`, `0047-slip-admission-arms.md`, `0048-visible-companion-state-axes.md` (the cycle's three new records)
- Dated correction notes added this cycle: `2026-07-26-animation-density-axis.md` (L4's remainder), `2026-07-21-generation-arm-loop.md` (K2's cross-geometry claim), `2026-07-09-recurrent-families.md` / `2026-07-09-phase-e-gate.md` / `research/algorithm_cards/recurrent_families.md` / `research/decision_records/0032-map-elites-ga-gate-disposition.md` (the 52→54 count), `2026-07-26-phase-l-gate.md` (the visible-state count)
- `data/archives/elite_population_measures_stage0.json`, `geometry_decision_stage0.json`, `slip_admission_arms_stage0.json`, `family_ancestry_stage0.json` · `data/architecture/companion_state_survey_stage0.json`
- `research/experiment_reports/2026-07-26-phase-l-gate.md` (the cycle this one opened from)
- `docs/project-research/validity-research.md` (§1.17), `deep-research/01/deep-research.md`, `research/questions.md` (Evolution Q3)
- `tools/ci/run_sweep.py` (the closing sweep)
