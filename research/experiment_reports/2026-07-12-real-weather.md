# Experiment Report: Real Weather — the Zero-Seam-Change Promise, Verified (Cycle 17 · SHARED · G4)

Date: 2026-07-12

## WHY

DR 0021's weather design made a promise: "real snapshots drop into
the same seam with no session-runner change." The seam shipped
(DR 0018/0020) and the game has run on synthetic forecasts since;
G2 landed real snapshots. G4 cashes the promise in the client.

## WHAT

**Zero seam changes, verified**: `build_weather_source` gains one
FORECAST NAME (`"real"`) whose source is the G2 ingest report's
`ingested_snapshots` VERBATIM (epoch order) — the engine's
`cubff_pressure_source` seam is untouched, and its defensive reads
supply honest defaults for the fields checkpoints do not store
(replication scores, lineage events, brotli size). The client's
weather keys gain **4 = REAL**; the era record's provenance carries
the engine's own per-generation real snapshot ids.

**Measured** (`data/game_client/real_weather_stage0.json`, status
complete, session scale, twin-equal): a real-weather era ran all six
generations (38 elites, no extinction) with every per-generation
snapshot id a REAL id. **The measured direction, recorded not
assumed: real early-phase weather is MILD** — dropout multipliers
0.77–0.85, below baseline and far below the synthetic storm's 1.17×
precedent. The mechanism is the seam's own honesty: entropy is high
on early-phase soup, but the replication and lineage channels read
their silent defaults (checkpoints store neither), and the engine's
trait math lands below 1. Harsh REAL weather awaits post-takeover
soup or the Python-callback export path that lights those channels —
named, not tuned around.

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_real_weather.py"
Ran 1 test ... FAILED (errors=1)   # RED: no "real" forecast
# after implementation:
Ran 5 tests ... OK                 # verbatim source, provenance, determinism
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 152 tests ... OK
PS> uv run python -B game/evidence.py   # real_weather_stage0: complete
```

## HONEST REMAINDER

1. **Two pressure channels stay silent by format** — checkpoints
   store no replication scores or lineage events; the
   Python-callback export path would light them (a named
   upstream-integration increment, not smuggled defaults).
2. **Mild is the truth of THIS corpus** — the storm forecast remains
   the harsh option until real post-takeover soup exists; nothing
   was tuned to make real weather feel dramatic.
3. **The bundled release ships without the ingest report** — the
   `real` forecast needs a checkout (or a bundle that adds the
   report); selecting it without one refuses with a named error.

## Sources

- `audits/TODO.md` (cycle 17 G4), `research/decision_records/0021-game-loop.md` (the promise), `0018`/`0020` (the seam)
- `packages/mecha_engine/src/mecha_engine/runtime/_cubff.py` (the untouched seam)
- `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json` (the verbatim source)
- `game/src/mecha_game/campaign.py` (+ `game/tests/test_real_weather.py`), `data/game_client/real_weather_stage0.json`
