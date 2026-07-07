# Human Studies Protocol (T10 / T20 — pipelines built, data from humans)

Date: 2026-07-06. The og human studies, specified and tooled so a study
can start the day the owner schedules one. STANDING RULE (unchanged by
any authorization): human data is never fabricated; these pipelines
collect, they do not invent.

## T10 — workshop evaluation studies

Instrumentation (SHIPPED): the workshop server tracks the og metrics
per session — validations, invalid verdicts with per-error counts
(validator-clarity evidence), saves/releases/exports/imports, and the
time-to-first-valid proxy; `GET /api/metrics` reads them and
`POST /api/metrics/flush` persists a provenance-marked session record
under `data/workshop/metrics/`.

Studies (owner schedules; recruits per og):
1. **Semantic-vs-plain editor test** (8 participants): same authoring
   task in the workshop vs a plain pixel editor; success = the semantic
   editor reduces invalid exports by >= 50% (og threshold). Instrument:
   session records per participant per condition.
2. **First-session usability** (>= 5 participants): create one creature
   + one SLIP profile unaided; success = completion <= 45 minutes (og).
   Instrument: session records + observer notes.
3. **SLIP creator pilot** (5–10 creators): success = >= 90% of profiles
   validate within two edits, >= 80% generate a valid companion (og).
   Instrument: slip-creator validations per profile id.

## T20 — pairwise preference studies

Protocol: blind pairwise forced choice (RUN TWO's preference over
rubric scoring — less rater-calibration drift). Pairs are sampled
deterministically from the target corpus; each rater sees anonymized
A/B renders and picks one; results are Bradley–Terry scored
(`labs/readability_benchmark/bradley_terry.py`, stdlib MM algorithm,
tooling-validated on synthetic data clearly marked as such).
Serves: the T17 human panel arm and the CUBFF transducer's preference
gate. The rating tool gains a pairwise collection mode when the first
study is scheduled (recorded remaining tooling).

## Sources

+ `workshop/server/workshop_server.py` (instrumentation), `audits/TODO.md` (T10, T20)
+ `.depreciated/01-formatted.md` (Stage 6/7 metrics), `.depreciated/02-design.md` (statistical standards)
+ `labs/readability_benchmark/bradley_terry.py`

---
