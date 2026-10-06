"""The Keeper's recorded era outcomes, read without advancing or training a campaign.

DR 0021 Review/Collect consumes DR 0022's public, blob-authoritative history.
This view never writes a ledger or changes the live campaign's era offset.
"""
from __future__ import annotations

import copy
import json
import sqlite3
from pathlib import Path

from mecha_engine.storage import SUPPORTED_READ_SCHEMA_VERSIONS, campaign_history
from mecha_game.execution_readout import execution_lines, load_execution_summary
from mecha_game.campaign import KeeperCampaign

AXIS_LABELS = {
    "niche_mastery": "Niche mastery", "bloodline_depth": "Bloodline depth",
    "quality_diversity": "Quality-diversity", "storm_record": "Storm record",
    "legibility": "Legibility",
}


def _metric(value):
    if value is None:
        return "not recorded"
    return str(value)


class EraReview:
    def __init__(self, history: dict | None = None, *, error: str | None = None, executions=None):
        self.history = copy.deepcopy(history or {"eras": [], "unlocks": []})
        self.index = max(0, len(self.history["eras"]) - 1)
        self.error = error
        self.notice: str | None = None
        self.executions = copy.deepcopy(executions or {})

    @classmethod
    def load(cls, keeper_dir: str | Path, *, campaign_id: str | None = None):
        keeper = Path(keeper_dir)
        if campaign_id is None:
            state_path = keeper / "campaign_state.json"
            if not state_path.is_file():
                return cls()
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
            except (ValueError, UnicodeError) as error:
                raise ValueError("The recorded campaign state is not readable JSON.") from error
            if not isinstance(state, dict) or state.get("state_format") not in (KeeperCampaign.STATE_FORMAT, KeeperCampaign.POPULATION_STATE_FORMAT):
                raise ValueError("The recorded campaign state has an unsupported format.")
            if state['state_format'] == KeeperCampaign.POPULATION_STATE_FORMAT:
                from mecha_game.campaign_recovery import validate_ledger_state
                KeeperCampaign.validate_state_payload(state)
                validate_ledger_state(state, keeper / 'campaign.sqlite3')
            campaign_id = state.get("campaign_id")
        if not isinstance(campaign_id, str) or not campaign_id:
            raise ValueError("The recorded campaign has no valid identity.")
        ledger = keeper / "campaign.sqlite3"
        if not ledger.is_file():
            raise ValueError("The recorded campaign ledger is missing.")
        try:
            # The connection is read-only even for empty, corrupt or foreign
            # databases. The existing public query owns the storage schema.
            conn = sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True)
            try:
                version = conn.execute("PRAGMA user_version").fetchone()[0]
                if version not in SUPPORTED_READ_SCHEMA_VERSIONS:
                    raise ValueError(f"Unsupported campaign-ledger schema version: {version}")
                history = campaign_history(conn, campaign_id)
                executions = {era["era_index"]: load_execution_summary(conn, campaign_id, era["era_index"])
                              for era in history["eras"]}
            finally:
                conn.close()
        except (sqlite3.Error, KeyError) as error:
            raise ValueError(f"Recorded era history is unavailable: {error}") from error
        if any(not isinstance(era.get("report"), dict) or
               not isinstance(era.get("weather") or {}, dict) for era in history["eras"]):
            raise ValueError("The ledger contains an invalid era report.")
        view = cls(history, executions=executions)
        try:
            # Check every saved page now: a malformed older blob must yield an
            # unavailable view, not crash the app later when the player browses.
            for index in range(len(history["eras"])):
                view.index = index
                view.lines()
        except (KeyError, TypeError, AttributeError) as error:
            raise ValueError("The ledger contains an invalid era report.") from error
        view.index = max(0, len(history["eras"]) - 1)
        return view

    @property
    def current(self) -> dict | None:
        eras = self.history["eras"]
        return eras[self.index] if eras else None

    @property
    def execution(self):
        return self.executions.get(self.current["era_index"]) if self.current is not None else None

    def move(self, delta: int) -> int:
        self.notice = None
        self.index = max(0, min(max(0, len(self.history["eras"]) - 1), self.index + delta))
        return self.index

    def earned(self) -> list[dict]:
        if self.current is None:
            return []
        return [fact for fact in self.history["unlocks"]
                if fact.get("campaign_id") == self.history.get("campaign_id")
                and fact["earned_era_index"] == self.current["era_index"]]

    def lines(self) -> list[str]:
        lines = self._lines()
        if self.notice:
            lines.insert(1, self.notice)
        return lines

    def _lines(self) -> list[str]:
        if self.error:
            return ["ERA REVIEW unavailable", "Your companion is paused.", self.error, "T or Escape returns to care."]
        era = self.current
        if era is None:
            return ["ERA REVIEW", "Your companion is paused.", "No era has been recorded for this bloodline yet.",
                    "E run the first era   T or Escape returns to care."]
        report = era["report"]
        summary = report.get("summary") or {}
        archive = summary.get("archive") or {}
        weather = era.get("weather") or {}
        result = "bloodline ended" if era.get("went_extinct") else "bloodline continued"
        lines = [
            f"ERA {era['era_index']} [{weather.get('forecast', 'not recorded')}]   {self.index + 1}/{len(self.history['eras'])}",
            f"{result}; generations {_metric(summary.get('generation_count'))}/{_metric(report.get('generations_requested'))}",
            f"Niches {_metric(archive.get('filled_niches'))}   coverage {_metric(archive.get('coverage'))}",
            f"QD {_metric(archive.get('qd_score'))}   lineage depth {_metric(summary.get('max_lineage_generation'))}",
            "Your companion is paused. [ ] eras   T close",
            "B archive   V replay   C covenant   E era",
        ]
        if report.get('body_response') == 'workload-v1':
            lines.append('Recorded body response: workload-v1; play energy follows each evaluated body.')
        population = report.get('living_population')
        if population is not None:
            termination = population['termination']
            lines[2:2] = [
                f"Living breeders: {len(population['final_breeders'])}   Historical archive: {_metric(archive.get('filled_niches'))}",
                'Population: living generations; survival environment: '+population['survival_regime'],
                f"Evaluated {population['evaluated_candidates']}/{population['requested_candidate_slots']}; unexecuted {population['unexecuted_candidate_slots']}",
                f"Final cohort: {termination['lifecycle_deaths']} lifecycle deaths; {termination['structural_disqualifications']} structural disqualifications",
                'Archives retain history; they do not refill the living population.',
            ]
            if termination['ended']:
                lines.append('Population ended: '+termination['reason'].replace('_',' ')+'. C opens preparation; N: Create successor.')
        elif report.get('survival_regime'):
            lines.append('Survival environment: '+report['survival_regime'])
        facts = self.earned()
        lines.append(f"UNLOCKS EARNED THIS ERA: {len(facts)}")
        if not facts:
            lines.append("No new unlocks. Previously earned tiers remain available.")
        for fact in facts:
            lines.append(f"{AXIS_LABELS.get(fact['axis'], fact['axis'])} tier {fact['tier']}: "
                         f"{fact['metric_value']} met threshold {fact['threshold']}")
        inherited = sum(fact.get("campaign_id") != self.history.get("campaign_id") for fact in self.history["unlocks"])
        if inherited:
            lines.append(f"{inherited} unlock facts inherited from earlier bloodlines.")
        lines.append("WEATHER RECORD")
        pressure = (report.get("cubff_pressure") or {}).get("by_generation") or []
        if not pressure:
            lines.append("No CuBFF multiplier recorded; base era damage still applies.")
        for index, row in enumerate(pressure):
            lines.append(f"Generation {index}: dropout x{row['dropout_multiplier']} / {row['snapshot_id']}")
        founders = report.get("founders")
        if founders is not None:
            lines.append(f"FOUNDERS: {len(founders['admitted_ids'])} admitted; {len(founders['rejected'])} refused")
            for grid_id in founders["admitted_ids"]:
                lines.append(f"ADMITTED: {grid_id}")
            for rejected in founders["rejected"]:
                lines.append(f"{rejected['grid_id']}: {'; '.join(rejected['errors'])}")
        lines.extend(execution_lines(self.execution))
        lines.append("These are recorded era results; viewing them does not run the soup.")
        return lines
