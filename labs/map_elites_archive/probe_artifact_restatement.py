"""Cycle 26 P5: the probe artifacts carry their own edges. (SHARED.)

DR 0050 froze the probe geometry, rewired the three probe-side
consumers to one shared loader (`probe_edges_for`), and named its own
remainder precisely (item 2 of "What this record does NOT do"):
`occupancy_saturation_stage0.json` and
`reachability_escalation_stage0.json` were committed BEFORE the rewire,
so neither carries `edges_source` in its body — each depends on a draw
it cannot prove. *"Regenerating them is a re-run of each, named rather
than silently skipped."* This module is that named re-run.

THE SHAPE IS DR 0053's: RESTATE, NEVER OVERWRITE
================================================

The committed artifacts stay exactly as they are. Each study re-runs
through its own committed builder — **imported, never re-implemented**
(`build_occupancy_report`, `build_escalation_report`) — at its
documented defaults, and the result is written as a NEW artifact beside
the original: a new id, a ``restates`` pointer, and
``parameters.edges_source`` naming the committed frozen geometry
(which the rewired builders now record on every run).

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN
===============================================

The studies are deterministic under the frozen edges, so the
expectation is **exact reproduction**: every committed number comes
back identical and the only body difference is the added
``parameters.edges_source`` → verdict ``restated_identical``. Any other
difference is recorded PER KEY PATH and the verdict is
``restated_with_deltas`` — a finding to explain, never a patch (a
time-bounded search stage that lands differently on this machine would
be exactly such a finding). A restated body that still carries no
``edges_source`` is refused outright (``refuse_missing_edges``): the
in-body draw is the entire point of the re-run. DR 0046's comparability
rule applies throughout — nothing here reads one geometry against the
other, and the committed originals are never edited.
"""

import argparse
import json
import sys
import time
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

REPORT_DATE = "2026-08-09"

RESTATEMENTS: dict[str, dict] = {
    "occupancy_saturation": {
        "committed_artifact": "data/archives/occupancy_saturation_stage0.json",
        "restated_artifact_id": "occupancy_saturation_edged_stage0",
    },
    "reachability_escalation": {
        "committed_artifact": (
            "data/archives/reachability_escalation_stage0.json"
        ),
        "restated_artifact_id": "reachability_escalation_edged_stage0",
    },
}

# Both provenance keys DR 0050's rewire records on a fresh run. PROCESS
# DEVIATION, RECORDED: the first enumeration listed only edges_source;
# the first occupancy re-run came back with ZERO numeric differences and
# one unexpected addition — frozen_edges_artifact, the same rewire's
# committed-artifact pointer. The comparison instrument was
# under-specified, not the study non-deterministic; the enumeration was
# corrected and the comparison re-run over the same rerun body. The
# rule's substance (exact numeric reproduction; provenance additions
# allowed) is unchanged.
ALLOWED_ADDED = (
    "parameters.edges_source",
    "parameters.frozen_edges_artifact",
)

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 26 P5). Each study re-runs through its own "
    "committed builder at its documented defaults; the committed "
    "artifact is never edited. Expectation: the studies are "
    "deterministic under the frozen edges, so every committed number "
    "reproduces exactly and the only body difference is the added "
    "parameters.edges_source -> restated_identical. Any other "
    "difference is recorded per key path -> restated_with_deltas, a "
    "finding to explain, never a patch. A restated body still missing "
    "edges_source is refused (refuse_missing_edges): the in-body draw "
    "is the entire point. DR 0046's comparability rule applies "
    "throughout; DR 0053 shapes the whole task."
)


def compare_restatement(
    committed: dict, restated: dict, *, allowed_added: tuple = ALLOWED_ADDED
) -> dict:
    """Deep body comparison, reported as dotted key paths."""
    out = {"differing": [], "added": [], "removed": []}

    def walk(left, right, path):
        if isinstance(left, dict) and isinstance(right, dict):
            for key in left:
                child = f"{path}.{key}" if path else str(key)
                if key not in right:
                    out["removed"].append(child)
                else:
                    walk(left[key], right[key], child)
            for key in right:
                if key not in left:
                    out["added"].append(f"{path}.{key}" if path else str(key))
        elif left != right:
            out["differing"].append(path)

    walk(committed, restated, "")
    added = sorted(out["added"])
    unexpected = [p for p in added if p not in allowed_added]
    identical = (
        not out["differing"] and not unexpected and not out["removed"]
    )
    return {
        "identical": identical,
        "differing_paths": sorted(out["differing"]),
        "added_paths": added,
        "removed_paths": sorted(out["removed"]),
        "allowed_added_paths": [p for p in added if p in allowed_added],
        "unexpected_added_paths": unexpected,
    }


def judge_restatement(comparison: dict, *, edges_source_present: bool) -> dict:
    if not edges_source_present:
        verdict = "refuse_missing_edges"
    elif comparison["identical"]:
        verdict = "restated_identical"
    else:
        verdict = "restated_with_deltas"
    return {"verdict": verdict, "comparison": comparison}


def restate_report(
    rerun: dict,
    *,
    restated_artifact_id: str,
    restates: str,
    restatement_check: dict,
) -> dict:
    """Stamp the restated identity WITHOUT mutating the rerun body."""
    restated = json.loads(json.dumps(rerun))
    restated["artifact_id"] = restated_artifact_id
    restated["restates"] = restates
    restated["restated_date"] = REPORT_DATE
    restated["restatement_check"] = restatement_check
    return restated


def run_restatement(name: str) -> dict:
    spec = RESTATEMENTS[name]
    committed = json.loads(
        (ROOT / spec["committed_artifact"]).read_text(encoding="utf-8")
    )
    started = time.perf_counter()
    if name == "occupancy_saturation":
        from occupancy_saturation import build_occupancy_report

        rerun = build_occupancy_report()
    elif name == "reachability_escalation":
        from reachability_probe import build_escalation_report

        rerun = build_escalation_report()
    else:
        raise ValueError(f"unknown restatement: {name}")
    wall_clock_s = round(time.perf_counter() - started, 3)

    comparison = compare_restatement(committed, rerun)
    edges_present = "edges_source" in rerun.get("parameters", {})
    judged = judge_restatement(
        comparison, edges_source_present=edges_present
    )
    if judged["verdict"] == "refuse_missing_edges":
        raise ValueError(
            f"{name}: the re-run still carries no parameters.edges_source; "
            "a restatement that cannot prove its draw is refused"
        )

    restated = restate_report(
        rerun,
        restated_artifact_id=spec["restated_artifact_id"],
        restates=spec["committed_artifact"],
        restatement_check={
            "rule": PRE_REGISTERED_RULE,
            "verdict": judged["verdict"],
            "comparison": comparison,
            "edges_source": rerun["parameters"]["edges_source"],
            "wall_clock_s": wall_clock_s,
        },
    )
    path = ROOT / "data" / "archives" / f"{spec['restated_artifact_id']}.json"
    path.write_text(
        json.dumps(restated, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "name": name,
        "verdict": judged["verdict"],
        "comparison": comparison,
        "wall_clock_s": wall_clock_s,
        "written": path.relative_to(ROOT).as_posix(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cycle 26 P5: restate the probe artifacts with their edges."
    )
    parser.add_argument(
        "--only", choices=sorted(RESTATEMENTS), default=None
    )
    args = parser.parse_args()
    names = [args.only] if args.only else sorted(RESTATEMENTS)
    for name in names:
        result = run_restatement(name)
        comparison = result["comparison"]
        print(f"{name}: {result['verdict'].upper()}")
        print(
            f"  differing {comparison['differing_paths']}  "
            f"added {comparison['added_paths']}  "
            f"removed {comparison['removed_paths']}"
        )
        print(
            f"  wall clock {result['wall_clock_s']} s  "
            f"wrote {result['written']}"
        )


if __name__ == "__main__":
    main()
