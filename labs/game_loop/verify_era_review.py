"""T1 observed native-era creation/restart and source pygame report interactions."""
import argparse
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for relative in ("game/src", "packages/mecha_engine/src"):
    sys.path.insert(0, str(ROOT / relative))
import pygame
from mecha_game.app import run
from mecha_game.era_review import EraReview
from mecha_game.footer import FooterPager
from mecha_game.session import CompanionSession


def inventory(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


def key(value):
    return pygame.event.Event(pygame.KEYDOWN, key=value, mod=0)


def interact(keeper, label, events, screenshots, *, scale=2):
    """Only supply input events and observe rendered output; run real app logic."""
    frames, pages, images = 0, [], []
    busy_pages = []
    painting_busy = False
    original_layout = FooterPager.layout
    def poll():
        nonlocal frames
        frames += 1
        if frames > len(events) + 1:
            raise AssertionError("interactive flow failed to quit")
        return events[frames - 1] if frames <= len(events) else [pygame.event.Event(pygame.QUIT)]
    def layout(pager, lines, measure, width, rows):
        nonlocal painting_busy
        page = original_layout(pager, lines, measure, width, rows)
        record = dict(frame=frames, page=page.page, page_count=page.page_count,
                      all_lines=list(lines), visible=list(page.lines), width=width,
                      fits=all(measure(line) <= width for line in page.lines))
        painting_busy = bool(lines and lines[0].startswith('ERA RUNNING'))
        if painting_busy:
            busy_pages.append(record)
        else:
            pages.append(record)
        return page
    def capture():
        suffix = f"-busy-{len(busy_pages):03d}" if painting_busy else ""
        target = screenshots / f"{label}-{frames:02d}{suffix}.png"
        pygame.image.save(pygame.display.get_surface(), str(target))
        images.append(target.relative_to(ROOT).as_posix())
    with patch.dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy"), \
         patch("pygame.event.get", side_effect=poll), patch.object(FooterPager, "layout", layout), \
         patch("pygame.display.flip", side_effect=capture), contextlib.redirect_stderr(io.StringIO()) as errors:
        code = run(["--keeper-dir", str(keeper), "--era-scale", "tiny", "--scale", str(scale),
                    "--tick-frames", "1", "--fps", "0"])
    return dict(label=label, frames=frames, returncode=code, screenshots=images, pages=pages, busy_pages=busy_pages, rendered_frames=len(images), stderr=errors.getvalue())


def verify(bundle, screenshots):
    executable = bundle / ("Mechagotchi.exe" if os.name == "nt" else "Mechagotchi")
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", PYTHONDONTWRITEBYTECODE="1")
    screenshots.mkdir(parents=True, exist_ok=True)
    checks, launches, flows = {}, [], []
    with tempfile.TemporaryDirectory(prefix="mechagotchi-era-review-") as directory:
        root = Path(directory)
        keeper = root / "native-history"
        def launch(label, *extra):
            command = [str(executable), "--keeper-dir", str(keeper), "--ticks", "1", "--tick-frames", "1",
                       "--fps", "0", "--era-scale", "tiny", *extra]
            result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=120,
                                    **({"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}))
            launches.append(dict(label=label, command=command, returncode=result.returncode,
                                 stdout=result.stdout, stderr=result.stderr))
            if result.returncode or "Traceback" in result.stderr:
                raise AssertionError(launches[-1])
        launch("native_new_two_eras", "--new", "--eras", "2")
        first = EraReview.load(keeper)
        checks["native_two_recorded_eras"] = len(first.history["eras"]) == 2
        checks["native_default_remains_incumbent"] = CompanionSession.load(keeper / "companion.json").learning_policy == "incumbent"
        ledger_before = (keeper / "campaign.sqlite3").read_bytes()
        launch("native_resume_without_era")
        checks["native_resume_preserves_campaign_ledger"] = ledger_before == (keeper / "campaign.sqlite3").read_bytes()
        launch("native_next_era", "--eras", "1")
        native = EraReview.load(keeper)
        checks["native_resume_appends_era_without_replacing_history"] = (len(native.history["eras"]) == 3 and
                native.history["eras"][:2] == first.history["eras"] and
                len({era["rng_seed"] for era in native.history["eras"]}) == 3)
        before = inventory(keeper)
        flow = interact(keeper, "saved-history", [[key(pygame.K_t)], [key(pygame.K_PAGEDOWN)],
            [key(pygame.K_PAGEDOWN)], [key(pygame.K_LEFTBRACKET)], [key(pygame.K_LEFTBRACKET)],
            [key(pygame.K_PAGEDOWN)], [key(pygame.K_RIGHTBRACKET)], [key(pygame.K_RIGHTBRACKET)],
            [key(pygame.K_F1)], [key(pygame.K_ESCAPE)], [key(pygame.K_f), key(pygame.K_s), key(pygame.K_g)],
            [pygame.event.Event(pygame.QUIT)]], screenshots)
        flows.append(flow)
        pages = flow["pages"]
        checks["review_and_quit_preserve_all_native_keeper_bytes"] = inventory(keeper) == before
        checks["era_navigation_and_help_return"] = (pages[0]["all_lines"][0].startswith("ERA 2 ") and
                pages[3]["all_lines"][0].startswith("ERA 1 ") and pages[4]["all_lines"][0].startswith("ERA 0 ") and
                pages[7]["all_lines"][0].startswith("ERA 2 ") and pages[8]["all_lines"][0].startswith("HELP") and
                pages[9]["all_lines"][0].startswith("ERA 2 "))
        native.index = 0
        checks["earned_facts_visible_with_stored_values_and_thresholds"] = bool(native.earned()) and all(
            f"{fact['metric_value']} met threshold {fact['threshold']}" in " ".join(pages[5]["visible"])
            for fact in native.earned())
        checks["paging_reaches_weather_record"] = any("WEATHER RECORD" in " ".join(p["visible"]) for p in pages[:3])
        age = CompanionSession.load(keeper / "companion.json").state["age_ticks"]
        flow = interact(keeper, "return-to-care", [[key(pygame.K_t)], [key(pygame.K_f)],
            [key(pygame.K_t)], [pygame.event.Event(pygame.QUIT)]], screenshots, scale=10)
        flows.append(flow)
        checks["close_review_advances_one_care_tick_without_queued_input"] = CompanionSession.load(keeper / "companion.json").state["age_ticks"] == age + 1
        flow = interact(keeper, "review-to-covenant", [[key(pygame.K_t)], [key(pygame.K_c)],
            [key(pygame.K_c)], [pygame.event.Event(pygame.QUIT)]], screenshots)
        flows.append(flow)
        checks["review_opens_current_covenant"] = "COVENANT" in " ".join(flow["pages"][1]["all_lines"])
        age = CompanionSession.load(keeper / "companion.json").state["age_ticks"]
        flow = interact(keeper, "next-era", [[key(pygame.K_3), key(pygame.K_t)], [key(pygame.K_e)],
            [pygame.event.Event(pygame.QUIT)]], screenshots)
        flows.append(flow)
        after = EraReview.load(keeper)
        checks["interactive_next_era_opens_new_report_without_care_tick"] = (len(after.history["eras"]) == 4 and
            flow["pages"][1]["all_lines"][0].startswith("ERA 3 [storm]") and
            CompanionSession.load(keeper / "companion.json").state["age_ticks"] == age)
        # Empty/corrupt campaign views use a real saved pet but no valid campaign.
        empty = root / "empty-history"
        CompanionSession.load(keeper / "companion.json").save_checkpoint(empty / "companion.json")
        before = inventory(empty)
        flow = interact(empty, "empty-history", [[key(pygame.K_t)], [pygame.event.Event(pygame.QUIT)]], screenshots)
        flows.append(flow)
        checks["empty_view_names_first_era_without_creating_campaign"] = (before == inventory(empty) and
            "E run the first era" in " ".join(flow["pages"][0]["all_lines"]))
        (empty / "campaign_state.json").write_text("broken", encoding="utf-8")
        before = inventory(empty)
        flow = interact(empty, "unavailable-history", [[key(pygame.K_t)], [key(pygame.K_e)],
            [pygame.event.Event(pygame.QUIT)]], screenshots)
        flows.append(flow)
        checks["unavailable_view_preserves_corrupt_source"] = (before == inventory(empty) and
            flow["pages"][0]["all_lines"][0] == "ERA REVIEW unavailable")
        records = []
        for index in range(len(after.history["eras"])):
            after.index = index
            records.append(dict(era_index=after.current["era_index"], rng_seed=after.current["rng_seed"],
                summary=after.current["report"]["summary"], earned=after.earned(), lines=after.lines()))
    checks["all_real_flows_exit_cleanly_and_fit"] = all(flow["returncode"] == 0 and all(page["fits"] for page in flow["pages"]) for flow in flows)
    return dict(artifact_id="era_review_release_stage0", date="2026-10-04", status="observed_native_and_source",
        purpose="Make recorded outcomes and earned progression readable after restart without changing engine state.",
        source_artifacts=["game/src/mecha_game/era_review.py", "game/src/mecha_game/app.py", "labs/game_loop/verify_era_review.py"],
        metrics=dict(checks=checks, launches=launches, interactive=flows, recorded_eras=records,
                     native_executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest()),
        closed_states=[name for name, ok in checks.items() if ok],
        blocked_states=["Native keyboard interactions were not automated; source pygame inputs used native-created records.",
                        "Historical replays and archive bodies remain outside this report-only scope.",
                        "Full local closing gate and exact-published-SHA Windows/Ubuntu CI are separate gates."],
        decision=dict(verdict="verified" if all(checks.values()) else "withhold"),
        next_research_step="Complete the full local gate and preserve all earlier scientific observations before closure.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--screenshots", type=Path, default=ROOT / ".development/t1-ui")
    args = parser.parse_args()
    report = verify(args.bundle.resolve(), args.screenshots.resolve())
    report["artifact_id"] = args.output.stem
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(checks=report["metrics"]["checks"], launches=len(report["metrics"]["launches"]),
                         flows=len(report["metrics"]["interactive"])), indent=2))
    raise SystemExit(0 if report["decision"]["verdict"] == "verified" else 1)
