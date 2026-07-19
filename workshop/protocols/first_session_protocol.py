"""H5 (cycle 18): the scripted first-session protocol.

The documented UX goal: a first session authors a creature + its SLIP
from blank state through release in <=45 minutes. This protocol drives
the REAL workshop server through that whole journey — the editor pages,
the first refusal (the validator's words are the teaching moment), the
finished creature, the species SLIP with deliberation, the layered
save, the clip scrub, the release, and the animated share — timing
every step.

Honesty contract: the scripted wall-clock is a PROXY. It proves the
path exists end to end and counts the interactions; it does not
measure a human. The human pass is PREPARED (its step list rides the
artifact) and recorded as not blocking — the calibration pattern.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SERVER_DIR = ROOT / "workshop" / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from workshop_server import start_workshop_server  # noqa: E402


FIRST_SESSION_BOUND_SECONDS = 45 * 60
ARTIFACT_ID = "workshop_first_session_stage0"

# The first creature: a 16x16 moth at the ratified default scale.
# Body mass 30 — the species SLIP below is authored to bound it.
FIRST_CREATURE = [
    list(row)
    for row in [
        "................",
        "................",
        "......EBBE......",
        ".....BBBBBB.....",
        ".....BBABBB.....",
        ".....BBBBBB.....",
        "......BMMB......",
        "......BBBB......",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]
]
# The first refusal: the same body with its anchor erased — the
# validator's words teach the anchor invariant.
BROKEN_FIRST_DRAFT = [row[:] for row in FIRST_CREATURE]
BROKEN_FIRST_DRAFT[4][7] = "B"

FIRST_SPECIES = {
    "slip_version": "0.2.0",
    "profile_id": "slip_first_session",
    "name": "First Session Species",
    "grid": {
        "allowed_palettes": ["lcd_green", "amber_terminal"],
        "body_mass_min": 4,
        "body_mass_max": 40,
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
    "deliberation": {"max_ticks": 3, "confidence_threshold": 0.72},
}

HUMAN_PASS_STEPS = [
    "open the workshop (mechas workshop) and the slip creator",
    "draw a first 16x16 creature; meet at least one refusal and fix it "
    "from the validator's words",
    "author the species SLIP (palettes, mass bounds, organ roles, "
    "mutation caps, behavior/survival weights, deliberation depth) "
    "until the authority accepts it",
    "save the creature with its semantic layers",
    "scrub a clip on the timeline (onion skin on) and adjust the anchor "
    "until the motion reads",
    "release the creature into the ecosystem",
    "export the animated APNG carrying the scrubbed clip",
    "record total wall-clock against the 45-minute bound",
]


def _post(base: str, path: str, payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        base + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def _get_text(base: str, path: str) -> tuple[int, str]:
    with urllib.request.urlopen(base + path) as response:
        return response.status, response.read().decode("utf-8")


def _post_raw(base: str, path: str, payload: dict) -> tuple[int, bytes, str]:
    request = urllib.request.Request(
        base + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
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
        return error.code, error.read(), ""


def _layers_for(matrix: list[list[str]]) -> list[dict]:
    """The deterministic stratum split the editor uses for adoption."""
    size = len(matrix)
    strata = {
        name: [["." for _ in range(size)] for _ in range(size)]
        for name in ("body", "organs", "decoration", "effects")
    }
    for y in range(size):
        for x in range(size):
            token = matrix[y][x]
            if token == ".":
                continue
            home = (
                "body"
                if token in ("B", "A")
                else "organs" if token in ("E", "M") else "decoration"
            )
            strata[home][y][x] = token
    return [
        {"name": name, "matrix": strata[name], "visible": True}
        for name in ("body", "organs", "decoration", "effects")
    ]


def run_first_session_protocol() -> dict:
    import tempfile

    steps: list[dict] = []
    started = time.perf_counter()

    def step(name: str, purpose: str, run) -> dict:
        begin = time.perf_counter()
        ok, requests, evidence = run()
        record = {
            "name": name,
            "purpose": purpose,
            "ok": ok,
            "requests": requests,
            "elapsed_seconds": round(time.perf_counter() - begin, 4),
            "evidence": evidence,
        }
        steps.append(record)
        return record

    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        server = start_workshop_server(
            port=0,
            grids_dir=base_dir / "grids",
            slips_dir=base_dir / "slips",
            released_dir=base_dir / "released",
        )
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            def open_workshop():
                status_editor, editor = _get_text(base, "/")
                status_slip, slip_page = _get_text(base, "/slip")
                ok = (
                    status_editor == 200
                    and status_slip == 200
                    and "animation" in editor
                    and "deliberation" in slip_page
                )
                return ok, 2, {
                    "editor_serves_the_timeline": "animation" in editor,
                    "slip_creator_serves_deliberation": "deliberation" in slip_page,
                }

            step(
                "open_the_workshop",
                "both authoring pages exist and carry the Phase-H depth",
                open_workshop,
            )

            def first_refusal():
                status, verdict = _post(
                    base,
                    "/api/validate",
                    {"matrix": BROKEN_FIRST_DRAFT, "palette_id": "lcd_green"},
                )
                errors = verdict.get("errors", [])
                ok = status == 200 and not verdict.get("valid") and errors
                return bool(ok), 1, {"errors": errors}

            step(
                "first_marks_and_first_refusal",
                "the validator's words are the teaching moment",
                first_refusal,
            )

            def author_creature():
                status, verdict = _post(
                    base,
                    "/api/validate",
                    {"matrix": FIRST_CREATURE, "palette_id": "lcd_green"},
                )
                ok = status == 200 and verdict.get("valid")
                return bool(ok), 1, {"valid": bool(verdict.get("valid"))}

            step(
                "author_the_creature",
                "the finished 16x16 creature passes the engine",
                author_creature,
            )

            def author_slip():
                status, verdict = _post(
                    base, "/api/slip/validate", {"profile": FIRST_SPECIES}
                )
                if status != 200 or not verdict.get("valid"):
                    return False, 1, {"errors": verdict.get("errors", [])}
                status, saved = _post(
                    base, "/api/slip/save", {"profile": FIRST_SPECIES}
                )
                ok = status == 200 and saved.get("ok")
                return bool(ok), 2, {
                    "authority_valid": True,
                    "saved_as": saved.get("file"),
                    "deliberation": FIRST_SPECIES["deliberation"],
                }

            step(
                "author_the_species_slip",
                "the species contract (deliberation included) accepted "
                "by the authority and saved",
                author_slip,
            )

            def save_creature():
                status, saved = _post(
                    base,
                    "/api/save",
                    {
                        "name": "first_moth",
                        "matrix": FIRST_CREATURE,
                        "palette_id": "lcd_green",
                        "layers": _layers_for(FIRST_CREATURE),
                    },
                )
                ok = status == 200 and saved.get("ok")
                return bool(ok), 1, {"file": saved.get("file")}

            step(
                "save_the_creature",
                "the layered save (H2's sidecar rides beside the grid)",
                save_creature,
            )

            def see_it_move():
                status, scrub = _post(
                    base,
                    "/api/preview/clip",
                    {
                        "matrix": FIRST_CREATURE,
                        "palette_id": "lcd_green",
                        "clip": "ill",
                    },
                )
                frames = scrub.get("frames", [])
                first = frames[0]["cells"] if frames else None
                moved = any(
                    frame["cells"] != first for frame in frames[1:]
                )
                ok = status == 200 and scrub.get("ok") and moved
                return bool(ok), 1, {
                    "frame_count": scrub.get("frame_count"),
                    "moved": bool(moved),
                }

            step(
                "see_it_move",
                "the timeline scrubs the engine's clip frames (H3)",
                see_it_move,
            )

            def release():
                status, released = _post(
                    base, "/api/release", {"name": "first_moth"}
                )
                ok = status == 200 and released.get("ok")
                return bool(ok), 1, {"file": released.get("file")}

            step(
                "release_into_the_ecosystem",
                "release-time re-validation + the lineage mark",
                release,
            )

            def share():
                status, png, content_type = _post_raw(
                    base,
                    "/api/export/apng",
                    {
                        "matrix": FIRST_CREATURE,
                        "palette_id": "lcd_green",
                        "profile_id": "slip_first_session",
                        "name": "first_moth",
                        "clip": "ill",
                    },
                )
                index = png.find(b"acTL")
                frame_count = (
                    int.from_bytes(png[index + 4 : index + 8], "big")
                    if index >= 0
                    else 0
                )
                ok = (
                    status == 200
                    and content_type == "image/png"
                    and frame_count == 4
                )
                return bool(ok), 1, {"apng_clip_frames": frame_count}

            step(
                "share_it",
                "the animated share carries the scrubbed clip (H3)",
                share,
            )
        finally:
            server.shutdown()

    total = round(time.perf_counter() - started, 4)
    all_ok = all(record["ok"] for record in steps)
    interaction_count = sum(record["requests"] for record in steps)
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete" if all_ok else "blocked",
        "date": "2026-07-19",
        "purpose": (
            "H5: prove the documented first-session journey (blank state "
            "-> creature + SLIP -> release -> share) exists end to end "
            "against the REAL workshop server, timed against the "
            "45-minute bound as a labeled scripted proxy"
        ),
        "source_artifacts": [
            "workshop/server/workshop_server.py",
            "workshop/grid_editor/grid_editor.html",
            "workshop/slip_creator/slip_creator.html",
            "research/experiment_reports/2026-07-12-semantic-layers.md",
            "research/experiment_reports/2026-07-19-onion-skin-timeline.md",
            "research/experiment_reports/2026-07-19-behavior-editor.md",
        ],
        "steps": steps,
        "metrics": {
            "scripted_proxy": True,
            "total_elapsed_seconds": total,
            "bound_seconds": FIRST_SESSION_BOUND_SECONDS,
            "under_bound": total < FIRST_SESSION_BOUND_SECONDS,
            "interaction_count": interaction_count,
            "step_count": len(steps),
        },
        "human_pass": {
            "prepared": True,
            "blocking": False,
            "steps": HUMAN_PASS_STEPS,
            "note": (
                "the scripted proxy proves the PATH and counts the "
                "interactions; only a human pass measures the 45-minute "
                "goal for real — prepared here, recorded not blocking "
                "(the calibration pattern)"
            ),
        },
        "closed_states": [
            "first_session_path_exists_end_to_end",
            "scripted_proxy_under_bound",
        ],
        "blocked_states": [
            "manual_human_first_session_timing (prepared, not blocking "
            "- the calibration pattern)"
        ],
        "decision": (
            "the first-session journey is real at every step against the "
            "live server; the scripted time is a proxy and says so"
        ),
        "next_research_step": (
            "H6: the Phase-H gate consolidates the authoring-depth "
            "ladder and hands the community system to DR 0035's "
            "post-alpha scope"
        ),
    }


def write_first_session_artifacts(output_dir: str | Path, report: dict) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / "first_session_stage0.json"
    artifact.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the scripted first-session protocol (H5)."
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "data" / "workshop"),
        help="where first_session_stage0.json is written",
    )
    args = parser.parse_args()
    report = run_first_session_protocol()
    write_first_session_artifacts(args.output_dir, report)
    print(
        json.dumps(
            {
                "artifact_id": report["artifact_id"],
                "status": report["status"],
                "metrics": report["metrics"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
