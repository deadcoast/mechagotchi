# Decision Record 0021: The Game Loop (R4) — Eras of the Soup

Date: 2026-07-07

## Status

**Accepted** (DR 0017 R4 — "the game loop decision record"; owner
purpose a.2: an incremental progression, survival and simulation game
as the showcase of the CuBFF engine). This record is R4's deliverable
AND the governing design for the game-loop build track. Its completion
is a checkpoint; each build gate below gets its own plan.

## The duality this record serves

The engine needs the game to be discovered; the game needs the engine
to be worth playing (DR 0017). Consequently the game's FIRST LAW:
**every number, event, and image the player sees is engine truth** — a
report field, an artifact, a replayed render packet. No mechanic may be
invented UI. Where a mechanic needs a number the engine does not yet
produce, the engine grows the number first (its own lab, its own
tests), and only then does the game show it.

## The player fantasy

The player is a **Keeper**: custodian of a mechagotchi lineage evolving
inside a computational-life soup they do not control — they steward it.
The soup has weather (CuBFF dynamics), the creatures have minds (CTM
deliberation) and legibility (learned readability), and the Keeper's
covenant with their species is the SLIP profile. The game is the story
of a bloodline surviving eras.

## The core loop — one session

1. **Review** — the last era's report and replay: who survived, what
   the storms did, how the species changed (R5's scrubber is the
   window; until it ships, the report artifacts are).
2. **Covenant** — adjust the species SLIP within the unlocked budget
   (palettes, organ roles, mutation caps, `deliberation` depth,
   `lineage_preferences`). The SLIP schema ladder (DR 0012) IS the
   progression surface: fields unlock as the lineage earns them.
3. **Contribute** — optionally craft a creature in the workshop and
   RELEASE it; released creatures enter the next era as founders
   through the engine's own gates (`founder_grids`, DR 0016 — admission
   or verbatim rejection, both shown).
4. **Choose the era's weather** — a CuBFF pressure source
   (`cubff_pressure_source`, DR 0018/0020): calm soups, storm soups,
   mixed forecasts; later, REAL ingested CuBFF runs (currently blocked:
   `awaiting_real_cubff_snapshots` — the game ships on synthetic
   weather and upgrades to real exports with zero seam changes).
5. **Run the era** — one `mecha_engine.runtime.evolve` run (the
   promoted surface): generations of candidates, damage cycles scaled
   by that era's weather, archive selection, lineage deepening.
6. **Collect** — progression unlocks computed from the era report's
   engine metrics; the era is persisted; the next era's founder pool is
   the archive's elites (see Persistence).

## Survival sessions

An **era** is one evolve run; a **campaign** is the chain of eras. The
survival stakes are real engine dynamics, not scripted events:

- **Storm eras**: high-instability pressure sources drive the measured
  1.17x damage multiplier (R2) — visibly harsher generations. Surviving
  a storm is a real achievement because the damage was real.
- **Extinction risk**: the evolve loop already ends evolution when the
  archive empties ("an empty archive ends evolution" — measured, not
  asserted). An extinct campaign's lineage is over; the Keeper starts a
  successor bloodline carrying only their unlocks — roguelite stakes
  from an existing engine behavior.
- **The stress regime** (hard survival, shipped pre-R1) is the
  difficulty dial: sheltered eras for onboarding, hard-survival eras
  for veterans.

## Incremental progression (a.3: growth at CuBFF scale)

Progression currencies are engine metrics, verbatim from reports:

| Unlock axis | Engine-truth source | What grows |
| --- | --- | --- |
| Niche mastery | `summary.archive.filled_niches` / `coverage` | new allowed palettes and organ roles in the SLIP budget |
| Bloodline depth | `max_lineage_generation` | `deliberation.max_ticks` (+1 per tier — the species literally learns to think longer; R1) |
| Quality-diversity | `summary.archive.qd_score` | population and generation caps per era — the exponential axis: caps double per tier, so campaign scale climbs toward CuBFF-experiment population magnitudes |
| Storm record | `cubff_pressure.by_generation` survived at multiplier ≥ threshold | harsher forecasts + weather provenance display (snapshot ids) |
| Legibility | `readability_selection.mean_learned_readability_by_generation` trend | readability-aware parenting blend increments (R3) |

Threshold VALUES are tuning, not architecture: they live in the session
lab (gate G2) as data, proven falsifiable by tests (a threshold met in
a fixture report must unlock; unmet must not).

## What the player NOTICES per session (a.4 — the living ecosystem)

Each felt phenomenon maps to a shipped engine mechanism, by design:

1. **The weather changes the world** — storm eras wreck more cells than
   calm ones (R2's measured directionality), and the forecast cites its
   CuBFF snapshot provenance.
2. **Creatures visibly think** — deliberation traces (R1) render as
   thinking pauses before decisions; deeper-tick species deliberate
   observably longer.
3. **The species becomes easier to read** — generations get measurably
   more legible under the learned model (R3's A/B: 0.498 vs 0.199 by
   generation 3) — the player literally sees bodies clarify over eras.
4. **Your creature's blood persists** — a released workshop founder's
   descendants carry its lineage; the inspector already browses
   released ancestry and evolution traces.
5. **Absence hurts** — offline persistence (below) means the soup
   simmered while away: the return screen replays what the bloodline
   endured, deterministically reproducible from the stored seed.

## Persistence — unblocking the `storage` module

Era-chaining is the persistence spine: **the next era's
`founder_grids` are the previous era's archive elites**, re-admitted
through the engine's own gates. This works TODAY with two shipped
surfaces (`evolve` returns the archive; `founder_grids` accepts grids)
and no new engine code.

What must persist across sessions (and therefore what the deferred
`storage` module must store):

- the campaign chain: era reports + rng seeds (full deterministic
  replayability of a campaign's history),
- the current archive elites (the living bloodline),
- the Keeper's SLIP profiles and unlock state,
- released-workshop lineage records,
- replay artifacts (R5).

This record UNBLOCKS the `storage` module decision record (deferred
since DR 0006; DR 0011 already ratified SQLite as the direction): the
storage DR is build gate G1 below and must be proposed before any
persistence code. JSON-artifact persistence (the existing pattern)
remains the interim so the session lab (G2) does not wait on G1.

## Build gates (each gets its own plan/checkpoint)

- **G1 · `storage` module decision record** — schema for campaigns,
  eras, unlocks, lineage; SQLite per DR 0011's pointer; stdlib
  `sqlite3` keeps the package dependency policy intact.
- **G2 · Session-runner lab** (`labs/game_loop/`) — one full session
  over the promoted surfaces: era-chaining via founders, weather
  selection, unlock evaluation from report metrics, extinction and
  succession. Deterministic; the triad convention like every lab.
- **G3 · Replay (R5)** — the recorder + scrubber this loop's Review
  step consumes; already queued as its own task.
- **G4 · The Keeper's surface** — session UI following the workshop
  server pattern (stdlib server + served page, DR 0010's delivery
  stack); `mechas` gains session commands (DR 0007's charter: new
  operational workflows become `mechas` commands).

## Scope boundaries

- No monetization/economy design; no UI framework beyond the ratified
  served-page stack.
- The manual rating system remains the readability FALLBACK everywhere
  in the game; the learned model (R3) is the primary signal.
- Real CuBFF weather stays honestly blocked on the ingest gate; the
  game's weather system is designed so real exports drop in with no
  seam changes.

## Consequences

- The showcase has a governing design traceable to engine truth,
  closing R4 to its description.
- The `storage` module DR (G1) is now unblocked and queued.
- R5 (replay) gains its consumer: the Review step.

## Sources

- `research/decision_records/0017-recalibration-engine-game-duality.md` (R4, the duality)
- `research/decision_records/0016-evolve-founder-grids.md` (era-chaining spine)
- `research/decision_records/0018-cubff-live-lineage-pressure.md`, `research/decision_records/0020-cubff-pressure-runtime-promotion.md` (the weather)
- `research/decision_records/0019-learned-readability.md` (legibility progression)
- `research/decision_records/0011-run-one-run-two-reconciliation.md` (SQLite pointer), `research/decision_records/0006-create-mecha-engine-repair-target.md` (storage deferral)
- `research/decision_records/0010-start-mecha-workshop-build-track.md`, `research/decision_records/0007-mechas-companion-cli.md` (delivery stack)
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py` (the era engine)
- `audits/complete/01/audit-devspec.md` (the og core-function finding)
- `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json` (the honest weather blocker)
