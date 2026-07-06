import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import typer  # noqa: F401
    from typer.testing import CliRunner

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
        self.assertIn("mechas", result.output)

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
            self.assertIn(flag, result.output)

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
        for flag in ("--editor", "--slip", "--preview", "--release", "--port", "--no-browser"):
            self.assertIn(flag, result.output)

    def test_workshop_targets_include_the_slip_creator(self):
        result = self.runner.invoke(self.app, ["workshop"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("--slip", result.output)
        self.assertIn("--preview", result.output)
        self.assertIn("--release", result.output)

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
