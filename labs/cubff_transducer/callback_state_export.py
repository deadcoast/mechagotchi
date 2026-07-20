"""Cycle 19 I3: the Python-callback export path — the silent channels lit.

Runs IN WSL against the upstream pybind11 module built from the audited
commit f212e84 (`make CUDA=0 bin/cubff$(python3-config --extension-suffix)`
with pybind11 provisioned in a venv — no system changes). Loads the I1
committed checkpoints via `load_from`, evaluates self-replication
(`eval_selfrep`), and exports the first evaluated state per checkpoint as
JSONL with the FULL soup and `replication_per_prog` — the channel the
binary checkpoint format cannot carry. The compact committed form (tape +
soup hash + full replication scores) lives at
`data/cubff_real_ingest/callback_states/callback_states_compact.json`;
the raw ~100 MB JSONL is reproducible from this script, not committed.

This script cannot run on Windows (the .so is a Linux build); that is a
documented property of the path, not an omission.
"""

import json
import sys
sys.path.insert(0, "/home/deadcoast/cubff_g2")
from bin import cubff

CHECKPOINTS = [
    ("/home/deadcoast/i1_runs/run_seed0_num131072/0000002048.dat", "early_control"),
    ("/home/deadcoast/i1_runs/run_seed0_num131072/0000004096.dat", "post_takeover"),
    ("/home/deadcoast/i1_runs/run_seed0_num131072/0000032768.dat", "post_takeover_late"),
]
OUT = "/home/deadcoast/i1_runs/callback_states.jsonl"

language = cubff.GetLanguage("bff_noheads")
records = []
for path, label in CHECKPOINTS:
    captured = {}
    def callback(state):
        captured["record"] = {
            "snapshot_id": f"callback_{label}_{state.epoch:010d}",
            "epoch": int(state.epoch),
            "language": "bff_noheads",
            "soup": list(state.soup),
            "brotli_size": int(state.brotli_size),
            "brotli_bpb": float(state.brotli_bpb),
            "higher_entropy": float(state.higher_entropy),
            "bytes_per_prog": float(state.bytes_per_prog),
            "replication_per_prog": [float(v) for v in state.replication_per_prog],
        }
        return True  # stop after the first evaluated state
    params = cubff.SimulationParams()
    params.num_programs = 131072
    params.seed = 0
    params.eval_selfrep = True
    params.callback_interval = 1
    params.load_from = path
    language.RunSimulation(params, None, callback)
    rec = captured["record"]
    print(label, "epoch", rec["epoch"], "brotli", rec["brotli_size"],
          "rep>0:", sum(1 for v in rec["replication_per_prog"] if v > 0),
          flush=True)
    records.append(rec)

with open(OUT, "w") as fh:
    for rec in records:
        fh.write(json.dumps(rec) + "\n")
print("wrote", OUT)
