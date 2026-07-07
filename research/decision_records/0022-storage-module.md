# Decision Record 0022: The `storage` Module — Campaign Ledger (G1)

Date: 2026-07-07

## Status

**Accepted** (DR 0021 build gate G1 — "the storage DR ... must be
proposed before any persistence code"). `storage` has been a deferred
`mecha_engine` module target since the scaffold (DR 0004), reaffirmed at
every promotion (DR 0006/0008/0009); DR 0011 verdict #10 ratified
SQLite as its direction. This record authorizes the
`mecha_engine.storage` target and fixes its schema and contracts. It
creates NO code: like `repair` (DR 0006), the target is authorized here
and the module lands only when its lab evidence exists and
`labs/package_promotion/package_promotion_gate.py` says
`promotion_ready`. The G2 session lab does not wait — JSON-artifact
persistence remains the ratified interim (DR 0021), with the migration
contract below keeping those artifacts un-stranded.

## What storage is — and is not

Storage is the **campaign ledger**: a deterministic, transactional
store of engine truth. It inherits the game's first law (DR 0021):
everything it holds is a report field, an artifact, or a grid the
engine actually produced — verbatim.

Consequently storage **never computes game logic**. Unlock thresholds
are tuning DATA in the session lab (G2, DR 0021: "threshold VALUES are
tuning, not architecture"); the session lab evaluates them and storage
records the resulting unlock **facts**, each citing the report metric
and value that earned it. Storage also never invents identity: ids,
dates, and seeds are caller-injected, so the module is deterministic
end to end (no wall-clock, no os-random — the same rule every promoted
module obeys).

## Decision — SQLite through stdlib `sqlite3`

One SQLite database file is the campaign ledger (lab default
`data/game_loop/campaign_ledger.sqlite`; the stage-0 JSON report stays
the evidence artifact, the `.sqlite` file is a binary payload like the
workshop labs' PNGs). Stdlib `sqlite3` keeps the package dependency
policy intact — the deliberately-blocked `[project]` dependencies list
stays empty. Foreign keys are enforced (`PRAGMA foreign_keys = ON`) and
the schema is versioned by `PRAGMA user_version` (v1 below); migrations
are forward-only functions keyed on that version.

### The blob-authoritative rule

Engine artifacts (era reports, grids, elite records, SLIP profiles,
rejection errors) are stored as **canonical JSON text** —
`json.dumps(value, sort_keys=True, separators=(",", ":"))` — and the
blob is the single source of truth. A small set of scalar columns is
*derived* from the blob at write time purely for indexing and query
(fitness, qd_score, decision status, ...). A contract test pins every
derived column equal to its blob field; round-trips are byte-identical
after re-canonicalization. Nothing is ever lossily normalized: the era
report the engine returned is the era report the ledger returns.

## Schema v1 (`PRAGMA user_version = 1`)

Everything DR 0021's persistence list names maps to a table:

```sql
CREATE TABLE campaigns (
  campaign_id               TEXT PRIMARY KEY,
  keeper_label              TEXT NOT NULL,
  created_date              TEXT NOT NULL,   -- caller-injected ISO date
  predecessor_campaign_id   TEXT REFERENCES campaigns(campaign_id),
  status                    TEXT NOT NULL
    CHECK (status IN ('active', 'extinct', 'retired'))
);

CREATE TABLE slip_profiles (              -- the Keeper's covenant, per era
  profile_id    INTEGER PRIMARY KEY,
  campaign_id   TEXT NOT NULL REFERENCES campaigns(campaign_id),
  era_index     INTEGER NOT NULL,
  slip_version  TEXT NOT NULL,            -- derived: profile.slip_version
  profile_json  TEXT NOT NULL             -- authoritative
);

CREATE TABLE eras (                       -- one runtime.evolve run each
  campaign_id             TEXT NOT NULL REFERENCES campaigns(campaign_id),
  era_index               INTEGER NOT NULL,
  rng_seed                INTEGER NOT NULL,
  slip_profile_id         INTEGER NOT NULL REFERENCES slip_profiles(profile_id),
  weather_json            TEXT,           -- cubff_pressure_source snapshots
                                          -- verbatim; NULL = no source (the
                                          -- byte-identical default, DR 0020)
  report_json             TEXT NOT NULL,  -- the evolve report, verbatim
  -- derived query columns, each pinned to report_json by contract test:
  decision_status         TEXT NOT NULL,  -- report.decision.status
  filled_niches           INTEGER NOT NULL,
  coverage                REAL NOT NULL,
  qd_score                REAL NOT NULL,
  max_lineage_generation  INTEGER NOT NULL,
  went_extinct            INTEGER NOT NULL, -- generations ran < requested:
                                            -- the measured empty-archive end
  PRIMARY KEY (campaign_id, era_index)
);

CREATE TABLE elites (                     -- the living bloodline, per era
  campaign_id  TEXT NOT NULL,
  era_index    INTEGER NOT NULL,
  niche_key    TEXT NOT NULL,             -- the archive's descriptor key
  grid_id      TEXT NOT NULL,             -- derived: elite.grid_id
  fitness      REAL NOT NULL,             -- derived: elite.fitness
  elite_json   TEXT NOT NULL,             -- the six-field elite record
                                          -- verbatim (grid, descriptor,
                                          -- fitness, fitness_components,
                                          -- validation, provenance)
  PRIMARY KEY (campaign_id, era_index, niche_key),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);

CREATE TABLE founders (                   -- released-workshop lineage +
  campaign_id           TEXT NOT NULL,    -- era-chained elites, as admitted
  era_index             INTEGER NOT NULL, -- or rejected by the engine
  grid_id               TEXT NOT NULL,
  source                TEXT NOT NULL
    CHECK (source IN ('workshop_release', 'era_elite')),
  admitted              INTEGER NOT NULL,
  rejection_errors_json TEXT,             -- the engine's errors verbatim
                                          -- (DR 0016) when admitted = 0
  grid_json             TEXT NOT NULL,
  PRIMARY KEY (campaign_id, era_index, grid_id),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);

CREATE TABLE unlocks (                    -- facts, never logic
  campaign_id      TEXT NOT NULL REFERENCES campaigns(campaign_id),
  axis             TEXT NOT NULL          -- DR 0021's five unlock axes
    CHECK (axis IN ('niche_mastery', 'bloodline_depth',
                    'quality_diversity', 'storm_record', 'legibility')),
  tier             INTEGER NOT NULL,
  earned_era_index INTEGER NOT NULL,
  metric_path      TEXT NOT NULL,         -- the report field cited
  metric_value     TEXT NOT NULL,         -- JSON scalar, evidence verbatim
  threshold        TEXT NOT NULL,         -- the tuning value met (G2 data)
  PRIMARY KEY (campaign_id, axis, tier)
);

CREATE TABLE replays (                    -- R5 artifacts stay files;
  campaign_id   TEXT NOT NULL,            -- the ledger stores pointers
  era_index     INTEGER NOT NULL,
  artifact_path TEXT NOT NULL,            -- repo-relative POSIX (L-08 rule)
  artifact_sha256 TEXT NOT NULL,
  PRIMARY KEY (campaign_id, era_index, artifact_path),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);
```

Design notes:

- **Succession without copying** (DR 0021's roguelite stakes): an
  extinct campaign's successor row points at it via
  `predecessor_campaign_id`; the Keeper's carried unlocks are resolved
  by following that chain at read time. Unlock rows are never
  duplicated, so every unlock keeps citing the exact era report that
  earned it.
- **Era-chaining is a read, not a copy**: `load_founder_pool` returns
  the latest era's elites ordered by niche key — the same deterministic
  ordering `evolve` itself uses for elite parents — ready to pass as
  the next era's `founder_grids`. The spine works today because both
  ends already ship (DR 0016 + DR 0021).
- **Deterministic replayability is a schema property**: `rng_seed` +
  `profile_json` + `weather_json` + the previous era's stored founder
  pool are exactly the inputs `evolve` needs, so any stored era can be
  re-run and must reproduce `report_json` — the gate below makes that
  falsifiable rather than aspirational.
- **Weather provenance**: `weather_json` stores the snapshots verbatim
  including `snapshot_id`, so the storm-record unlock axis and the
  forecast display cite real provenance (DR 0018/0020). When real CuBFF
  exports clear the ingest gate, they persist through the same column —
  no schema change.

## Proposed public surface (to be proven in the lab first)

```python
open_ledger(path) -> sqlite3.Connection   # creates/migrates via user_version
record_campaign(conn, campaign) -> None
record_era(conn, campaign_id, era_index, *, rng_seed, slip_profile,
           weather, founders, archive, report) -> None   # one transaction
load_founder_pool(conn, campaign_id) -> list[dict]       # niche-key order
record_unlocks(conn, campaign_id, unlock_facts) -> None
load_unlock_state(conn, campaign_id) -> dict             # follows the chain
campaign_history(conn, campaign_id) -> dict              # replay-sufficient
ingest_session_artifacts(conn, artifact_paths) -> dict   # the G2 migration
```

One era = one transaction: the era row, its elites, its founder
admissions, and its unlock facts commit atomically or not at all — a
campaign ledger never holds a half-written era.

## Gates — contract tests required before promotion

Proven lab-first in `labs/game_loop/` (`campaign_store.py` +
`test_campaign_store.py`, registered as a promotion-gate candidate),
then ported verbatim to `mecha_engine.storage` under the standing
rules (stdlib-only, no `labs` imports, no `sys.path`, lab-side parity
pins):

1. **Round-trip fidelity** — a stored era report re-canonicalizes
   byte-identical to what `evolve` returned; same for grids, elites,
   SLIP profiles, and rejection errors.
2. **Derived-column pin** — every derived scalar equals its
   `report_json`/`elite_json` field on real evolve output.
3. **Chain integrity** — era N's admitted `era_elite` founders equal
   era N−1's stored elites in niche-key order.
4. **Deterministic replay** — re-running `evolve` from a stored era's
   seed, profile, weather, and founder pool reproduces the stored
   report (the DR 0021 replayability claim, executed).
5. **Unlock falsifiability** — a fixture report meeting a threshold
   must produce the unlock fact; the same report below threshold must
   not; every stored fact's `metric_path` resolves in its cited era
   report to `metric_value`.
6. **Extinction and succession** — a run that ends on the measured
   empty-archive break stores `went_extinct = 1`; a successor campaign
   resolves the predecessor's unlocks without copying rows.
7. **Interim migration** — `ingest_session_artifacts` imports the G2
   lab's JSON-artifact persistence losslessly (gate 1 holds across the
   migration), so nothing G2 records before promotion is stranded.
8. **Determinism scan** — no wall-clock, no os-random, no absolute
   paths in stored strings (repo-relative POSIX per the L-08 rule).

## Consequences

- The last DR 0011-ratified stack pointer (SQLite → storage module) is
  now a design, not a pointer; `render` and `slip` remain the deferred
  module targets awaiting their own decision records.
- G2 (the session-runner lab) proceeds on JSON artifacts with a
  guaranteed migration path, and gains the schema vocabulary
  (campaign/era/unlock/founder) this record fixes.
- The scaffold verification gate's deferred-set note is updated: the
  `storage` target is authorized (this record) while module creation
  still waits on its lab evidence and a `promotion_ready` verdict.

## Sources

- `research/decision_records/0021-game-loop.md` (G1, the persistence list, the first law)
- `research/decision_records/0011-run-one-run-two-reconciliation.md` (verdict #10: SQLite pointer ratified)
- `research/decision_records/0004-mecha-engine-package-scaffold.md`, `research/decision_records/0006-create-mecha-engine-repair-target.md` (the deferral and the authorize-then-gate pattern)
- `research/decision_records/0016-evolve-founder-grids.md` (founder admission semantics stored verbatim)
- `research/decision_records/0018-cubff-live-lineage-pressure.md`, `research/decision_records/0020-cubff-pressure-runtime-promotion.md` (weather provenance)
- `packages/mecha_engine/src/mecha_engine/runtime/evolve.py` (the report and founder shapes the schema stores)
- `packages/mecha_engine/src/mecha_engine/archive/store.py` (`_elite_entry` — the six-field elite record)
- `research/package_specs/mecha_engine_scaffold_verification_gate.md` (deferred-set negative check)
- `labs/package_promotion/package_promotion_gate.py` (the promotion authority)
