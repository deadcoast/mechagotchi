# Decision Record 0084: immutable era inputs and founder provenance

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


2026-10-06, Cycle38 X5. Select the approved retained-input and provenance integration
through the existing engine/storage/client authorities. This decision authorizes
implementation and falsifiable verification; it does not claim passing gates.

Retain exact ordered execution bytes in additive ledger tables and preserve every
legacy table/blob. Observe actual founder admission by ordinal without changing the
scientific result. Preserve the lab's legacy directory arm; prove already-promoted
package size semantics through a separate optional lab direct-founder input.

Use a versioned pending/source format so old clients refuse to discard evidence.
Read supported old ledgers without migration; migrate only through the ordinary writer.
Make cache identity content-sensitive and preserve corrupt/conflicting cache evidence.

Expose recorded provenance and explicit full-result reproduction. Missing historical
inputs or unsupported runtime/calibration identity produce an honest unavailable state.
Never replace original best-evaluation footage or infer ancestry from niche/morphology
or duplicate IDs. Keep incumbent scientific controls and all negative findings.

Local closure requires the preregistered complete checks. Publication, cloud CI,
remote setup and Git mutations remain separate owner actions.

## Sources

- docs/development/cycle-38-immutable-era-inputs.md; sunsetted/TODO.md X5.
- research/decision_records/0016-evolve-founder-grids.md; 0022-storage-module.md; 0074-original-best-elite-recording.md.
- labs/game_loop/campaign_store.py; labs/runtime_integration/mecha_engine_runtime_loop.py.
- packages/mecha_engine/src/mecha_engine/{runtime/evolve.py,storage/store.py}.
- game/src/mecha_game/{campaign,era_plan,campaign_recovery,execution,app,contribute,era_review,recorded_review,repertoire}.py.
- .development/x5/baseline.json; .development/x4/preservation-final.json.
