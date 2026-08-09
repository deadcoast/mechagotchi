# The Probe Artifacts Carry Their Own Edges — Both Restatements Come Back Identical to the Number (Cycle 26 · SHARED · P5)

Date: 2026-08-09

## WHY

DR 0050 froze the probe geometry, rewired the three probe-side
consumers to one shared loader, and named its own remainder precisely
(item 2 of "What this record does NOT do"):
`occupancy_saturation_stage0.json` and
`reachability_escalation_stage0.json` were committed **before** the
rewire, so neither carries `edges_source` in its body — each depends on
a draw it cannot prove, and K3's blocking-axis bounds are expressed as
*"octile intervals from the frozen edges"* in an artifact carrying no
edges at all. *"Regenerating them is a re-run of each, named rather
than silently skipped."* P5 is that named re-run.

## WHAT

`labs/map_elites_archive/probe_artifact_restatement.py` (+ 15 pins;
rule pre-registered). DR 0053 shapes the whole task: **the committed
artifacts are never edited** — each study re-runs through its own
committed builder (**imported, never re-implemented**) at its
documented defaults, and the result is written as a **new restated
artifact beside the original**: a new id
(`*_edged_stage0`), a `restates` pointer, and
`parameters.edges_source` naming the committed frozen geometry.

**The pre-registered expectation**: the studies are deterministic under
the frozen edges, so every committed number reproduces **exactly**
(`restated_identical`); any difference is recorded per key path
(`restated_with_deltas` — a finding to explain, never a patch, with a
time-bounded search stage landing differently named in advance as the
plausible case); and a restated body still missing `edges_source` is
refused outright (`refuse_missing_edges`) — the in-body draw is the
entire point. DR 0046's comparability rule applies throughout; nothing
reads one geometry against the other.

## FINDINGS

**Both restatements: `RESTATED_IDENTICAL`.**

| study | differing paths | removed paths | additions | wall clock |
| --- | --- | --- | --- | --- |
| `occupancy_saturation` | none | none | the two provenance keys | 67.6 s |
| `reachability_escalation` | none | none | the two provenance keys | 85.3 s |

1. **Every committed number reproduced exactly, in both bodies** — the
   support ceiling, the arms, the per-bin escalation results, all of
   it. The deep comparison covers the *entire* artifact body, not a
   headline sample; zero differing paths, zero removals.
2. **The draw is now provable in-body.** Both restated artifacts carry
   `parameters.edges_source` (the committed frozen geometry) and
   `parameters.frozen_edges_artifact` (DR 0050's committed pointer) —
   the defect DR 0050 named is closed for the last two artifacts that
   had it.
3. **The time-bounded concern did not materialize**: the escalation
   re-run finished in 85.3 s against its 900 s bound and reproduced
   its committed body exactly.
4. **The committed originals still carry no edges — deliberately.**
   They are records; the restatements live beside them, pinned so
   (`test_the_committed_bodies_still_do_not_carry_edges`).

## Process deviation, recorded

The first comparison enumeration allowed only `parameters.edges_source`
as an addition; the first occupancy re-run came back with **zero
numeric differences** and one *unexpected* addition —
`parameters.frozen_edges_artifact`, the same DR 0050 rewire's
committed-artifact pointer — and was verdicted `restated_with_deltas`
by the under-specified instrument. The enumeration was corrected to
cover both provenance keys of the rewire and the comparison re-run over
the re-run body. This is an instrument under-specification caught at
first run (the K2/N3 pattern: recorded, not absorbed); the rule's
substance — exact numeric reproduction, provenance additions allowed —
was never touched, and no gate, bar, or verdict text changed after any
number was known.

## HONEST REMAINDERS

1. **The restatements prove the draw, not the numbers' stability.**
   DR 0050's item 3 stands: the support ceiling ranges 447–462 across
   evaluation resamples; the committed 460 is one draw from that
   spread, and removing the *population* contingency remains its own
   task with its own protocol.
2. **The two engine move-set descents stay un-rerun** (DR 0050 item 1)
   — the edges are identical, which is exactly why.

## Verification

RED:

```text
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_probe_artifact_restatement.py"
ModuleNotFoundError: No module named 'probe_artifact_restatement'
FAILED (errors=1)
```

GREEN (the pins read the written restated artifacts):

```text
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_probe_artifact_restatement.py"
Ran 15 tests in 0.020s
OK
PS> python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
Ran 464 tests in 132.611s
OK
```

The lab invocations that produced the artifacts:

```text
PS> python -B labs/map_elites_archive/probe_artifact_restatement.py --only occupancy_saturation
occupancy_saturation: RESTATED_IDENTICAL
  differing []  added ['parameters.edges_source', 'parameters.frozen_edges_artifact']  removed []
  wall clock 67.601 s  wrote data/archives/occupancy_saturation_edged_stage0.json

PS> python -B labs/map_elites_archive/probe_artifact_restatement.py --only reachability_escalation
reachability_escalation: RESTATED_IDENTICAL
  differing []  added ['parameters.edges_source', 'parameters.frozen_edges_artifact']  removed []
  wall clock 85.315 s  wrote data/archives/reachability_escalation_edged_stage0.json
```

## Sources

- `sunsetted/TODO.md` (cycle 26 P5)
- `research/decision_records/0050-probe-geometry-frozen.md` (the record whose named remainder this executes; no new DR)
- `labs/map_elites_archive/probe_artifact_restatement.py` (+ `test_probe_artifact_restatement.py`, 15 pins)
- `data/archives/occupancy_saturation_edged_stage0.json`, `data/archives/reachability_escalation_edged_stage0.json` (the restated artifacts) · `data/archives/occupancy_saturation_stage0.json`, `data/archives/reachability_escalation_stage0.json` (the committed originals, untouched)
- `labs/map_elites_archive/occupancy_saturation.py`, `labs/map_elites_archive/reachability_probe.py` (the committed builders, imported)
- `research/experiment_reports/2026-07-28-probe-edge-freeze.md` (N2), `2026-07-20-occupancy-saturation.md`, `2026-07-21-reachability-escalation.md`
- `research/decision_records/0046-two-geometry-split.md`, `0053-admission-policy-belongs-at-the-call-site.md`
