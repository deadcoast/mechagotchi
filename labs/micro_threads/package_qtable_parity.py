"""Reproduce the original Q1 record and run full package parity vectors.

Writes a NEW package integration artifact; never rewrites the lab gate.
Run with the repository interpreter from any working directory.
"""
import hashlib
import io
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qtable_consumer_gate import build_qtable_consumer_report
from test_package_qtable_parity import PackageQtableParityTests


def build_report():
    output=io.StringIO()
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(PackageQtableParityTests))
    if not result.wasSuccessful():
        raise AssertionError(output.getvalue())
    path=ROOT/"data/micro_threads/qtable_consumer_gate_stage0.json"
    original=json.loads(path.read_text(encoding="utf-8"))
    reproduced=build_qtable_consumer_report()
    left,right=deepcopy(original),deepcopy(reproduced)
    # Wall-clock timing is the only nondeterministic field; all instrument
    # records, parameters, actions, keeper counts and verdicts must match.
    left["metrics"].pop("wall_clock_s")
    right["metrics"].pop("wall_clock_s")
    if left != right:
        raise AssertionError("complete Q1 instrument record did not reproduce")
    return {
        "artifact_id":"package_qtable_parity_stage0", "date":"2026-10-04",
        "status":"package_parity_verified_defaults_off",
        "purpose":"Promote the bounded producer and follower without changing the Q1 instrument or incumbent runtime defaults.",
        "source_artifacts":[str(path.relative_to(ROOT)).replace(chr(92),"/"),
            "labs/micro_threads/test_package_qtable_parity.py",
            "packages/mecha_engine/src/mecha_engine/learning/threads.py",
            "packages/mecha_engine/src/mecha_engine/learning/_switchboard.py"],
        "parameters":original["parameters"],
        "metrics":{"package_parity_tests":result.testsRun,"parity_output":output.getvalue(),
            "complete_q1_record_reproduced":True,
            "original_q1_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "q1_reproduced_metrics":reproduced["metrics"]},
        "closed_states":["producer and full decision parity", "pure inputs", "cold/warm and confidence floor", "deliberation provenance", "complete Q1 record reproduced"],
        "blocked_states":["current game default adoption requires R3"],
        "decision":{"verdict":"promote_explicit_opt_in_only"},
        "next_research_step":"R2 playable persistence and R3 actual-game adoption comparison."
    }


if __name__=="__main__":
    report=build_report()
    path=ROOT/"data/micro_threads/package_qtable_parity_stage0.json"
    path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"artifact":str(path),"decision":report["decision"],"parity_tests":report["metrics"]["package_parity_tests"]}))
