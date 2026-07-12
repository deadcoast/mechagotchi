# Experiment Report: Product Hardening (Cycle 15 · GAME · F11)

Date: 2026-07-12

## WHY

Three named product frictions from the F5–F10 reports: the era
bench's ~6 s lazy model training per process; the console-only
release build; and DR 0007's standing charter — new operational
workflows become `mechas` commands — unmet for the game. An
operational rung: its pins live in the existing suites, and it
records no new statistics (no stage-0 artifact — named, not
smuggled).

## WHAT

1. **The model cache** (`load_campaign_inputs(cache_dir=…)`): the
   repair model — the slow trainer — caches to
   `keeper/model_cache/repair_model_<key>.json`, keyed on the
   training corpus's grid ids + epochs + seed. **A cached load is
   byte-equal to fresh training** (the trainer is deterministic in
   its inputs) and a second load HITS the cache (mtime untouched) —
   both PINNED by `test_model_cache_is_byte_equal_to_fresh_training`.
   The era bench wires it through the keeper dir; the cache is play
   state, gitignored with everything else under `keeper/`.
2. **The windowed build**: `game/build_release.py --windowed`
   produces the player-facing (no-console) bundle; console stays the
   default per the F5 report's diagnostics note.
3. **`mechas game`** (DR 0007's charter): `--play [--ticks N]
   [--new]`, `--build [--windowed]`, `--evidence` — the supportive
   layer driving the game's own scripts with the WORKSPACE
   interpreter (the established `_workspace_python` rule; the game
   group's pygame-ce lives in the workspace venv). Registered on the
   root app; surface-tested like every command; verified live
   (`mechas game --play --ticks 3` launched the real window, exit 0).

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_campaign.py"
Ran 14 tests ... OK        # incl. the byte-equal cache pin
PS> uv run python -B -m unittest discover -s tools/mechas_cli/tests -p "test_*.py"
Ran 23 tests ... OK        # incl. the game surface tests
PS> mechas game --play --ticks 3
pygame-ce 2.5.7 (SDL 2.32.10, Python 3.13.9)   # window, exit 0
```

## HONEST REMAINDER

1. **The cache keys on grid IDS, not grid contents** — a mutated
   corpus under unchanged ids would serve a stale model. The corpus
   is committed fixtures (content changes come with id/test churn),
   so ids are a sufficient key TODAY; if generated corpora ever feed
   the trainer, the key must grow a content hash — named here.
2. **`mechas game --build --windowed` shells the same builder** — the
   windowed bundle was not separately launch-verified (the console
   bundle was, at F5); the flag flips one documented PyInstaller
   switch.
3. **The generation model is retrained per load** (fast; only the
   repair trainer was the measured cost).

## Sources

- `audits/TODO.md` (cycle 15 F11), `research/decision_records/0007-mechas-companion-cli.md` (the charter)
- `game/src/mecha_game/{campaign,app}.py`, `game/build_release.py`, `game/tests/test_campaign.py`
- `tools/mechas_cli/src/mechas_cli/workflows/game.py` (+ `tests/test_cli_surface.py`)
- `research/experiment_reports/2026-07-12-installable-release.md` (the console-default note)
