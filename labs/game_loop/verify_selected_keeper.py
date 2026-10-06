"""X3 connected selected-Keeper API/native-source demonstration in owned fixtures."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from labs.game_loop.verify_integrated_finish import interact, key, run, CompanionSession, pygame, inventory
from mecha_game.creator_bridge import CreatorBridge
from mecha_game.keeper_context import read_keeper
from mecha_game.packs import pack_digest


def request(url, path, body=None):
    raw = None if body is None else json.dumps(body).encode("utf-8")
    req = Request(url + path.lstrip("/"), data=raw, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=45) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def pins(context):
    return dict(context_id=context["context_id"], expected_context_revision=context["context_revision"])


def verify(fixtures, screenshots, bundle=None):
    fixtures.mkdir(parents=True, exist_ok=False)
    screenshots.mkdir(parents=True, exist_ok=True)
    checks, flows, responses, launches = {}, [], {}, []
    a, b = fixtures / "keeper-a", fixtures / "keeper-b"
    for keeper in (a, b):
        assert run(["--keeper-dir", str(keeper), "--era-scale", "tiny", "--eras", "1",
                    "--ticks", "1", "--tick-frames", "1", "--fps", "0", "--scale", "1"]) == 0
    initial_b = inventory(b)
    bridges = [CreatorBridge(a), CreatorBridge(b)]
    try:
        with patch("mecha_game.creator_bridge.webbrowser.open", return_value=False):
            urls = [bridge.open() for bridge in bridges]
        ca = request(urls[0], "/api/context")[1]
        cb = request(urls[1], "/api/context")[1]
        checks["distinct_native_contexts"] = ca["available"] and cb["available"] and ca["context_id"] != cb["context_id"]
        rows = request(urls[0], "/api/context/creatures")[1]["creatures"]
        chosen = next(row for row in rows if row["source"] == "companion")
        code, loaded = request(urls[0], "/api/context/document", dict(pins(ca), ref=chosen["ref"]))
        assert code == 200, loaded
        doc = copy.deepcopy(loaded["document"])
        doc["grid"]["grid_id"] = "x3_selected_release"
        doc["grid"].setdefault("metadata", {})["creator_note"] = "Exact selected Keeper specimen"
        doc["grid"]["cells"][0]["mutation_weight"] = .613
        code, preview = request(urls[0], "/api/preview/clip", dict(pins(ca), document=doc, draft_revision=1, clip="idle"))
        checks["selected_exact_document_preview"] = code == 200 and preview.get("draft_revision") == 1
        code, released = request(urls[0], "/api/release", dict(pins(ca), name="x3_selected_release",
                                document=doc, draft_revision=1, expected_release_revision=None))
        assert code == 200, released
        responses["release"] = released
        checks["release_is_staging"] = released["status"] == "staged"
        checks["released_semantics_preserved"] = released["released_document"]["grid"]["cells"] == doc["grid"]["cells"]
        checks["release_context_provenance"] = released["release_provenance"]["keeper_id"] == ca["keeper_id"]
        # A valid 8x8 candidate demonstrates staging versus actual 16x16 admission.
        small = json.loads((ROOT / "data/seed_grids/mg_seed_002.json").read_text(encoding="utf-8"))
        small["grid_id"] = "x3_valid_but_incompatible"
        code, refusal_candidate = request(urls[0], "/api/release", dict(pins(ca), name="x3_small",
                document=dict(format=doc["format"], grid=small), draft_revision=2, expected_release_revision=None))
        assert code == 200, refusal_candidate
        checks["other_keeper_unchanged_during_authoring"] = inventory(b) == initial_b
        profile = copy.deepcopy(ca["covenant"])
        profile["profile_id"] = "x3_shared_covenant"
        composition = dict(pins(ca), draft_revision=3, pack_id="x3_exchange", title="Selected Keeper exchange",
            provenance=dict(source="Supported selected-Keeper API demonstration", keeper_id=ca["keeper_id"]),
            slips=[profile], creatures=[released["released_document"]["grid"], refusal_candidate["released_document"]["grid"]])
        code, built = request(urls[0], "/api/packs/build", composition)
        assert code == 200 and built["all_accepted"], built
        pack = built["pack"]
        # Check binary download using the actual supported export adapter.
        req = Request(urls[0] + "api/packs/export", data=json.dumps(composition).encode("utf-8"),
                      headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=20) as response:
            exported = response.read()
            responses["export_filename"] = response.headers.get("Content-Disposition")
        checks["export_exact_composition"] = json.loads(exported) == pack
        (fixtures / "mechagotchi-pack_x3_exchange.json").write_bytes(exported)
        before_a = inventory(a)
        code, imported = request(urls[1], "/api/packs/import", dict(pins(cb), draft_revision=4,
                    pack=pack, expected_pack_digest=pack_digest(pack)))
        assert code == 200, imported
        responses["import"] = imported
        checks["all_format_valid_items_staged"] = imported["all_accepted"]
        checks["incompatibility_reported_before_era"] = any(not row.get("compatibility", {}).get("ok", True) for row in imported["creatures"])
        checks["first_keeper_unchanged_by_second_import"] = inventory(a) == before_a
        # A changed selection cannot re-use the reviewed digest.
        tampered = copy.deepcopy(pack); tampered["title"] += " changed"
        before_b = inventory(b)
        code, refused = request(urls[1], "/api/packs/import", dict(pins(cb), draft_revision=5,
                    pack=tampered, expected_pack_digest=pack_digest(pack)))
        checks["tampered_review_refused_without_writes"] = code >= 400 and inventory(b) == before_b
        responses["tampered_review"] = refused
    finally:
        for bridge in bridges:
            bridge.close()
    checks["owned_api_servers_closed"] = all(bridge.server is None for bridge in bridges)

    def play(keeper, label, batches):
        flow = interact(keeper, label, batches, screenshots, scale=16)
        flows.append(flow)
        checks[label + "_exit_and_fit"] = flow["code"] == 0 and all(page["fits"] for page in flow["pages"])
        checks[label + "_workers_joined"] = all(not row["alive"] for row in flow["joins"])
        return flow

    first_before = inventory(a)
    flow = play(b, "second-keeper-covenant-era", [[key(pygame.K_i)], [key(pygame.K_RETURN)],
                [key(pygame.K_ESCAPE)], [key(pygame.K_w)], [key(pygame.K_e)],
                [key(pygame.K_F1)], [key(pygame.K_ESCAPE)]])
    checks["first_keeper_unchanged_by_second_era"] = inventory(a) == first_before
    saved = read_keeper(b)
    checks["restart_context_available"] = saved["context"]["available"]
    checks["imported_covenant_applied"] = saved["context"]["covenant"]["profile_id"] == profile["profile_id"]
    current = saved["lineage"]["campaigns"][0]
    era = current["eras"][-1]
    verdict = era["report"].get("founders", {})
    checks["selected_release_actually_admitted"] = "x3_selected_release" in verdict.get("admitted_ids", [])
    checks["incompatible_release_actually_refused"] = any(row["grid_id"] == "x3_valid_but_incompatible" for row in verdict.get("rejected", []))
    records = {row["grid_id"]: row for row in era["founder_records"]}
    checks["full_admitted_source_survives_restart"] = records.get("x3_selected_release", {}).get("grid") == released["released_document"]["grid"]
    checks["full_refused_source_survives_restart"] = records.get("x3_valid_but_incompatible", {}).get("grid") == refusal_candidate["released_document"]["grid"]
    responses["recorded_founder_verdict"] = verdict
    responses["recorded_era_index"] = era["era_index"]
    responses["recorded_genetic_relations"] = [
        dict(grid_id=row["grid_id"], lineage=row["grid"].get("lineage", {}),
             parent_grid_id=row["grid"].get("parent_grid_id"))
        for row in era["elites"]]
    checks["recorded_elites_inspectable"] = bool(era["elites"])
    play(b, "restart-archive", [[key(pygame.K_t)], [key(pygame.K_b)], [key(pygame.K_F1)]])
    with patch("mecha_game.creator_bridge.webbrowser.open", return_value=False):
        age = CompanionSession.load(b / "companion.json").session_tick
        play(b, "native-source-creator", [[key(pygame.K_j)], [key(pygame.K_f)], [key(pygame.K_j), key(pygame.K_f)]])
    checks["creator_view_paused_care"] = CompanionSession.load(b / "companion.json").session_tick == age
    # Reopened selected inspection resolves recorded elites from the saved ledger.
    bridge = CreatorBridge(b)
    try:
        with patch("mecha_game.creator_bridge.webbrowser.open", return_value=False):
            url = bridge.open()
        context = request(url, "/api/context")[1]
        entries = request(url, "/api/context/creatures")[1]["creatures"]
        elite = next(row for row in entries if row["source"] == "era_elite" and row["ref"]["era_index"] == era["era_index"])
        code, selected = request(url, "/api/context/document", dict(pins(context), ref=elite["ref"]))
        checks["restart_exact_elite_selection"] = code == 200 and selected["document"]["grid"]["grid_id"] == elite["grid_id"]
        lineage = request(url, "/api/context/lineage")[1]
        checks["http_restart_actual_admission"] = lineage["campaigns"][0]["eras"][-1]["report"]["founders"] == verdict
    finally:
        bridge.close()
    if bundle is not None:
        env = os.environ.copy(); env.pop("SDL_VIDEODRIVER", None); env.pop("SDL_AUDIODRIVER", None)
        for action in ("launch", "resume"):
            before = CompanionSession.load(b / "companion.json")
            start = time.perf_counter()
            process = subprocess.run([str(bundle.resolve()), "--keeper-dir", str(b.resolve()),
                "--ticks", "1", "--tick-frames", "1", "--fps", "0", "--scale", "16"],
                cwd=ROOT, env=env, capture_output=True, timeout=60)
            after = CompanionSession.load(b / "companion.json")
            passed = process.returncode == 0 and after.keeper_id == before.keeper_id and after.session_tick == before.session_tick + 1
            checks["native_" + action] = passed
            launches.append(dict(action=action, returncode=process.returncode, seconds=time.perf_counter()-start, passed=passed))
    return dict(schema_version=1, scope="X3 selected-Keeper source/API and native-process integration",
        passed=all(checks.values()), checks=checks, flows=flows, responses=responses, native_launches=launches,
        bundle=str(bundle) if bundle else None, bundle_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest() if bundle else None,
        fixtures=str(fixtures), limits=["Source events are injected; native process launches do not prove OS keyboard automation.",
        "Named pack API exchange complements the independent real browser UI composition/download/import evidence.",
        "Recorded genotype relations are shown verbatim; missing ancestry and historical founder sources are not inferred.",
        "Tiny eras are integration observations, not new scientific adoption or performance evidence.",
        "Detached resource delivery and packaged creator availability remain X4 gates."])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--screenshots", type=Path, required=True)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.fixtures, args.screenshots, args.bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(passed=result["passed"], checks=len(result["checks"]),
                         failed=[name for name,value in result["checks"].items() if not value],
                         flows=len(result["flows"]), native_launches=len(result["native_launches"]))))
    raise SystemExit(0 if result["passed"] else 1)
