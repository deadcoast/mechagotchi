# Experiment Report: The Carried Remainders Close (Cycle 16 · GAME · F17)

Date: 2026-07-12

## WHY

Three named product remainders carried through the F10/F7/F11
reports: replays were recorded on demand and lost on restart; the
ACTIVE spent covenant was process-state (re-earned from facts on
relaunch); the windowed bundle was never launch-verified. An
operational rung — its pins live in the suite, its observations here.

## WHAT

1. **Replay persistence** (`KeeperCampaign.save_review_replay` /
   `load_review_replay`): the DR 0022 pointer rule consumed — the
   replay artifact stays a FILE (`keeper/replays/…_era<N>.json`), the
   ledger's `record_replay` stores the pointer + sha256 (duplicate
   pointers skipped), and **a loaded replay is hash-verified — a
   tampered artifact is refused with the hash named** (pinned). The
   client's V now loads a persisted review when one exists and
   persists the one it records.
2. **Campaign resume** (`save_state`/`load_state`,
   `keeper_campaign_state_v1`): the ACTIVE state — the SPENT covenant
   included, the earned and inherited facts, the era-chain position —
   survives restart; the resumed first era's founders come from the
   LEDGER's own pool (`load_founder_pool`), era indices and seeds
   continue from the offset, and the ledger append stays idempotent
   across the boundary (absolute era indices). **Pinned: a resumed
   continuation matches the unbroken run byte for byte.** Observed
   live: two separate process launches ran era 0 then era 1 of ONE
   campaign (state era_count 2, ledger 2 rows). This also closes the
   F7 report's named covenant-resume remainder.
3. **The windowed bundle launch-verified**: `build_release.py
   --windowed` built and ran headless (`--ticks 3`, exit 0, saves
   written) — the F11 report's named gap; the verify build is
   deleted after observation (installers are built, never committed;
   the ignore rule generalized to `game/dist*/`).

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_persistence.py"
Ran 1 test ... FAILED (errors=1)   # RED: no save/load surfaces
# after implementation:
Ran 4 tests ... OK                 # incl. the unbroken-run byte pin
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 147 tests ... OK
PS> # the live two-launch resume (one campaign, two processes):
PS> uv run python -B game/run_game.py --ticks 3 --eras 1 --era-scale tiny --keeper-dir <home>
PS> uv run python -B game/run_game.py --ticks 3 --eras 1 --era-scale tiny --keeper-dir <home>
# state era_count: 2 · ledger eras: 2 · exit 0
PS> uv run python -B game/build_release.py --windowed --dist game/dist_windowed
PS> .\game\dist_windowed\Mechagotchi\Mechagotchi.exe --ticks 3 ...   # exit 0
```

## HONEST REMAINDER

1. **Resume rebuilds in-memory browsing lazily** — the repertoire
   browses eras run THIS process; past eras' elites live in the
   ledger and feed the founder chain, but a ledger-backed repertoire
   page is a named next increment, not smuggled.
2. **One replay pointer per era** — re-recording an era's review
   reuses the persisted artifact (deterministic, hash-verified); a
   multi-take history has no consumer yet.
3. **The state file is play state** (gitignored under `keeper/`),
   never evidence — the ledger remains the record.

## Sources

- `audits/TODO.md` (cycle 16 F17); the F7/F10/F11 reports (the named remainders)
- `research/decision_records/0022-storage-module.md` (the pointer rule), `packages/mecha_engine/src/mecha_engine/storage/store.py`
- `game/src/mecha_game/{campaign,app}.py` (+ `game/tests/test_persistence.py`)
