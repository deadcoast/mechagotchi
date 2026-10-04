"""S1 actual source/CLI/native recovery and saved-policy continuity observations."""
import argparse
import hashlib
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
from mecha_game.session import CompanionSession, load_session_inputs


def fixture(policy):
    grid, slip, model = load_session_inputs(
        ROOT / "data/seed_grids_16x16/mg_seed16_001_beetle.json",
        ROOT / "data/slips/valid/slip_v2_cleanliness.json")
    session = CompanionSession(grid, slip, model=model, learning_policy=policy)
    for _ in range(24):
        state = session.state
        care = ("feed" if state["hunger"] > .55 else "sleep" if state["energy"] < .35
                else "clean" if state["cleanliness"] < .6 else None)
        session.advance(care)
    return session


def inventory(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


def render_recovery(directory, screenshots):
    """Capture the actual app, including its recovery notice and paged policy."""
    import pygame
    from mecha_game.app import run
    screenshots.mkdir(parents=True, exist_ok=True)
    captured = []
    for policy in ("incumbent", "qtable"):
        keeper = directory / ("render-" + policy)
        path = keeper / "companion.json"
        session = fixture(policy)
        session.save(path)
        session.save(path)
        path.write_text('{"broken": true}', encoding="utf-8")
        frames = 0
        def events():
            nonlocal frames
            frames += 1
            if frames == 1:
                return []
            if frames < 7:
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEDOWN)]
            return [pygame.event.Event(pygame.QUIT)]
        def capture():
            target = screenshots / f"{policy}-page-{frames:02d}.png"
            pygame.image.save(pygame.display.get_surface(), str(target))
            captured.append(str(target.relative_to(ROOT)))
        with patch.dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy"), \
             patch("pygame.event.get", side_effect=events), \
             patch("pygame.display.flip", side_effect=capture):
            assert run(["--keeper-dir", str(keeper), "--recover-backup", "--tick-frames", "1000", "--fps", "0"]) == 0
    return captured


def verify(bundle, screenshots):
    executable = bundle / ("Mechagotchi.exe" if os.name == "nt" else "Mechagotchi")
    if not executable.is_file():
        raise FileNotFoundError(executable)
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=os.pathsep.join(str(ROOT / p) for p in
                   ("tools/mechas_cli/src", "game/src", "packages/mecha_engine/src")))
    fast = ["--tick-frames", "1", "--fps", "0", "--scale", "2"]
    paths = (("source", [sys.executable, "-B", str(ROOT / "game/run_game.py"), *fast]),
             ("cli", [sys.executable, "-B", "-m", "mechas_cli.app", "game", "--play"]),
             ("native", [str(executable), *fast]))
    runs, checks = [], {}
    with tempfile.TemporaryDirectory(prefix="mechagotchi-safe-resume-") as temporary:
        root = Path(temporary)
        def launch(label, base, keeper, *args, expected=0):
            command = [*base, "--keeper-dir", str(keeper), "--ticks", "1", *args]
            result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=120,
                                    **({"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}))
            runs.append(dict(label=label, returncode=result.returncode, expected=expected,
                             command=command, stdout=result.stdout, stderr=result.stderr))
            if result.returncode != expected or "Traceback" in result.stderr:
                raise AssertionError(runs[-1])
            return result
        for entry, base in paths:
            for policy in ("incumbent", "qtable"):
                label = entry + "_" + policy
                keeper = root / label
                path = keeper / "companion.json"
                backup = path.with_suffix(".bak.json")
                session = fixture(policy)
                session.save(path)
                session.save(path)
                original = backup.read_bytes()
                broken = json.loads(path.read_text(encoding="utf-8"))
                broken["generation_model"]["width"] = 8
                path.write_text(json.dumps(broken), encoding="utf-8")
                damaged = path.read_bytes()
                before = inventory(keeper)
                result = launch(label + "_corrupt", base, keeper, expected=2)
                checks[label + "_corrupt_refusal_preserves_bytes"] = before == inventory(keeper) and "--recover-backup" in result.stderr
                other = "qtable" if policy == "incumbent" else "incumbent"
                launch(label + "_policy_conflict", base, keeper, "--recover-backup", "--learning-policy", other, expected=2)
                checks[label + "_policy_conflict_preserves_bytes"] = before == inventory(keeper)
                launch(label + "_new_conflict", base, keeper, "--recover-backup", "--new", expected=2)
                checks[label + "_new_conflict_preserves_bytes"] = before == inventory(keeper)
                session.advance()
                result = launch(label + "_recover", base, keeper, "--recover-backup")
                saved = CompanionSession.load(path)
                archives = list(keeper.glob("companion.before-recovery-*.json"))
                checks[label + "_restores_exact_state_and_preserves_both_files"] = (
                    saved.state == session.state and saved.learning_policy == policy
                    and backup.read_bytes() == original and len(archives) == 1
                    and archives[0].read_bytes() == damaged and "Recovered prior save" in result.stdout)
                session.advance()
                launch(label + "_resume", base, keeper)
                checks[label + "_continues_deterministically"] = CompanionSession.load(path).state == session.state
                path.unlink()  # only this harness's explicitly created temporary fixture
                before = inventory(keeper)
                launch(label + "_missing_primary", base, keeper, expected=2)
                checks[label + "_missing_primary_never_starts_new_life"] = before == inventory(keeper) and not path.exists()
                launch(label + "_recover_missing", base, keeper, "--recover-backup")
                checks[label + "_backup_only_recovery"] = CompanionSession.load(path).state == session.state
                backup.write_text("broken backup", encoding="utf-8")
                before = inventory(keeper)
                launch(label + "_bad_backup", base, keeper, "--recover-backup", expected=2)
                checks[label + "_bad_backup_preserves_bytes"] = before == inventory(keeper)
        images = render_recovery(root, screenshots)
    return dict(artifact_id="safe_resume_release_stage0", date="2026-10-04", status="observed_native_windows_and_source",
                purpose="Validate explicit saved-companion recovery and policy continuity through actual launchers.",
                source_artifacts=["game/src/mecha_game/session.py", "game/src/mecha_game/app.py", "labs/game_loop/verify_safe_resume_release.py"],
                metrics=dict(checks=checks, runs=runs, screenshots=images,
                             native_executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest()),
                closed_states=[name for name, passed in checks.items() if passed],
                blocked_states=["Remote Windows/Ubuntu CI and signing unverified; Q-table default adoption remains refused."],
                decision=dict(verdict="verified" if all(checks.values()) else "withhold"),
                next_research_step="Complete S1 full local gate and preserve restart evidence.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--screenshots", type=Path, default=ROOT / ".development/s1-ui")
    args = parser.parse_args()
    report = verify(args.bundle.resolve(), args.screenshots.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(checks=report["metrics"]["checks"], launches=len(report["metrics"]["runs"])), indent=2))
    raise SystemExit(0 if report["decision"]["verdict"] == "verified" else 1)
