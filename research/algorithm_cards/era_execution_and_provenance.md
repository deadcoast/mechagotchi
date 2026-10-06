# Era execution inputs and recorded provenance

## X5 local closure (2026-10-06 UTC)

Full 20261006T025926-d1272de7 passed **2,983 tests / 24 suites**, 2 documented DR0034 zlib skips, 2307 JSON artifacts valid, with zero source mutations.
X5 immutable inputs, ordered admission provenance and explicit reproduction are locally
complete. Source acceptance: 13 checks; relocated native acceptance: 20 checks across
12 executable invocations, including two normal Windows SDL launches. Full measured
findings, retained failures and review repairs are in
`research/experiment_reports/2026-10-06-reproducible-era-inputs.md`;
`data/game_client/era_execution_stage0.json` binds the delivered artifact and sources.

Resume from `.development/x5/resume.json`, `source-final.json` and
`preservation-final.json`. Owner HEAD `d4b4337d0dacbdfa816d990297c03a5da2d0cdca`,
all 144 incoming dirty identities and both live saves are preserved. Existing TODO X6
is next; review/preregister in fresh context before RED. No repeated X4/X5 sweep,
Git mutation, remote executor or exact-published-SHA CI result is implied.


Application evidence/storage/reproduction adapters, not a new scientific algorithm.
Capture exact ordered effective inputs and independently retained source bytes before
the real engine call. Preserve model key order through encoded byte payloads; retain
historical metadata meanings. The actual verdict branch supplies ordinal admissions.

Existing ledger schema v2 adds immutable blobs/manifests/occurrences. Historical rows
stay exact; absent historical evidence stays unavailable. v3 preparation/pending results
retain sources and execution through failure/retry without another evolution.

Reproduction validates retained bytes and supported runtime/calibration identity, then
compares the full report and every complete elite record. Readouts never simulate;
explicit reproduction never changes Keeper history or original footage. Ambiguous
source/descendant links remain ambiguous. Scientific adoption thresholds are unchanged.

Status: locally verified implementation. Exact closure and retained failures are above; results live in
research/experiment_reports/2026-10-06-reproducible-era-inputs.md and DR0084.

## Sources

- docs/development/cycle-38-immutable-era-inputs.md; sunsetted/TODO.md X5.
- research/decision_records/0016-evolve-founder-grids.md; 0022-storage-module.md; 0074-original-best-elite-recording.md.
- labs/game_loop/campaign_store.py; labs/runtime_integration/mecha_engine_runtime_loop.py.
- packages/mecha_engine/src/mecha_engine/{runtime/evolve.py,storage/store.py}.
- game/src/mecha_game/{campaign,era_plan,campaign_recovery,execution,app,contribute,era_review,recorded_review,repertoire}.py.
- .development/x5/baseline.json; .development/x4/preservation-final.json.
