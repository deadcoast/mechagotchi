# mechas CLI — Status Audit

Date: 2026-07-05 (v0.1.0, same-day follow-up to the initial release).
Every command and failure path below was executed against the real
workspace through the installed `mechas` command. Findings were fixed
during the audit and each fix carries a regression test; nothing here is
assumed.

## Verdict

**Working and safe to hand to reviewers.** The full rating loop
(`mechas rate --creatures --autoexport`) is verified end-to-end including
a live browser pass. The audit surfaced five defects — all fixed, all
regression-tested, 14/14 CLI tests green (25/25 repeat runs on the
previously flaky suite).

## Test matrix (executed, not assumed)

| Surface | Result |
| --- | --- |
| `mechas --version` / `--help` / `rate --help` | pass — themed, commands and flags documented |
| `mechas status` | pass — engine modules + calibration state with next command |
| `mechas rate` (bare) | pass — lists targets with copyable examples, exit 0 (never an error) |
| `mechas rate --status` | pass — 0/63 rows, reviewers, next-steps panel |
| `mechas rate --ingest <missing>` | pass — friendly error, exit 1 |
| `mechas rate --ingest <wrong header>` | pass — explains the expected header, writes nothing, exit 1 |
| `mechas rate --ingest <valid>` | pass — saves with backup, runs the gate, themed summary (test rows deleted after) |
| `mechas rate --creatures --no-browser --port 0` | pass — serves on a free port; GET tool 200; POST bad CSV 400 |
| `--autoexport` full loop (live browser, earlier session) | pass — finished pass auto-saved 21 rows, CLI narrated, fabricated rows deleted |
| Missing tool HTML | pass — auto-regenerates via the builder lab; output byte-identical to the committed artifact |
| Busy port | pass (after fix A5) — "Port 8423 is busy. Try --port 0" |
| Run from outside the repo (`C:\`) | pass — workspace found via the editable-install anchor |
| Legacy console (cp1252) | pass (fixed pre-audit) — degraded glyphs, never a crash |

## Findings (all fixed this audit)

- **A1 — wrong interpreter for workspace scripts (critical).** The
  installed CLI runs in uv's isolated tool environment; gate/builder
  subprocesses used `sys.executable` and crashed on missing lab
  dependencies (pydantic). Fix: `_workspace_python()` prefers the
  workspace `.venv`; regression test pins it.
- **A2 — `uv sync --group cli` silently removed the lab group.** uv
  syncs the venv to exactly the named groups. Provisioning guidance is
  now `uv sync --group lab --group cli` (TOOLS.md, tools README).
- **A3 — gate summary parsed guessed keys.** `_run_gate` read
  `ratings_collected` (nonexistent). Now reads the verified keys
  (`valid_rating_row_count`, `reviewer_count`, `row_error_count`,
  `manual_readability_calibration_ready`) and surfaces row errors.
- **A4 — URLs truncated in status tables.** A clipped rating-page URL is
  a dead end; value columns now fold across lines.
- **A5 — busy port hung instead of erroring (Windows).** `SO_REUSEADDR`
  let a second server bind an in-use port silently. The server now binds
  exclusively (`SO_EXCLUSIVEADDRUSE`), the conflict raises, and the CLI
  explains `--port 0`; regression test pins the raise.

Fixed before the audit, same release: cp1252 console crash (lossy UTF-8
reconfigure), Rich markup rendered literally in tables/panels, and an
export-callback race (callback now completes before the HTTP response;
verified over 25 clean runs).

## Known gaps (accepted, tracked in the reference's roadmap)

- Ingesting a header-only CSV reports "Saved 0 rows" without a warning
  tone — harmless but could be more explicit.
- A failing gate prints its raw traceback (styled, exit 1) — functional,
  not yet catered.
- No `--reviewer` prefill, no shell completion, no `mechas gates` /
  `doctor` yet (roadmap, `mechas-cli.md`).

## Sources

- `docs/cli/mechas-cli.md`
- `docs/cli/mechas-cli-design.md`
- `tools/mechas_cli/src/mechas_cli/workflows/rate.py`
- `tools/mechas_cli/src/mechas_cli/ratings_server.py`
- `tools/mechas_cli/src/mechas_cli/theme.py`
- `tools/mechas_cli/tests/test_ratings_server.py`
- `tools/mechas_cli/tests/test_cli_surface.py`
- `TOOLS.md`
