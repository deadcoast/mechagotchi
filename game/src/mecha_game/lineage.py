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

    def __init__(self, lineage_records: list[dict]) -> None:
        if not lineage_records:
            raise ValueError("no lives recorded yet")
        self.records = lineage_records
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
        return lines
