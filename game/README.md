# Mechagotchi — the Game Client

The second of the two builds (`docs/gap-analysis.md` §0): the playable
desktop client showcasing the Mechagotchi Computational Life Engine.
Technology decided by decision record 0033 (pygame-ce — the engine
imported in-process, packets consumed verbatim). The first law
(DR 0021): every number, event, and image shown is engine truth.

## Layout

- `src/mecha_game/` — the client package (no `sys.path` text; imports
  `mecha_engine`, never `labs`):
  - `packets.py` — the engine-truth packet source (adoption through
    `lifecycle.initial_state`; frames from `genome.render_packet_v2`)
  - `rasterize.py` — the pure, pygame-free compositor (the packet→pixel
    spec: palette raster, scanline, temporal `lcd_ghosting`)
  - `session.py` — the companion loop (F2, MVP 0.1): W1 semantics +
    the documented beg-mediated interaction model (the companion begs,
    only the keeper feeds), death → the engine's child, the
    `keeper_lineage_v1` file of verbatim engine blocks
  - `hud.py` — pure engine-truth bars (hunger/energy) + `ui_hints` icons
  - `app.py` — the playable window (fixed-timestep pygame-ce loop)
- `tests/` — the F1 gates (headless; pygame cases skip unless the
  `game` group is provisioned)
- `evidence.py` — the stage-0 evidence harness
  (`data/game_client/front_end_skeleton_stage0.json`)
- `run_game.py` — the dev-checkout launcher
- `pyproject.toml` — the installable form (`mechagotchi` entry point;
  packaging is F5's rung)

## Run it (dev checkout)

```powershell
# Reuse the provisioned repository environment (Python 3.13.9 here).
.venv/Scripts/python.exe -B game/run_game.py            # play until ESC/close
.venv/Scripts/python.exe -B game/run_game.py --ticks 24 # bounded verification run
```

Controls: **F1** full controls / care pause · **PgUp/PgDn** or wheel casing pages ·
**G** clean when enabled · **F** feed · **P** play · **S** sleep (queued for the next
lifecycle tick) · **ENTER** adopt the successor when the companion
dies · **E** run an evolution era (**1–5** pick the weather) ·
**A** adopt the era's best elite as your companion · **C** covenant
mode (**1/2/3/4** spend earned unlocks: palette / thinking /
population / generations) · **H** hatch a new founder under your
covenant and adopt it (its origin trace shows) · **R** release your
companion's genome as a founder for the next era · **W** gather the
workshop's released creatures for the next era (the engine admits or
rejects them — the verdict shows) · **V** review the last era's best
elite's recorded original evaluation (SPACE play/pause, **.** step, **,**
back) · **B** browse the repertoire — your bloodline's whole archive,
niche by niche (**.**/**,** page, **[**/**]** switch eras, **A**
adopt the one you're looking at) · **L** read your bloodline's story,
life by life (origins, death causes, the growing ancestor chain) ·
**X** exports your covenant as a shareable SLIP file. **I** opens the
covenant inbox; **K** opens the pack inbox. Select with arrows or comma/period,
then **Enter** imports the previewed file through the engine's gates.
Covenants and creatures from packs stage into the inboxes with item verdicts;
`data/packs/mechagotchi_starter_pack.json` is the committed example.
**ESC** closes help first; in play it requests quit. Close requests quit; failed saves pause for retry. Saves land in
`keeper/` (gitignored) — quit and come back, the client resumes. The
companion begs when it wants food — only you can feed it; neglect
starves it (measured: ~10 ticks).

## Experimental learning policy

The current default remains `incumbent`. Try the bounded Q-table learner in
a separate save directory; the choice and learned state survive quit/resume.
Successors retain the choice and learn afresh. Only you can feed the companion.
The casing pages show its actual recommendation and followed decision.

```powershell
.venv/Scripts/python.exe -B game/run_game.py --new --learning-policy qtable --keeper-dir "$env:USERPROFILE/.mechagotchi-qtable"
# Resume without repeating the policy:
.venv/Scripts/python.exe -B game/run_game.py --keeper-dir "$env:USERPROFILE/.mechagotchi-qtable"
# Supportive source CLI (with tools/mechas_cli/src on PYTHONPATH):
.venv/Scripts/python.exe -B -m mechas_cli.app game --play --new --learning-policy qtable --keeper-dir "$env:USERPROFILE/.mechagotchi-qtable-example"
```

An explicit policy conflicting with a saved companion is refused before writes.
`--learning-policy incumbent` selects the original behavior for a new life.
The latest locally closed V1 native build is
`game/dist/v1-niche-history/Mechagotchi/Mechagotchi.exe`; keep `_internal` beside it.
Use the same policy arguments there. New native saves use
`$env:USERPROFILE/.mechagotchi`; an explicit `--keeper-dir` selects another
home. Existing bundled `_internal/keeper` lives continue in place when no
user-home save exists. If both exist, the user-home save wins and the bundled
save remains untouched. The experimental policy was not adopted as default:
the inherited research corpus does not fully match the current covenant.

## Recover an earlier companion save

Invalid saved model data is refused before play. If `companion.bak.json` exists,
explicitly restore it with the same save directory:

```powershell
.venv/Scripts/python.exe -B game/run_game.py --keeper-dir keeper --recover-backup
# Supportive source CLI:
.venv/Scripts/python.exe -B -m mechas_cli.app game --play --keeper-dir keeper --recover-backup
```

The native executable accepts the same `--recover-backup` option. Recovery
validates the backup first, keeps the old primary byte-for-byte as
`companion.before-recovery-<digest>.json`, then resumes the earlier save. Its
policy, learned state and age come from that backup. The recovery notice names
the archive; the casing pages show the active policy. Recovery rolls back to
the prior save, so progress after that save is not included in the resumed life.

A missing primary with an existing backup requires `--recover-backup` or an
explicit `--new`; it never silently starts a replacement pet. Bad backups and
conflicting new-life/policy options are refused without writes. Saves use
atomic replacement of each file. The companion and lineage files are separate
writes, not a transactional pair; recovery restores the companion save and its
embedded lineage. The app reconciles the derived export from that validated
save before play, preserving replaced export bytes in its backup.

## Save during play and retry a failed save

**Ctrl+S** saves now without queuing sleep. Death, succession, hatch/adoption and
normal quit checkpoint the companion, including its embedded lineage and
learning state. Repeated unchanged checkpoints keep the prior recovery backup.

If the companion cannot be saved, care pauses and the current pet stays in
memory. Fix the write problem, then press **Ctrl+S** to retry; if you were
quitting, a successful retry closes the window. **Ctrl+Q** explicitly quits
without saving those in-memory changes. The earlier on-disk companion remains.
A bounded `--ticks` run reports the error and exits nonzero instead of hanging.

`companion.json` is the save authority. Failure to update the separate lineage
export warns you but still saves the pet. Missing/stale lineage exports are
repaired on resume, including after explicit backup recovery. This also repairs
exports left inconsistent by older app versions; it does not merge newer data
from an export into an older companion.

The S2 checkpoint build is `game/dist/s2-safe-checkpoints/Mechagotchi/Mechagotchi.exe`
with its adjacent `_internal`. Actual source/CLI/native fault checks passed;
its full closing gate passed 2,537 tests; details are recorded in the
`research/experiment_reports/2026-10-04-safe-checkpoints.md` report.

## Review recorded eras (T1)

**T** opens the latest recorded era for the current bloodline, including after
restarting. The companion stays visible and care pauses. **[ / ]** (or comma /
period) moves between eras; **PgUp/PgDn** or the wheel pages wrapped details.
The view shows stored outcomes, coverage/QD, generations, earned unlock values
and thresholds, weather snapshots and founder admission facts.

**T** or **Escape** returns to care. **F1** opens help and returns to the report.
**C** opens the current covenant; **E** runs the next era and opens its report.
Only reading history performs no training or evolution. No prior campaign is
created by an empty view; unreadable records show an unavailable notice.
**Ctrl+S** and save-failure retry/discard keep their existing behavior.

T1 build: `game/dist/t1-era-review/Mechagotchi/Mechagotchi.exe`, with adjacent
`_internal`. Verification and limits are in
`research/experiment_reports/2026-10-04-era-review.md`. T1 is the report browser;
T2 adds saved archive access; T3 below reopens recorded lives after restart.

## Browse and adopt saved creatures (T2)

**B** opens the latest saved archive after restarting. From a **T** era report,
B opens that selected era. **Comma/period** selects creatures; **[ / ]** selects
eras; **PgUp/PgDn** or the wheel pages their recorded details. Bodies are rendered
from their stored grids under that era's covenant. Care pauses while browsing;
care keys are ignored. **F1** help returns to the same selection.

**T** opens the selected era's report. **B** or **Escape** returns to the report
or care you entered from. **A** adopts the selected creature under the current
covenant, preserves your chosen learning policy, checkpoints and returns to care.
A refused adoption keeps your pet and names the engine's refusal. Empty/corrupt
archives are explicit; a corrupt archive cannot start further planning actions.
An empty history can still run its first era with **E**.

**C** budget and spending controls now appear before care status on the first
small-window page. Covenant mode keeps its existing live care timing; F1 pauses
care while reading help. The incumbent policy remains the default.

Locally closed build: `game/dist/t2-saved-archive/Mechagotchi/Mechagotchi.exe`, retain its
adjacent `_internal`. Evidence and full-gate status:
`research/experiment_reports/2026-10-04-saved-archive.md`.

## Replay recorded lives (T3)

**V** opens the latest era's saved recording, or the selected era from **T**,
after restart. **Space** plays/pauses, **comma/period** steps within the saved
frames. Care pauses and care/planning keys are ignored. **F1** pauses playback
and returns to the same frame. **V/Escape** returns to the entry report or care;
**T** opens that recording's era report. Existing Ctrl+S retry/discard remains.

The preserved T3 build made **post-era recorded lives at the era seed**;
those saved artifacts remain clearly labelled legacy recordings. Current U1
source captures the original best-elite evaluation during E, as described below.
Missing, malformed or hash-mismatched artifacts are never reconstructed or
replaced. V only reads a saved recording.

Locally closed T3 build: `game/dist/t3-saved-replays/Mechagotchi/Mechagotchi.exe`, with
adjacent `_internal`. Its implementation evidence and passed full gate are
in `research/experiment_reports/2026-10-04-saved-replays.md`.

## Keep the next-era plan (T4)

**R** stages a copy of the current companion's genome; your companion stays
with you. **W** gathers released workshop creatures. Exact repeats stage once;
**Backspace** unstages copies without deleting creatures. **1-5** selects weather
outside covenant mode. These choices save immediately and survive restart.
They also work while a **T** report keeps care paused. The next-era line shows
the saved weather and staged count; **F1** lists preparation controls.

**C** spending and **I** covenant imports save successful changes immediately.
Inside C, **1-4** still spends the earned budget. Covenant mode retains its
existing live-care timing; F1 pauses it. New state retains the original budget
base so repeated restart does not increase an already spent cap. Old states
without that field keep their established interpretation.

**E** runs the prepared next era of the current bloodline, including when you
are viewing an older report. The engine admits or refuses contributions through
its existing gates. The resulting report shows outcome, niche count and QD on
page one, then full admitted IDs and verbatim refusal reasons. **B**, **A** and
**V** continue into archive, adoption and saved replay with explicit provenance as described above.
An adopted companion can be contributed to a later era through the same R flow.

If saving an already computed era fails, its journal retains the result. **E**
retries saving that result; it does not run another era. This works after restart.
Preparation changes remain paused until completion, and staged contributions
clear only after the ledger and state are saved. Care and recorded-history views
remain available. Corrupt preparation or conflicting external state is preserved
and reported. No offline evolution or new default policy is introduced.

Locally closed build: `game/dist/t4-keeper-loop/Mechagotchi/Mechagotchi.exe`, with adjacent
`_internal`. Exact verification/closure status is in
`research/experiment_reports/2026-10-04-keeper-loop.md`.

## Install it (F5)

```powershell
.venv/Scripts/python.exe -B game/build_release.py --windowed
.\game\dist\Mechagotchi\Mechagotchi.exe --keeper-dir "$env:USERPROFILE\.mechagotchi"
```

Quit and come back: the client auto-resumes your companion from the
save file (`--new` starts a fresh one). Saves live in `keeper/` in a
checkout. The current native bundle starts new saves in `~/.mechagotchi`.
An existing bundled `_internal/keeper` save continues there if no user-home
save exists. Explicit `--keeper-dir` overrides discovery and never migrates
an existing companion. R4 repaired the save-home limitation recorded at Q5.

## Test it

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p "test_*.py"
```

## Sources

- `research/decision_records/0033-game-front-end-technology.md`
- `research/experiment_reports/2026-07-12-front-end-client-skeleton.md`
- `research/decision_records/0021-game-loop.md` (the design input)
- `docs/gap-analysis.md` (Phase F)

## Covenant-authored cleaning (Q2, 2026-10-04)

A v0.2 covenant can opt into cleanliness with
`"mechanics": {"cleanliness": true}`. The game shows the engine's value in
the footer and **G** queues a clean action for the next lifecycle tick.
Cleaning takes a tick; it does not feed the companion. The default covenant
stays unchanged. Opt-in survives quitting, resuming, and succession.

Try the authored example in a separate save directory:

```powershell
uv sync --locked --group lab --group cli --group game
uv run --no-sync python -B game/run_game.py --new --slip data/slips/valid/slip_v2_cleanliness.json --keeper-dir keeper/cleanliness-example
# Resume that same companion (omit --new):
uv run --no-sync python -B game/run_game.py --keeper-dir keeper/cleanliness-example
```

`--new` replaces the companion in the selected keeper directory. The example
directory separates this trial from ordinary `keeper/` play. For code consumers,
`CompanionSession(..., mechanics=None)` inherits the covenant; an explicit
`mechanics=()` disables it, and that override survives save/load/succession.

## Sources for Q2

- `research/decision_records/0063-covenant-mechanics-authorship.md`
- `game/tests/test_slip_mechanics.py`
- `data/slips/valid/slip_v2_cleanliness.json`

## 2026-10-04: New default companions can be cleaned (DR 0064)

New lives now use the measured v0.2 cleanliness covenant. **G** cleans on the
next lifecycle tick; the footer shows the engine's value. Feeding, playing and
sleeping still matter; cleaning takes time and does not feed the companion.
Existing saves and existing campaigns retain their own covenants.

The normal launcher now supports authored profiles and separate save homes:

```powershell
mechas game --play
mechas game --play --new --slip data/slips/valid/slip_v2_cleanliness.json --keeper-dir keeper/cleanliness-example
mechas game --play --keeper-dir keeper/cleanliness-example
```

The last command resumes that example. A supplied --slip applies to a new
companion; if that directory already contains a save, choose --new explicitly
or a separate directory. A new evolution campaign starts under that companion's
covenant. A resumed campaign keeps its saved, possibly earned/spent covenant.
The earlier Q2 default note above describes the state before this gated flip.

## Sources for Q3

- `research/decision_records/0064-default-covenant-cleanliness.md`
- `research/experiment_reports/2026-10-04-default-covenant-gate.md`
- `data/game_client/default_covenant_gate_stage0.json`, `default_covenant_release_stage0.json`

## Readable controls (Q4)

F1 opens the full controls and pauses lifecycle care. Escape closes help first;
PgUp/PgDn or the wheel browse wrapped casing pages. New notices and mode changes
return to page one. Small LCD scales retain a 384-pixel window width.
The preserved Q4 Windows bundle is `game/dist/q4-controls/Mechagotchi/Mechagotchi.exe`;
keep its adjacent `_internal` folder. Built/tested with this repo Python 3.13.9.
See DR 0065 for scripted verification and its limits.

## Phase-Q consolidation (2026-10-04)

The actual direct/source-CLI launch examples, isolated save continuity and
existing native bundle passed Q5 checks; see
`research/experiment_reports/2026-10-04-phase-q-gate.md`.
Q2/Q3 notes above remain dated history. The current default supports G clean;
old saves keep their own covenant. Cycle 28 now provides the package
producer/consumer and explicit playable opt-in. Its actual-game adoption gate
REFUSED the default because the inherited corpus is not fully compatible with
the current covenant; the incumbent remains the default. The dependency-only workspace has no installed `mechagotchi`
console script; use the source launcher or one-folder native executable.

## Responsive era execution (T5 locally closed)

During an interactive **E** era, care and the held creature pause while the
existing casing reports preparation, completed candidate evaluations and saving.
**F1** opens the era's help. **Escape** closes that help first, then cancels
uncommitted computation; staged inputs and the next seed remain available.
Cancellation during a cold model load waits for that phase to finish, while the
window continues responding. Other care, preparation and repeated-E commands
received during work are ignored instead of executing later.

Closing the window requests cancellation and waits for work to stop before the
normal companion checkpoint. Once saving a completed result starts, it finishes
that attempt; T4's retained result/journal can still recover from save failure.
Headless `--eras` remains synchronous. Exact measurements, tested scale limits
and native-build status are in
`research/experiment_reports/2026-10-04-era-responsiveness.md`.


## Original evaluation recording (U1 locally closed)

New E eras save the actual damage/repair evaluation of their final best elite.
V from care or a selected T report plays those recorded frames; V in B opens
only that matching selected elite. Other selections explicitly say not recorded.
Playback keeps care paused and returns to the entry report/archive. Existing
post-era recordings remain labelled as legacy footage; missing historical
originals are never reconstructed. Later covenant or parameter changes do not
change already recorded footage.

Capture retains one best record, limited to 2,048 frames and 8 MiB per era.
Exceeding a bound leaves an explicit unavailable reason; it does not truncate
footage or alter the era result. Earlier recordings are not deleted. Interrupted
completion retains the captured bytes in a versioned journal: use the current
client to finish saving; older clients refuse that pending format safely.
Current source/native verification is recorded in
`research/experiment_reports/2026-10-04-original-era-recordings.md`.

Full U1 `20261004T224746-6ccc82b0` passed 2,624 tests / 24 suites, two
documented zlib skips and 2,290 JSON artifacts without mutations. Eleven native
launches and 25 source flows covered the connected loop and recovery; native
keyboard and maximum-scale behavior remain unobserved. Local completion does
not claim hosted distribution or exact-published-SHA Windows/Ubuntu CI.

## Recorded niche history (V1 locally closed)

In **B**, press **N** to browse saved occurrences of the selected exact seven-axis
niche. **, / .** or **[ / ]** move through occurrences; each shows its recorded
campaign, era and body. **T** opens that occurrence's report, **V** its saved
recording, and **A** adopts under the current active covenant. **N**, **B** or
**Escape** returns to the original archive selection.

In **T**, **Ctrl+[ / Ctrl+]** follow saved predecessor-campaign links; the usual
**[ / ]** still select eras. **L** keeps the companion-life story and links to
campaign story through **T**. Care pauses in these views. Historical navigation
does not switch the active campaign; preparation and new eras still use it.

History compares saved bin labels, not families or ancestry. Historical
calibration is not recorded. Missing links, cycles, incomplete archives and
incompatible axes are explicit; use casing pages for notices. Only the active
campaign's recorded predecessor chain is searched. No E5 regrouping or repair-
parent founder inference is performed. Actual verification and closure are in
`research/experiment_reports/2026-10-04-niche-history.md`.

Full V1 `20261004T234803-5750f659` passed 2,636 tests / 24 suites, two
documented zlib skips and 2,292 valid JSON artifacts without mutations. The final
application demonstration passed 21 checks, four native launches and seven
source pygame flows / 59 frames. Native keyboard and maximum-history performance
remain unobserved; the local result does not claim published-SHA cloud CI.

## Named import inboxes (W1)

Put covenant JSON files in `<save directory>/covenants/` and pack JSON files in
`<save directory>/packs/`; files can keep their names. **I** and **K** open paused
selectors. **Comma/period** or arrows select, **Home/End** go to the first/last
file, **Enter** imports, **F5** refreshes, and **Escape** returns. **F1** explains
the active inbox; **PgUp/PgDn** or the wheel reaches full names and verdicts.
The actual folder path appears in the details. Backup files are excluded.

For the committed example, copy `data/packs/mechagotchi_starter_pack.json` to
your save directory's `packs/` folder. Press **K**, select it, then **Enter**.
Press **I** to choose a staged covenant and **Enter** to apply it. Close the
picker before **W** gathers staged creatures; **E** then uses the prepared era.
Each creature still faces the engine's era-admission gates. No renaming to
`covenant_import.json` or `pack_import.json` is required. Those filenames still
work as ordinary selectable files.

Imports govern future eras, hatches and adoptions; your current pet keeps its
covenant and learning policy. Successful imports save immediately. Refusals
show their actual reasons, and care remains paused while you read them. Files
changed after preview require F5 before import. Repeated pack items with equal
JSON are already staged without rewriting the file; different existing content
is preserved and reported as a conflict. Partial failures show each outcome
and can be retried after fixing the problem.

Verification: `research/experiment_reports/2026-10-05-import-inboxes.md`.
Native keyboard interaction and maximum-inbox performance remain unobserved.
