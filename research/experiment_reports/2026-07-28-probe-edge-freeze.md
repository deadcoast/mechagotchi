# Experiment Report: The Probe's Edges, Frozen — and the Defect Was Not the One the Queue Described (Cycle 24 · SHARED · N2)

Date: 2026-07-28

## WHY

DR 0046 named this its **strongest** follow-on. The repo runs two scale
geometries, and DR 0046 froze the split rather than converging it — but
the two are protected very differently:

- the **incumbent** is derived once and **committed**; every consumer
  reads it through `load_frozen_scale_edges()`;
- the **probe** is **re-derived live on every run**, from three separate
  call sites each carrying its own copy of the recipe.

DR 0049 then measured what that exposure is worth: re-deriving the probe
recipe at another seed **re-addresses 31% of a population**. The
incumbent is protected from exactly that; the probe was not.

## WHAT

### The charter's premise is wrong, and the real defect is sharper

`audits/TODO.md` recorded that each probe number *"is contingent on a
draw **no artifact records**"*. Read against the committed artifacts
rather than the sentence:

| artifact | records the edges it counts under? |
| --- | --- |
| `reachability_probe_stage0.json` | **YES** — at `metrics.edges` |
| `occupancy_saturation_stage0.json` | **NO** |
| `reachability_escalation_stage0.json` | **NO** |

So the probe geometry was never unrecorded. **One artifact recorded it
and two others silently depended on the same draw**, with nothing
pinning any of them together — a re-derivation at a different seed or
count would have moved all three and **only one would have shown it**.
Worse, K3's blocking-axis bounds are expressed as *"the required octile
interval from the frozen edges"* in an artifact that carries no edges at
all.

This is the third cycle running in which reading the engine contradicted
a sentence about the engine, and the correction makes the task *more*
worth doing, not less.

### The rule, pre-registered in the module before the run

Four gates, every verdict first-class.

- **G1 PROVENANCE** — the frozen edges must equal the edges
  `reachability_probe_stage0.json` already records, because that is the
  draw the committed 508/512 was counted under. **Structural, with no
  tolerance**: the two are supposed to be the same object, and a
  tolerance would let a real redefinition pass as rounding.
- **G2 DETERMINISM** — two independent derivations at the documented
  parameters must be identical. DR 0046 *asserted* the probe is
  "deterministic in practice (a fixed default seed)"; this measures the
  claim instead of inheriting it.
- **G3 CONSUMER INVARIANCE** — the probe-side headline numbers
  re-expressed against the frozen set must not move, judged against a
  **MEASURED** floor (DR 0049's construction): hold the frozen edges
  fixed, resample only the counted population, and see how far the count
  moves for reasons that have nothing to do with the freeze. The
  **tightest** measured floor is taken, so a movement must sit inside
  the *strictest* noise estimate before it is called noise.
- **G4 SEPARATION** — the frozen probe set must **not** equal the frozen
  incumbent set. DR 0046 refused convergence on the measurement; a
  freeze that quietly adopted the incumbent edges would undo that record
  without saying so.

**Sizing** follows DR 0049's measured guidance: frozen at E1's own
**600**, because a larger derivation buys address stability but *not*
aggregate stability (the probe's occupied-count movement never reaches
the measured floor anywhere on a 64× ladder), while 600 keeps the two
geometries size-comparable and is the draw every committed probe-side
number was already counted under.

## FINDINGS

### All four gates pass — `FREEZE ACCEPTED`

| gate | verdict | evidence |
| --- | --- | --- |
| G1 provenance | **`provenance_matched`** | a fresh derivation reproduces the recorded probe edges exactly |
| G2 determinism | **`reproducible`** | two independent derivations identical |
| G3 consumer invariance | **`invariant`** | both headline numbers recount **exactly** |
| G4 separation | **`separated`** | max abs delta **0.037500** |

**G3 is the one that could have embarrassed the ledger, and it did
not.** Both committed probe-side headlines were recomputed from scratch
under the frozen set:

| headline | committed | re-expressed | delta |
| --- | --- | --- | --- |
| support ceiling (`occupancy_saturation`) | **460** | **460** | **0** |
| reached by generators (`reachability_probe`) | **495** | **495** | **0** |

This matters because M2 had already found one cross-geometry headline
(K2's 460) that did not survive being recounted. These two do. The
freeze is a **verified** no-op on the committed numbers, not an assumed
one — and `occupancy_saturation`'s ceiling is now confirmed to have been
counted under exactly the edges `reachability_probe` recorded, which was
previously an assumption nothing checked.

G4's separation of **0.037500** is precisely the figure L3 measured for
the split, so the two geometries remain the two geometries DR 0046
decided to keep.

### The freeze removes one contingency and leaves another standing

The measured floors are the interesting part, and they qualify how `460`
should be read:

| floor | population | distinct counts across resamples | pairwise movements | floor |
| --- | --- | --- | --- | --- |
| evaluation | 3,000 | `[460, 457, 462, 447, 454, 451]` | `[3, 15, 3]` | **7** |
| pool | 9,000 | `[495, 497, 493, 496]` | `[2, 3]` | **2.5** |

The first replicate of each is the committed population, which is why
each series opens on the committed number.

> **Freezing the edges does not freeze the number.** The support ceiling
> over a 3,000-creature evaluation population ranges **447–462** across
> six draws. The committed **460** is one draw from that spread, and
> N2 removes the *derivation* contingency without touching the
> *population* contingency.

That is not a defect this task was chartered to fix, and no attempt is
made to fix it here. It is stated because a reader who now sees "frozen"
beside the support ceiling could reasonably conclude the number is
pinned, and it is not — only the coordinate system it is counted in is.

### The probe geometry is measurably noisier in the aggregate than the incumbent

The two floors were measured over **the same six populations** (same
seeds, same stride, same corpus — DR 0049 and this study share the
construction), differing *only* in which frozen edge set does the
binning:

| geometry | pairwise movements at 3,000 | floor |
| --- | --- | --- |
| incumbent (DR 0049) | `[2, 6, 4]` | **4** |
| probe (here) | `[3, 15, 3]` | **7** |

Because the populations are identical and only the geometry differs,
this is a controlled comparison of the two geometries' *variability* —
not of their levels, which DR 0046's comparability rule forbids reading
against each other. It is **suggestive, not established**: three pairs
each, and the probe's floor is carried largely by one movement of 15.
It does sit consistently with DR 0049's finding that the probe's
occupied-count movement never reached its floor anywhere on the ladder
while the incumbent's did.

### What the freeze actually changed in the code

The recipe now lives in **one** place (`derive_probe_edges`) instead of
three private copies. All three probe-side derivation sites —
`build_reachability_report`, `build_escalation_report` and
`build_occupancy_report` — call one loader, and **each artifact now
records `edges_source`** so the draw is visible in every future run
rather than inferable only from a module's source.

The loader keeps the parameters honest rather than overriding them: a
caller passing the documented count and seed gets the **frozen** set; a
caller asking for any other draw gets a **live** derivation and the
artifact says `"live"`. Silently returning frozen edges to a caller who
asked for a different derivation would have made the parameter a lie.

**The parity pin is what makes this real**: a live re-derivation is
asserted equal to the committed frozen set on every suite run, so
drift **fails the suite** instead of silently re-addressing 31% of
creatures.

## HONEST REMAINDERS

1. **The two engine move-set descents were NOT re-run.** 508/512 is a
   composed number — 495 reached by the generators (a binning result,
   re-expressed here) plus 8 from the probe's descent and 5 from K3's
   escalation (search results). The descent counts are unchanged
   **because the edges are identical**, which is G1 — not because they
   were recomputed. Had the edges moved, re-running both would have been
   mandatory.
2. **`occupancy_saturation` and `reachability_escalation` still do not
   carry the edges in their own committed artifacts.** They now name a
   committed source and record `edges_source`, and regenerating those
   two artifacts to carry it is a re-run of each — named here rather
   than silently skipped.
3. **Freezing the edges does not freeze the headline numbers** (see
   above): the support ceiling spans 447–462 over evaluation resamples.
4. **The floors rest on three and two pairs respectively.** A floor that
   coarse bounds the movement; it does not resolve a small one.
5. **The cross-geometry variability comparison is suggestive only**, and
   the probe's floor is carried largely by a single movement of 15.
6. **DR 0046's comparability rule is untouched** — probe-geometry
   numbers still may not be read against incumbent-geometry numbers.

## Verification

RED — the pins, written before the module existed:

```powershell
PS> python -B -m unittest test_probe_edge_freeze   # (from labs/map_elites_archive)
Traceback (most recent call last):
  File "C:\Python314\Lib\unittest\loader.py", line 137, in loadTestsFromName
    module = __import__(module_name)
  File "labs\map_elites_archive\test_probe_edge_freeze.py", line 28, in <module>
    from probe_edge_freeze import (  # noqa: E402
    ...<16 lines>...
    )
ModuleNotFoundError: No module named 'probe_edge_freeze'


----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN — the new pins together with the three rewired consumers' own
suites, which must still pass unchanged:

```powershell
PS> python -B -m unittest test_probe_edge_freeze test_occupancy_saturation test_reachability_probe test_reachability_escalation
................................................
----------------------------------------------------------------------
Ran 48 tests in 53.007s

OK
```

The lab invocation that produced the artifact:

```powershell
PS> python -B labs/map_elites_archive/probe_edge_freeze.py
G1 provenance   -> PROVENANCE_MATCHED
G2 determinism  -> REPRODUCIBLE
G4 separation   -> SEPARATED (max |delta| 0.037500)
  support_ceiling: committed 460 -> re-expressed 460 (delta 0)
  reached_by_generators: committed 495 -> re-expressed 495 (delta 0)
  floors: evaluation 7, pool 2.5, tightest 2.5
G3 invariance   -> INVARIANT

FREEZE ACCEPTED
wrote data/archives/probe_edge_freeze_stage0.json
```

Wall clock 447.912 s.

The archive lab total, measured rather than quoted (N1's baseline of 365
plus this slice's 30 pins — it reconciles here, which N1's did not):

```powershell
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
----------------------------------------------------------------------
Ran 395 tests in 193.366s

OK
```

The full sweep:

```powershell
PS> python -B tools/ci/run_sweep.py
lab:animation_system             OK  OK  [15.5s]
lab:architecture                 OK  OK  [18.8s]
lab:asset_pipeline               OK  OK  [0.6s]
lab:cellular_automata            OK  OK  [44.2s]
lab:ctm_ticks                    OK  OK  [0.1s]
lab:cubff_transducer             OK  OK  [0.7s]
lab:datasets                     OK  OK  [3.2s]
lab:game_loop                    OK  OK  [8.5s]
lab:grid_genome                  OK  OK  [8.1s]
lab:lifecycle_sim                OK  OK  [0.5s]
lab:map_elites_archive           OK  OK  [184.1s]
lab:micro_threads                OK  OK  [9.4s]
lab:package_promotion            OK  OK  [0.2s]
lab:readability_benchmark        OK  OK  [3.0s]
lab:repair_boundary              OK  OK  [3.6s]
lab:runtime_integration          OK  OK  [90.9s]
lab:slip_validator               OK  OK  [0.8s]
lab:wfc_grid                     OK  OK  [6.9s]
lab:workshop_editor              OK  OK  [7.2s]
package                          OK  OK  [8.3s]
cli                              OK  OK (skipped=15)  [3.8s]
game                             OK  OK (skipped=5)  [16.1s]
workshop                         OK  <sys>:0: ResourceWarning: unclosed <socket.socket fd=680, family=2, type=1, proto=0, laddr=('127.0.0.1', 12385)>  [207.8s]
data artifacts                   OK  2242 JSON artifacts valid  [0.8s]

SWEEP GREEN
```

## Sources

- `audits/TODO.md` (cycle 24 N2) · `research/decision_records/0050-probe-geometry-frozen.md` (the record this study produced)
- `research/decision_records/0046-two-geometry-split.md` (the record that named this follow-on), `0049-derivation-size-and-octile-determinacy.md` (N1 — the sizing guidance and the floor construction reused here)
- `research/experiment_reports/2026-07-27-derivation-size-stability.md` (N1), `2026-07-27-geometry-decision.md` (M2), `2026-07-26-geometry-consistency.md` (L3 — the 0.0375 split), `2026-07-21-reachability-escalation.md` (K3 — the blocking-axis bounds), `2026-07-20-occupancy-saturation.md` (the support ceiling)
- `labs/map_elites_archive/probe_edge_freeze.py` (+ `test_probe_edge_freeze.py`, 30 pins) · `data/archives/probe_edge_freeze_stage0.json`
- `labs/map_elites_archive/reachability_probe.py` (both report builders rewired), `occupancy_saturation.py` (rewired) · `labs/wfc_grid/wfc_population_throughput.py` (`load_frozen_scale_edges`, the pattern mirrored)
- `research/algorithm_cards/niche_scale_archive.md` (the geometry card, updated)
- `data/archives/reachability_probe_stage0.json`, `occupancy_saturation_stage0.json`, `reachability_escalation_stage0.json`, `niche_scale_archive_stage0.json`, `geometry_decision_stage0.json`, `derivation_size_stability_stage0.json`
