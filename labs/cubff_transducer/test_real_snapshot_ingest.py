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
    TAKEOVER_COMPRESSION_RATIO,
    audit_upstream_tree,
    build_ingest_report,
    ingest_snapshot_file,
    load_metrics_log,
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


class PhaseLabelingTests(unittest.TestCase):
    """Cycle 19 I1: phase labels come from the run's OWN metrics log,

    joined on the checkpoint header epoch (the filename+1 observation:
    file 0000002048.dat carries header epoch 2049, and the metrics row
    for that state is epoch 2049). Nothing is recomputed or fabricated:
    a snapshot with no measured brotli evidence stays "unmeasured".
    """

    def test_load_metrics_log_parses_rows_and_skips_malformed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "metrics.csv"
            log_path.write_text(
                "epoch,brotli_size,soup_size,higher_entropy\n"
                "2049,482593,8192,0.105027\n"
                "not,a,valid,row,at,all\n"
                "4097,1503234,131072,5.332264\n",
                encoding="utf-8",
            )

            rows = load_metrics_log(log_path)

        self.assertEqual({2049, 4097}, set(rows))
        self.assertEqual(482593, rows[2049]["brotli_size"])
        self.assertEqual(5.332264, rows[4097]["higher_entropy"])

    def test_checkpoint_joins_sibling_metrics_and_labels_early_phase(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            # Filename epoch 2048, header epoch 2049 — the +1 observation.
            (input_dir / "0000002048.dat").write_bytes(
                checkpoint_bytes(num_programs=4, epoch=2049)
            )
            (input_dir / "metrics.csv").write_text(
                "epoch,brotli_size,soup_size,higher_entropy\n"
                "2049,230,4,0.105027\n",
                encoding="utf-8",
            )

            report = build_ingest_report(
                input_dir=input_dir,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        snapshot = report["ingested_snapshots"][0]
        # 230 compressed bytes over 4 * 64 = 256 raw soup bytes.
        self.assertEqual("early_phase", snapshot["phase"])
        self.assertAlmostEqual(230 / 256, snapshot["compression_ratio"], places=6)
        self.assertEqual(230, snapshot["metrics"]["brotli_size"])
        self.assertEqual(2049, snapshot["metrics"]["metrics_epoch"])

    def test_checkpoint_labels_post_takeover_below_ratio_threshold(self):
        self.assertEqual(0.5, TAKEOVER_COMPRESSION_RATIO)
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            (input_dir / "0000002048.dat").write_bytes(
                checkpoint_bytes(num_programs=4, epoch=2049)
            )
            (input_dir / "metrics.csv").write_text(
                "epoch,brotli_size,soup_size,higher_entropy\n"
                "2049,100,4,5.332264\n",
                encoding="utf-8",
            )

            report = build_ingest_report(
                input_dir=input_dir,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        snapshot = report["ingested_snapshots"][0]
        self.assertEqual("post_takeover", snapshot["phase"])
        self.assertAlmostEqual(100 / 256, snapshot["compression_ratio"], places=6)

    def test_checkpoint_without_metrics_row_is_unmeasured(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            (input_dir / "0000002048.dat").write_bytes(
                checkpoint_bytes(num_programs=4, epoch=2049)
            )
            (input_dir / "metrics.csv").write_text(
                "epoch,brotli_size,soup_size,higher_entropy\n"
                "1,255,4,-0.000301\n",
                encoding="utf-8",
            )

            report = build_ingest_report(
                input_dir=input_dir,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        snapshot = report["ingested_snapshots"][0]
        self.assertEqual("unmeasured", snapshot["phase"])
        self.assertNotIn("compression_ratio", snapshot)
        self.assertNotIn("metrics", snapshot)

    def test_python_state_in_record_brotli_labels_phase(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "state.json"
            state_path.write_text(
                json.dumps(
                    [
                        {"epoch": 65, "soup": [7] * 128, "brotli_size": 20},
                        {"epoch": 66, "soup": [7] * 128, "brotli_size": 88},
                    ]
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

        early, late = sorted(result["snapshots"], key=lambda s: s["epoch"])
        self.assertEqual("post_takeover", early["phase"])  # 20 / 128
        self.assertEqual("early_phase", late["phase"])  # 88 / 128
        self.assertAlmostEqual(20 / 128, early["compression_ratio"], places=6)

    def test_run_json_is_provenance_not_a_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            (input_dir / "0000002048.dat").write_bytes(
                checkpoint_bytes(num_programs=4, epoch=2049)
            )
            (input_dir / "run.json").write_text(
                json.dumps(
                    {
                        "seed": 0,
                        "num_programs": 131072,
                        "command": "./bin/main --lang bff_noheads --seed 0",
                    }
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

        self.assertEqual(1, report["ingested_snapshot_count"])
        self.assertEqual([], report["rejected_files"])
        snapshot = report["ingested_snapshots"][0]
        self.assertEqual(
            "./bin/main --lang bff_noheads --seed 0",
            snapshot["provenance"]["run_parameters"]["command"],
        )

    def test_run_id_disambiguates_snapshot_ids_across_runs(self):
        # Two runs both save 0000002048.dat; a corpus of runs must not
        # collide ids — the run manifest's run_id prefixes the stem.
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            for run_id in ("run_a", "run_b"):
                run_dir = input_dir / run_id
                run_dir.mkdir()
                (run_dir / "0000002048.dat").write_bytes(
                    checkpoint_bytes(num_programs=4, epoch=2049)
                )
                (run_dir / "run.json").write_text(
                    json.dumps({"run_id": run_id, "seed": 0}),
                    encoding="utf-8",
                )

            report = build_ingest_report(
                input_dir=input_dir,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        self.assertEqual(
            ["run_a/0000002048", "run_b/0000002048"],
            sorted(report["snapshot_ids"]),
        )

    def test_report_phase_summary_and_corpus_truth(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            run_a = input_dir / "run_a"
            run_b = input_dir / "run_b"
            run_a.mkdir()
            run_b.mkdir()
            (run_a / "0000002048.dat").write_bytes(
                checkpoint_bytes(num_programs=4, epoch=2049)
            )
            (run_a / "metrics.csv").write_text(
                "epoch,brotli_size,soup_size,higher_entropy\n"
                "2049,230,4,0.105027\n",
                encoding="utf-8",
            )
            (run_b / "0000004096.dat").write_bytes(
                checkpoint_bytes(num_programs=4, epoch=4097)
            )
            (run_b / "metrics.csv").write_text(
                "epoch,brotli_size,soup_size,higher_entropy\n"
                "4097,46,4,5.332264\n",
                encoding="utf-8",
            )

            report = build_ingest_report(
                input_dir=input_dir,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        self.assertEqual(
            {"early_phase": 1, "post_takeover": 1, "unmeasured": 0},
            report["phase_summary"],
        )
        self.assertEqual("early_and_post_takeover", report["corpus_truth"])

    def test_corpus_truth_names_single_phase_honestly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir)
            (input_dir / "0000002048.dat").write_bytes(
                checkpoint_bytes(num_programs=4, epoch=2049)
            )
            (input_dir / "metrics.csv").write_text(
                "epoch,brotli_size,soup_size,higher_entropy\n"
                "2049,230,4,0.105027\n",
                encoding="utf-8",
            )

            report = build_ingest_report(
                input_dir=input_dir,
                source_repo=CUBFF_REPO_URL,
                source_commit="f212e849027c98fcf4b242eccfb5fed435223e23",
                language="bff_noheads",
                seed=0,
            )

        self.assertEqual(
            {"early_phase": 1, "post_takeover": 0, "unmeasured": 0},
            report["phase_summary"],
        )
        self.assertEqual("early_phase_only", report["corpus_truth"])


if __name__ == "__main__":
    unittest.main()
