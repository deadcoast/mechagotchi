"""DR 0061: a fixed byte-stream oracle independent of native Path sorting."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'packages/mecha_engine/src'))
from mecha_engine.provenance import hash_included_path as package_hash
from provenance_ledger import hash_included_path as lab_hash


class ProvenancePortabilityTests(unittest.TestCase):
    def test_mixed_case_and_nested_names_follow_one_explicit_byte_stream(self):
        # This literal order is part of the oracle, not computed using Path.
        entries = [('B.txt', b'upper\n'), ('a.txt', b'lower\n'),
                   ('a/child.bin', b'\x00\xff\r\n'), ('z.txt', b'last')]
        stream = b''.join(name.encode() + b'\0' + hashlib.sha256(body).hexdigest().encode()
                          + b'\0' for name, body in entries)
        expected = {'hash_algorithm': 'sha256-tree', 'hash': hashlib.sha256(stream).hexdigest()}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, body in reversed(entries):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
            self.assertEqual(expected, lab_hash(root))
            self.assertEqual(expected, package_hash(root))
            (root / 'B.txt').write_bytes(b'upper\r\n')
            self.assertNotEqual(expected, lab_hash(root))
            self.assertEqual(lab_hash(root), package_hash(root))


if __name__ == '__main__':
    unittest.main()
