import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


CUBFF_REPO_URL = "https://github.com/paradigms-of-intelligence/cubff"
CUBFF_PAPER_URL = "https://arxiv.org/abs/2406.19108"
PROGRAM_SIZE = 64
CHECKPOINT_FIELDS = ["reset_index", "num_programs", "epoch", "soup_bytes"]
SNAPSHOT_EXTENSIONS = {".dat", ".json", ".jsonl"}
DATA_ARTIFACT_EXTENSIONS = {".dat", ".bin", ".json", ".jsonl", ".npy", ".npz", ".ppm"}
METRICS_LOG_HEADER = "epoch,brotli_size,soup_size,higher_entropy"


def ingest_snapshot_file(
    path: Path,
    *,
    source_repo: str,
    source_commit: str,
    language: str,
    seed: int | None = None,
) -> list[dict]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".dat":
        return [
            _parse_binary_checkpoint(
                path,
                source_repo=source_repo,
                source_commit=source_commit,
                language=language,
                seed=seed,
            )
        ]
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        records = payload if isinstance(payload, list) else [payload]
        return [
            _normalize_python_state(
                record,
                path=path,
                index=index,
                source_repo=source_repo,
                source_commit=source_commit,
                language=language,
                seed=seed,
            )
            for index, record in enumerate(records)
            if isinstance(record, dict)
        ]
    if suffix == ".jsonl":
        snapshots = []
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            record = json.loads(line)
            if isinstance(record, dict):
                snapshots.append(
                    _normalize_python_state(
                        record,
                        path=path,
                        index=index,
                        source_repo=source_repo,
                        source_commit=source_commit,
                        language=language,
                        seed=seed,
                    )
                )
        return snapshots
    return []


def build_ingest_report(
    *,
    input_dir: Path,
    source_repo: str,
    source_commit: str,
    language: str,
    seed: int | None = None,
    upstream_root: Path | None = None,
) -> dict:
    input_dir = Path(input_dir)
    snapshots = []
    rejected_files = []
    non_snapshot_files = []

    files = sorted(path for path in input_dir.rglob("*") if path.is_file()) if input_dir.exists() else []
    for path in files:
        if path.suffix.lower() not in SNAPSHOT_EXTENSIONS:
            non_snapshot_files.append(_relative_path(path, input_dir))
            continue
        try:
            ingested = ingest_snapshot_file(
                path,
                source_repo=source_repo,
                source_commit=source_commit,
                language=language,
                seed=seed,
            )
            if ingested:
                snapshots.extend(ingested)
            else:
                non_snapshot_files.append(_relative_path(path, input_dir))
        except (OSError, ValueError, json.JSONDecodeError, struct.error) as exc:
            rejected_files.append(
                {
                    "path": _relative_path(path, input_dir),
                    "reason": str(exc),
                }
            )

    status = "ingested_real_cubff_snapshots" if snapshots else "awaiting_real_cubff_snapshots"
    report = {
        "lab_id": "cubff_real_snapshot_ingest_stage0",
        "source_mode": "real_cubff_snapshot_ingest",
        "source_repo": source_repo,
        "source_commit": source_commit,
        "language": language,
        "seed": seed,
        "input_dir": str(input_dir.as_posix()),
        "status": status,
        "ingested_snapshot_count": len(snapshots),
        "rejected_file_count": len(rejected_files),
        "non_snapshot_file_count": len(non_snapshot_files),
        "snapshot_ids": [snapshot["snapshot_id"] for snapshot in snapshots],
        "ingested_snapshots": snapshots,
        "feature_summary": _feature_summary(snapshots),
        "rejected_files": rejected_files,
        "non_snapshot_files": non_snapshot_files,
        "checkpoint_format": _checkpoint_format(),
        "decision": _decision(len(snapshots)),
        "source_anchors": [
            CUBFF_REPO_URL,
            CUBFF_PAPER_URL,
            f"{CUBFF_REPO_URL}/blob/main/common_language.h",
            f"{CUBFF_REPO_URL}/blob/main/cubff_py.cc",
        ],
    }
    if upstream_root is not None:
        report["upstream_audit"] = audit_upstream_tree(upstream_root)
    return report


def audit_upstream_tree(root: Path) -> dict:
    root = Path(root)
    files = sorted(path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts)
    snapshot_artifacts = []
    run_logs = []
    trace_tools = []

    for path in files:
        relative = _relative_path(path, root)
        suffix = path.suffix.lower()
        if suffix == ".txt" and _looks_like_metrics_log(path):
            run_logs.append(relative)
            continue
        if suffix in DATA_ARTIFACT_EXTENSIONS and _looks_like_snapshot_artifact(relative):
            snapshot_artifacts.append(relative)
            continue
        if relative in {
            "cubff_example.py",
            "cubff_walk_back.py",
            "python/save_bff_trace.py",
            "python/analyse_soup.py",
        }:
            trace_tools.append(relative)

    return {
        "audited_file_count": len(files),
        "snapshot_artifacts": snapshot_artifacts,
        "snapshot_artifact_count": len(snapshot_artifacts),
        "run_logs": run_logs,
        "run_log_count": len(run_logs),
        "trace_tools": trace_tools,
        "checkpoint_format": _checkpoint_format(),
        "finding": (
            "No committed soup/checkpoint snapshot artifacts were found in the "
            "audited upstream tree; metrics logs are useful provenance but are "
            "not sufficient for semantic transducer ingestion."
        ),
    }


def write_report_outputs(output_dir: Path, report: dict) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "real_snapshot_ingest_stage0_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def _parse_binary_checkpoint(
    path: Path,
    *,
    source_repo: str,
    source_commit: str,
    language: str,
    seed: int | None,
) -> dict:
    data = path.read_bytes()
    if len(data) < 24:
        raise ValueError("CuBFF checkpoint is too short for three 64-bit header fields")
    reset_index, num_programs, epoch = struct.unpack("<QQQ", data[:24])
    soup = data[24:]
    expected = num_programs * PROGRAM_SIZE
    if len(soup) != expected:
        raise ValueError(
            f"CuBFF checkpoint soup length mismatch: expected {expected}, got {len(soup)}"
        )
    return _snapshot_record(
        snapshot_id=path.stem,
        source_type="real_cubff_checkpoint",
        capture_method="official_cubff_binary_checkpoint",
        source_path=path,
        source_repo=source_repo,
        source_commit=source_commit,
        language=language,
        seed=seed,
        epoch=int(epoch),
        soup=list(soup),
        brotli_size=None,
        replication_scores=[],
        extra_metadata={"reset_index": int(reset_index)},
    )


def _normalize_python_state(
    record: dict,
    *,
    path: Path,
    index: int,
    source_repo: str,
    source_commit: str,
    language: str,
    seed: int | None,
) -> dict:
    soup = _coerce_byte_list(record.get("soup", record.get("soup_bytes")))
    snapshot_id = str(record.get("snapshot_id") or (path.stem if index == 0 else f"{path.stem}_{index:03d}"))
    return _snapshot_record(
        snapshot_id=snapshot_id,
        source_type="real_cubff_python_state",
        capture_method="cubff_python_callback_state",
        source_path=path,
        source_repo=source_repo,
        source_commit=source_commit,
        language=str(record.get("language") or language),
        seed=seed,
        epoch=_int_or_zero(record.get("epoch")),
        soup=soup,
        brotli_size=record.get("brotli_size"),
        replication_scores=_coerce_number_list(record.get("replication_per_prog", [])),
        extra_metadata={
            "brotli_bpb": record.get("brotli_bpb"),
            "higher_entropy": record.get("higher_entropy"),
            "bytes_per_prog": record.get("bytes_per_prog"),
        },
    )


def _snapshot_record(
    *,
    snapshot_id: str,
    source_type: str,
    capture_method: str,
    source_path: Path,
    source_repo: str,
    source_commit: str,
    language: str,
    seed: int | None,
    epoch: int,
    soup: list[int],
    brotli_size: Any,
    replication_scores: list[int | float],
    extra_metadata: dict,
) -> dict:
    if len(soup) < PROGRAM_SIZE or len(soup) % PROGRAM_SIZE != 0:
        raise ValueError("CuBFF soup must contain one or more 64-byte programs")
    program_count = len(soup) // PROGRAM_SIZE
    tape = soup[:PROGRAM_SIZE]
    record = {
        "snapshot_id": snapshot_id,
        "source_type": source_type,
        "epoch": epoch,
        "language": language,
        "program_size": PROGRAM_SIZE,
        "num_programs": program_count,
        "soup_size": len(soup),
        "soup_sha256": hashlib.sha256(bytes(soup)).hexdigest(),
        "tape": tape,
        "replication_scores": replication_scores,
        "lineage_events": [],
        "provenance": {
            "source_repo": source_repo,
            "source_commit": source_commit,
            "source_path": source_path.as_posix(),
            "capture_method": capture_method,
            "seed": seed,
        },
        "metadata": extra_metadata,
    }
    if _is_number(brotli_size):
        record["brotli_size"] = int(brotli_size)
    return record


def _feature_summary(snapshots: list[dict]) -> dict:
    if not snapshots:
        return {
            "mean_tape_length": 0,
            "mean_program_count": 0,
            "mean_replication_score_count": 0,
        }
    return {
        "mean_tape_length": _mean(len(snapshot["tape"]) for snapshot in snapshots),
        "mean_program_count": _mean(snapshot["num_programs"] for snapshot in snapshots),
        "mean_replication_score_count": _mean(
            len(snapshot.get("replication_scores", [])) for snapshot in snapshots
        ),
    }


def _checkpoint_format() -> dict:
    return {
        "source": "CuBFF common_language.h checkpoint writer",
        "endianness_assumption": "little_endian_64_bit_size_t",
        "program_size_bytes": PROGRAM_SIZE,
        "fields": CHECKPOINT_FIELDS,
        "notes": (
            "The official writer stores three size_t fields followed by "
            "num_programs * 64 raw soup bytes. Replication scores are not "
            "stored in checkpoints and require Python callback/state export."
        ),
    }


def _decision(snapshot_count: int) -> dict:
    if snapshot_count:
        return {
            "status": "ready_for_real_transducer_comparison",
            "adoption": "still_no_core_dependency_decision",
            "reason": (
                "Real-format CuBFF snapshots were ingested. The next step is "
                "to run the semantic transducer comparison against these records."
            ),
        }
    return {
        "status": "blocked_real_snapshot_absent",
        "adoption": "do_not_revisit_cubff_adoption",
        "reason": (
            "The upstream audit found run logs and checkpoint-writing code, but "
            "no committed soup/checkpoint snapshots. Metrics logs alone cannot "
            "prove semantic transducer value."
        ),
    }


def _coerce_byte_list(value: Any) -> list[int]:
    if isinstance(value, str):
        compact = "".join(value.split())
        if len(compact) % 2 != 0:
            raise ValueError("hex soup strings must have an even number of characters")
        return list(bytes.fromhex(compact))
    if not isinstance(value, list):
        raise ValueError("CuBFF state JSON must contain a soup list or hex string")
    soup = []
    for item in value:
        if not isinstance(item, int) or isinstance(item, bool):
            raise ValueError("CuBFF soup values must be integers")
        soup.append(item % 256)
    return soup


def _coerce_number_list(value: Any) -> list[int | float]:
    if not isinstance(value, list):
        return []
    return [item for item in value if _is_number(item)]


def _looks_like_metrics_log(path: Path) -> bool:
    try:
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, UnicodeDecodeError, IndexError):
        return False
    return first_line.startswith(METRICS_LOG_HEADER)


def _looks_like_snapshot_artifact(relative_path: str) -> bool:
    lower = relative_path.lower()
    return any(
        marker in lower
        for marker in ("snapshot", "checkpoint", "state", "soup", "frame")
    )


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _int_or_zero(value: Any) -> int:
    return int(value) if isinstance(value, int) and not isinstance(value, bool) else 0


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _mean(values) -> float:
    items = list(values)
    return round(sum(items) / len(items), 6) if items else 0


def _readme_text(report: dict) -> str:
    return (
        "# CuBFF Real Snapshot Ingest Stage 0\n\n"
        "This directory records the real CuBFF snapshot-ingestion gate for the "
        "semantic transducer research track.\n\n"
        "Key results:\n\n"
        f"- Status: {report['status']}\n"
        f"- Ingested snapshots: {report['ingested_snapshot_count']}\n"
        f"- Non-snapshot files ignored: {report['non_snapshot_file_count']}\n"
        f"- Decision: {report['decision']['status']}\n\n"
        "Metrics logs are not treated as snapshots. CuBFF adoption remains "
        "blocked until real soup/checkpoint or Python state exports are ingested "
        "and compared against the existing semantic transducer baseline.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/cubff_real_ingest/source_snapshots"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/cubff_real_ingest"))
    parser.add_argument("--source-repo", default=CUBFF_REPO_URL)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--language", default="bff_noheads")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--upstream-root", type=Path, default=None)
    args = parser.parse_args()

    report = build_ingest_report(
        input_dir=args.input_dir,
        source_repo=args.source_repo,
        source_commit=args.source_commit,
        language=args.language,
        seed=args.seed,
        upstream_root=args.upstream_root,
    )
    write_report_outputs(args.output_dir, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
