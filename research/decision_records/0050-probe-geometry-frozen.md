# Decision Record 0050: The Probe Geometry Is Frozen and Committed — Both Geometries Now Protected the Same Way

Date: 2026-07-28

## Status

**ACCEPTED** — `FREEZE ACCEPTED`, all four gates pre-registered in
`labs/map_elites_archive/probe_edge_freeze.py` before the run.

The probe scale geometry is now a committed artifact with recorded
regeneration provenance, loaded by every probe-side consumer through one
shared loader and **pinned against a live re-derivation** so drift fails
the suite.

## Context

DR 0046 froze the two-geometry split and named this its **strongest**
follow-on:

> **Freezing the probe's edges to a committed artifact.** The incumbent
> is protected from its own 20% instability by being frozen once and
> committed; the probe has no such protection and is re-derived live.

DR 0049 then priced the exposure: re-deriving the probe recipe at
another seed **re-addresses 31% of a population**.

### The queue's description of the defect was wrong, and the truth is sharper

`audits/TODO.md` recorded that each probe number *"is contingent on a
draw **no artifact records**"*. Measured against the committed
artifacts:

| artifact | records its edges? |
| --- | --- |
| `reachability_probe_stage0.json` | **YES** (`metrics.edges`) |
| `occupancy_saturation_stage0.json` | **NO** |
| `reachability_escalation_stage0.json` | **NO** |

The probe geometry was never unrecorded. **One artifact recorded it and
two others silently depended on the same draw**, with nothing pinning
them together — a re-derivation would have moved all three and only one
would have shown it. K3's blocking-axis bounds are expressed as *"the
required octile interval from the frozen edges"* in an artifact carrying
no edges at all.

## Pre-registered gates

Every verdict first-class.

- **G1 PROVENANCE** — the frozen edges must equal the edges
  `reachability_probe_stage0.json` records, that being the draw the
  committed 508/512 was counted under. **Structural, no tolerance.**
- **G2 DETERMINISM** — two independent derivations at the documented
  parameters must be identical, testing DR 0046's *asserted*
  "deterministic in practice" rather than inheriting it.
- **G3 CONSUMER INVARIANCE** — the probe-side headline numbers
  re-expressed against the frozen set must not move, against a
  **MEASURED** floor (DR 0049's construction: frozen edges held fixed,
  only the counted population resampled), with the **tightest** floor
  taken.
- **G4 SEPARATION** — the frozen probe set must **not** equal the frozen
  incumbent set; DR 0046 refused convergence and a freeze that adopted
  the incumbent edges would undo that record silently.

**Sizing**, on DR 0049's measured guidance: frozen at E1's own **600** —
a larger derivation buys address stability but *not* aggregate
stability, while 600 keeps the geometries size-comparable and is the
draw every committed probe-side number was already counted under.

## Measured verdict — all four pass

| gate | verdict |
| --- | --- |
| G1 provenance | **`provenance_matched`** |
| G2 determinism | **`reproducible`** |
| G3 consumer invariance | **`invariant`** |
| G4 separation | **`separated`** (max abs delta **0.037500**) |

**G3 recomputed both committed headlines from scratch and both came back
exact**: support ceiling **460 → 460**, reached-by-generators
**495 → 495**, deltas **0**. M2 had already found one cross-geometry
headline that did not survive recounting; these two do. The freeze is a
**verified** no-op, and `occupancy_saturation`'s ceiling is now confirmed
to have been counted under exactly the edges `reachability_probe`
recorded — previously an assumption nothing checked.

G4's 0.037500 is precisely L3's measured split, so the two geometries
remain two geometries.

## Decision

**1. The probe geometry is FROZEN and COMMITTED** at
`data/archives/probe_edge_freeze_stage0.json`, pointer
`metrics.frozen_edges.edges`, with its recipe, derivation count, rng
seed, corpus, sizing rationale and regeneration command recorded beside
it. Both geometries are now protected the same way; neither is
privileged.

**2. The recipe lives in ONE place.** `derive_probe_edges` replaces the
three private copies that `build_reachability_report`,
`build_escalation_report` and `build_occupancy_report` each carried.

**3. Every probe-side artifact records `edges_source`.** The draw is
visible in the artifact rather than inferable only from module source —
which is the defect this record closes.

**4. The parameters stay honest.** `probe_edges_for` returns the frozen
set only for the documented count and seed; any other draw derives
**live** and the artifact says `"live"`. Silently handing frozen edges to
a caller who asked for a different derivation would make the parameter a
lie.

**5. A parity pin makes drift fail the suite.** A live re-derivation is
asserted equal to the committed frozen set on every run. This is what
converts "deterministic in practice" from an assertion into an enforced
property.

**6. No geometry moves and no number is retracted.** DR 0046's
comparability rule stands unchanged.

## What this record does NOT do

1. **It does not re-run the two engine move-set descents.** 508/512 is
   composed of 495 (binning, re-expressed here) + 8 (probe descent) + 5
   (K3 escalation). The descent counts are unchanged **because the edges
   are identical — that is G1** — not because they were recomputed. Had
   the edges moved, re-running both would have been mandatory.
2. **It does not regenerate `occupancy_saturation_stage0.json` or
   `reachability_escalation_stage0.json`** to carry `edges_source` in
   their committed bodies. They now name a committed source and will
   record it on their next run; regenerating them is a re-run of each,
   named rather than silently skipped.
3. **It does not freeze the headline numbers, only the coordinate system
   they are counted in.** The support ceiling ranges **447–462** across
   six evaluation resamples (`[460, 457, 462, 447, 454, 451]`); the
   committed **460** is one draw from that spread. A reader who sees
   "frozen" beside the ceiling could reasonably conclude the number is
   pinned. **It is not.** Removing the *population* contingency is a
   different task with its own protocol.

## Reported beside the verdict, deliberately outside it

The two resampling floors were measured over **the same six
populations**, differing only in which frozen edge set does the binning:

| geometry | pairwise movements at 3,000 | floor |
| --- | --- | --- |
| incumbent (DR 0049) | `[2, 6, 4]` | **4** |
| probe (here) | `[3, 15, 3]` | **7** |

Because the populations are identical, this is a controlled comparison
of the geometries' *variability* — not of their levels, which DR 0046
forbids reading against each other. **Suggestive, not established**:
three pairs each, and the probe's floor is carried largely by one
movement of 15. It sits consistently with DR 0049's finding that the
probe's occupied-count movement never reached its floor on the ladder
while the incumbent's did. It is recorded here and **kept out of the
gate**, which judged only what it pre-registered.

## Sources

- `research/experiment_reports/2026-07-28-probe-edge-freeze.md` (this record's study)
- `labs/map_elites_archive/probe_edge_freeze.py` (+ `test_probe_edge_freeze.py`, 30 pins) · `data/archives/probe_edge_freeze_stage0.json`
- `labs/map_elites_archive/reachability_probe.py`, `occupancy_saturation.py` (the rewired consumers) · `labs/wfc_grid/wfc_population_throughput.py` (`load_frozen_scale_edges`, the pattern mirrored)
- `research/decision_records/0046-two-geometry-split.md` (the record that named this follow-on), `0049-derivation-size-and-octile-determinacy.md` (the sizing guidance and floor construction)
- `research/experiment_reports/2026-07-27-derivation-size-stability.md`, `2026-07-27-geometry-decision.md`, `2026-07-26-geometry-consistency.md`, `2026-07-21-reachability-escalation.md`, `2026-07-20-occupancy-saturation.md`
- `research/algorithm_cards/niche_scale_archive.md`
- `audits/TODO.md` (cycle 24 N2)
