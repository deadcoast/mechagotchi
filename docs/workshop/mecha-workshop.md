# mecha_workshop — Reference

Date: 2026-07-05. The living overview of the workshop build track
(decision record 0010). Design rules live in `mecha-workshop-design.md`
(binding); this file tracks what exists, what is planned, and what each
surface stands on. Update both in the same change as any workshop work.

## Status

**Slice 1 shipped (2026-07-05).** The grid editor is live:
`mechas workshop --editor` serves `workshop/grid_editor/` with the
workshop server (`workshop/server/workshop_server.py`, 7 tests). Live
validation is the engine's own verdict (`mecha_engine.genome
.validate_grid`), SLIP compatibility per profile is the Stage 0
authority, morphology stats include the contracted structural load
with the 0.95 collapse boundary explained, and saving is strict
(engine-valid grids only, backup-before-overwrite) into
`data/workshop/grids/`. Verified end-to-end in a live browser: draw ->
verdict flips valid -> profile chips teach -> save lands. Slice 2
(SLIP profile creator) is next.

## The research the workshop stands on

Every planned surface maps to proven lab work (all ledgered in
`research/README.md`):

| Planned surface | Proven ground |
| --- | --- |
| Grid editor + live validation | `labs/grid_genome/validator.py` → promoted `mecha_engine.genome.validate_grid`; `research/grid_genome/grid_invariants.md` |
| SLIP profile creator | `research/slip/slip.schema.json`; `labs/workshop_editor/slip_authoring_panel.py`; slip validator labs (stdlib + pydantic mirror) |
| Profile ↔ grid compatibility | `labs/grid_genome/slip.py` alignment; profile compatibility matrix |
| Behavior/mutation preview | `labs/workshop_editor` preview gates (`slip_behavior_mutation_preview`, lifecycle/archive effects, runtime selection policy, long-horizon behavior) |
| Animation/state preview | `mecha_engine.genome.render_packet_from_grid`; `mecha_engine.runtime.live_cycle` |
| PNG import/export | `labs/workshop_editor` PNG suite (sidecar decoders/writers, Adam7, deep color, textual metadata policy) |
| APNG import/export | APNG frame/playback/metadata labs |
| Aseprite import/export | Aseprite document suite (tags/layers, tilemaps, linked cels, external properties, variant resolution, user-data writer) |
| Spritesheet handling | spritesheet + foreign-fixture conformance labs |
| Genome inspector / lineage browser | grid schema, archive elites, lineage records (`slip_offspring_lineage_gate`, multigeneration lineage runner) |
| UI data payloads | the labs' `window.MECHAGOTCHI_*` `_data.js` artifacts in `data/workshop_editor/` |

## Build slices (charter section 6)

- [x] 1. Grid editor + live validation (2026-07-05)
- [ ] 2. SLIP profile creator
- [ ] 3. Preview (render packets, behavior/mutation, live_cycle)
- [ ] 4. Import/export (PNG/APNG/Aseprite/spritesheet; strict on export)
- [ ] 5. Genome inspector + lineage browser
- [ ] 6. Community asset/profile system (deferred: needs `storage` DR +
      licensing/provenance policy)

## Delivery

Local-first, dependency-free web surfaces served by `mechas workshop`
(reserved in the CLI roadmap since the CLI charter) — the rating-tool
pattern: served HTML, local save-to-project APIs, backup-before-
overwrite. Scale-up to a TypeScript + React toolchain only by decision
record with forcing evidence (charter section 5).

## Sources

- `docs/workshop/mecha-workshop-design.md`
- `research/decision_records/0010-start-mecha-workshop-build-track.md`
- `docs/01-brainstorming.md`
- `research/README.md`
- `docs/cli/mechas-cli.md`
