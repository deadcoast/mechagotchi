import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools/mechas_cli/src'))
from typer.testing import CliRunner
from mechas_cli.app import app


class GameLaunchOptionsTests(unittest.TestCase):
    def test_authored_covenant_and_separate_save_directory_reach_the_client(self):
        slip = ROOT/'data/slips/valid/slip_v2_cleanliness.json'
        directory = ROOT/'keeper/a separate example'
        with patch('mechas_cli.workflows.game.subprocess.run', return_value=SimpleNamespace(returncode=0)) as launch:
            result = CliRunner().invoke(app, ['game', '--play', '--new', '--slip', str(slip), '--keeper-dir', str(directory), '--ticks', '2'])
        self.assertEqual(0, result.exit_code, result.output)
        arguments = launch.call_args.args[0]
        self.assertEqual(str(slip.resolve()), arguments[arguments.index('--slip')+1])
        self.assertEqual(str(directory.resolve()), arguments[arguments.index('--keeper-dir')+1])
        self.assertIn('--new', arguments)

    def test_conflicting_modes_and_misplaced_player_options_do_not_launch(self):
        for args in (['--play', '--build'], ['--play', '--evidence'], ['--build', '--keeper-dir', 'keeper/example'], ['--play', '--ticks', '0']):
            with self.subTest(args=args), patch('mechas_cli.workflows.game.subprocess.run') as launch:
                result = CliRunner().invoke(app, ['game', *args])
                self.assertEqual(2, result.exit_code)
                launch.assert_not_called()

    def test_experimental_learning_policy_reaches_the_client(self):
        with patch('mechas_cli.workflows.game.subprocess.run', return_value=SimpleNamespace(returncode=0)) as launch:
            result = CliRunner().invoke(app, ['game', '--play', '--learning-policy', 'qtable'])
        self.assertEqual(0, result.exit_code, result.output)
        args=launch.call_args.args[0]
        self.assertEqual('qtable',args[args.index('--learning-policy')+1])

    def test_invalid_or_misplaced_policy_does_not_launch(self):
        for args in (['--play','--learning-policy','unknown'],['--learning-policy','qtable']):
            with self.subTest(args=args), patch('mechas_cli.workflows.game.subprocess.run') as launch:
                result=CliRunner().invoke(app,['game',*args])
                self.assertEqual(2,result.exit_code)
                launch.assert_not_called()
