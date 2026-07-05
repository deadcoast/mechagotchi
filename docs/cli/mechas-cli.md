# mechas CLI — Command Reference

Date: 2026-07-05. The living overview of the `mechas` command surface.
Design rules live in `mechas-cli-design.md`; this file tracks what exists
and what is planned. Update both in the same change as any CLI code.

`mechas` is a **supportive layer, not the application** — the application
is the Mechagotchi Computational Life Engine (standing constraint, root
`README.md`).

## Install

One-time, from the repository root:

```powershell
uv tool install --editable .\tools\mechas_cli
```

That puts `mechas` on your PATH everywhere. Alternatives:

```powershell
uv sync --group lab --group cli                      # dev venv (both groups — uv sync is exact)
.venv\Scripts\python -m mechas_cli --help            # run without installing
```

Quick cheat sheet: root `TOOLS.md`. Current tested status:
`mechas-cli-audit.md`.

The CLI finds the workspace automatically (it is installed editable from
inside the repo); `MECHAGOTCHI_ROOT` overrides if ever needed.

## CLI menu structure

```text
mechas                          the main command (help + version)
├── rate                        rating workflows
│   ├── --creatures             launch the creature readability session
│   │   ├── --autoexport        save finished passes into the project automatically
│   │   ├── --port <n>          local port (default 8423; 0 = pick free)
│   │   └── --no-browser        don't auto-open the browser
│   ├── --status                collection progress, then exit
│   └── --ingest <csv>          bring a downloaded ratings CSV into the project
├── workshop                    the creative authoring layer
│   ├── --editor                launch the grid editor (live engine validation)
│   ├── --port <n>              local port (default: pick a free one)
│   └── --no-browser            don't auto-open the browser
└── status                      workspace at a glance (modules, gates, open tasks)
```

## Commands

### `mechas rate`

The standardized rating system. With no flags it lists the available
rating targets with copyable examples (never an error).

| Flag / option | What it does |
| --- | --- |
| `--creatures` | Launches the creature readability rating session: serves the visual rating tool locally, opens your browser, receives finished ratings back over `POST /api/export`, writes them to `data/readability/slip_readability_calibration_ratings.csv` (backing up any existing file first), and runs the calibration gate when the session ends. |
| `--autoexport` | With `--creatures`: each completed reviewer pass saves itself into the project — no export click, no file moving. |
| `--port <n>` | Serve on a specific port (default: pick a free one — Windows reserves shifting port ranges, so fixed defaults are fragile). |
| `--browser/--no-browser` | Auto-open the rating page (default on). |
| `--status` | Show rows collected (of 63), reviewer names, and calibration readiness. |
| `--ingest <path>` | Validate and copy a manually downloaded ratings CSV into place, then run the gate. |

Under the hood: the rating page itself is a generated artifact
(`labs/readability_benchmark/rating_tool_builder.py`); `mechas`
regenerates it if missing. The page detects being served and switches its
export button from "Download CSV" to "Save to project".

Rating-page QoL (2026-07-05 additions): per-question **locks** carry a
rating across creatures (same-palette batches), a **rate all** row rates
all five questions in one click and can itself be locked, and **keyboard
rating** (`1–5` rate, `Enter` next, arrows move). Locks fill unset values
only, respect each other (question lock beats rate-all), and reset per
reviewer pass.

### `mechas workshop`

The creative authoring layer (charter:
`docs/workshop/mecha-workshop-design.md`). `--editor` launches the grid
editor: the workshop server runs in the workspace interpreter (it
imports the engine for live validation), saves engine-valid grids to
`data/workshop/grids/` with backup-before-overwrite, and the page
explains every engine constraint in place.

### `mechas status`

Workspace overview: engine module promotion state and the readability
calibration state, each with the command that moves it forward.

### `mechas --version`

Version of the CLI itself.

## Development TODO (roadmap)

Extracted from the founding design direction — candidates, in rough value
order, each to be built to the charter's three pillars (1-A UI design,
2-A QoL development, 3-A ease of use):

- [ ] `mechas gates` — run/rerun the promotion + scaffold gates with a
      themed results table (replaces raw lab invocations).
- [ ] `mechas rate --creatures --reviewer <name>` — prefill the reviewer
      id for hand-off sessions.
- [ ] `mechas test [lab]` — themed wrapper over the unittest sweeps with
      a per-lab summary instead of raw discover output.
- [ ] `mechas regen <lab>` — regenerate a lab's data artifacts with a
      diff summary of what changed.
- [ ] `mechas doctor` — environment check (interpreter, dependency
      groups, tool freshness) with fix-it commands.
- [ ] Served rating page shows project-level progress (rows already
      saved in the CSV, not just this browser's passes) via a
      `GET /api/status` endpoint.
- [ ] Shell completion once the command set stabilizes
      (`add_completion` is off until then, to keep help output clean).
- [x] `mechas workshop --editor` — shipped with workshop slice 1
      (2026-07-05); grows with each workshop slice.

## Sources

- `docs/cli/mechas-cli-design.md`
- `research/decision_records/0007-mechas-companion-cli.md`
- `tools/mechas_cli/`
- `labs/readability_benchmark/rating_tool_builder.py`
- `data/readability/slip_readability_calibration_rating_tool.html`
