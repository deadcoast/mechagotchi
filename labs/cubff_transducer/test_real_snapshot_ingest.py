import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from real_snapshot_ingest import (  # noqa: E402
    CUBFF_REPO_URL,
    audit_upstream_tree,
    build_ingest_report,
    ingest_snapshot_file,
)


def checkpoint_bytes(num_programs: int = 4, epoch: int = 17) -> bytes:
    header = struct.pack("<QQQ", 1, num_programs, epoch)
    soup = bytes(index % 256 for index in range(num_programs * 64))
    return header + soup


class RealCuBffSnapshotIngestTests(unittest.TestCase):
    def test_ingests_official_binary_checkpoint_shape(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            checkpoint = Path(temp_dir) / "0000000016.dat"
            checkpoint.write_bytes(checkpoint_bytes())

            result = ingest_snapshot_file(
                checkpoint,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        snapshots = result["snapshots"]
        self.assertEqual(1, len(snapshots))
        self.assertEqual([], result["rejected_records"])
        snapshot = snapshots[0]
        self.assertEqual("real_cubff_checkpoint", snapshot["source_type"])
        self.assertEqual("0000000016", snapshot["snapshot_id"])
        self.assertEqual(17, snapshot["epoch"])
        self.assertEqual(4, snapshot["num_programs"])
        self.assertEqual(64, snapshot["program_size"])
        self.assertEqual(list(range(64)), snapshot["tape"])
        self.assertEqual(256, snapshot["soup_size"])
        self.assertEqual(CUBFF_REPO_URL, snapshot["provenance"]["source_repo"])
        self.assertEqual(
            "official_cubff_binary_checkpoint",
            snapshot["provenance"]["capture_method"],
        )

    def test_ingests_python_state_json_with_provenance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "epoch": 65,
                        "language": "bff",
                        "soup": [7] * 64 + [11] * 64,
                        "brotli_size": 88,
                        "replication_per_prog": [0, 48],
                    }
                ),
                encoding="utf-8",
            )

            result = ingest_snapshot_file(
                state_path,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff",
                seed=3,
            )

        snapshots = result["snapshots"]
        self.assertEqual(1, len(snapshots))
        self.assertEqual([], result["rejected_records"])
        snapshot = snapshots[0]
        self.assertEqual("real_cubff_python_state", snapshot["source_type"])
        self.assertEqual("state", snapshot["snapshot_id"])
        self.assertEqual(65, snapshot["epoch"])
        self.assertEqual(2, snapshot["num_programs"])
        self.assertEqual([7] * 64, snapshot["tape"])
        self.assertEqual([0, 48], snapshot["replication_scores"])
        self.assertEqual(88, snapshot["brotli_size"])

    def test_metrics_logs_are_not_promoted_to_snapshots(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            (input_dir / "bff_noheads.txt").write_text(
                "epoch,brotli_size,soup_size,higher_entropy\n"
                "1,8388776,131072,-0.000190\n",
                encoding="utf-8",
            )

            report = build_ingest_report(
                input_dir=input_dir,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        self.assertEqual(0, report["ingested_snapshot_count"])
        self.assertEqual(1, report["non_snapshot_file_count"])
        self.assertEqual(
            "awaiting_real_cubff_snapshots",
            report["status"],
        )
        self.assertEqual(
            "blocked_real_snapshot_absent",
            report["decision"]["status"],
        )

    def test_mixed_jsonl_file_keeps_valid_records_and_isolates_bad_ones(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            (input_dir / "states.jsonl").write_text(
                json.dumps({"epoch": 1, "soup": [7] * 64}) + "\n"
                + "this is not json\n"
                + json.dumps({"epoch": 2, "soup": [1] * 63}) + "\n"
                + json.dumps({"epoch": 3, "soup": [9] * 64}) + "\n",
                encoding="utf-8",
            )

            report = build_ingest_report(
                input_dir=input_dir,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        self.assertEqual(2, report["ingested_snapshot_count"])
        self.assertEqual([1, 3], [s["epoch"] for s in report["ingested_snapshots"]])
        self.assertEqual(0, report["rejected_file_count"])
        self.assertEqual([], report["rejected_files"])
        self.assertEqual(2, report["rejected_record_count"])
        rejected_by_line = {r["line_number"]: r for r in report["rejected_records"]}
        self.assertEqual("JSONDecodeError", rejected_by_line[2]["error_family"])
        self.assertEqual("ValueError", rejected_by_line[3]["error_family"])
        self.assertEqual("states.jsonl", rejected_by_line[3]["path"])
        self.assertEqual("ingested_real_cubff_snapshots", report["status"])

    def test_mixed_json_list_keeps_valid_records_and_isolates_bad_one(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            (input_dir / "states.json").write_text(
                json.dumps(
                    [
                        {"epoch": 1, "soup": [7] * 64},
                        {"epoch": 2, "soup": [1] * 63},
                        {"epoch": 3, "soup": [9] * 64},
                    ]
                ),
                encoding="utf-8",
            )

            report = build_ingest_report(
                input_dir=input_dir,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        self.assertEqual(2, report["ingested_snapshot_count"])
        self.assertEqual(0, report["rejected_file_count"])
        self.assertEqual(1, report["rejected_record_count"])
        rejected = report["rejected_records"][0]
        self.assertEqual("states.json", rejected["path"])
        self.assertEqual(1, rejected["record_index"])
        self.assertEqual("ValueError", rejected["error_family"])

    def test_file_with_zero_valid_records_is_rejected_at_file_level(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            (input_dir / "states.json").write_text(
                json.dumps([{"epoch": 1, "soup": [1] * 63}]),
                encoding="utf-8",
            )

            report = build_ingest_report(
                input_dir=input_dir,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        self.assertEqual(0, report["ingested_snapshot_count"])
        self.assertEqual(1, report["rejected_file_count"])
        self.assertEqual("zero_valid_records", report["rejected_files"][0]["reason"])
        self.assertEqual(1, report["rejected_record_count"])
        self.assertEqual("awaiting_real_cubff_snapshots", report["status"])

    def test_audit_upstream_tree_reports_logs_without_snapshot_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "testdata").mkdir()
            (root / "python").mkdir()
            (root / "common_language.h").write_text(
                "fwrite(&reset_index, sizeof(reset_index), 1, f);\n"
                "fwrite(&num_programs, sizeof(num_programs), 1, f);\n"
                "fwrite(&epoch_to_save, sizeof(epoch), 1, f);\n"
                "fwrite(state.soup.data(), 1, state.soup.size(), f);\n",
                encoding="utf-8",
            )
            (root / "python" / "save_bff_trace.py").write_text(
                "evaluate_and_save(bytearray(program_bytes), output_path, 131072, True)\n",
                encoding="utf-8",
            )
            (root / "testdata" / "bff_noheads.txt").write_text(
                "epoch,brotli_size,soup_size,higher_entropy\n",
                encoding="utf-8",
            )

            audit = audit_upstream_tree(root)

        self.assertEqual(0, audit["snapshot_artifact_count"])
        self.assertEqual(["testdata/bff_noheads.txt"], audit["run_logs"])
        self.assertEqual(
            ["reset_index", "num_programs", "epoch", "soup_bytes"],
            audit["checkpoint_format"]["fields"],
        )


if __name__ == "__main__":
    unittest.main()
