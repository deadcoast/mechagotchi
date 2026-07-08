import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SERVER_DIR = ROOT / "workshop" / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from workshop_server import start_workshop_server  # noqa: E402


VALID_MATRIX = [
    [".", "E", ".", ".", "E", ".", ".", "."],
    [".", ".", "B", "B", ".", ".", ".", "."],
    [".", "B", "A", "B", "B", ".", ".", "."],
    [".", ".", "B", "B", ".", "M", ".", "."],
    [".", ".", ".", "B", "B", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
]
BROKEN_MATRIX = [row[:] for row in VALID_MATRIX]
BROKEN_MATRIX[2][2] = "."  # no anchor anywhere


def _post(url: str, payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def _get(url: str) -> tuple[int, dict]:
    with urllib.request.urlopen(url) as response:
        return response.status, json.loads(response.read())


class SharedDrawAssetTests(unittest.TestCase):
    """E2 (DR 0026's recorded cleanup): one shared packet drawer, served;
    the pages import it and no longer carry inline duplicates. The grid
    editor's draw() is a distinct authoring surface and stays local."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.server = start_workshop_server(
            port=0,
            grids_dir=base / "grids",
            slips_dir=base / "slips",
            session_dir=base / "game_loop",
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def _page(self, path: str) -> str:
        with urllib.request.urlopen(f"{self.base}{path}") as response:
            self.assertEqual(200, response.status)
            return response.read().decode("utf-8")

    def test_the_shared_asset_serves_with_the_three_helpers(self):
        asset = self._page("/shared/draw.js")
        for name in ("MechaDraw", "drawPacket", "woundOverlay", "bodyPacketAt"):
            self.assertIn(name, asset)

    def test_preview_and_session_import_it_and_carry_no_duplicates(self):
        for path in ("/preview", "/session"):
            page = self._page(path)
            self.assertIn('src="/shared/draw.js"', page, path)
            self.assertIn("MechaDraw.", page, path)
            # The inline duplicates are gone.
            self.assertNotIn("function drawReplayPacket(", page, path)
            self.assertNotIn("function replayBodyPacket(", page, path)
        # Preview keeps only the thin wrapper pinning its historical
        # damage-stroke behavior — the loop itself lives in the asset.
        preview = self._page("/preview")
        self.assertIn("MechaDraw.drawPacket(canvas, packet, { showDamage: true })", preview)

    def test_the_editor_draw_stays_a_distinct_local_surface(self):
        editor = self._page("/")
        self.assertIn("function draw()", editor)  # matrix drawer, local
        self.assertNotIn('src="/shared/draw.js"', editor)


class CompanionEndpointTests(unittest.TestCase):
    """W1: the living companion over HTTP — adoption through the
    engine's gate, tending as engine ticks, autonomous life with the
    switchboard, honest death, persistence across requests."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.server = start_workshop_server(
            port=0,
            grids_dir=base / "grids",
            slips_dir=base / "slips",
            session_dir=base / "game_loop",
            released_dir=base / "released",
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_the_page_is_served(self):
        with urllib.request.urlopen(f"{self.base}/companion") as response:
            self.assertEqual(200, response.status)
            body = response.read().decode("utf-8")
        self.assertIn("your companion", body)
        self.assertIn("/shared/draw.js", body)

    def test_adoption_runs_through_the_engines_gate(self):
        # A covenant that forbids the creature's palette: the ENGINE
        # refuses the adoption with its own alignment error.
        status, refused = _post(
            f"{self.base}/api/companion/adopt",
            {
                "source": "seed",
                "name": "mg_seed_001",
                "profile_id": "slip_amber_social",
            },
        )
        self.assertEqual(400, status)
        self.assertIn("SLIP", refused["error"])
        # Unknown source and unknown profile are named refusals.
        status, _ = _post(
            f"{self.base}/api/companion/adopt",
            {"source": "nowhere", "name": "x"},
        )
        self.assertEqual(400, status)
        status, _ = _post(
            f"{self.base}/api/companion/adopt",
            {"source": "seed", "name": "mg_seed_001", "profile_id": "nope"},
        )
        self.assertEqual(404, status)
        # No campaign to adopt from yet — honestly refused.
        status, refused = _post(
            f"{self.base}/api/companion/adopt",
            {"source": "campaign", "name": "best"},
        )
        self.assertEqual(409, status)
        self.assertIn("session page", refused["error"])

    def test_adopt_tend_live_die_and_adopt_again(self):
        # 1. No companion yet; tending nothing is refused.
        status, payload = _get(f"{self.base}/api/companion")
        self.assertEqual(200, status)
        self.assertFalse(payload["exists"])
        status, refused = _post(
            f"{self.base}/api/companion/act", {"action": "feed"}
        )
        self.assertEqual(409, status)
        self.assertIn("adopt", refused["error"])

        # 2. Adopt: the engine builds the live state.
        status, snap = _post(
            f"{self.base}/api/companion/adopt",
            {
                "source": "seed",
                "name": "mg_seed_001",
                "profile_id": "slip_lcd_seed",
                "companion_name": "gizmo",
            },
        )
        self.assertEqual(200, status)
        self.assertTrue(snap["alive"])
        self.assertEqual("gizmo", snap["name"])
        self.assertEqual(0, snap["age_ticks"])
        self.assertIn(snap["animation"], snap["animation_vocabulary"])
        self.assertIn("cells", snap["packet"])

        # 3. Tend it: one engine tick per button.
        status, snap = _post(
            f"{self.base}/api/companion/act", {"action": "feed"}
        )
        self.assertEqual(200, status)
        self.assertEqual(1, snap["age_ticks"])
        self.assertEqual("keeper", snap["log"][-1]["actor"])
        status, refused = _post(
            f"{self.base}/api/companion/act", {"action": "cuddle"}
        )
        self.assertEqual(400, status)
        self.assertIn("unsupported lifecycle action", refused["error"])

        # 4. Let it live: the switchboard chooses.
        status, snap = _post(f"{self.base}/api/companion/tick", {})
        self.assertEqual(200, status)
        self.assertEqual(2, snap["age_ticks"])
        self.assertEqual("companion", snap["log"][-1]["actor"])
        self.assertIn(snap["log"][-1]["action"], snap["actions"])

        # 5. Persistence: a fresh GET sees the same life.
        status, snap = _get(f"{self.base}/api/companion")
        self.assertEqual(200, status)
        self.assertTrue(snap["exists"])
        self.assertEqual(2, snap["age_ticks"])

        # 6. Neglect kills (starvation ~tick 11); death is honest and
        #    tending the dead is refused with the cause named.
        for _ in range(20):
            status, snap = _post(
                f"{self.base}/api/companion/act", {"action": "idle"}
            )
            if status != 200 or not snap.get("alive", False):
                break
        if status == 200:
            self.assertFalse(snap["alive"])
            self.assertIsNotNone(snap["death_cause"])
        status, refused = _post(
            f"{self.base}/api/companion/act", {"action": "feed"}
        )
        self.assertEqual(409, status)
        self.assertIn("died of", refused["error"])
        self.assertIn("adopt a successor", refused["error"])

        # 7. A successor from the wrong species is REFUSED by the same
        #    gate (mg_seed_002 is gameboy_gray; the covenant is lcd)...
        status, refused = _post(
            f"{self.base}/api/companion/adopt",
            {
                "source": "seed",
                "name": "mg_seed_002",
                "profile_id": "slip_lcd_seed",
            },
        )
        self.assertEqual(400, status)
        self.assertIn("SLIP", refused["error"])
        # ...and a covenant-true successor is the way on (mg_seed_006
        # is the next lcd_green body in the corpus).
        status, snap = _post(
            f"{self.base}/api/companion/adopt",
            {
                "source": "seed",
                "name": "mg_seed_006",
                "profile_id": "slip_lcd_seed",
            },
        )
        self.assertEqual(200, status)
        self.assertTrue(snap["alive"])
        self.assertEqual(0, snap["age_ticks"])


class KeeperSessionEndpointTests(unittest.TestCase):
    """G4 (DR 0021): the Keeper's session — persistent, engine-run.

    A tiny-parameter session keeps the era run fast; the numbers the
    endpoints return are read straight from the session lab's read model
    over verbatim engine reports."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.session_dir = base / "game_loop"
        # Isolated released dir: the Contribute step must be exercised
        # against test fixtures, never the repo's live releases.
        cls.released_dir = base / "released"
        cls.released_dir.mkdir(parents=True)
        cls.server = start_workshop_server(
            port=0,
            grids_dir=base / "grids",
            slips_dir=base / "slips",
            session_dir=cls.session_dir,
            released_dir=cls.released_dir,
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_the_keeper_session_plays_end_to_end(self):
        # 1. No session yet.
        status, payload = _get(f"{self.base}/api/session/state")
        self.assertEqual(200, status)
        self.assertFalse(payload["exists"])
        self.assertIn("storm", payload["weather_names"])

        # 2. Running an era without a session is refused honestly.
        status, refused = _post(
            f"{self.base}/api/session/era", {"weather": "calm"}
        )
        self.assertEqual(409, status)
        self.assertFalse(refused["ok"])

        # 3. Start the bloodline (fast engine parameters via the state
        #    file are the lab's concern; the endpoint uses defaults, so
        #    shrink them directly in the state for test speed).
        status, created = _post(f"{self.base}/api/session/new", {})
        self.assertEqual(200, status)
        self.assertTrue(created["ok"])
        self.assertEqual(
            "keeper_campaign_001", created["active_campaign_id"]
        )
        state_path = self.session_dir / "keeper_session.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["engine_parameters"].update(
            generations=2,
            population=3,
            damage_cycles=1,
            ticks=8,
            repair_epochs=20,
        )
        state_path.write_text(
            json.dumps(state, indent=2) + "\n", encoding="utf-8"
        )

        # 4. A second start is refused while the session exists.
        status, duplicate = _post(f"{self.base}/api/session/new", {})
        self.assertEqual(409, status)
        self.assertFalse(duplicate["ok"])

        # 4b. The Contribute step (E5, DR 0021 core loop step 3): a
        #     RELEASED creature enters the next era as a founder through
        #     the engine's own gates. Fixture: an lcd seed copy under a
        #     released id (engine-valid, profile-aligned -> admitted).
        released = json.loads(
            (ROOT / "data" / "seed_grids" / "mg_seed_001.json").read_text(
                encoding="utf-8"
            )
        )
        released["grid_id"] = "released_e5_contribute"
        (self.released_dir / "released_e5_contribute.json").write_text(
            json.dumps(released), encoding="utf-8"
        )

        # 5. Run one storm era: the turn is a real evolve run's digest,
        #    and the released creature founded it.
        status, turn_payload = _post(
            f"{self.base}/api/session/era", {"weather": "storm"}
        )
        self.assertEqual(200, status)
        self.assertTrue(turn_payload["ok"])
        turn = turn_payload["turn"]
        self.assertEqual("storm", turn["era"]["forecast"])
        self.assertTrue(
            all(
                sid.startswith("weather_storm_")
                for sid in turn["era"]["snapshot_ids"]
            )
        )
        self.assertEqual("active", turn["status"])
        self.assertEqual(1, turn["era"]["founders_admitted"])
        self.assertEqual(
            "founders_plus_seed_pool",
            turn["era"]["parent_source_generation_0"],
        )

        # 6. The persisted state and the DR 0022 ledger both updated —
        #    since C3 the ledger is the promoted storage module's
        #    SQLite file, rebuilt through the migration path.
        status, refreshed = _get(f"{self.base}/api/session/state")
        self.assertEqual(1, refreshed["campaigns"][0]["era_count"])
        sys.path.insert(
            0, str(ROOT / "packages" / "mecha_engine" / "src")
        )
        from mecha_engine.storage import campaign_history, open_ledger

        conn = open_ledger(self.session_dir / "campaign_ledger.sqlite")
        try:
            history = campaign_history(conn, "keeper_campaign_001")
            self.assertEqual(1, len(history["eras"]))
            self.assertEqual(
                "storm", history["eras"][0]["weather"]["forecast"]
            )
        finally:
            conn.close()

        # 7. Unknown forecasts are rejected.
        status, bad = _post(
            f"{self.base}/api/session/era", {"weather": "hurricane"}
        )
        self.assertEqual(400, status)
        self.assertFalse(bad["ok"])

        # 7b. The Covenant step (C4): over-budget spends are rejected
        #     with named violations; within-budget spends persist and
        #     the summary reflects the new covenant.
        status, rejected = _post(
            f"{self.base}/api/session/covenant", {"population": 99}
        )
        self.assertEqual(400, status)
        self.assertFalse(rejected["ok"])
        self.assertTrue(
            any("cap" in v for v in rejected["violations"])
        )
        status, accepted = _post(
            f"{self.base}/api/session/covenant", {"population": 4}
        )
        self.assertEqual(200, status)
        self.assertTrue(accepted["ok"])
        self.assertEqual(4, accepted["engine_parameters"]["population"])
        self.assertIn("covenant_budget", accepted)

        # 8. The era's stored replay serves from the ledger (C5): the
        #    best elite's recorded life at the era's own seed.
        status, replay_payload = _get(
            f"{self.base}/api/session/replay?campaign=keeper_campaign_001&era=0"
        )
        self.assertEqual(200, status)
        replay = replay_payload["replay"]
        self.assertEqual("mechagotchi_replay_v1", replay["replay_format"])
        self.assertGreater(replay["frame_count"], 0)
        self.assertEqual("birth", replay["frames"][0]["phase"])
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(
                f"{self.base}/api/session/replay?campaign=nope&era=7"
            )
        self.assertEqual(404, caught.exception.code)

    def test_serves_the_session_page(self):
        with urllib.request.urlopen(f"{self.base}/session") as response:
            body = response.read().decode("utf-8")
        self.assertEqual(200, response.status)
        self.assertIn("/api/session/era", body)
        self.assertIn("keeper session", body)


class WorkshopServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.grids_dir = Path(cls.temp.name)
        cls.server = start_workshop_server(
            port=0, grids_dir=cls.grids_dir
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_serves_the_editor_page_at_root(self):
        with urllib.request.urlopen(f"{self.base}/") as response:
            body = response.read().decode("utf-8")
        self.assertEqual(200, response.status)
        self.assertIn("mecha_workshop", body)
        self.assertIn("/api/validate", body)

    def test_palettes_endpoint_lists_engine_palettes(self):
        status, payload = _get(f"{self.base}/api/palettes")
        self.assertEqual(200, status)
        self.assertIn("lcd_green", payload["palettes"])
        self.assertEqual(3, len(payload["palettes"]["lcd_green"]))

    def test_validate_returns_the_engine_verdict_and_stats(self):
        status, payload = _post(
            f"{self.base}/api/validate",
            {"matrix": VALID_MATRIX, "palette_id": "lcd_green"},
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["errors"])
        stats = payload["stats"]
        self.assertGreater(stats["body_mass"], 0)
        self.assertEqual(2, stats["sensor_count"])
        self.assertGreaterEqual(stats["stress_load"], 0.0)
        self.assertLessEqual(stats["stress_load"], 1.0)
        self.assertIn("collapse_risk", stats)
        # SLIP alignment per available profile, from the Stage 0 authority.
        self.assertIn("slip_lcd_seed", payload["alignment"])
        self.assertTrue(payload["alignment"]["slip_lcd_seed"]["ok"])

    def test_validate_reports_engine_errors_verbatim(self):
        status, payload = _post(
            f"{self.base}/api/validate",
            {"matrix": BROKEN_MATRIX, "palette_id": "lcd_green"},
        )
        self.assertEqual(200, status)
        self.assertFalse(payload["valid"])
        self.assertGreater(len(payload["errors"]), 0)

    def test_save_is_strict_per_the_compatibility_pillar(self):
        status, payload = _post(
            f"{self.base}/api/save",
            {
                "name": "broken creature",
                "matrix": BROKEN_MATRIX,
                "palette_id": "lcd_green",
            },
        )
        self.assertEqual(400, status)
        self.assertFalse(payload["ok"])
        self.assertGreater(len(payload["errors"]), 0)
        self.assertEqual([], list(self.grids_dir.glob("broken_creature*.json")))

    def test_save_and_reload_a_valid_grid_with_backup(self):
        status, payload = _post(
            f"{self.base}/api/save",
            {
                "name": "First Creature!",
                "matrix": VALID_MATRIX,
                "palette_id": "lcd_green",
            },
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        saved = self.grids_dir / payload["file"]
        self.assertTrue(saved.exists())
        grid = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual("workshop_grid_editor", grid["metadata"]["source"])

        # Overwrite backs up the previous file.
        status, payload = _post(
            f"{self.base}/api/save",
            {
                "name": "First Creature!",
                "matrix": VALID_MATRIX,
                "palette_id": "amber_terminal",
            },
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["backup"])
        self.assertTrue(any(self.grids_dir.glob("*.bak.json")))

        status, listing = _get(f"{self.base}/api/grids")
        self.assertEqual(200, status)
        names = [entry["name"] for entry in listing["grids"]]
        self.assertIn("first_creature", names)

        status, loaded = _get(f"{self.base}/api/grids/first_creature")
        self.assertEqual(200, status)
        self.assertEqual(VALID_MATRIX, loaded["matrix"])
        self.assertEqual("amber_terminal", loaded["palette_id"])

    def test_malformed_matrix_fails_loudly(self):
        status, payload = _post(
            f"{self.base}/api/validate",
            {"matrix": [["Z"]], "palette_id": "lcd_green"},
        )
        self.assertEqual(400, status)
        self.assertFalse(payload["ok"])


if __name__ == "__main__":
    unittest.main()


VALID_PROFILE = {
    "slip_version": "0.1.0",
    "profile_id": "workshop_test_profile",
    "name": "Workshop Test Profile",
    "grid": {
        "allowed_palettes": ["lcd_green", "amber_terminal"],
        "body_mass_min": 4,
        "body_mass_max": 24,
        "required_organ_roles": ["sensor", "expression"],
    },
    "mutation": {
        "cell_mutation_rate_max": 0.15,
        "organ_shift_rate_max": 0.05,
        "palette_shift_rate_max": 0.05,
        "symmetry_break_rate_max": 0.05,
    },
    "behavior": {"curiosity": 0.6, "neediness": 0.4, "sleepiness": 0.5},
    "survival_weights": {"stability": 0.5, "novelty": 0.25, "bond": 0.25},
}


class SlipCreatorEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.grids_dir = base / "grids"
        cls.slips_dir = base / "slips"
        cls.server = start_workshop_server(
            port=0, grids_dir=cls.grids_dir, slips_dir=cls.slips_dir
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_serves_the_slip_creator_page(self):
        with urllib.request.urlopen(f"{self.base}/slip") as response:
            body = response.read().decode("utf-8")
        self.assertEqual(200, response.status)
        self.assertIn("slip creator", body)
        self.assertIn("/api/slip/validate", body)

    def test_validate_profile_returns_authority_verdict_and_grid_compat(self):
        status, payload = _post(
            f"{self.base}/api/slip/validate", {"profile": VALID_PROFILE}
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["errors"])
        # Grid compatibility: the seed corpus summary is always present.
        compat = payload["grid_compat"]
        self.assertEqual(50, compat["seed_corpus"]["total"])
        self.assertGreaterEqual(compat["seed_corpus"]["aligned"], 1)
        # The authoring review records availability honestly (H-01 style).
        self.assertIn("available", payload["authoring_review"])

    def test_validate_profile_reports_authority_errors_verbatim(self):
        broken = dict(VALID_PROFILE)
        broken = json.loads(json.dumps(VALID_PROFILE))
        broken["grid"]["allowed_palettes"] = ["neon_pink"]
        status, payload = _post(
            f"{self.base}/api/slip/validate", {"profile": broken}
        )
        self.assertEqual(200, status)
        self.assertFalse(payload["valid"])
        self.assertGreater(len(payload["errors"]), 0)

    def test_slip_save_is_strict_and_roundtrips(self):
        broken = json.loads(json.dumps(VALID_PROFILE))
        broken["slip_version"] = "9.9.9"
        files_before = sorted(self.slips_dir.glob("*.json")) if self.slips_dir.exists() else []
        status, payload = _post(
            f"{self.base}/api/slip/save", {"profile": broken}
        )
        self.assertEqual(400, status)
        self.assertFalse(payload["ok"])
        self.assertGreater(len(payload["errors"]), 0)
        files_after = sorted(self.slips_dir.glob("*.json")) if self.slips_dir.exists() else []
        self.assertEqual(files_before, files_after)

        status, payload = _post(
            f"{self.base}/api/slip/save", {"profile": VALID_PROFILE}
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        self.assertTrue((self.slips_dir / payload["file"]).exists())

        status, listing = _get(f"{self.base}/api/slips")
        self.assertEqual(200, status)
        entries = {e["profile_id"]: e["source"] for e in listing["slips"]}
        self.assertEqual("workshop", entries["workshop_test_profile"])
        self.assertEqual("curated", entries.get("slip_lcd_seed", "curated"))

        status, loaded = _get(f"{self.base}/api/slips/workshop_test_profile")
        self.assertEqual(200, status)
        self.assertEqual(VALID_PROFILE, loaded["profile"])

    def test_authored_profiles_join_grid_editor_alignment(self):
        _post(f"{self.base}/api/slip/save", {"profile": VALID_PROFILE})
        status, payload = _post(
            f"{self.base}/api/validate",
            {"matrix": VALID_MATRIX, "palette_id": "lcd_green"},
        )
        self.assertEqual(200, status)
        self.assertIn("workshop_test_profile", payload["alignment"])
        self.assertTrue(payload["alignment"]["workshop_test_profile"]["ok"])


class PreviewEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.grids_dir = base / "grids"
        cls.slips_dir = base / "slips"
        cls.server = start_workshop_server(
            port=0, grids_dir=cls.grids_dir, slips_dir=cls.slips_dir
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        # A saved workshop creature to preview.
        _post(
            f"{cls.base}/api/save",
            {
                "name": "preview subject",
                "matrix": VALID_MATRIX,
                "palette_id": "lcd_green",
            },
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_serves_the_preview_page(self):
        with urllib.request.urlopen(f"{self.base}/preview") as response:
            body = response.read().decode("utf-8")
        self.assertEqual(200, response.status)
        self.assertIn("preview", body)
        self.assertIn("/api/preview/live", body)

    def test_creature_listing_offers_seeds_and_workshop_grids(self):
        status, listing = _get(f"{self.base}/api/preview/creatures")
        self.assertEqual(200, status)
        sources = {(e["source"], e["name"]) for e in listing["creatures"]}
        self.assertIn(("workshop", "preview_subject"), sources)
        self.assertIn(("seed", "mg_seed_001"), sources)

    def test_render_returns_the_engine_packet(self):
        status, payload = _post(
            f"{self.base}/api/preview/render",
            {"source": "workshop", "name": "preview_subject"},
        )
        self.assertEqual(200, status)
        packet = payload["packet"]
        self.assertEqual([8, 8], packet["grid_size"])
        # The packet carries its own colors — the page never guesses.
        self.assertTrue(all("visual" in cell for cell in packet["cells"]))
        # No profile → the full vocabulary (byte-identical to pre-E1).
        self.assertEqual(
            ["idle", "blink", "sleep", "beg", "ill"],
            packet["animation_vocabulary"],
        )

    def test_render_uses_the_promoted_slip_vocab_gate(self):
        # E1 (cycle 05): the render endpoint now calls the PROMOTED
        # mecha_engine.genome.render_packet_v2, which bounds the portrait
        # vocabulary to the species' visual_grammar. Save a nocturne
        # profile (vocab idle+sleep) and confirm the packet reflects it.
        nocturne = json.loads(
            (
                ROOT / "data" / "slips" / "zoo" / "nocturne_v00.json"
            ).read_text(encoding="utf-8")
        )
        status, saved = _post(
            f"{self.base}/api/slip/save", {"profile": nocturne}
        )
        self.assertEqual(200, status)
        self.assertTrue(saved["ok"], saved)
        status, payload = _post(
            f"{self.base}/api/preview/render",
            {
                "source": "workshop",
                "name": "preview_subject",
                "profile_id": "nocturne_v00",
            },
        )
        self.assertEqual(200, status)
        self.assertEqual(
            ["idle", "sleep"], payload["packet"]["animation_vocabulary"]
        )

    def test_live_preview_is_the_engine_running_the_creature(self):
        status, payload = _post(
            f"{self.base}/api/preview/live",
            {
                "source": "seed",
                "name": "mg_seed_001",
                "profile_id": "slip_lcd_seed",
                "cycles": 2,
                "ticks": 24,
            },
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        report = payload["report"]
        self.assertEqual(2, len(report["cycles"]))
        for cycle in report["cycles"]:
            self.assertIn("removed_cell_count", cycle)
            self.assertIn("episode", cycle)
        self.assertIn("packet", payload["before"])
        self.assertIn("packet", payload["after"])

    def test_replay_is_a_recorded_life_for_the_scrubber(self):
        # R5 (DR 0023): the player's window — birth/wound/repair frames
        # plus every episode tick, all engine truth verbatim.
        status, payload = _post(
            f"{self.base}/api/preview/replay",
            {
                "source": "seed",
                "name": "mg_seed_001",
                "profile_id": "slip_lcd_seed",
                "cycles": 2,
                "ticks": 16,
                "rng_seed": 20260512,
            },
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        replay = payload["replay"]
        self.assertEqual("mechagotchi_replay_v1", replay["replay_format"])
        frames = replay["frames"]
        self.assertEqual("birth", frames[0]["phase"])
        self.assertIsNotNone(frames[0]["packet"])
        phases = {frame["phase"] for frame in frames}
        self.assertEqual(
            {"birth", "wound", "repair", "episode_tick"}, phases
        )
        wounds = [f for f in frames if f["phase"] == "wound"]
        self.assertEqual(2, len(wounds))
        for wound in wounds:
            self.assertEqual(
                wound["removed_cell_count"], len(wound["removed_cells"])
            )
        self.assertEqual(
            replay["tick_frame_count"],
            sum(1 for f in frames if f["phase"] == "episode_tick"),
        )
        # Deterministic: the same request replays the same life.
        _, again = _post(
            f"{self.base}/api/preview/replay",
            {
                "source": "seed",
                "name": "mg_seed_001",
                "profile_id": "slip_lcd_seed",
                "cycles": 2,
                "ticks": 16,
                "rng_seed": 20260512,
            },
        )
        self.assertEqual(replay, again["replay"])

    def test_offspring_preview_generates_engine_children(self):
        status, payload = _post(
            f"{self.base}/api/preview/offspring",
            {
                "source": "seed",
                "name": "mg_seed_001",
                "profile_id": "slip_lcd_seed",
                "count": 3,
                "rng_seed": 20260512,
            },
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        self.assertEqual(3, len(payload["children"]))
        for child in payload["children"]:
            self.assertIn("packet", child)
            self.assertTrue(child["valid"])
            self.assertTrue(child["aligned"])

    def test_offspring_preview_explains_parent_profile_mismatch(self):
        # mg_seed_001 is lcd_green; slip_amber_social forbids that palette:
        # the engine's own alignment errors come back instead of children.
        status, payload = _post(
            f"{self.base}/api/preview/offspring",
            {
                "source": "seed",
                "name": "mg_seed_001",
                "profile_id": "slip_amber_social",
                "count": 3,
            },
        )
        self.assertEqual(200, status)
        self.assertFalse(payload["ok"])
        self.assertGreater(len(payload["errors"]), 0)
        self.assertNotIn("children", payload)


def _post_raw(url: str, data: bytes) -> tuple[int, bytes, str]:
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/octet-stream"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            return (
                response.status,
                response.read(),
                response.headers.get("Content-Type", ""),
            )
    except urllib.error.HTTPError as error:
        return error.code, error.read(), error.headers.get("Content-Type", "")


class ImportExportEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.server = start_workshop_server(
            port=0, grids_dir=base / "grids", slips_dir=base / "slips"
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def _export_png(self, matrix, palette_id, profile_id):
        payload = json.dumps(
            {"matrix": matrix, "palette_id": palette_id, "profile_id": profile_id}
        ).encode("utf-8")
        return _post_raw(f"{self.base}/api/export/png", payload)

    def test_png_export_is_strict_on_validity_and_alignment(self):
        status, body, _ = self._export_png(BROKEN_MATRIX, "lcd_green", "slip_lcd_seed")
        self.assertEqual(400, status)
        self.assertGreater(len(json.loads(body)["errors"]), 0)
        # Valid grid, wrong profile: the engine's alignment errors block it.
        status, body, _ = self._export_png(VALID_MATRIX, "lcd_green", "slip_amber_social")
        self.assertEqual(400, status)
        self.assertGreater(len(json.loads(body)["errors"]), 0)

    def test_png_roundtrip_restores_the_creature(self):
        status, png, content_type = self._export_png(
            VALID_MATRIX, "lcd_green", "slip_lcd_seed"
        )
        self.assertEqual(200, status)
        self.assertEqual("image/png", content_type)
        self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))

        status, body, _ = _post_raw(f"{self.base}/api/import/png", png)
        self.assertEqual(200, status)
        result = json.loads(body)
        self.assertTrue(result["ok"])
        self.assertEqual(VALID_MATRIX, result["matrix"])
        self.assertEqual("lcd_green", result["palette_id"])
        self.assertTrue(result["engine_valid"])

    def test_png_import_rejects_foreign_bytes_with_reasons(self):
        status, body, _ = _post_raw(
            f"{self.base}/api/import/png", b"not a png at all"
        )
        self.assertEqual(400, status)
        result = json.loads(body)
        self.assertFalse(result["ok"])
        self.assertGreater(len(result["errors"]), 0)

    def test_apng_export_is_animated(self):
        payload = json.dumps(
            {
                "matrix": VALID_MATRIX,
                "palette_id": "lcd_green",
                "profile_id": "slip_lcd_seed",
            }
        ).encode("utf-8")
        status, png, content_type = _post_raw(
            f"{self.base}/api/export/apng", payload
        )
        self.assertEqual(200, status)
        self.assertEqual("image/png", content_type)
        self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertIn(b"acTL", png)  # the APNG animation control chunk
        self.assertIn(b"fcTL", png)


class AsepriteSpritesheetEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.server = start_workshop_server(
            port=0, grids_dir=base / "grids", slips_dir=base / "slips"
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def _export(self, kind):
        payload = json.dumps(
            {
                "matrix": VALID_MATRIX,
                "palette_id": "lcd_green",
                "profile_id": "slip_lcd_seed",
                "name": "fourbee",
            }
        ).encode("utf-8")
        return _post_raw(f"{self.base}/api/export/{kind}", payload)

    def test_aseprite_roundtrip_restores_the_creature(self):
        status, project, content_type = self._export("aseprite")
        self.assertEqual(200, status)
        self.assertEqual("application/octet-stream", content_type)
        self.assertGreater(len(project), 1000)  # embedded semantics aboard

        status, body, _ = _post_raw(
            f"{self.base}/api/import/aseprite", project
        )
        self.assertEqual(200, status)
        result = json.loads(body)
        self.assertTrue(result["ok"])
        self.assertEqual(VALID_MATRIX, result["matrix"])
        self.assertEqual("lcd_green", result["palette_id"])

    def test_aseprite_import_rejects_foreign_bytes_with_families(self):
        status, body, _ = _post_raw(
            f"{self.base}/api/import/aseprite", b"not an aseprite project"
        )
        self.assertEqual(400, status)
        result = json.loads(body)
        self.assertFalse(result["ok"])
        self.assertGreater(len(result["errors"]), 0)

    def test_spritesheet_export_returns_the_lab_pair(self):
        status, body, content_type = self._export("spritesheet")
        self.assertEqual(200, status)
        self.assertIn("application/json", content_type)
        payload = json.loads(body)
        import base64

        png = base64.b64decode(payload["png_base64"])
        self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
        sidecar = payload["sidecar"]
        self.assertEqual(3, sidecar["asset_binding"]["frame_count"])
        self.assertIn("animation_binding", sidecar)

    def test_spritesheet_roundtrip_restores_the_creature(self):
        status, body, _ = self._export("spritesheet")
        exported = json.loads(body)
        status, body, _ = _post_raw(
            f"{self.base}/api/import/spritesheet",
            json.dumps(
                {
                    "png_base64": exported["png_base64"],
                    "sidecar": exported["sidecar"],
                }
            ).encode("utf-8"),
        )
        self.assertEqual(200, status)
        result = json.loads(body)
        self.assertTrue(result["ok"])
        self.assertEqual(VALID_MATRIX, result["matrix"])

    def test_spritesheet_import_needs_its_sidecar(self):
        status, body, _ = self._export("spritesheet")
        exported = json.loads(body)
        # Tampered sidecar binding: the codec recomputes the sheet's hash
        # and its own validation speaks.
        sidecar = exported["sidecar"]
        sidecar["asset_binding"]["content_hash"] = "sha256:" + "0" * 64
        status, body, _ = _post_raw(
            f"{self.base}/api/import/spritesheet",
            json.dumps(
                {"png_base64": exported["png_base64"], "sidecar": sidecar}
            ).encode("utf-8"),
        )
        self.assertEqual(400, status)
        result = json.loads(body)
        self.assertFalse(result["ok"])
        self.assertGreater(len(result["errors"]), 0)


class ReleaseEndpointTests(unittest.TestCase):
    """T1.3: releasing a creature into the ecosystem is strict and traced."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.grids_dir = base / "grids"
        cls.released_dir = base / "released"
        cls.server = start_workshop_server(
            port=0,
            grids_dir=cls.grids_dir,
            slips_dir=base / "slips",
            released_dir=cls.released_dir,
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        _post(
            f"{cls.base}/api/save",
            {
                "name": "release candidate",
                "matrix": VALID_MATRIX,
                "palette_id": "lcd_green",
            },
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_release_requires_a_saved_engine_valid_creature(self):
        status, payload = _post(
            f"{self.base}/api/release", {"name": "never saved"}
        )
        self.assertEqual(404, status)
        self.assertFalse(payload["ok"])

    def test_release_copies_into_the_ecosystem_with_lineage_mark(self):
        status, payload = _post(
            f"{self.base}/api/release", {"name": "release candidate"}
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        released = self.released_dir / payload["file"]
        self.assertTrue(released.exists())
        grid = json.loads(released.read_text(encoding="utf-8"))
        self.assertEqual("workshop_grid_editor", grid["metadata"]["source"])
        self.assertIn(
            "released_into_ecosystem",
            grid["lineage"]["mutation_events"],
        )
        # The draft stays; release is a copy, not a move.
        self.assertTrue((self.grids_dir / "release_candidate.json").exists())

        status, listing = _get(f"{self.base}/api/released")
        self.assertEqual(200, status)
        names = [entry["name"] for entry in listing["released"]]
        self.assertIn("release_candidate", names)

    def test_release_backs_up_on_re_release(self):
        _post(f"{self.base}/api/release", {"name": "release candidate"})
        status, payload = _post(
            f"{self.base}/api/release", {"name": "release candidate"}
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["backup"])
        self.assertTrue(any(self.released_dir.glob("*.bak.json")))


class SlipLadderEndpointTests(unittest.TestCase):
    """DR 0012 rung T3.1 through the workshop surfaces."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.server = start_workshop_server(
            port=0, grids_dir=base / "grids", slips_dir=base / "slips"
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_v2_profile_with_forbidden_traits_validates_and_binds(self):
        profile = json.loads(json.dumps(VALID_PROFILE))
        profile["profile_id"] = "workshop_v2_guard"
        profile["slip_version"] = "0.2.0"
        profile["forbidden_traits"] = {"roles": ["shell"]}
        status, payload = _post(
            f"{self.base}/api/slip/validate", {"profile": profile}
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["valid"], payload["errors"])
        # Seed corpus fitting still computes under the ladder field.
        self.assertEqual(50, payload["grid_compat"]["seed_corpus"]["total"])

    def test_v1_profile_with_ladder_field_is_version_gated(self):
        profile = json.loads(json.dumps(VALID_PROFILE))
        profile["forbidden_traits"] = {"roles": ["shell"]}
        status, payload = _post(
            f"{self.base}/api/slip/validate", {"profile": profile}
        )
        self.assertEqual(200, status)
        self.assertFalse(payload["valid"])
        self.assertTrue(
            any("0.2.0" in error for error in payload["errors"])
        )


class RenderPacketV2EndpointTests(unittest.TestCase):
    """T16: the previewer plays the five-state vocabulary."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.server = start_workshop_server(
            port=0, grids_dir=base / "grids", slips_dir=base / "slips"
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_packet_carries_the_selected_state_and_projected_visuals(self):
        status, payload = _post(
            f"{self.base}/api/preview/render",
            {"source": "seed", "name": "mg_seed_001", "animation": "blink"},
        )
        self.assertEqual(200, status)
        packet = payload["packet"]
        self.assertEqual("blink", packet["animation"])
        self.assertEqual(
            ["idle", "blink", "sleep", "beg", "ill"],
            packet["animation_vocabulary"],
        )
        background = packet["palette"]["colors"][
            packet["palette"]["background_index"]
        ]
        eyes = {c["visual"] for c in packet["cells"] if c["role"] == "eye"}
        self.assertEqual({background}, eyes)

    def test_unknown_state_fails_loudly(self):
        status, payload = _post(
            f"{self.base}/api/preview/render",
            {"source": "seed", "name": "mg_seed_001", "animation": "dance"},
        )
        self.assertEqual(400, status)
        self.assertFalse(payload["ok"])


class TraitEditorEndpointTests(unittest.TestCase):
    """T9: per-cell traits + the full role vocabulary (DR 0015)."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.grids_dir = base / "grids"
        cls.server = start_workshop_server(
            port=0, grids_dir=cls.grids_dir, slips_dir=base / "slips"
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def _validate(self, overrides):
        return _post(
            f"{self.base}/api/validate",
            {
                "matrix": VALID_MATRIX,
                "palette_id": "lcd_green",
                "cell_overrides": overrides,
            },
        )

    def test_material_and_weight_overrides_apply(self):
        status, payload = self._validate(
            {"2,2": {"material": "light", "mutation_weight": 0.7}}
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["valid"], payload["errors"])
        cell = next(
            c for c in payload["grid_cells"] if (c["x"], c["y"]) == (2, 2)
        )
        self.assertEqual("light", cell["material"])
        self.assertEqual(0.7, cell["mutation_weight"])

    def test_role_overrides_remap_organs_across_the_vocabulary(self):
        # Body cell at (1,2) becomes a shell; eye at (1,0) becomes antenna.
        status, payload = self._validate(
            {"1,2": {"role": "shell"}, "1,0": {"role": "antenna"}}
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["valid"], payload["errors"])
        cells = {(c["x"], c["y"]): c for c in payload["grid_cells"]}
        self.assertEqual("shell", cells[(1, 2)]["role"])
        self.assertEqual("carapace", cells[(1, 2)]["organ"])
        self.assertEqual("antenna", cells[(1, 0)]["role"])
        self.assertEqual("antennae", cells[(1, 0)]["organ"])

    def test_bad_overrides_fail_loudly(self):
        for overrides in (
            {"2,2": {"material": "plasma"}},
            {"2,2": {"mutation_weight": 1.5}},
            {"2,2": {"role": "wings"}},
            {"9,9": {"material": "hard"}},
            {"0,0": {"material": "hard"}},  # empty cell
        ):
            status, payload = self._validate(overrides)
            self.assertEqual(400, status, overrides)
            self.assertFalse(payload["ok"], overrides)

    def test_engine_verdict_still_governs(self):
        # Turning the only mouth into decoration removes the expression
        # organ: the ENGINE's alignment/validation must speak, not us.
        status, payload = self._validate({"5,3": {"role": "decoration"}})
        self.assertEqual(200, status)
        alignment = payload["alignment"]["slip_lcd_seed"]
        self.assertFalse(alignment["ok"])
        self.assertTrue(
            any("expression" in error for error in alignment["errors"])
        )

    def test_save_persists_overrides(self):
        status, payload = _post(
            f"{self.base}/api/save",
            {
                "name": "trait creature",
                "matrix": VALID_MATRIX,
                "palette_id": "lcd_green",
                "cell_overrides": {"2,2": {"material": "glass"}},
            },
        )
        self.assertEqual(200, status)
        grid = json.loads(
            (self.grids_dir / payload["file"]).read_text(encoding="utf-8")
        )
        cell = next(
            c for c in grid["cells"] if (c["x"], c["y"]) == (2, 2)
        )
        self.assertEqual("glass", cell["material"])


class InspectorEndpointTests(unittest.TestCase):
    """Slice 5: genome inspector + lineage browser (og responsibilities)."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.server = start_workshop_server(
            port=0, grids_dir=base / "grids", slips_dir=base / "slips"
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        _post(
            f"{cls.base}/api/save",
            {
                "name": "inspect me",
                "matrix": VALID_MATRIX,
                "palette_id": "lcd_green",
            },
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_serves_the_inspector_page(self):
        with urllib.request.urlopen(f"{self.base}/inspect") as response:
            body = response.read().decode("utf-8")
        self.assertEqual(200, response.status)
        self.assertIn("inspector", body)
        self.assertIn("/api/inspect", body)

    def test_inspect_returns_the_engine_judged_genome(self):
        status, payload = _get(
            f"{self.base}/api/inspect?source=workshop&name=inspect_me"
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["validation"]["ok"])
        self.assertIn("stats", payload)
        organs = payload["organs"]
        self.assertEqual(
            {"core", "sensors", "expression"}, set(organs)
        )
        self.assertEqual(10, organs["core"]["cell_count"])
        lineage = payload["lineage"]
        self.assertEqual(0, lineage["generation"])
        self.assertIn("mutation_events", lineage)
        self.assertEqual(13, len(payload["cells"]))

    def test_inspect_seed_and_missing(self):
        status, payload = _get(
            f"{self.base}/api/inspect?source=seed&name=mg_seed_001"
        )
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        try:
            _get(f"{self.base}/api/inspect?source=workshop&name=ghost")
            self.fail("expected 404")
        except urllib.error.HTTPError as error:
            self.assertEqual(404, error.code)

    def test_lineage_browser_reads_the_wire_evidence(self):
        status, payload = _get(f"{self.base}/api/lineage")
        self.assertEqual(200, status)
        self.assertIn("released", payload)
        # The committed wire artifact traces workshop ancestry.
        self.assertIn("evolution_runs", payload)
        wire = next(
            (
                run
                for run in payload["evolution_runs"]
                if run["lab_id"]
                == "mecha_engine_evolution_workshop_wire_stage0"
            ),
            None,
        )
        self.assertIsNotNone(wire)
        self.assertEqual(
            ["released_tall_wisp", "released_wide_sentinel"],
            wire["founder_ids"],
        )
        self.assertIn("creature_count_by_generation", wire)


class MetricsInstrumentationTests(unittest.TestCase):
    """T10 pipeline: og workshop metrics, instrumented (data from humans)."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        base = Path(cls.temp.name)
        cls.metrics_dir = base / "metrics"
        cls.server = start_workshop_server(
            port=0,
            grids_dir=base / "grids",
            slips_dir=base / "slips",
            metrics_dir=cls.metrics_dir,
        )
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.temp.cleanup()

    def test_session_counters_track_the_og_metrics(self):
        _post(
            f"{self.base}/api/validate",
            {"matrix": BROKEN_MATRIX, "palette_id": "lcd_green"},
        )
        _post(
            f"{self.base}/api/validate",
            {"matrix": VALID_MATRIX, "palette_id": "lcd_green"},
        )
        _post(
            f"{self.base}/api/save",
            {"name": "metric creature", "matrix": VALID_MATRIX, "palette_id": "lcd_green"},
        )
        status, metrics = _get(f"{self.base}/api/metrics")
        self.assertEqual(200, status)
        session = metrics["session"]
        self.assertGreaterEqual(session["validations"], 2)
        self.assertGreaterEqual(session["invalid_verdicts"], 1)
        self.assertGreaterEqual(session["saves"], 1)
        self.assertIn("validator_error_counts", session)
        self.assertIn("started_at", session)

    def test_flush_persists_the_session_artifact(self):
        status, payload = _post(f"{self.base}/api/metrics/flush", {})
        self.assertEqual(200, status)
        self.assertTrue(payload["ok"])
        files = list(self.metrics_dir.glob("session_*.json"))
        self.assertEqual(1, len(files))
        record = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertIn("validations", record)
        self.assertEqual(
            "instrumented_pipeline_no_human_study_data",
            record["provenance"],
        )
