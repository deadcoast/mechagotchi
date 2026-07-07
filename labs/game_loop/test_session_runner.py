"""G2 gates: the session runner composes ONLY promoted surfaces and its
session mechanics — era-chaining, weather, unlocks, extinction and
succession, the DR 0022 JSON-interim ledger — are each falsifiable."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from session_runner import (  # noqa: E402
    SESSION_FORMAT,
    UNLOCK_THRESHOLDS,
    advance_keeper_state,
    apply_succession,
    build_campaign_ledger,
    build_session_report,
    build_seed_grids,
    build_weather_source,
    evaluate_unlocks,
    keeper_state_summary,
    load_keeper_state,
    new_keeper_state,
    plan_succession,
    resolve_unlock_state,
    run_campaign,
    run_keeper_session,
    save_keeper_state,
    train_legibility_model,
    train_session_models,
    write_session_artifacts,
)

BASE_SEED = 20260707
SESSION_KW = dict(
    weather_schedule=("calm", "storm"),
    base_seed=BASE_SEED,
    generations=2,
    population=3,
    damage_cycles=1,
    ticks=8,
)


def _fixture_era(
    *,
    era_index=2,
    filled_niches=9,
    qd_score=6.5,
    max_lineage=2,
    storm=1.45,
    legibility=0.31,
) -> dict:
    """A minimal era record for threshold falsifiability (the DR 0021
    pattern: met-must-unlock / unmet-must-not on fixtures)."""
    return {
        "era_index": era_index,
        "report": {
            "summary": {
                "archive": {
                    "filled_niches": filled_niches,
                    "coverage": 0.0,
                    "qd_score": qd_score,
                },
                "max_lineage_generation": max_lineage,
            }
        },
        "derived": {
            "max_dropout_multiplier_survived": storm,
            "elite_mean_learned_readability": legibility,
        },
    }


class SessionRunnerTests(unittest.TestCase):
    seeds: list[dict]

    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        cls.generation_model, cls.repair_model = train_session_models(
            cls.seeds, repair_epochs=20, rng_seed=BASE_SEED
        )
        cls.legibility_model = train_legibility_model()
        cls.models = dict(
            seed_grids=cls.seeds,
            generation_model=cls.generation_model,
            repair_model=cls.repair_model,
            legibility_model=cls.legibility_model,
        )
        cls.session = run_keeper_session(**cls.models, **SESSION_KW)

    # -- composition and determinism ------------------------------------

    def test_deterministic_session(self):
        again = run_keeper_session(**self.models, **SESSION_KW)
        self.assertEqual(self.session, again)

    def test_session_report_and_ledger_are_json_serializable(self):
        report = build_session_report(self.session)
        ledger = build_campaign_ledger(self.session)
        json.dumps(report)
        json.dumps(ledger)
        self.assertEqual("session_loop_composed", report["decision"]["status"])

    # -- era-chaining: the DR 0021 persistence spine ---------------------

    def test_era_chaining_founders_are_the_previous_eras_elites(self):
        campaign = self.session["campaigns"][0]
        first, second = campaign["eras"][0], campaign["eras"][1]
        elite_ids = [elite["grid_id"] for elite in first["elites"]]
        self.assertTrue(elite_ids)
        self.assertEqual(elite_ids, second["founders_submitted"])
        # Admitted through the engine's own gates, verbatim (DR 0016).
        self.assertEqual(
            elite_ids, second["report"]["founders"]["admitted_ids"]
        )
        self.assertEqual([], second["report"]["founders"]["rejected"])
        self.assertEqual(
            "founders_plus_seed_pool",
            second["report"]["generations"][0]["parent_source"],
        )

    def test_the_first_era_has_no_founders(self):
        first = self.session["campaigns"][0]["eras"][0]
        self.assertEqual([], first["founders_submitted"])
        self.assertNotIn("founders", first["report"])
        self.assertEqual(
            "seed_pool",
            first["report"]["generations"][0]["parent_source"],
        )

    # -- weather: DR 0018/0020 as the era's forecast ----------------------

    def test_calm_forecast_is_the_byte_identical_no_source_default(self):
        self.assertIsNone(build_weather_source("calm"))
        calm_era = self.session["campaigns"][0]["eras"][0]
        self.assertNotIn("cubff_pressure", calm_era["report"])
        self.assertEqual([], calm_era["weather"]["snapshot_ids"])

    def test_storm_forecast_reaches_the_engine_with_provenance(self):
        storm_era = self.session["campaigns"][0]["eras"][1]
        self.assertEqual("storm", storm_era["weather"]["forecast"])
        block = storm_era["report"]["cubff_pressure"]
        self.assertEqual(
            len(storm_era["report"]["generations"]),
            len(block["by_generation"]),
        )
        for snapshot_id in storm_era["weather"]["snapshot_ids"]:
            self.assertTrue(snapshot_id.startswith("weather_storm_"))

    def test_storm_weather_does_more_measured_damage_than_stable(self):
        kw = dict(
            self.models,
            base_seed=BASE_SEED,
            generations=2,
            population=3,
            damage_cycles=1,
            ticks=8,
        )
        storm = run_campaign(
            campaign_id="wx_storm", weather_schedule=("storm",), **kw
        )
        stable = run_campaign(
            campaign_id="wx_stable", weather_schedule=("stable_soup",), **kw
        )
        self.assertGreater(
            storm["eras"][0]["derived"]["total_removed_cells"],
            stable["eras"][0]["derived"]["total_removed_cells"],
        )

    def test_unknown_forecast_is_rejected(self):
        with self.assertRaises(ValueError):
            build_weather_source("hurricane")

    # -- unlocks: facts, falsifiable ---------------------------------------

    def test_met_thresholds_must_unlock_and_unmet_must_not(self):
        met = evaluate_unlocks(_fixture_era(), [])
        by_axis = {}
        for fact in met:
            by_axis.setdefault(fact["axis"], []).append(fact["tier"])
        self.assertEqual([1, 2], by_axis["niche_mastery"])  # 9 >= 4, 8
        self.assertEqual([1], by_axis["bloodline_depth"])  # 2 >= 2
        self.assertEqual([1, 2], by_axis["quality_diversity"])  # 6.5
        self.assertEqual([1, 2], by_axis["storm_record"])  # 1.45
        self.assertEqual([1], by_axis["legibility"])  # 0.31 >= 0.25
        unmet = evaluate_unlocks(
            _fixture_era(
                filled_niches=3,
                qd_score=2.0,
                max_lineage=1,
                storm=1.0,
                legibility=0.2,
            ),
            [],
        )
        self.assertEqual([], unmet)

    def test_earned_unlocks_are_never_re_earned(self):
        first = evaluate_unlocks(_fixture_era(), [])
        again = evaluate_unlocks(_fixture_era(era_index=3), first)
        self.assertEqual([], again)

    def test_unresolvable_axes_are_skipped_not_faked(self):
        # A calm era has no storm record; a fully extinct era has no
        # legibility — the axis is skipped, never defaulted.
        era = _fixture_era(storm=None, legibility=None)
        facts = evaluate_unlocks(era, [])
        axes = {fact["axis"] for fact in facts}
        self.assertNotIn("storm_record", axes)
        self.assertNotIn("legibility", axes)

    def test_live_unlock_facts_resolve_in_their_cited_era_records(self):
        from session_runner import _resolve_metric

        campaign = self.session["campaigns"][0]
        eras = {era["era_index"]: era for era in campaign["eras"]}
        self.assertTrue(campaign["unlocks"])
        for fact in campaign["unlocks"]:
            value = _resolve_metric(
                eras[fact["earned_era_index"]], fact["metric_path"]
            )
            self.assertEqual(fact["metric_value"], value)
            self.assertGreaterEqual(value, fact["threshold"])
            self.assertIn(fact["axis"], UNLOCK_THRESHOLDS)

    # -- extinction and succession ----------------------------------------

    def test_a_living_campaign_plans_no_succession(self):
        self.assertEqual("active", self.session["campaigns"][0]["status"])
        self.assertIsNone(plan_succession(self.session["campaigns"][0]))

    def test_extinct_fixture_campaign_triggers_succession(self):
        extinct = {
            "campaign_id": "doomed",
            "keeper_label": "keeper_test",
            "created_date": "2026-07-07",
            "predecessor_campaign_id": None,
            "status": "extinct",
            "base_seed": BASE_SEED,
            "unlocks": [
                {
                    "axis": "niche_mastery",
                    "tier": 1,
                    "earned_era_index": 0,
                    "metric_path": "report.summary.archive.filled_niches",
                    "metric_value": 5,
                    "threshold": 4,
                }
            ],
        }
        succession = plan_succession(extinct)
        self.assertEqual("doomed_successor", succession["campaign_id"])
        self.assertEqual("doomed", succession["predecessor_campaign_id"])
        self.assertNotEqual(BASE_SEED, succession["base_seed"])
        successor = run_campaign(
            **succession,
            weather_schedule=("calm",),
            generations=2,
            population=3,
            damage_cycles=1,
            ticks=8,
            **self.models,
        )
        # A fresh bloodline: seeds only, no inherited founders.
        self.assertEqual(
            "seed_pool",
            successor["eras"][0]["report"]["generations"][0][
                "parent_source"
            ],
        )
        # The Keeper's unlock state carries the predecessor's facts by
        # pointer — never by copy (DR 0022's succession rule).
        state = resolve_unlock_state(
            [extinct, successor], successor["campaign_id"]
        )
        self.assertIn(extinct["unlocks"][0], state)
        self.assertEqual(extinct["unlocks"][0]["earned_era_index"], 0)

    # -- the DR 0022 JSON-interim ledger ------------------------------------

    def test_ledger_matches_dr0022_schema_v1_vocabulary(self):
        ledger = build_campaign_ledger(self.session)
        self.assertEqual("dr0022_v1_json_interim", ledger["schema"])
        self.assertEqual(
            {
                "ledger_id",
                "schema",
                "campaigns",
                "eras",
                "elites",
                "founders",
                "unlocks",
                "replays",
            },
            set(ledger),
        )
        # C5: one replay row per era, path by convention, hash over the
        # replay's canonical JSON (pure functions of state).
        era_count = sum(
            len(campaign["eras"]) for campaign in self.session["campaigns"]
        )
        self.assertEqual(era_count, len(ledger["replays"]))
        for row in ledger["replays"]:
            self.assertRegex(
                row["artifact_path"], r"^replays/.+_era\d{3}\.json$"
            )
            self.assertEqual(64, len(row["artifact_sha256"]))

    def test_ledger_era_rows_pin_derived_columns_to_the_verbatim_report(self):
        ledger = build_campaign_ledger(self.session)
        live_eras = {
            (campaign["campaign_id"], era["era_index"]): era
            for campaign in self.session["campaigns"]
            for era in campaign["eras"]
        }
        self.assertTrue(ledger["eras"])
        for row in ledger["eras"]:
            era = live_eras[(row["campaign_id"], row["era_index"])]
            # Blob-authoritative: the report is stored verbatim...
            self.assertEqual(era["report"], row["report"])
            # ...and every derived column equals its blob field.
            report = row["report"]
            self.assertEqual(
                report["decision"]["status"], row["decision_status"]
            )
            summary = report["summary"]
            self.assertEqual(
                summary["archive"]["filled_niches"], row["filled_niches"]
            )
            self.assertEqual(summary["archive"]["coverage"], row["coverage"])
            self.assertEqual(summary["archive"]["qd_score"], row["qd_score"])
            self.assertEqual(
                summary["max_lineage_generation"],
                row["max_lineage_generation"],
            )
            self.assertEqual(row["rng_seed"], report["rng_seed"])

    def test_ledger_elite_rows_carry_the_full_elite_record(self):
        ledger = build_campaign_ledger(self.session)
        self.assertTrue(ledger["elites"])
        for row in ledger["elites"]:
            self.assertEqual(row["grid_id"], row["elite"]["grid_id"])
            self.assertEqual(row["fitness"], row["elite"]["fitness"])
            # The six-field archive contract, auditable without the
            # original pipeline objects.
            for field in (
                "grid",
                "descriptor",
                "fitness",
                "fitness_components",
                "validation",
                "provenance",
            ):
                self.assertIn(field, row["elite"])

    def test_ledger_founder_rows_mirror_the_engines_admissions(self):
        ledger = build_campaign_ledger(self.session)
        chained = self.session["campaigns"][0]["eras"][1]
        rows = [
            row
            for row in ledger["founders"]
            if row["era_index"] == chained["era_index"]
        ]
        self.assertEqual(
            chained["report"]["founders"]["admitted_ids"],
            [row["grid_id"] for row in rows if row["admitted"]],
        )
        self.assertEqual(
            [], [row for row in rows if not row["admitted"]]
        )

    # -- the Keeper's persistent session (G4) --------------------------------

    def _fresh_state(self) -> dict:
        return new_keeper_state(
            campaign_id="keeper_test",
            base_seed=BASE_SEED,
            engine_parameters=dict(
                generations=2,
                population=3,
                damage_cycles=1,
                ticks=8,
                dropout_rate=0.2,
                repair_epochs=20,
            ),
        )

    def test_incremental_advances_equal_the_batch_campaign(self):
        state = self._fresh_state()
        for weather in ("calm", "storm"):
            advance_keeper_state(state, weather, **self.models)
        batch = run_campaign(
            campaign_id="keeper_test",
            keeper_label="keeper",
            base_seed=BASE_SEED,
            weather_schedule=("calm", "storm"),
            generations=2,
            population=3,
            damage_cycles=1,
            ticks=8,
            **self.models,
        )
        self.assertEqual(batch, state["campaigns"][0])

    def test_advance_returns_the_turn_summary(self):
        state = self._fresh_state()
        turn = advance_keeper_state(state, "storm", **self.models)
        self.assertEqual("keeper_test", turn["campaign_id"])
        self.assertEqual("active", turn["status"])
        self.assertEqual("storm", turn["era"]["forecast"])
        self.assertIsNone(turn["succession"])
        self.assertEqual(
            len(turn["unlocks_earned"]), turn["unlock_state_count"]
        )

    def test_state_save_load_round_trips_with_backup_and_ledger(self):
        # C3 (DR 0022): the derived ledger is the promoted storage
        # module's SQLite file, rebuilt through the migration path.
        from mecha_engine.storage import campaign_history, open_ledger

        state = self._fresh_state()
        advance_keeper_state(state, "calm", **self.models)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keeper_session.json"
            ledger_path = Path(tmp) / "campaign_ledger.sqlite"
            save_keeper_state(state, path, ledger_path)
            self.assertEqual(state, load_keeper_state(path))
            conn = open_ledger(ledger_path)
            try:
                history = campaign_history(conn, "keeper_test")
                self.assertEqual(1, len(history["eras"]))
                self.assertEqual(
                    state["campaigns"][0]["eras"][0]["report"],
                    history["eras"][0]["report"],
                )
            finally:
                conn.close()
            save_keeper_state(state, path, ledger_path)
            self.assertTrue(
                (Path(tmp) / "keeper_session.bak.json").exists()
            )

    def test_summary_is_a_digest_read_model(self):
        state = self._fresh_state()
        advance_keeper_state(state, "calm", **self.models)
        summary = keeper_state_summary(state)
        self.assertEqual(SESSION_FORMAT, summary["session_format"])
        self.assertEqual(1, summary["campaigns"][0]["era_count"])
        # Digests only — the verbatim reports stay in the state file.
        self.assertNotIn("report", summary["campaigns"][0]["eras"][0])
        json.dumps(summary)

    def test_extinction_hands_the_session_to_the_successor(self):
        state = self._fresh_state()
        campaign = state["campaigns"][0]
        campaign["status"] = "extinct"
        campaign["unlocks"].append(
            {
                "axis": "niche_mastery",
                "tier": 1,
                "earned_era_index": 0,
                "metric_path": "report.summary.archive.filled_niches",
                "metric_value": 5,
                "threshold": 4,
            }
        )
        succession = apply_succession(state, campaign)
        self.assertEqual(
            "keeper_test_successor", succession["successor_campaign_id"]
        )
        self.assertEqual(1, succession["carried_unlock_count"])
        self.assertEqual(
            "keeper_test_successor", state["active_campaign_id"]
        )
        # The successor plays from seeds, carrying only the unlocks.
        turn = advance_keeper_state(state, "calm", **self.models)
        self.assertEqual("keeper_test_successor", turn["campaign_id"])
        self.assertEqual("seed_pool", turn["era"]["parent_source_generation_0"])
        self.assertGreaterEqual(turn["unlock_state_count"], 1)

    def test_advancing_an_extinct_campaign_is_refused(self):
        state = self._fresh_state()
        state["campaigns"][0]["status"] = "extinct"
        with self.assertRaises(ValueError):
            advance_keeper_state(state, "calm", **self.models)

    def test_succession_is_refused_for_living_campaigns(self):
        state = self._fresh_state()
        with self.assertRaises(ValueError):
            apply_succession(state, state["campaigns"][0])

    # -- artifacts -----------------------------------------------------------

    def test_era_replays_are_recorded_engine_truth(self):
        # C5: every era carries its best elite's recorded life at the
        # era's own seed — the DR 0023 recorder, per era.
        for campaign in self.session["campaigns"]:
            for era in campaign["eras"]:
                replay = era["replay"]
                self.assertIsNotNone(replay)
                self.assertEqual("mechagotchi_replay_v1", replay["replay_format"])
                self.assertEqual(era["rng_seed"], replay["parameters"]["rng_seed"])
                best = max(
                    era["elites"], key=lambda e: (e["fitness"], e["niche_key"])
                )
                self.assertEqual(
                    best["grid_id"], replay["creature"]["grid_id"]
                )
                self.assertGreater(replay["frame_count"], 0)

    def test_replay_files_match_their_ledger_rows(self):
        import hashlib

        from session_runner import write_replay_files

        ledger = build_campaign_ledger(self.session)
        self.assertTrue(ledger["replays"])
        with tempfile.TemporaryDirectory() as tmp:
            written = write_replay_files(self.session, tmp)
            self.assertEqual(len(ledger["replays"]), written)
            for row in ledger["replays"]:
                payload = (Path(tmp) / row["artifact_path"]).read_bytes()
                self.assertEqual(
                    row["artifact_sha256"],
                    hashlib.sha256(payload).hexdigest(),
                )
                json.loads(payload)  # a valid replay artifact

    def test_write_session_artifacts_round_trips(self):
        report = build_session_report(self.session)
        with tempfile.TemporaryDirectory() as tmp:
            write_session_artifacts(tmp, report, self.session)
            written = json.loads(
                (Path(tmp) / "session_runner_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
            ledger = json.loads(
                (Path(tmp) / "campaign_ledger.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(report, written)
            self.assertEqual(build_campaign_ledger(self.session), ledger)
            self.assertTrue((Path(tmp) / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
