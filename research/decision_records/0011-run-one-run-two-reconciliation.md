# Decision Record 0011: RUN ONE / RUN TWO Design Reconciliation

Date: 2026-07-05

## Status

**Accepted** (audit task T14; owner directive "BEGIN DEVELOPMENT FROM THE
TASKLISTS", 2026-07-05). Ends the silent fork found by the dev-spec
audit addendum: the two historical research programs
(`.depreciated/01-*.md` "RUN ONE", `.depreciated/02-*.md` "RUN TWO")
propose conflicting designs in several places, and the shipped system
resolved each conflict implicitly. This record makes every resolution
explicit so no future session rediscovers the fork. Verdict vocabulary:
the repo's card verbs (**adopt / watch / prototype / reject**); RUN
TWO's "defer" maps to "watch" here, usually with a queued task.

## Verdicts

| # | RUN TWO delta | Verdict | Rationale / where it lives |
| --- | --- | --- | --- |
| 1 | SLIP shape: sizes + allowed_roles constraints (vs RUN ONE's palettes + body-mass + organ roles) | **ADOPT RUN ONE (ratified)** | RUN ONE's shape shipped, is enforced by both validators and every gate, and carries all promoted-module evidence. RUN TWO's `allowed_roles` and size constraints become candidates inside the T3 schema ladder, paired with T15 (role vocabulary) and T6 (sizes). |
| 2 | SLIP `render` block: effects enum (lcd_ghosting/scanline/crt_bloom/glitch) + `animation_vocab` | **WATCH → queued** | Real og intent both runs share; enters through T3 (schema ladder) + T4 (animation vocabulary) + T16 (render packet v2). Not adopted before its consumers exist. |
| 3 | SLIP behaviors `mischief`, `sociability` | **WATCH → queued (T3)** | Behavior weights need lifecycle/switchboard consumers before schema admission — the shipped rule that every SLIP field is enforced or consumed, never decorative. |
| 4 | SLIP mutation knobs `limb_growth`, `max_edit_fraction` | **WATCH → queued (T3)** | `max_edit_fraction` is implementable against current operators; `limb_growth` is blocked on limb roles gaining coverage (T15). |
| 5 | `species_class` required in SLIP + grid | **WATCH → queued (T3.5/T7)** | Wanted by both runs; lands with the taxonomy work, not before. |
| 6 | Grid cell `value` byte channel (0–255) | **REJECT** | The shipped `visual` hex field carries color everywhere — corpora, validator, codecs, render packets, workshop. A parallel byte channel duplicates state with no consumer. |
| 7 | Material vocabulary `metal/gel/wire/organic` | **REJECT (shipped set ratified)** | The shipped enum `void/soft/hard/glass/joint/light/signal` is already in the schema and corpora and is the richer retro-material set. Its dormant members are T15's cover-or-trim scope. |
| 8 | z3/SMT (+ASP) constraint-solver validation track | **WATCH** | The stdlib BFS+rules validator fully covers current invariants (proven against the 200-case invalid corpus). Revisit when invariants outgrow it — multi-size bodies (T6), animation-state constraints (T4), or organ-layout reachability. Stdlib-first doctrine (DR 0005) governs until then. |
| 9 | Jupyter experiment notebooks | **REJECT (superseded)** | Executable labs + JSON artifacts + unittest + verification blocks are this repo's reproducibility mechanism and are strictly stronger for gating. |
| 10 | Stack rows already decided elsewhere (pytest→unittest, NumPy→stdlib, TS+React→served pages, SQLite→storage module) | **ADOPT existing records** | CLAUDE.md conventions, DR 0005 (lab dependency exceptions), DR 0010 (workshop delivery), deferred `storage` module. No new decision needed; pointers ratified. |
| 11 | Statistical protocol standards (holdout splits, bootstrap CIs, blind pairwise + Bradley–Terry, threats-to-validity notes) | **ADOPT as program** | Queued concretely: T17 (formal bake-off), T18 (MAP-Elites comparators), T19 (learner ablation), T20 (pairwise protocol, owner-gated data). Adoption means the protocols run, not that past Stage-0 results are invalidated — they remain honestly scoped. |
| 12 | REUSE `LICENSES/` repository structure | **ADOPT → queued (T21)** | SPDX ids already live in the provenance ledger; the REUSE layout completes the machine-readable story. |
| 13 | ADR verb set adopt/defer/watch/reject | **REJECT (cosmetic)** | The shipped card verbs stand; "defer" ≡ "watch (+queued task)". |

## Consequences

- The fork is closed: RUN ONE's SLIP shape is the ratified baseline; every
  RUN TWO idea is either rejected with a reason or queued with a task id.
- `audits/TODO.md` remains the single development queue; this record is
  its design-authority companion for anything RUN TWO proposed.
- Future schema changes cite this record plus their T3/T4/T6/T7/T15
  task instead of re-arguing the historical documents.

## Sources

- `audits/audit-devspec.md` (addendum A0–A6), `audits/TODO.md` (T14)
- `.depreciated/01-design.md`, `.depreciated/01-formatted.md`, `.depreciated/01-research.md`
- `.depreciated/02-design.md`, `.depreciated/02-research.md`
- `research/slip/slip.schema.json`, `research/grid_genome/grid_genome.schema.json`
- `research/decision_records/0005-declare-lab-dependency-manifest.md`, `0010-start-mecha-workshop-build-track.md`
