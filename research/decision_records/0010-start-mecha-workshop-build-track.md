# Decision Record 0010: Start the mecha_workshop Build Track (Design Phase)

Date: 2026-07-05

## Status

**Accepted** (owner: "start the mecha_workshop design charter",
2026-07-05). Authorizes the workshop **design phase** — the binding design
charter and the living reference document. Implementation slices follow
the charter and the repo's normal gates; the first implementation slice
starts when the owner approves the charter's build order (or amends it).

## Context

mecha_workshop is the second build of the two-build model
(`docs/01-brainstorming.md`): the creative authoring layer — pixel-art
grid editor, SLIP profile creator, trait/behavior editing, preview,
genome inspection, lineage browsing, import/export. Its founding law,
from the brainstorming document itself: **"The workshop creates
compatible profiles, but the engine remains autonomous."**

The research phase for the workshop is complete and is the largest lab in
the repo: ~30 `labs/workshop_editor` modules proving PNG/APNG/Aseprite/
spritesheet interoperability with stdlib-only codecs, the external
metadata sidecar strategy, SLIP authoring validation, behavior/mutation
preview gates, and multi-profile roundtrips — many already emitting
`window.MECHAGOTCHI_*` `_data.js` payloads designed for exactly this UI.
The engine side is ready: eight promoted modules including
`render_packet_from_grid` (the renderer-neutral visual contract) and
`runtime.live_cycle`/`evolve` for previews.

Owner corrections that govern this record: the workshop was never
deferred (2026-07-05 correction — the survey-data deferral covers only
survey data), and it is part of the application proper — unlike the
`mechas` CLI, which remains a supportive layer under the identity
constraint. The engine stays the core; the workshop authors *for* it.

## Decision

- Create the design pair, following the charter-first pattern proven by
  the CLI (doctrine → charter → implementation):
  - `docs/workshop/mecha-workshop-design.md` — the binding design charter.
  - `docs/workshop/mecha-workshop.md` — the living reference (module map,
    build-slice roadmap, status).
- The charter binds all future workshop implementation the way the CLI
  charter binds `mechas` commands; MIVIM doctrine (root `README.md`)
  applies in full.
- Compatibility is a gate, not a goal: everything the workshop exports
  must pass the engine's own validators and gates — the workshop may
  never emit a profile or grid the engine would reject.
- Delivery direction (charter section 5, revisitable by decision record):
  local-first, dependency-free web surfaces served by `mechas` — the
  pattern the rating tool proved end-to-end — consuming the engine's
  render packets and the labs' `_data.js` evidence. The brainstorming
  document's TypeScript + React suggestion is recorded as the scale-up
  path if complexity demands it, gated by its own decision record.

## Consequences

- The application's second build begins with a governed identity instead
  of accreting one.
- Workshop implementation slices inherit the full ecosystem obligations:
  research triads where new algorithms appear, specs, tests, ledger
  entries, and the charter's pillars.
- `render`/`storage`/`slip` package modules remain deferred; if workshop
  slices need them promoted, each takes its own decision record.

## Evidence

- `docs/01-brainstorming.md` (sections 1.4, 1.7, 1.8, 1.19, 1.20)
- `labs/workshop_editor/` and its ledgered triads (`research/README.md`)
- `research/slip/slip.schema.json`, `data/slips/valid/`
- `packages/mecha_engine/` (eight promoted modules; render packet
  contract)
- `docs/cli/mechas-cli-design.md` (the charter-first pattern)
- `docs/workshop/mecha-workshop-design.md`
- `docs/workshop/mecha-workshop.md`
