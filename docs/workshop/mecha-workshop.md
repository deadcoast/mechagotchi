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
verdict flips valid -> profile chips teach -> save lands.

**Slice 2 shipped (2026-07-05).** The SLIP profile creator is live at
`mechas workshop --slip` (`workshop/slip_creator/`, same server, 12
tests total). Authoring is form-first (palette/organ toggles, mass
bounds, mutation/behavior/survival sliders with plain-language hints);
validation is the Stage 0 authority (`labs/grid_genome/slip
.validate_slip`) live, with the lab authoring panel (pydantic +
migration review) layered on when its dependencies exist (recorded
per-run, H-01 style). The compatibility panel answers the authoring
question directly: how many of the 50 seed creatures fit this profile,
and each saved workshop creature judged with reasons. Saves are strict
(authority-clean only, curated profile_ids protected, backup before
overwrite) into `data/workshop/slips/`; authored profiles immediately
join the grid editor's live alignment chips — verified live both ways
in the browser.

**Slice 3 shipped (2026-07-05).** Preview is live at `mechas workshop
--preview` (`workshop/preview/`, same server, 18 tests total) — three
engine-truth panels, per the charter's section 4 (previews are the
engine's answers): the PORTRAIT draws every pixel from
`mecha_engine.genome.render_packet_from_grid` (the packet's own
colors, never a workshop guess); A DAY IN THE LIFE runs
`mecha_engine.runtime.live_cycle` for real (before/after packets,
per-cycle damage size, restoration rate, guard fixes, episode
survival, contract statuses); POSSIBLE CHILDREN breeds via
`mecha_engine.generation` under the chosen profile, each child
validated and alignment-checked. When a creature does not belong to
the chosen profile the engine's own alignment errors ARE the preview
(verified live: lcd creature x amber profile). Creatures come from
the seed corpus and saved workshop grids; profiles include authored
ones. Read-only — preview writes nothing.

**Slice 4, PNG/APNG portion shipped (2026-07-05).** The grid editor's
SHARE panel exports the drawn creature as a **self-contained PNG** via
the proven embedded-sidecar codec (`labs/workshop_editor
/png_embedded_sidecar_writer`): pixels plus the full semantic sidecar
(grid contract, SLIP profile snapshot, semantic overlay, integrity
hashes) in one tEXt chunk. Export is strict per 4-W: the engine's
validity AND profile-alignment verdicts gate it, with a profile picker
for the binding. **Import PNG** restores the creature onto the grid
through the codec's own integrity checks (hash binding, pixel
canonical match), with its failure families verbatim on rejection —
permissive in UX, honest in verdicts, nothing written. **Export APNG**
produces the lab's animated share artifact (base + pulse frames).
Verified: server-side roundtrip tests plus a live-browser UI roundtrip
(export -> wipe -> import -> all 13 cells restored, anchor included).
**Slice 4b shipped (2026-07-05), completing slice 4:** Aseprite
import/export via the user-data-chunk writer lab — a self-contained
LibreSprite/Aseprite project whose user-data chunks carry the full
semantic sidecar — and spritesheet import/export via the sidecar
decoder lab, traveling as the pair the external-sidecar strategy
defines (sheet PNG + sidecar JSON; import requires both, and the
codec's binding checks — recomputed content hash, frame rects, frame
pixel hashes, restored-grid validity and alignment — judge the pair).
All exports remain engine-strict and profile-bound; all imports
return codec failure families verbatim. Verified: 27 workshop tests
plus live-browser UI roundtrips through the real handlers for both
formats (all 13 cells restored, anchor included).

## The ecosystem wire (T1, owner DESIGN-CORRECTION)

**Released creatures live in the engine's world.** The grid editor's
Release button, `POST /api/release`, and `mechas workshop --release
<name>` copy a saved, engine-valid creature (lineage-marked
`released_into_ecosystem`) into `data/workshop/released/`; evolution
runs admit that directory as generation-0 founders through the
engine's own gates and trace every descendant
(`--workshop-dir data/workshop/released`). First measured result:
both founding fixtures went extinct at generation 0 against the seed
corpus — the ecosystem does not grant favors, and the editor's
structural-load meter is the tool for authoring fitter founders
(`research/experiment_reports/2026-07-05-workshop-engine-wire.md`).

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
- [x] 2. SLIP profile creator (2026-07-05)
- [x] 3. Preview (render packets, live_cycle day-in-the-life, engine-bred offspring) (2026-07-05)
- [x] 4a. Import/export PNG (self-contained embedded-sidecar roundtrip) + APNG export (2026-07-05)
- [x] 4b. Import/export Aseprite (self-contained user-data project) + spritesheet (sheet+sidecar pair) (2026-07-05)
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
