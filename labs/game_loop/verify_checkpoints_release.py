"""S2 observed process failures and interactive save retry/discard, with isolated pets."""
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
from mecha_game.session import CompanionSession, load_session_inputs


def fixture(policy):
    grid, slip, model = load_session_inputs(ROOT / "data/seed_grids_16x16/mg_seed16_001_beetle.json",
                                           ROOT / "data/slips/valid/slip_v2_cleanliness.json")
    return CompanionSession(grid, slip, model=model, learning_policy=policy)


def inventory(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


def interactive(root, screenshots):
    import pygame
    from mecha_game.app import run
    screenshots.mkdir(parents=True, exist_ok=True)
    observations = []
    for policy in ("incumbent", "qtable"):
        for choice in ("retry", "discard"):
            label = policy + "_" + choice
            keeper = root / label
            path = keeper / "companion.json"
            fixture(policy).save_checkpoint(path)
            before = path.read_bytes()
            blocked = path.with_suffix(".bak.json")
            blocked.mkdir()  # only this isolated fixture: deterministic OS replacement failure
            frames, images = 0, []
            def events():
                nonlocal frames
                frames += 1
                if frames > 6:
                    raise AssertionError("save flow did not finish")
                if frames == 1:
                    return []
                if frames == 2:
                    return [pygame.event.Event(pygame.QUIT)]
                if frames == 3:
                    return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f)]
                if frames == 4:
                    return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEDOWN)]
                if choice == "retry":
                    blocked.rmdir()  # our empty fixture directory only
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s if choice == "retry" else pygame.K_q,
                                           mod=pygame.KMOD_CTRL)]
            def capture():
                if frames in (3, 4):
                    target = screenshots / f"{label}-{frames:02d}.png"
                    pygame.image.save(pygame.display.get_surface(), str(target))
                    images.append(str(target.relative_to(ROOT)))
            with patch.dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy"), \
                 patch("pygame.event.get", side_effect=events), patch("pygame.display.flip", side_effect=capture), \
                 contextlib.redirect_stderr(io.StringIO()) as errors:
                code = run(["--keeper-dir", str(keeper), "--fps", "0", "--tick-frames", "1"])
            loaded = CompanionSession.load(path)
            ok = (frames == 5 and loaded.learning_policy == policy and
                  ((choice == "retry" and code == 0 and loaded.state["age_ticks"] == 1) or
                   (choice == "discard" and code == 1 and path.read_bytes() == before)))
            observations.append(dict(label=label, passed=ok, returncode=code, frames=frames,
                                     saved_age=loaded.state["age_ticks"], screenshots=images, stderr=errors.getvalue()))
    return observations


def verify(bundle, screenshots):
    executable = bundle / ("Mechagotchi.exe" if os.name == "nt" else "Mechagotchi")
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=os.pathsep.join(str(ROOT / p) for p in
                   ("tools/mechas_cli/src", "game/src", "packages/mecha_engine/src")))
    fast = ["--tick-frames", "1", "--fps", "0", "--scale", "2"]
    entries = (("source", [sys.executable, "-B", str(ROOT / "game/run_game.py"), *fast]),
               ("cli", [sys.executable, "-B", "-m", "mechas_cli.app", "game", "--play"]),
               ("native", [str(executable), *fast]))
    checks, runs = {}, []
    with tempfile.TemporaryDirectory(prefix="mechagotchi-checkpoints-") as directory:
        root = Path(directory)
        def launch(label, base, keeper, *args, expected=0):
            command = [*base, "--keeper-dir", str(keeper), "--ticks", "1", *args]
            result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", timeout=120,
                                    **({"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}))
            runs.append(dict(label=label, command=command, returncode=result.returncode, expected=expected,
                             stdout=result.stdout, stderr=result.stderr))
            if result.returncode != expected or "Traceback" in result.stderr:
                raise AssertionError(runs[-1])
            return result
        for entry, base in entries:
            for policy in ("incumbent", "qtable"):
                label = entry + "_" + policy
                keeper = root / label
                path, lineage = keeper / "companion.json", keeper / "lineage.json"
                launch(label + "_new", base, keeper, "--new", "--learning-policy", policy)
                loaded = CompanionSession.load(path)
                checks[label + "_new_checkpoint"] = loaded.state["age_ticks"] == 1 and loaded.learning_policy == policy
                original = path.read_bytes()
                damaged = json.loads(original)
                damaged["generation_model"]["width"] = 8
                path.write_text(json.dumps(damaged), encoding="utf-8")
                before = inventory(keeper)
                launch(label + "_invalid_model", base, keeper, expected=2)
                checks[label + "_invalid_model_still_refused_before_writes"] = before == inventory(keeper)
                path.write_bytes(original)  # exact private fixture snapshot; never an owner save
                before = inventory(keeper)
                launch(label + "_policy_conflict", base, keeper, "--learning-policy",
                       "qtable" if policy == "incumbent" else "incumbent", expected=2)
                checks[label + "_policy_conflict_still_preserves_bytes"] = before == inventory(keeper)
                lineage.unlink()
                lineage.mkdir()
                result = launch(label + "_blocked_export", base, keeper)
                checks[label + "_blocked_export_keeps_progress"] = (CompanionSession.load(path).state["age_ticks"] == 2
                    and "Companion saved. Lineage export unavailable" in result.stderr)
                lineage.rmdir()
                launch(label + "_repair_export", base, keeper)
                saved = CompanionSession.load(path)
                checks[label + "_export_repaired_on_resume"] = (saved.state["age_ticks"] == 3
                    and saved.lineage == json.loads(lineage.read_text(encoding="utf-8"))["records"])
                future = fixture(policy)
                while future.alive:
                    future.advance()
                future.succeed()
                future.save_lineage(lineage)
                future_export = lineage.read_bytes()
                primary = path.read_bytes()
                backup = path.with_suffix(".bak.json")
                backup.unlink()
                backup.mkdir()
                launch(label + "_blocked_primary", base, keeper, expected=1)
                checks[label + "_blocked_primary_reconciles_without_losing_old_pet"] = (
                    primary == path.read_bytes() and saved.lineage == json.loads(lineage.read_text(encoding="utf-8"))["records"]
                    and future_export == lineage.with_suffix(".bak.json").read_bytes())
                backup.rmdir()
                launch(label + "_primary_retry", base, keeper)
                older = path.read_bytes()
                newer = CompanionSession.load(path)
                while newer.alive:
                    newer.advance()
                newer.succeed()
                newer.save_checkpoint(path)
                newer_bytes, newer_export = path.read_bytes(), lineage.read_bytes()
                checks[label + "_retry_advances_exactly_once"] = json.loads(older)["state"]["age_ticks"] == 4
                launch(label + "_recover_earlier_checkpoint", base, keeper, "--recover-backup")
                recovered = CompanionSession.load(path)
                expected = CompanionSession._from_payload(json.loads(older))
                expected.advance()
                archives = list(keeper.glob("companion.before-recovery-*.json"))
                checks[label + "_recovery_keeps_policy_state_and_lineage_coherent"] = (
                    recovered.state == expected.state and recovered.learning_policy == policy
                    and recovered.lineage == json.loads(lineage.read_text(encoding="utf-8"))["records"]
                    and len(archives) == 1 and archives[0].read_bytes() == newer_bytes
                    and lineage.with_suffix(".bak.json").read_bytes() == newer_export)
        ui = interactive(root, screenshots)
    return dict(artifact_id="safe_checkpoints_release_stage0", date="2026-10-04", status="observed_native_windows_and_source",
                purpose="Preserve play progress through actual save failures and keep derived lineage consistent on resume.",
                source_artifacts=["game/src/mecha_game/session.py", "game/src/mecha_game/app.py", "labs/game_loop/verify_checkpoints_release.py"],
                metrics=dict(checks=checks, runs=runs, interactive=ui,
                             native_executable_sha256=hashlib.sha256(executable.read_bytes()).hexdigest()),
                closed_states=[name for name, ok in checks.items() if ok],
                blocked_states=["Published-SHA Windows/Ubuntu CI and signing unverified; lineage remains a derived export, not a second save authority."],
                decision=dict(verdict="verified" if all(checks.values()) and all(row["passed"] for row in ui) else "withhold"),
                next_research_step="Run the S2 full local gate against final source before closing the slice.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--screenshots", type=Path, default=ROOT / ".development/s2-ui")
    args = parser.parse_args()
    report = verify(args.bundle.resolve(), args.screenshots.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(checks=report["metrics"]["checks"], launches=len(report["metrics"]["runs"]),
                         interactive=[{k:v for k,v in row.items() if k != "stderr"} for row in report["metrics"]["interactive"]]), indent=2))
    raise SystemExit(0 if report["decision"]["verdict"] == "verified" else 1)
