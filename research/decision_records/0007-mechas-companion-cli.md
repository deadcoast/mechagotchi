# Decision Record 0007: The mechas Companion CLI

Date: 2026-07-05

## Status

Accepted. Creates the `tools/` surface, the `mechas` command, and the
root `cli` dependency group (Typer, Rich).

## Context

The manual readability calibration exposed a workflow failure class: the
repository's tasks were operated through ad-hoc mechanics (hand-served
files, manually moved CSVs, raw lab invocations). The 2026-07-05 rating
session required improvising a local server because the browser extension
could not open `file://` URLs, and the exported CSV had to be dragged into
place by hand. Every such improvisation is a place where a
non-developer — the project's actual target user — gets stuck.

The user directed (2026-07-05, recorded verbatim in spirit in
`docs/cli/mechas-cli-design.md`): standardize how everyone interacts with
the application through a supportive Python CLI built on Typer and Rich,
modular and themed to use case, prioritizing user experience and quality
of life over raw speed, with the readability rating workflow as the first
standardized task.

## Decision

- **Surface**: `tools/mechas_cli/` — a separate installable package. It is
  deliberately NOT a lab (labs stay stdlib-only research prototypes) and
  NOT engine code (`packages/mecha_engine` stays dependency-free; the
  package dependency policy remains blocked). `tools/` is the home for
  user-facing operational tooling.
- **Command name**: `mechas` — on theme, not an industry-standard word,
  and general enough that future capabilities will not outgrow it.
- **Dependencies**: Typer and Rich, declared twice on purpose:
  `tools/mechas_cli/pyproject.toml` (the runtime package, with the
  `mechas` entry point) and the root `[dependency-groups].cli` (in-repo
  development and tests), following decision record 0005's group pattern.
  Install: `uv tool install --editable .\tools\mechas_cli` (global
  command) or `uv sync --group cli` (dev environment).
- **Design contract**: `docs/cli/mechas-cli-design.md` governs how
  commands look and behave; `docs/cli/mechas-cli.md` is the living command
  reference. New commands must follow both.
- **First standardized task**: `mechas rate --creatures` runs the whole
  rating loop — serve the visual tool, open the browser, receive the
  ratings back over `POST /api/export`, write them into
  `data/readability/` with backup-before-overwrite, and run the
  calibration gate. `--autoexport` removes the last manual step.
- **Honesty boundary unchanged**: the CLI operates gates and moves
  evidence; it never fabricates it. Rating rows still come only from
  humans, and the calibration gate remains the sole judge of readiness.

## Consequences

- The repository gains a third code surface with its own conventions:
  `labs/` (research, stdlib), `packages/` (promoted engine, stdlib),
  `tools/` (user-facing operations, curated dependencies).
- CLI tests live in `tools/mechas_cli/tests`; the stdlib parts (server,
  workspace resolution) run anywhere, the Typer-surface tests skip when
  the `cli` group is not provisioned — the H-01 rule (never pin
  environment observations) continues to apply.
- Future workflows (gate reruns, artifact regeneration, workshop tasks)
  should be added as `mechas` commands rather than new ad-hoc
  instructions.

## Evidence

- `docs/cli/mechas-cli.md`
- `docs/cli/mechas-cli-design.md`
- `tools/mechas_cli/`
- `research/decision_records/0005-declare-lab-dependency-manifest.md`
- `research/experiment_reports/2026-07-05-slip-readability-rating-tool.md`
- `labs/readability_benchmark/rating_tool_builder.py`
