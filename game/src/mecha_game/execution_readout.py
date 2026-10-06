"""Immutable era evidence for readers and explicit disposable reproduction.

Inspection does not simulate, load live fixtures, train, or write a Keeper.
"""
from __future__ import annotations

import base64
import copy
import json
from pathlib import Path
import sqlite3


def unavailable(reason):
    return {"status": "unavailable", "reason": str(reason)}


def summarize_execution(bundle):
    """Discard bulky retained models/raw bytes after verified, read-only inspection."""
    from mecha_game.execution import inspect_execution, body_arguments
    status = inspect_execution(bundle)
    if bundle is None:
        return status
    manifest = bundle["manifest"]
    result = dict(status, campaign_id=manifest["campaign_id"], era_index=manifest["era_index"],
                  founder_occurrences=copy.deepcopy(manifest["founder_occurrences"]),
                  sources=copy.deepcopy(manifest["sources"]))
    # Only the corpus identities are retained by this view. No model is rebuilt.
    digest = manifest["inputs"]["seed_corpus_sha256"]
    seeds = json.loads(base64.b64decode(bundle["blobs"][digest]["data_base64"]).decode("utf-8"))
    result["seed_ids"] = [grid.get("grid_id") for grid in seeds]
    result.update(body_arguments(bundle))
    return result


def load_execution_summary(conn, campaign_id, era_index):
    from mecha_engine.storage import load_era_execution
    try:
        return summarize_execution(load_era_execution(conn, campaign_id, era_index))
    except (ValueError, KeyError, TypeError, AttributeError, sqlite3.Error) as error:
        return unavailable(f"Recorded inputs cannot be verified: {error}")


def execution_lines(evidence):
    if evidence is None:
        evidence = unavailable("Immutable inputs were not recorded for this historical era.")
    status = evidence["status"]
    reason = evidence.get("reason") or "inputs missing"
    if reason == "historical_inputs_not_recorded":
        reason = "Immutable inputs were not recorded for this historical era."
    lines = ["REPRODUCTION: " + ("available; D explicitly compares recorded inputs" if status == "available"
                               else "unavailable - " + str(reason))]
    if evidence.get("body_response") == "workload-v1":
        lines.append("Recorded body response: workload-v1; immutable play workload model.")
    occurrences = evidence.get("founder_occurrences", [])
    if not occurrences:
        if "founder_occurrences" in evidence:
            lines.append("No founder occurrences were submitted.")
        return lines
    lines.append("RECORDED FOUNDER OCCURRENCES (submission order)")
    sources = evidence.get("sources", [])
    for row in occurrences:
        label = row.get("label")
        if label is None:
            matches = [source for source in sources if source.get("role") == "founder"
                       and source.get("source_position") == row.get("source_position")
                       and source.get("source_kind") == row.get("source_kind")]
            if len(matches) == 1:
                label = matches[0].get("label")
        verdict = "ADMITTED" if row["admitted"] else "REFUSED"
        lines.append(f"Occurrence {row['ordinal']}: {row['grid_id']} - {verdict}")
        kind = row['source_kind'].replace('_', ' ')
        position = row.get('source_position')
        position = 'not recorded' if position is None else str(position)
        lines.append(f"Source: {kind}; position {position}; "
                     + (label or "no source filename recorded"))
        if row.get("life_id"):
            lines.append(f"Staged Keeper life: {row['life_id']}")
        if row.get("campaign_id") is not None:
            if row.get('source_kind') == 'era_breeder':
                lines.append(f"Prior living breeder: {row['campaign_id']} era {row.get('era_index')}; generation {row.get('generation_index')}, candidate {row.get('candidate_index')}, slot {row.get('source_position')}")
            else:
                lines.append(f"Recorded prior origin: {row['campaign_id']} era {row.get('era_index')} niche {row.get('niche_key', 'not recorded')}")
        if not row["admitted"]:
            lines.extend(row.get("rejection_errors") or ["Refusal details not recorded."])
    return lines


def _living_descendant_lines(evidence, report, elite):
    """Follow verified occurrence references, including nonwinning parents."""
    from mecha_engine.runtime.care import care_grid_sha256
    if not isinstance(elite.get('grid'), dict):
        return ['Release-origin link unavailable: the archived body is missing.']
    digest = care_grid_sha256(elite['grid'])
    occurrences, matches = {}, []
    for generation in report.get('generations', []):
        for row in generation.get('creatures', []):
            breeding = row.get('breeding')
            if not isinstance(breeding, dict): continue
            ref = breeding.get('occurrence') or {}
            key = (ref.get('generation_index'), ref.get('candidate_index'))
            if key in occurrences:
                return ['Release-origin link unavailable: duplicate evaluated occurrence.']
            occurrences[key] = breeding
            if breeding.get('final_grid_sha256') == digest:
                matches.append(key)
    if len(matches) != 1:
        return ['Release-origin link unavailable: the archived body has no unique evaluated occurrence.']
    current, seen, steps = matches[0], set(), 1
    founders = evidence.get('founder_occurrences', [])
    while current not in seen:
        seen.add(current)
        parent = occurrences[current].get('parent_occurrence') or {}
        kind = parent.get('kind')
        if kind == 'submitted_founder':
            rows = [row for row in founders if row.get('ordinal') == parent.get('submission_index')]
            if len(rows) != 1 or not rows[0].get('admitted'):
                break
            row = rows[0]
            return [f"Recorded founder origin: occurrence {row['ordinal']} ({row['grid_id']}); {steps} recorded evaluation parent link(s).",
                    'This follows exact submitted and living-parent occurrences; declared ancestry and cared lives remain separate.']
        if kind == 'seed_corpus':
            return ['Recorded evaluation chain reaches the seed corpus; no released-founder origin is established.']
        if kind != 'generation_breeder': break
        prior = (parent.get('generation_index'), parent.get('candidate_index'))
        if (prior not in occurrences or prior[0] != current[0] - 1
                or not occurrences[prior].get('eligible')):
            break
        if parent.get('grid_sha256') is not None and parent['grid_sha256'] != occurrences[prior].get('final_grid_sha256'):
            break
        current = prior
        steps += 1
    return ['Release-origin link unavailable: the recorded occurrence chain is incomplete.']


def descendant_lines(evidence, report, elite):
    """Follow actual evaluation parent events under the verified runtime contract.

The supported live_cycle names its final body candidate_cNN. This is not an
authored ancestor_ids join. Missing, repeated or colliding identities refuse it.
"""
    if not evidence or evidence.get("status") != "available":
        return ["Release-origin link unavailable: verified execution inputs are required."]
    if report.get('living_population') is not None:
        return _living_descendant_lines(evidence, report, elite)
    founders = evidence.get("founder_occurrences", [])
    seeds = evidence.get("seed_ids", [])
    graph = {}
    for generation in report.get("generations", []):
        for row in generation.get("creatures", []):
            if row.get("archive_decision") not in ("inserted", "replaced"):
                continue
            candidate = row.get("candidate_grid_id")
            cycles = row.get("cycles", [])
            if not isinstance(candidate, str) or not isinstance(cycles, list):
                continue
            if cycles and [cycle.get("cycle") for cycle in cycles] != list(range(1, len(cycles) + 1)):
                continue
            final_id = f"{candidate}_c{len(cycles):02d}" if cycles else candidate
            graph.setdefault(final_id, []).append(row.get("parent_grid_id"))
    current, seen, steps = elite.get("grid_id"), set(), 0
    while current is not None and current not in seen:
        seen.add(current)
        occurrences = [row for row in founders if row.get("grid_id") == current]
        seed_count = seeds.count(current)
        if occurrences:
            admitted = [row for row in occurrences if row.get("admitted")]
            if len(occurrences) != 1 or seed_count or current in graph:
                return [f"Release-origin link ambiguous: {current} has repeated input or evaluation identities."]
            if len(admitted) != 1 or not steps:
                break
            row = admitted[0]
            title = {'workshop_release': 'Recorded release origin',
                     'keeper_companion': 'Recorded released companion origin',
                     'era_elite': 'Recorded prior-era founder',
                     'in_memory': 'Recorded in-memory founder'}.get(row.get('source_kind'), 'Recorded founder origin')
            return [f"{title}: occurrence {row['ordinal']} ({current}); "
                    f"{steps} recorded evaluation parent link(s).",
                    "Admission and evaluation records support this link; declared ancestry and cared lives remain separate."]
        if seed_count:
            if seed_count != 1 or current in graph:
                return [f"Release-origin link ambiguous: {current} has repeated seed or evaluation identities."]
            return ["Recorded evaluation chain reaches the seed corpus; no released-founder origin is established."]
        parents = graph.get(current, [])
        if len(parents) > 1:
            return [f"Release-origin link ambiguous: {current} has multiple recorded evaluations."]
        if not parents:
            break
        current = parents[0]
        steps += 1
    return ["Release-origin link unavailable: the recorded evaluation chain is incomplete."]


def reproduce_saved_era(keeper_dir, campaign_id, era_index, *, progress_callback=None):
    """Own the read-only connection in the caller's thread, including UI workers."""
    from mecha_engine.storage import SUPPORTED_READ_SCHEMA_VERSIONS
    from mecha_game.execution import reproduce_era
    ledger = Path(keeper_dir) / "campaign.sqlite3"
    if not ledger.is_file():
        return unavailable("The recorded campaign ledger is missing.")
    try:
        conn = sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version not in SUPPORTED_READ_SCHEMA_VERSIONS:
                return unavailable(f"Unsupported campaign-ledger schema version: {version}")
            return reproduce_era(conn, campaign_id, era_index, progress_callback=progress_callback)
        finally:
            conn.close()
    except (ValueError, OSError, sqlite3.Error) as error:
        return unavailable(error)


def comparison_notice(result):
    status = result["status"]
    if status == "matched":
        return "Reproduction MATCHED: complete report and every elite match. Original results and footage are unchanged."
    details = [result["reason"]] if result.get("reason") else []
    details.extend(result.get("differing_paths") or [])
    detail = "; ".join(details) or "No further detail recorded."
    return f"Reproduction {status.upper()}: {detail}. Original results and footage are unchanged."


def reproduce_to_directory(keeper_dir, campaign_id, era_index, output):
    """Write comparison/recomputed results only to a new, separate directory."""
    keeper = Path(keeper_dir).resolve()
    output = Path(output).resolve()
    if output == keeper or output.is_relative_to(keeper):
        raise ValueError("Reproduction output must be outside the Keeper directory.")
    if output.exists():
        raise ValueError("Reproduction output must be a new directory; existing files were preserved.")
    if type(era_index) is not int or era_index < 0 or not isinstance(campaign_id, str) or not campaign_id.strip():
        raise ValueError("Reproduction requires a nonnegative era and recorded campaign identity.")
    output.mkdir()
    result = reproduce_saved_era(keeper, campaign_id, era_index)
    for filename, value in (("comparison.json", result), ("report.json", result.get("report")),
                            ("elites.json", result.get("elites"))):
        if value is not None:
            with (output / filename).open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
                stream.write("\n")
    return result
