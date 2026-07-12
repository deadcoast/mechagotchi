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
- `companion_loop_stage0.json` - F2: MVP 0.1's loop as a product,
  measured under the documented beg-mediated model (D5/D6/DR 0021:
  the companion cannot feed itself). Real stakes from the engine's
  own dynamics: neglect starves at age 10 (4 begs unanswered);
  the attentive keeper's 79 answered feeds carry the companion
  through the full 400-tick budget. Twin runs byte-equal; succession
  is the engine's child (beetle -> gen_d42be33dc5a7bfa7, lineage
  verbatim, 2 records in keeper_lineage_v1). F3 owns the full render
  bridge; F4 eras/saves; F5 the installable release.
- `render_bridge_stage0.json` - F3 (first half): live clip DRIVING
  through the documented C2 graph (44-tick state sweep drives
  beg/idle/ill/sleep with ZERO illegal cuts - every cut a measured
  edge at a loop boundary) and the FULL effects contract rasterized
  (scanline, lcd_ghosting, crt_bloom riding beg, glitch riding ill
  with amplitude = engine stress). Twin runs byte-equal. The kept
  fleet's consumers await the thread promotion (F3's second half).

Produced by `game/evidence.py`.
