# Experiment Report: Real Weather Harshness — Measured Per Phase, and the Callback Path Made Real (Cycle 19 · SHARED · I3)

Date: 2026-07-20

## WHY

G4 verified real weather through the untouched seam and measured it
MILD (multipliers 0.77–0.85) — with two named reasons: the corpus was
early-phase, and the replication/lineage pressure channels are SILENT
on checkpoint data (the format stores neither). I1 committed the
two-phase corpus. I3 asks the pre-registered question: **does late
soup breach the synthetic storm's 1.17× precedent** (DR 0018's
measured figure) — the multiplier direction measured, never tuned —
and attempts the named callback export path, upstream permitting.

The game stake: weather is the pressure the player's creatures live
under. Whether REAL computational-life dynamics can drive the
ecosystem harder than the synthetic storm is a player-facing question
about how alive the world's weather really is.

## WHAT

**Through the checkpoint seam (zero changes): NOT breached — and
post-takeover measures MILDER.** Every committed snapshot through the
engine's own `_cubff_generation_pressure` (verbatim): early-phase
0.772–0.873 (mean 0.818), post-takeover 0.771–0.797 (mean 0.784).
The reason is structural, not tuned: post-takeover tape is
low-entropy (structured replicators), which drags the instability
channel DOWN, while the channels that would carry the harshness —
`0.5 × replication_rate` and the lineage terms — are exactly the ones
the checkpoint format cannot store.

**The callback export path: the upstream PERMITS.** The audited
commit's pybind11 module builds clean in WSL
(`make CUDA=0 bin/cubff$(python3-config --extension-suffix)`,
pybind11 from a venv — no system changes). `load_from` resumes the
I1 committed checkpoints; `eval_selfrep` lights
`replication_per_prog`. The channel tells the phase story loudly:
**2 replicating programs of 131,072 early vs 129,211 (98.6%)
post-takeover**. Compact records (tape + soup hash + FULL replication
scores) are committed
(`data/cubff_real_ingest/callback_states/callback_states_compact.json`,
the I1 ingest labeling their phases from in-record brotli); the raw
~100 MB soup JSONL is reproducible from the committed script
(`labs/cubff_transducer/callback_state_export.py`).

**With the replication channel lit: harsher, still under the storm.**
The engine's own math over the committed callback records — recomputed
LIVE by the evidence builder and its tests, never pasted: early
control 0.773; post-takeover **1.021**; post-takeover late **1.048**.
The direction is measured: real post-takeover weather IS harsher when
the channel that sees replicators is fed — and the synthetic storm's
1.17× precedent still stands unbeaten by real soup on every path.

Artifact: `data/game_client/real_weather_harshness_stage0.json`
(game suite 163 green; 10 new harshness pins, every engine number
recomputed from committed evidence).

## Verification

```powershell
PS> python -B -m unittest discover -s game/tests -p "test_real_weather_harshness.py"
ImportError: cannot import name 'STORM_PRECEDENT_MULTIPLIER' from 'evidence'
FAILED (errors=1)                              # RED: the builder absent
# after the checkpoint-seam measurement:
Ran 5 tests ... OK
# the callback block added RED first (KeyError 'callback_path'):
Ran 5 tests ... FAILED (errors=1)
# after the callback measurement + the channel-state pins updated:
Ran 10 tests ... OK
PS> python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 163 tests ... OK
PS> wsl -e bash -lc 'source ~/cubff_venv/bin/activate && cd ~/cubff_g2 && python3 callback_state_export.py'
early_control epoch 2050 brotli 7911584 rep>0: 2
post_takeover epoch 4098 brotli 1472320 rep>0: 129211
post_takeover_late epoch 32770 brotli 1631052 rep>0: 129564
```

## HONEST REMAINDER

1. **lineage_churn stays silent on EVERY real path** — neither
   checkpoints nor the callback state expose a lineage-event stream;
   the `0.3 × lineage_churn` instability channel reads 0. A harsher
   real weather may exist behind it; unmeasurable until the upstream
   exposes lineage events (an upstream-integration question, named).
2. **The callback export is WSL-only** (the .so is a Linux build);
   the committed compact records + the recorded protocol reproduce
   it — the same machine-boundary honesty as G2.
3. **A callback-sourced game forecast is not wired** — the records
   are seam-compatible today; wiring is a consumer decision, not
   smuggled in here.
4. **Three callback states from one run** — the channel contrast
   (2 vs ~129k replicators) is unambiguous, but a distributional
   claim about callback-path harshness would need its own protocol.

## Sources

- `audits/TODO.md` (cycle 19 I3)
- `research/experiment_reports/2026-07-12-real-weather.md` (G4 — the mildness finding and the named channels)
- `research/experiment_reports/2026-07-20-post-takeover-corpus.md` (I1 — the two-phase corpus)
- `game/evidence.py` (`build_real_weather_harshness_report`) + `game/tests/test_real_weather_harshness.py`
- `labs/cubff_transducer/callback_state_export.py` (the WSL-side protocol)
- `data/game_client/real_weather_harshness_stage0.json`, `data/cubff_real_ingest/callback_states/callback_states_compact.json`
- `research/decision_records/0018-cubff-live-lineage-pressure.md` (the 1.17× precedent), `0020-cubff-pressure-runtime-promotion.md`
