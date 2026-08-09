# Stage 2's Undispositioned Generator Arms — CPPN Rejected, Shape Grammar Watches the Incumbent It Cannot Beat

Date: 2026-08-08 · Cycle 25 · SHARED track · Phase O, task O4

## WHY

The research dossier names **shape grammar** and **CPPN** as
generator-adjacent methods, and neither has ever been dispositioned: no
card, no prototype, no reject/watch verdict — the same class of
documented-and-unmet debt N3 closed for the micro-learner conditions
after twelve cycles. O4 is deliberately **non-archive and non-loop**
after a cycle that spent four of six slices in the archive (the
anti-periscope rule's own instruction).

**The task's charter was corrected before any measurement code was
written** (recorded in the queue at design time, cycle-24's
check-the-instrument lesson applied to a framing):

1. **A bake-off-both framing is wrong for one of the two.** CPPN's
   dossier stance is *"Keep as a late exploratory generator"* — a
   generator bake-off IS its documented role. But shape grammar is filed
   under **Constraint systems**, whose stance is *"Use as validator or
   post-generator stabilizer"* — explicitly not a primary generator. A
   bake-off would have tested it at a job the dossier never gave it, and
   a rejection earned that way would have meant nothing.
2. **Shape grammar's documented role is already shipped.**
   `wfc_grid._finish` is documented in its own docstring as the
   post-generator stabilizer pass and is part of the adopted WFC arm
   (DR 0031). The real open question is sharper: **does a shape-grammar
   stabilizer beat the incumbent `_finish`?**

## WHAT

`labs/wfc_grid/stage2_generator_arms.py` (+ 25 pins in
`test_stage2_generator_arms.py` — the RED written first; see the process
note below). Each arm is judged **in its documented role**, under a rule
and a prediction **pre-registered in the module before the run**:

- **CPPN as a generator**, on the B2 bake-off's own terms: the smallest
  honest compositional pattern-producing network (six seeded hidden
  nodes over normalized x, y, radial distance, and the |x|
  bilateral-symmetry channel; one output channel per generator token;
  argmax per cell; two declared design choices — a centered radial bias
  on the empty channel and a center germ cell; one anchor anointed at
  the strongest body activation). Judged against the **adopted
  constrained layer's committed row** (DR 0042) with B2's own
  `measure_arm` — imported, never re-implemented.
- **Shape grammar as a post-generator stabilizer**, head-to-head against
  the incumbent `_finish` on the same raw-collapse stream: six named,
  deterministic, RNG-free productions (seed germ cell; anchors read as
  body; largest core survives; grow core to the DR 0029 floor; require a
  sensor cell; anoint one anchor), every applied production named in a
  trace — the dossier's stance includes "validator", and an
  unexplainable validator is worthless.
- **The instrument gate**: at the committed protocol (batch 100, seed
  1030, the 30/10/10 stratified split) the harness must reproduce the
  committed `wfc` row of `generation_bakeoff16_stage0.json` **exactly**
  on all five compared keys, or it raises instead of writing an
  artifact. The distinct-rate floor 0.68 is the committed refused
  `random` arm's own measured rate, re-derived from the committed
  artifact at run time so drift fails loudly.
- **Noise floors are measured, never picked**: the incumbent pipeline
  run twice (seeds 1030 and 2061), |Δ| per metric — cycle 22 L3's
  pattern. Measured: 0.0 on both validity and distinct rate.

**Pre-run prediction, recorded first**: CPPN rejects on validity (the
dossier's own named risk, *"hard integration with semantic pixels"*);
shape grammar raises validity over raw collapse but at best ties the
incumbent at its committed 1.0, landing watch.

## FINDINGS

**1. The instrument reproduced the committed row before anything new was
trusted.** All five keys of the committed `wfc` row — validity 1.0,
readability 0.685047, descriptor novelty 0.25, silhouette entropy
6.643856, 100 unique silhouettes — reproduced exactly.

**2. CPPN is REJECTED as a generator: validity 0.12 against the 0.85
dossier bar, and the mechanism is MASS, not incoherence.** Of the 88
invalid bodies, **79 fail only the DR 0029 mass floor** (a connected
core below 18 cells at 16×16) and just 9 disconnect —
`connectedness_rate` is 0.88. The indirect encoding composes coherent,
centered, connected bodies that are simply too small, 79% of the time.
Nothing offsets validity (pre-registered), but the record keeps what
the measurement actually showed the method is good at:

- **symmetry_mean 0.475226** — above the WFC family (wfc 0.3973, hybrid
  0.395171), below the parent-based constrained arm (0.809562). The
  dossier's *"regularity and symmetry"* claim shows up in the
  measurement.
- **100/100 unique silhouettes, training-copy rate 0.0** — it is a true
  de-novo generator (it never saw the corpus), including emitting the
  full rich alphabet with `sensor`, a role the committed wfc row lacks.
- readability_proxy_mean 0.446945 — well below the adopted layer's
  0.79663; distinct rate 1.0.

**3. Shape grammar does its documented job emphatically — and ties the
incumbent it was chartered to beat: WATCH.** On the same 100-candidate
raw-collapse stream (validity **0.01**; 99 disconnected cores, 52
missing anchors — the historical "98% disconnected" measurement
reproduced at 99%), the grammar repairs every candidate to **validity
1.00 with distinct retention 1.0**. The incumbent `_finish` pipeline
also measures 1.00/1.0 at the same protocol, and the two-seed noise
floor is 0.0 — a tie. **By the pre-registered rule a tie is not a
reason to replace a shipped incumbent** (the DR 0031 hybrid-refutation
logic pointed the other way: the challenger is not refuted as a method,
it just adds nothing at the gated criteria).

**4. Recorded, not judged** (the rule pre-registered validity and
distinct retention as the stabilizer's gated axes; these are
observations beside the verdict, not criteria): the grammar-stabilized
arm reads **readability 0.701285 vs the incumbent's 0.685047**
(+0.016238) and **descriptor novelty 0.21 vs 0.25** (−0.04); organ
F1 0.961409 vs 0.961929. Architecturally the grammar **repairs in one
deterministic pass** where the incumbent **spends bounded restarts** —
at this protocol both reach the same end state.

**5. The prediction was confirmed on both arms** — with one honest
refinement the prediction did not contain: it named *semantic-pixel
integration* as CPPN's failure; the measured failure is the **mass
floor** specifically, with connectivity largely intact.

## Verification

RED (the module does not exist; the restored pin file fails on import):

```text
PS> python -B -m unittest discover -s labs/wfc_grid -p "test_stage2_generator_arms.py"
ERROR: test_stage2_generator_arms (unittest.loader._FailedTest.test_stage2_generator_arms)
ImportError: Failed to import test module: test_stage2_generator_arms
ModuleNotFoundError: No module named 'stage2_generator_arms'
FAILED (errors=1)
```

GREEN (the 25 pins, then the whole lab suite):

```text
PS> python -B -m unittest discover -s labs/wfc_grid -p "test_stage2_generator_arms.py"
Ran 25 tests in 0.263s
OK

PS> python -B -m unittest discover -s labs/wfc_grid -p "test_*.py"
Ran 61 tests in 5.372s
OK
```

Lab (documented budget — batch 100, seed 1030; instrument gate shown
passing, then the verdicts):

```text
PS> python -B labs/wfc_grid/stage2_generator_arms.py
{
  "applicable": true,
  ...
  "comparisons": {
    "validity_rate": {"committed": 1.0, "measured": 1.0, "match": true},
    "readability_proxy_mean": {"committed": 0.685047, "measured": 0.685047, "match": true},
    "descriptor_novelty": {"committed": 0.25, "measured": 0.25, "match": true},
    "silhouette_entropy_bits": {"committed": 6.643856, "measured": 6.643856, "match": true},
    "unique_silhouettes": {"committed": 100, "measured": 100, "match": true}
  },
  "reproduced_committed_row": true
}
{
  "cppn": {"verdict": "reject",
    "reason": "validity 0.12 is below the dossier bar 0.85 ..."},
  "shape_grammar": {"verdict": "watch",
    "reason": "ties the incumbent _finish within the measured noise floor (1.0 vs 1.0, noise 0.0) ..."}
}
"prediction_confirmed"
wrote data/wfc_grid/stage2_generator_arms_stage0.json
```

Error-family diagnostic (the mechanism numbers in finding 2 and 3),
computed with the validator's own error strings via `run_baseline`:

```text
CPPN error families: {"body mass below minimum": 79, "required body core is disconnected": 9}
RAW error families: {"missing animation anchor": 52, "required body core is disconnected": 99}
```

## Process note

The RED pin file was designed in the previous session and briefly
committed while O3 was still open (the owner's IDE commits mid-session);
it was removed in commit `2361090` with the lesson recorded — *do not
write a RED into a lab directory until the previous task is committed.*
This slice restored that file **verbatim from git history**
(`git show 6db7fa5:labs/wfc_grid/test_stage2_generator_arms.py`), watched
it fail for the right reason, and only then implemented. One generator
design adjustment was made at GREEN stage, before the study ran: the
empty channel's radial bias was centered (`r − 0.5`) after a pinned seed
produced a germ-only body. No gate, bar, or verdict text was touched
after the run.

## Sources

- `labs/wfc_grid/stage2_generator_arms.py` (+ `test_stage2_generator_arms.py`, 25 pins)
- `data/wfc_grid/stage2_generator_arms_stage0.json` (the artifact)
- `labs/wfc_grid/wfc_grid.py` (`_finish`, the incumbent stabilizer), `labs/wfc_grid/generation_bakeoff16.py` (`measure_arm`, the instrument)
- `data/wfc_grid/generation_bakeoff16_stage0.json` (the committed baseline rows: constrained, wfc, random)
- `docs/project-research/deep-research/01/deep-research.md` (the constraint-systems and indirect-encoding rows; the method matrix)
- `research/decision_records/0031-wfc-generation-adoption.md`, `0042-generation-layer-loop-revisit.md` (the adopted layer), `0057-stage2-generator-arms-dispositioned.md` (this study's record)
- `research/algorithm_cards/cppn_generator.md`, `research/algorithm_cards/shape_grammar_stabilizer.md`
- `sunsetted/TODO.md` (cycle 25 O4, including the two recorded charter corrections)
