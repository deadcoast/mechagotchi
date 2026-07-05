# mecha_workshop — Design Charter

Date: 2026-07-05. The binding design document for the workshop build
track (decision record 0010). Companion to `mecha-workshop.md` (the
living reference). Every workshop surface is measured against this
charter the way every `mechas` command is measured against the CLI
charter; MIVIM doctrine (root `README.md`) applies in full.

## 1. What the workshop is

**The creative authoring layer of the Mechagotchi Computational Life
Engine** — the place where a person draws a creature body on the grid,
authors the SLIP profile that will govern its kind, previews how the
engine will treat both, and moves work in and out of the formats artists
already use (PNG, APNG, Aseprite, spritesheets).

The founding law, from the project's own brainstorming document and
unchanged since: **the workshop creates compatible profiles, but the
engine remains autonomous.** The workshop guides, constrains, remixes,
and authors; it never simulates, never decides survival, never learns.
Everything alive stays the engine's.

## 2. Who it is for

**Creators first** — pixel artists and companion-keepers, not engine
developers. The MIVIM audience rules apply verbatim: general users first;
technical-yet-catered; the tool should make its user feel smart, never
babied and never lost in development standards. A creator should be able
to draw a creature, understand *why* the engine would accept or reject
it, and export something that works — without reading a single research
document.

The second audience is the engine itself: every workshop output is an
engine input. That ordering is deliberate — when a creator convenience
and engine compatibility conflict, compatibility wins and the workshop's
job becomes *explaining* the constraint beautifully, not hiding it.

## 3. The pillars

The three MIVIM pillars, plus two the workshop adds:

- **1-A · UI design** — one visual language: the LCD-handheld theme the
  project already ships (the creature palettes, the rating tool's device
  framing, the `mechas` banner). The grid is the hero surface. Design for
  both light and dark, never crash on a hostile environment, and let the
  creature's own aesthetics carry the personality.
- **2-A · Quality-of-life development** — whole tasks, not fragments:
  draw → validate → preview → export is one flow. Backup before
  overwrite. The next step is always stated. Locks, keyboard flows, and
  batch affordances follow the rating tool's precedent.
- **3-A · Ease of use** — no dead ends. An invalid grid is an explained
  grid: the workshop translates the engine's validator and SLIP errors
  into pointing-at-the-pixels guidance ("the core splits here"; "this
  profile requires an expression cell — add a mouth"). Every error the
  engine can raise is a teaching surface.
- **4-W · Compatibility is sacred** — the workshop may never emit a grid
  or profile the engine would reject. Validation is live and built on the
  engine's own promoted surfaces (`mecha_engine.genome.validate_grid`,
  the SLIP schema and alignment checks) — never a reimplementation that
  can drift. Import is permissive (meet artists where their files are);
  export is strict (the engine's contracts, always).
- **5-W · Evidence-backed features** — a workshop feature exists only
  where a lab proved the ground under it. The PNG/APNG/Aseprite codecs,
  sidecar strategy, SLIP authoring validation, and preview gates are all
  proven in `labs/workshop_editor`; features map to those surfaces and
  cite them. New capability that needs new research gets a lab first,
  like everything else in this repository.

## 4. What the workshop shows: truth from the engine

Previews are **the engine's answers, not the workshop's guesses**. The
animation/state previewer renders the engine's render packets
(`render_packet_from_grid`); behavior and mutation previews reuse the
proven preview-gate semantics; a "how would it live?" preview runs the
engine's own `runtime.live_cycle`. Where a preview depends on something
honestly uncalibrated (proxy readability), the workshop shows the
uncalibrated status the same way the engine records it. The workshop
never fabricates engine behavior — it asks.

## 5. Delivery direction (revisitable by decision record)

Local-first, dependency-free web surfaces served by **`mechas workshop`**
— the pattern the rating tool proved end-to-end: self-contained HTML
generated or served from the repo, the CLI providing the local server,
file safety (backup-before-overwrite), and the save-to-project loop; the
labs' `window.MECHAGOTCHI_*` `_data.js` payloads were built for exactly
this consumption. The CLI remains the supportive layer (identity
constraint); the workshop is application content it serves.

The brainstorming document's TypeScript + React suggestion is recorded as
the scale-up path: if editor complexity outgrows the dependency-free
approach, that migration takes its own decision record with the evidence
that forced it. Start lean, prove the flows, earn the toolchain.

## 6. First build order (slices, each independently shippable)

1. **Grid editor + live validation** — draw on the 8×8 grid with the
   engine's palettes, roles, and organs; `validate_grid` and SLIP
   alignment run live with pointing-at-the-pixels explanations.
2. **SLIP profile creator** — author a profile against
   `research/slip/slip.schema.json` with the authoring-panel validation
   the labs proved; profile ↔ grid compatibility shown live.
3. **Preview** — render packets, animation states, behavior/mutation
   previews, and a `live_cycle` "day in the life" run.
4. **Import/export** — PNG/APNG/Aseprite/spritesheet round-trips over the
   proven codecs and the external-sidecar strategy; strict on export.
5. **Genome inspector + lineage browser** — read surfaces over grids,
   archives, and lineage records.
6. **Community asset/profile system** — deferred: requires storage
   decisions (`storage` module DR) and licensing/provenance policy; not
   before.

Each slice lands with the full ecosystem: tests, docs, ledger entries,
and — where new algorithms appear — research triads.

## 7. What the workshop is not

- Not the engine, and never upstream of it: it cannot mutate engine
  behavior, only author inputs the engine freely accepts or rejects.
- Not a generic pixel editor: every affordance exists because grids are
  genomes here — roles, organs, palettes, and profile constraints are
  first-class, not metadata bolted onto art.
- Not a hiding place for engine complexity: constraints are explained,
  not suppressed; honesty surfaces (uncalibrated readability, blocked
  states) render as-is.
- Not a dependency magnet: the stdlib-first discipline that built the
  codecs governs the workshop until a decision record says otherwise.

## Sources

- `docs/01-brainstorming.md` (sections 1.4, 1.7, 1.8, 1.19, 1.20)
- `research/decision_records/0010-start-mecha-workshop-build-track.md`
- `docs/workshop/mecha-workshop.md`
- `docs/cli/mechas-cli-design.md` (the charter pattern)
- `README.md` (identity constraint, MIVIM doctrine)
- `labs/workshop_editor/` (the proven research surface)
- `research/slip/slip.schema.json`
- `packages/mecha_engine/` (validation, render packets, runtime previews)
- `data/readability/slip_readability_calibration_rating_tool.html` (the
  delivery-pattern precedent)
