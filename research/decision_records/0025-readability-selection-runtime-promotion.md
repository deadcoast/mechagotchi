# Decision Record 0025: Readability Selection into `runtime.evolve` (C1)

Date: 2026-07-07

## Status

**Accepted** (cycle 03 C1, named by the G2 report: the legibility
currency was inert at the promoted surface because R3's
readability-aware parenting was a lab-loop consumer). The DR 0020
promotion pattern, applied to the R3 seam.

## Decision

`evolve(...)` gains `readability_selection: dict | None = None`
(keyword-only): the LEARNED readability model (DR 0019 — TRUE ML as the
primary path; the manual rating system stays the fallback and
calibration check) steers elite parenting exactly as in the lab loop —
parents ranked by `blend * learned_readability + (1 - blend) *
min-max-normalized fitness`, `parent_source:
archive_elites_readability_blend`, precedence over
`lineage_preferences`, and a rung-conditional report block carrying the
per-generation mean learned readability over candidates. Scoring runs
through `runtime/_readability.py` — a VERBATIM private copy of the lab
scorer and its structural-feature helpers (the `_damage`/`_cubff`
copy-never-import rule) with a lab-side drift guard. Default `None` is
byte-identical (every existing parity pin passes unmodified).

## Gates (all green at acceptance)

- Drift guard: mirror features + scores identical to the lab authority
  across the whole seed corpus and edge cases
  (`test_package_readability_parity.py`).
- Lab parity: package `evolve` with the trained arm reproduces the lab
  loop's `generations`, `summary`, and `readability_selection` block
  record-for-record at the same seed; precedence over
  `fitness_weighted` matches; defaults byte-identical
  (`test_readability_selection_parity.py`).
- The R3 directional claim holds on the PROMOTED surface: same seed,
  blend 0.7 vs 0.0, post-founder mean candidate readability higher
  with the model steering.
- Contract: seam shape, determinism, bounded means, authority string,
  weightless-arm rejection (`readability_selection` driver probe).

## Consequence — the legibility currency runs live

The session lab (G2/G4) now passes the arm on every era
(`LEGIBILITY_BLEND = 0.7`, tuning data) and reads the engine's own
per-generation means. Regenerated Stage-0 session: the legibility
unlock axis is EARNABLE live (tiers 1 and 2 earned in era 0, elite mean
0.401 vs 0.244 pre-C1; 8 unlock facts vs 6). Newly measured alongside:
**legibility drifts DOWN across chained eras** (elite means 0.401 →
0.182 → 0.014) — feature-level truth: chained founders breed more
fragmented (inverse component count 0.875 → 0.567), less symmetric
(0.337 → 0.191), less organ-legible (0.845 → 0.775) bodies. A real
ecosystem dynamic for C4 (the Covenant step) and C6 (the repair study)
to engage — recorded, not tuned away.

## Sources

- `research/decision_records/0019-learned-readability.md` (R3, the model)
- `research/decision_records/0020-cubff-pressure-runtime-promotion.md` (the promotion pattern)
- `research/experiment_reports/2026-07-07-game-loop-session-runner.md` (the seam named)
- `packages/mecha_engine/src/mecha_engine/runtime/_readability.py` + `evolve.py`
- `labs/readability_benchmark/test_package_readability_parity.py` (drift guard)
- `labs/runtime_integration/test_readability_selection_parity.py` (parity + A/B)
- `packages/mecha_engine/tests/test_runtime_contract.py` (+ driver probe)
- `labs/game_loop/session_runner.py` (the live consumer)
- `research/package_specs/mecha_engine_runtime_interface_spec.md` ("readability_selection")
