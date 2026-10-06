"""The executable example preserves user outputs and delegates actual app actions."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'game/src'))

class PublicExampleTests(unittest.TestCase):
    def test_existing_output_is_refused_before_process_creation(self):
        from mecha_game.examples import run_example
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'keep').write_bytes(b'exact owner bytes')
            with patch('subprocess.run') as launch:
                with self.assertRaisesRegex(ValueError,'exist'):
                    run_example(['Mechagotchi.exe'],root)
            launch.assert_not_called()
            self.assertEqual(b'exact owner bytes',(root/'keep').read_bytes())

    def test_weather_and_command_are_validated_before_output_creation(self):
        from mecha_game.examples import run_example
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'output'
            with self.assertRaises(ValueError): run_example([],root)
            with self.assertRaises(ValueError): run_example(['app'],root,weather='invented')
            self.assertFalse(root.exists())

if __name__=='__main__': unittest.main()
