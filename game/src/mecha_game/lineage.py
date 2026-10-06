"""The lineage browser — the Keeper's whole story (F14, MVP 0.3).

Pages the session's lineage records: each life's identity, how it
began (the additive `origin` fact — founder / hatched / era_elite /
succession), how it ended (the engine's own death cause), and the
grid schema's VERBATIM lineage block — generation, ancestor_ids,
mutation_events. The browser never invents a fact: every line is a
record field, absent fields stay absent.
"""

from __future__ import annotations

import json


class LineageBrowser:
    """Scrub the bloodline's lives, newest first on open."""

    def __init__(self, lineage_records: list[dict], *, chronicle: dict | None = None) -> None:
        if not lineage_records:
            raise ValueError("no lives recorded yet")
        self.records = lineage_records
        self.chronicle = chronicle
        self.index = len(lineage_records) - 1

    @property
    def count(self) -> int:
        return len(self.records)

    def current(self) -> dict:
        return self.records[self.index]

    def step(self) -> int:
        self.index = min(self.count - 1, self.index + 1)
        return self.index

    def back(self) -> int:
        self.index = max(0, self.index - 1)
        return self.index

    def caption(self) -> str:
        record = self.current()
        origin = record.get("origin", "?")
        if "death_cause" in record:
            ending = (
                f"died {record['death_cause']} at age "
                f"{record['died_age_ticks']}"
            )
        elif record.get("outcome") == "replaced_alive":
            ending = f"replaced alive at age {record['ended_age_ticks']}"
        elif record.get("outcome") == "unknown":
            ending = "outcome unavailable"
        else:
            ending = "alive"
        return (
            f"life {self.index + 1}/{self.count}  "
            f"{record['grid_id']}  [{origin}]  {ending}"
        )

    def detail_lines(self) -> list[str]:
        record = self.current()
        block = record.get("lineage") or {}
        lines = [
            f"parent {record.get('parent_grid_id')}   "
            f"generation {block.get('generation', 0)}   "
            f"born tick {record.get('born_session_tick', 0)}"
        ]
        ancestors = block.get("ancestor_ids") or []
        if ancestors:
            lines.append(f"Recorded ancestors ({len(ancestors)}), in stored order:")
            lines.extend(f"{index + 1}. {ancestor}" for index, ancestor in enumerate(ancestors))
        events = block.get("mutation_events") or []
        if events:
            lines.append(f"Recorded mutation events ({len(events)}):")
            # FooterPager makes the complete original fields reachable, including
            # object payloads; do not invent a label or discard earlier events.
            lines.extend(f"{index + 1}. " + (event if isinstance(event, str) else
                         json.dumps(event, ensure_ascii=False, sort_keys=True))
                         for index, event in enumerate(events))
        if "life_id" in record:
            lines.append(f"Keeper life {record['life_id']}")
        if "name" in record:
            lines.append(f"Name during this life: {record['name']}")
        if "previous_life_id" in record:
            lines.append(f"Previous cared life: {record['previous_life_id']}")
        if "parent_life_id" in record:
            lines.append(f"Recorded genetic parent life: {record['parent_life_id']}")
        if "ended_session_tick" in record:
            lines.append(f"Life ended at Keeper tick {record['ended_session_tick']}")
        if "source" in record:
            lines.append("Adoption source: " + json.dumps(record["source"], ensure_ascii=False, sort_keys=True))
        if "prior_history_unavailable" in record:
            lines.append("Earlier Keeper history unavailable: " + record["prior_history_unavailable"])
        if self.chronicle is not None:
            lines.append(f"Keeper identity: {self.chronicle['keeper_id']}")
            lines.append(f"Current recorded campaign: {self.chronicle.get('campaign_id') or 'not associated'}")
            if self.chronicle.get("prior_history") == "unavailable":
                lines.append("Earlier Keeper history unavailable: " + self.chronicle.get(
                    "prior_history_reason", "the legacy save did not preserve a complete prior chronicle."))
            links = [link for link in self.chronicle.get("campaign_links", [])
                     if link["life_id"] == record.get("life_id")]
            if links:
                lines.append("Campaign associations recorded during this life:")
                lines.extend(json.dumps(link, ensure_ascii=False, sort_keys=True) for link in links)
        from mecha_game.body_response import body_lines
        lines.extend(body_lines(record))
        selection = record.get("care_selection")
        if selection is not None:
            receipt = selection["receipt"]
            lines.append(f"Care selection: {receipt['policy']} / {receipt['evaluator']}.")
            lines.append(f"Selected trial {receipt['selected_index'] + 1}/{receipt['pool_size']} from the parent's retained care window.")
            lines.append("Morphology stress-test evidence; generated child cells and newborn learning start unchanged.")
        lines.append("Behavior priors belong to the species covenant; morphology descriptors are not individual personality.")
        summary = record.get("care_summary")
        if summary is not None:
            history = summary["history"]
            if history == "complete":
                lines.append(f"Care recorded from birth: {summary['ticks_observed']} ticks observed.")
            elif history == "partial":
                lines.append(f"Earlier care unavailable. Recorded from age {summary['from_age_ticks']}: "
                             f"{summary['ticks_observed']} ticks observed.")
            else:
                lines.append("Care history unavailable in the legacy save.")
            for key, label in (("keeper_actions", "Keeper actions"), ("companion_actions", "Companion actions")):
                counts = summary[key]
                lines.append(label + ": " + (", ".join(f"{action}: {count}" for action, count in counts.items())
                                               if counts else "none recorded"))
            lines.append(f"Engine beg requests: {summary['beg_requests']}")
            lines.append(f"Learning policy: {record.get('learning_policy', 'incumbent')}")
            events = record.get("events", [])
            lines.append(f"Recent observed events: {len(events)}; {record.get('events_omitted', 0)} earlier "
                         "events counted in care totals, outside the retained tail.")
            lines.extend(json.dumps(event, ensure_ascii=False, sort_keys=True) for event in events)
        return lines
