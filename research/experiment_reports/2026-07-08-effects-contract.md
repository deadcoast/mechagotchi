# Experiment Report: The Retro Effects Pipeline, Contract-Side (Cycle 11 · ENGINE · C5)

Date: 2026-07-08

## WHY

The gap table's rendering row names the retro effects pipeline
(scanline, lcd_ghosting, crt_bloom, glitch) and `ui_hints` (need icons,
attention ping) — present in the dossier's packet example, absent from
the packet. DR 0026's disposition stands: the engine never rasterizes;
effects are renderer-neutral DECLARATIONS consumers draw.

## WHAT

RED-first (5 new pins in `test_effects_contract.py`):

1. **`packet_effects(lifecycle_state, selected)`** — implemented as
   verbatim twins in the lab builder and
   `mecha_engine.genome.animation`, riding every v2 packet (state and
   clip paths): `effects` in the documented list shape,
   `effect_parameters` with deterministic values, `ui_hints` mirroring
   the T16 selection thresholds so icons and animation always agree.
   Engine truth in the parameters: glitch rides the ILL display with
   its amplitude being the engine's own stress number; crt_bloom rides
   the BEG display; scanline + lcd_ghosting are the standing LCD
   identity. The twin change keeps the full animation parity suite
   green (209 grid_genome tests — which correctly FAILED with 134
   errors when the change was momentarily one-sided).
2. **The consumer proof**: the shared workshop drawer gains
   `applyEffects` — scanline overlay, deterministic glitch row-shear
   scaled by the declared amplitude, bloom halo; `lcd_ghosting` needs
   temporal state and is honestly skipped in the static drawer (a
   live-player concern for Phase F's client, recorded in the asset's
   own doc). The workshop test pins the asset's helpers and that the
   render packet carries the full contract.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/animation_system -p "test_*.py"
Ran 33 tests in 7.987s
OK
PS> python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
Ran 209 tests in 4.767s
OK   # the twin builders stay verbatim
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 291 tests in 5.370s
OK
PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
Ran 60 tests in 106.481s
OK
```

## Sources

- `packages/mecha_engine/src/mecha_engine/genome/animation.py`, `labs/grid_genome/animation_states.py` (the twins)
- `labs/animation_system/test_effects_contract.py`
- `workshop/shared/draw.js` (`applyEffects`), `workshop/tests/test_workshop_server.py`
- `research/decision_records/0026` (consumers rasterize), `0013` (rung pattern)
- `docs/project-research/deep-research/01/deep-research.md` (the packet example)
- `audits/TODO.md` (cycle 11 C5), `docs/gap-analysis.md` (Phase C)
