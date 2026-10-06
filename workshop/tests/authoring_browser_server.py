"""Disposable real-browser fixture host; owns no project/user save paths."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "workshop/server"))
from workshop_server import start_workshop_server

scratch = Path(sys.argv[1]).resolve()
for name in ("grids", "slips", "released", "metrics", "session"):
    (scratch / name).mkdir(parents=True, exist_ok=True)
server = start_workshop_server(
    port=0, grids_dir=scratch / "grids", slips_dir=scratch / "slips",
    released_dir=scratch / "released", metrics_dir=scratch / "metrics", session_dir=scratch / "session",
)
grid = json.loads((ROOT / "data/seed_grids/mg_seed_001.json").read_text(encoding="utf-8"))
cell = next(c for c in grid["cells"] if c["role"] == "eye")
cell.update(role="antenna", material="signal", mutation_weight=0.91)
grid["parent_grid_id"] = "x2_original_parent"
grid.setdefault("metadata", {})["browser_provenance"] = "full document fixture"
(scratch / "grids/rich.json").write_text(json.dumps(grid), encoding="utf-8")
profile = json.loads(json.dumps(next(iter(server.curated_profiles.values()))))
profile.update(profile_id="x2_browser_profile", name="Browser profile", slip_version="0.2.0", mechanics={"cleanliness": True})
profile["grid"]["allowed_palettes"] = [grid["palette"]["palette_id"]]
profile["grid"]["body_mass_min"] = 1
profile["grid"]["body_mass_max"] = 256
profile["learning_switches"] = {"recent_interaction_ewma": True}
(scratch / "slips/x2_browser_profile.json").write_text(json.dumps(profile), encoding="utf-8")
print(json.dumps({"port": server.server_address[1], "scratch": str(scratch), "cell": [cell["x"],cell["y"]]}), flush=True)
try:
    sys.stdin.readline()
finally:
    server.shutdown()
    server.server_close()
