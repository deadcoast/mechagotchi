import os
import subprocess
import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Limit ambient colors; GitHub can still force bold/dim ANSI styling.
# Semantic help assertions therefore decode ANSI (DR 0061).
os.environ.pop("FORCE_COLOR", None)
os.environ["NO_COLOR"] = "1"

try:
    import typer  # noqa: F401
    from typer.testing import CliRunner
    from rich.text import Text

    _CLI_DEPS = True
except ModuleNotFoundError:
    _CLI_DEPS = False


@unittest.skipUnless(_CLI_DEPS, "typer/rich not installed (uv sync --group cli)")
class MechasCliSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from mechas_cli.app import app

        cls.app = app
        cls.runner = CliRunner()

    def test_root_help_lists_the_commands(self):
        result = self.runner.invoke(self.app, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("rate", result.output)
        self.assertIn("status", result.output)
        self.assertIn("game", result.output)
        self.assertIn("mechas", result.output)

    def test_game_help_lists_the_modes(self):
        result = self.runner.invoke(self.app, ["game", "--help"])
        self.assertEqual(0, result.exit_code)
        plain = Text.from_ansi(result.output).plain
        self.assertIn("--play", plain)
        self.assertIn("--build", plain)
        self.assertIn("--evidence", plain)

    def test_game_without_a_mode_guides(self):
        result = self.runner.invoke(self.app, ["game"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("--play", result.output)

    def test_version_flag(self):
        from mechas_cli import __version__

        result = self.runner.invoke(self.app, ["--version"])
        self.assertEqual(0, result.exit_code)
        self.assertIn(__version__, result.output)

    def test_rate_without_flags_shows_the_targets(self):
        result = self.runner.invoke(self.app, ["rate"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("--creatures", result.output)

    def test_rate_help_documents_the_flags(self):
        result = self.runner.invoke(self.app, ["rate", "--help"])
        self.assertEqual(0, result.exit_code)
        for flag in (
            "--creatures",
            "--autoexport",
            "--status",
            "--ingest",
            "--reviewer",
        ):
            self.assertIn(flag, Text.from_ansi(result.output).plain)

    def test_rate_status_reports_progress(self):
        result = self.runner.invoke(self.app, ["rate", "--status"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("63", result.output)

    def test_workshop_without_flags_shows_the_targets(self):
        result = self.runner.invoke(self.app, ["workshop"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("--editor", result.output)

    def test_workshop_help_documents_the_flags(self):
        result = self.runner.invoke(self.app, ["workshop", "--help"])
        self.assertEqual(0, result.exit_code)
        for flag in ("--editor", "--slip", "--preview", "--inspect", "--release", "--port", "--no-browser"):
            self.assertIn(flag, Text.from_ansi(result.output).plain)

    def test_workshop_targets_include_the_slip_creator(self):
        result = self.runner.invoke(self.app, ["workshop"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("--slip", result.output)
        self.assertIn("--preview", result.output)
        self.assertIn("--release", result.output)

    def test_session_without_flags_shows_the_targets(self):
        result = self.runner.invoke(self.app, ["session"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("--open", result.output)
        self.assertIn("--era", result.output)
        self.assertIn("--status", result.output)

    def test_session_help_documents_the_flags(self):
        result = self.runner.invoke(self.app, ["session", "--help"])
        self.assertEqual(0, result.exit_code)
        for flag in ("--open", "--era", "--status", "--new", "--port"):
            self.assertIn(flag, Text.from_ansi(result.output).plain)

    def test_help_assertions_survive_plain_and_github_terminals(self):
        methods = ['test_game_help_lists_the_modes', 'test_rate_help_documents_the_flags',
                   'test_session_help_documents_the_flags', 'test_workshop_help_documents_the_flags']
        for term in ('dumb', 'xterm-256color'):
            with self.subTest(term=term):
                env = dict(os.environ, TERM=term, GITHUB_ACTIONS='true', NO_COLOR='1')
                env.pop('_TYPER_FORCE_DISABLE_TERMINAL', None)
                result = subprocess.run(
                    [sys.executable, '-B', str(Path(__file__).resolve()),
                     *['MechasCliSurfaceTests.' + method for method in methods]],
                    env=env, capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_root_help_lists_session(self):
        result = self.runner.invoke(self.app, ["--help"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("session", result.output)

    def test_status_shows_workspace_overview(self):
        result = self.runner.invoke(self.app, ["status"])
        self.assertEqual(0, result.exit_code)

    def test_workspace_scripts_use_the_workspace_interpreter(self):
        # The installed CLI runs in uv's isolated tool environment, which
        # lacks the lab dependencies; gate/builder subprocesses must use
        # the workspace venv when it exists (audit finding, 2026-07-05).
        from mechas_cli.workflows.rate import _workspace_python
        from mechas_cli.workspace import find_workspace_root

        root = find_workspace_root()
        interpreter = Path(_workspace_python(root))
        if (root / ".venv").exists():
            self.assertIn(".venv", str(interpreter))
        self.assertTrue(interpreter.exists())


class WorkspaceResolutionTests(unittest.TestCase):
    def test_finds_repo_root_from_source_anchor(self):
        from mechas_cli.workspace import find_workspace_root

        root = find_workspace_root()
        self.assertTrue((root / "data" / "readability").exists())
        self.assertTrue((root / "labs").exists())


if __name__ == "__main__":
    unittest.main()
