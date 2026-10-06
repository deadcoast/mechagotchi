"""Selected Keeper startup is explicit and never guessed by the CLI."""
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from typer.testing import CliRunner
from mechas_cli.app import app
from mechas_cli.workflows.workshop import launch_workshop_server


class WorkshopContextTests(unittest.TestCase):
    def test_help_names_selected_context_and_pack_creator(self):
        result = CliRunner().invoke(app, ["workshop", "--help"], color=False)
        from rich.text import Text
        text = Text.from_ansi(result.output).plain
        self.assertEqual(0, result.exit_code)
        self.assertIn("--keeper-dir", text)
        self.assertIn("--packs", text)

    def test_browser_open_failure_keeps_supervision_and_closes_owned_process(self):
        process = MagicMock()
        process.poll.side_effect = [None, 0, 0]
        with patch("mechas_cli.workflows.workshop.find_workspace_root", return_value=Path.cwd()), \
                patch("mechas_cli.workflows.workshop.launch_workshop_server", return_value=(process, "http://127.0.0.1:2345/")), \
                patch("mechas_cli.workflows.workshop.webbrowser.open", side_effect=OSError("browser unavailable")), \
                patch("mechas_cli.workflows.workshop.time.sleep"):
            result = CliRunner().invoke(app, ["workshop", "--editor"])
        self.assertEqual(0, result.exit_code, result.exception)
        process.wait.assert_called_once_with(timeout=5)
        self.assertIn("browser", result.output.lower())

    def test_interrupted_startup_closes_owned_server_before_return(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "workshop/server/workshop_server.py"
            script.parent.mkdir(parents=True)
            script.write_text("# fixture", encoding="utf-8")
            process = MagicMock()
            process.stdout.readline.side_effect = KeyboardInterrupt()
            process.poll.return_value = None
            with patch("mechas_cli.workflows.workshop.subprocess.Popen", return_value=process), \
                    patch("mechas_cli.workflows.workshop._workspace_python", return_value="existing-python"):
                with self.assertRaises(KeyboardInterrupt):
                    launch_workshop_server(MagicMock(), root, 0, "")
            process.terminate.assert_called_once()
            process.wait.assert_called_once_with(timeout=5)

    def test_server_command_passes_exact_resolved_keeper_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "workshop/server/workshop_server.py"
            script.parent.mkdir(parents=True)
            script.write_text("# fixture", encoding="utf-8")
            keeper = root / "save with spaces"
            process = MagicMock()
            process.stdout = io.StringIO("Workshop http://127.0.0.1:2345/\n")
            process.poll.return_value = None
            with patch("mechas_cli.workflows.workshop.subprocess.Popen", return_value=process) as popen, \
                    patch("mechas_cli.workflows.workshop._workspace_python", return_value="existing-python"), \
                    patch("mechas_cli.workflows.workshop.urllib.request.urlopen"):
                result, url = launch_workshop_server(MagicMock(), root, 0, "packs", keeper_dir=keeper)
            command = popen.call_args.args[0]
            self.assertEqual(str(keeper.resolve()), command[command.index("--keeper-dir") + 1])
            self.assertEqual("http://127.0.0.1:2345/packs", url)
            self.assertIs(process, result)


if __name__ == "__main__":
    unittest.main()
