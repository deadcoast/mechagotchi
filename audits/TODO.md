# Development TODO — Cycle 08: COHERENCE — from proven mechanisms to one application

Source: the owner's course correction (2026-07-07): the mechanisms are
proven but the APPLICATION is not coherent — fragmented lab pages, no
single entry point, no living companion, internal jargon on player
surfaces, and a codebase the owner cannot yet read as a product. The
prior "standby" verdict measured against the research designs; this
cycle measures against "can a person launch this, play it, and
understand it." Governing rule unchanged (DR 0017: deep integrations
over breadth; the first law: everything shown is engine truth). A task
is complete when developed to its description, then marked; development
proceeds continuously; planning triggers only on exhaustion confirmed
COMPLETE.

- [x] **W1 · The living companion — the heart of the application.**
  (2026-07-07: `/companion` is live — adopt through the engine's own
  gate (`initial_state` refuses invalid bodies and covenant mismatches
  verbatim; the wrong-species successor case caught live in testing),
  tend with the engine's actions (buttons = `ACTIONS`, one
  `advance_tick` each), "let it live" hands the moments to the frozen
  switchboard with thoughts visible live, every frame packet v2 over
  the live state (the E1 grammar gate bounds expressions, mood stays
  honest), death honest and refusal-not-noop, persistence with backup.
  Lifecycle surface widened four → six exports (gate doc amended,
  exact-`__all__` pin updated). 12 lab gates + endpoint flow tests;
  nav links; `mechas session --companion`. Zero new engine numbers.)
- [ ] **W2 · One front door.** A home shell (`/`... the editor owns
  `/` today — a `/home` landing the other pages link back to, and the
  server's index becomes the shell) unifying companion / session /
  editor / slip / preview / inspector with plain-language descriptions
  of what each does; `mechas play` boots the server and opens it.
  Startup coherence: freeze the generation + repair models as
  committed artifacts (the F3 adopted-model pattern) so launch is
  fast and deterministic instead of retraining every boot.
- [ ] **W3 · Player-language pass.** Every label a player sees gets
  player words with the engine term as the tooltip, not the reverse
  (QD, niches, blend, dropout, parent_source → soup richness, body
  plans, guidance strength, storm damage, ancestry). Text only —
  values stay verbatim engine truth; a glossary panel links the
  research docs for the curious.
- [ ] **W4 · The owner's map.** `docs/architecture-map.md`: every
  package module, every lab, every page, every command — one plain
  paragraph each on what it is, why it exists, and what calls it —
  written for the OWNER to reconnect with the codebase mid-flight;
  refresh the root `README.md` to describe the application as it now
  is (engine + game + workshop + CLI) with a 60-second quickstart.
- [ ] **W5 · Adopt-from-anywhere and the companion↔era bond.** The
  companion is not a side toy: adopting the campaign's best elite
  makes the bloodline personal, releasing a workshop creature and
  adopting it closes the create→love→evolve loop, and a companion that
  dies in your care is the same mortality the eras measure. Wire the
  three adoption sources cleanly and surface the companion's lineage
  (the inspector already reads ancestry).

## Standing note

The identity constraint and DR 0017 govern. The owner-decision menu
(license, dependencies policy, manual calibration, CuBFF ingest,
pushing) stays open in `audits/complete/07/TODO.md`'s wording — none
of it blocks this cycle.

## Sources

- the owner's course correction (2026-07-07, this cycle's charter)
- `research/decision_records/0017-recalibration-engine-game-duality.md`
- `research/decision_records/0021-game-loop.md` (the game the companion joins)
- `packages/mecha_engine/src/mecha_engine/lifecycle/` (`advance_tick`, `choose_action_detailed` — W1's engine)
- `packages/mecha_engine/src/mecha_engine/genome/animation.py` (packet v2 — W1's frames)
