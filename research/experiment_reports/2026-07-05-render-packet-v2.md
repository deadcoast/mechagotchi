# Experiment Report: Render Packet Contract v2 (T16, lab-side)

Date: 2026-07-05

## Objective

Audit T16: restore the og render-packet contract — packets carry
`animation` and `mood`, and their cells show the selected state's
visuals. Lab-first per governance; the promoted
`mecha_engine.genome.render_packet_from_grid` stays v1 until its own
port decision record.

## Design

- `select_animation_state(lifecycle_state) -> (animation, mood)`:
  thresholds mirror `estimate_hidden_mood` (energy 0.2 / hunger 0.65 /
  stress 0.65) so mood and animation always agree; blink is a
  deterministic periodic tic (every fifth tick) in the curious band.
- `build_render_packet_v2(grid, lifecycle_state=None, *, animation=None)`
  wraps the PROMOTED packet builder over the T4 projection — structure
  and validation stay the engine's; v2 adds `animation`, `mood`,
  `animation_vocabulary`. No lifecycle state ⇒ idle/base (pinned equal
  to the v1 packet's cells). Explicit animation overrides (previewer).
- Workshop previewer consumes it: `/api/preview/render` accepts
  `animation`; the portrait gains five state buttons — the creature
  blinks, sleeps, begs, and shivers from engine truth.

## Verification

RED (builder absent, 2 failures) → GREEN:

```txt
labs/grid_genome  Ran 120 tests  OK  (4 new: selection thresholds, projected visuals ride the packet, idle/base pin, override)
workshop/tests    Ran 34 tests   OK  (2 new endpoint tests incl. loud unknown-state failure)
```

## Remaining T16 scope (tracked)

The promoted-module port (packet v2 into `mecha_engine.genome`) is
DR-gated with parity notes — queued with the ladder's package port.
Effects (SLIP render block) wait on their T3 rung per DR 0011 verdict 2.

## Sources

- `labs/grid_genome/animation_states.py`, `labs/grid_genome/test_animation_states.py`
- `workshop/server/workshop_server.py`, `workshop/preview/preview.html`, `workshop/tests/test_workshop_server.py`
- `research/experiment_reports/2026-07-05-animation-states.md`
- `audits/TODO.md` (T16), `research/decision_records/0011-run-one-run-two-reconciliation.md`
