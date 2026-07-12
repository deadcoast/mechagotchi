# Game Client Evidence

Measured evidence from the GAME build's client (`game/`, DR 0033) —
the playable front end, distinct from the workshop's authoring surfaces.

- `front_end_skeleton_stage0.json` - F1: the launchable pygame-ce
  hello-creature skeleton measured. Twin-run frame checksums byte-equal
  (deterministic composition), the idle clip cycling tick % 4, the
  always-on LCD identity (scanline + lcd_ghosting) rasterized with
  nothing declared skipped; lcd_ghosting implemented FIRST here (the
  named Phase-C remainder — 10 distinct frames from a 4-frame clip,
  the persistence transient). crt_bloom/glitch land at F3; the
  companion loop at F2; the installable release at F5.

Produced by `game/evidence.py`.
