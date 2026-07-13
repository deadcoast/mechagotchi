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
  fleet's consumers landed the same day (F3's second half, below).
- `fleet_consumers_stage0.json` - F3 (second half): the D6-kept five
  stream through the learning module's public fleet surface into the
  product session (dropped threads stay out). Consumers verbatim:
  "begs soon" = the hunger forecast's own anticipatory effect; idle
  clip choice = the bandit's recommendation (packet-side); felt mood
  = the HMM's MAP readout with entropy-honest confidence. Measured:
  hunger 0.983 / energy 0.869 / HMM 0.763 / timing 1.0 confidence on
  an 80-tick attentive life, the bandit honestly cold (0.0); twin
  runs byte-equal; decision divergence vs frozen = 0 (D6's ~0,
  reconfirmed at the product loop). Correction recorded: the fleet
  was already package code since cycle 12 - only the export and the
  consumers were missing.

- `keeper_campaign_stage0.json` - F4: the Keeper/era loop in the
  client at the A4 SESSION scale - calm/stable/storm, 3 eras
  SURVIVED, nine unlock facts across all five axes, founders chained
  from elites verbatim, first-era twin byte-equal, the best elite
  adoptable as the companion through the engine gate, the DR 0022
  ledger lossless. The learned readability scorer is injected from
  the new runtime export (the documented divergence from the lab
  session's proxy). Review-scrubber, Contribute, and covenant
  SPENDING are named remainders; the scale-geometry seam was NOT
  demanded by this consumer (recorded).

- `installable_release_stage0.json` - F5: MVP 0.1 installable -
  the REAL PyInstaller bundle launched fresh (exit 0, 4 ticks, save
  written) then launched again RESUMING the same life (exit 0, age
  4 -> 7), the data corpus bundled; keeper_session_v1 save/resume
  pinned byte-identical against a never-saved twin. Generated only
  against an existing build (game/build_release.py), never
  fabricated. CI/signing/multi-platform stays Phase G.

- `covenant_spending_stage0.json` - F7 (cycle 15, MVP 0.2): the
  earned facts SPEND - one calm era earns 8 facts; over-budget
  refused with nothing applied; palette + thinking + population(64)
  spent under the engine's SLIP authority; the era under the spent
  covenant fills 93 niches (the DR 0021 exponential axis observed).
  Successors inherit the unlock state, never the spends. Deferred
  axes named (organ roles, harsher forecasts).

- `hatchery_stage0.json` - F8 (cycle 15, MVP 0.2): species
  generation as a product path - three founders hatched under the
  covenant (engine-filtered, validator-gated, deterministic), every
  origin legible from the verbatim generation trace, all adoptable
  through the engine gate; the released founder led the next era's
  pool and the era survived. The hatchery is the constrained
  stabilizer (trace-carrying); WFC stays era-side (DR 0031).

- `contribute_bridge_stage0.json` - F9 (cycle 15, MVP 0.2): the
  Contribute step as a file bridge - the committed 8x8 workshop
  releases rejected VERBATIM on DR 0029 size coherence while an
  LCD-aligned 16x16 release was admitted and led the pool (the
  engine's own verdict, shown never smoothed); twin-equal; the era
  survived. Inboxes: data/workshop/released + keeper/released.

- `review_replay_stage0.json` - F10 (cycle 15, MVP 0.2): the Review
  step - the era's best elite lives one RECORDED life at the era's
  own seed (live_cycle record_frames, DR 0023): birth 1 / wound 2 /
  repair 2 / episode_tick 32, the scrubber invariant holding at
  every frame, twin-equal, the honest label riding the artifact.
  Raw seeds under the weak test-scale repair model truncate honestly
  (the G2 aligned-but-invalid boundary, pinned); elites record full.

- `repertoire_stage0.json` - F13 (cycle 16, MVP 0.3): the archive
  browsable - every elite rendered from its real packet under the
  covenant, captions/axes/components record-verbatim, era switching
  true, twin-equal. A adopts the BROWSED elite. Ledger-sourced
  cross-restart browsing rides F17; the family lens stays a named
  rung.

- `lineage_story_stage0.json` - F14 (cycle 16, MVP 0.3): the lineage
  browser - a real three-life story (founder -> starvation ->
  succession x2) with origins verbatim, engine death causes, and the
  ancestor chain growing 0 -> 1 -> 2 (generate_candidate's own
  ancestor_ids); twin-equal; the story rides the save file. Origins
  are additive Keeper facts; old saves stay loadable.

- `covenant_io_stage0.json` - F15 (cycle 16, MVP 0.3): covenants
  travel - the spent covenant exports verbatim and round-trips to
  identity; the zoo's gray covenant imports (8 seeds satisfy it) and
  its era fills 22 niches; the invalid fixture refused with the
  authority's verbatim error; the impossible one with the engine's
  no-seed-satisfies rule. Imports are new species contracts; spends
  re-apply by choice.

Produced by `game/evidence.py`.
