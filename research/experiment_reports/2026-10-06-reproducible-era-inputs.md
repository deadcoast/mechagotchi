# Cycle 38 X5: reproducible era inputs and released-founder provenance

## X5 local closure (2026-10-06 UTC)

Full 20261006T025926-d1272de7 passed **2,983 tests / 24 suites**, 2 documented DR0034 zlib skips, 2307 JSON artifacts valid, with zero source mutations.
The exact command was .venv/Scripts/python.exe -B -m mechas_cli.app develop
--verify full, with PYTHONPATH=tools/mechas_cli/src and PYTHONIOENCODING=utf-8.
.development/x5/full-invocation-02.log and the run summary/result retain the
complete output. The supported ENHANCE/POLISH transitions use this same current pass.

The final Windows artifact is game/dist/x5-immutable-era-inputs-02/Mechagotchi/Mechagotchi.exe (keep its whole directory).
EXE SHA256: bdb47839a0e74dceabf525040b193ad8c2b3a6c74b5dda56ea562e2c4801e6ba.
Its 353 manifest-covered payload files plus artifact-manifest.json
make 354 files / 61880086 bytes in the full folder.
Measured artifact: data/game_client/era_execution_stage0.json.

Final acceptance passed 13 source checks and 20 relocated native checks. Twelve actual
executable invocations include two normal Windows SDL launches. Every weather mode
(calm, stable_soup, storm, real, callback) matches its complete recorded report and
all ordered elite records. Source-to-frozen reproduction also matches after original
input paths were moved. The separate 73-frame W -> E -> recorded descendant ->
restart -> D source journey preserved every Keeper byte. Source events, native
processes, OS keyboard interaction and human usability remain distinct; the latter
two are not claimed.

All identified independent review findings are closed: exact typed JSON bindings,
report admission consistency, ordered elite input fidelity on restart, declared versus
loaded-code identity, imported base covenant source retention, and per-era covenant
binding when saving history after import. The unchanged exact restart comparison and
83 core regression controls pass; 22 storage, 86 runtime/28 package-runtime and 12
client controls have retained focused evidence. All failed diagnostics remain under
.development/x5, including superseded build01 and the faulty first footage path check.

Final preservation/diff evidence is .development/x5/preservation-final.json;
.development/x5/source-final.json and resume.json record the exact restart state.
The owner HEAD d4b4337d0dacbdfa816d990297c03a5da2d0cdca, all 144 incoming dirty-file
identities, historical evidence and both live-save hashes are preserved. Authorized
source changes are listed; other baseline bytes remain unchanged. No commits/sync/push,
registered remote executor or exact-published-SHA Windows/Ubuntu CI is claimed.
X5 is locally complete. Existing TODO X6 is next; review and preregister its scientific
operator contract in fresh context before RED. Do not repeat the completed X4/X5 gates.


## Why

Existing saves preserve scientific reports and original recordings, but do not retain
all ordered execution inputs. ID-only repair-cache keys miss changed corpus contents;
legacy founder rows omit duplicate-ID occurrences. X5 closes that approved application
and engine-evidence gap without new scientific mechanics or default promotion.

X4 closed on full 20261006T015224-25e2b473: 2,919 tests / 24 suites, two documented
DR0034 zlib skips, 2306 JSON artifacts valid, zero source mutations. Its first failed
full and repaired report-page evidence remain retained. X5 baseline records the actual
source root, owner HEAD d4b4337d0dacbdfa816d990297c03a5da2d0cdca, 4292 source files
and 144 incoming dirty identities. All Git actions remain the owner's.

## What is preregistered

Read cycle-38-immutable-era-inputs.md for the falsifiable contract. Existing storage
owns additive immutable blobs, manifests and ordered admissions. The lab-proven
observer captures actual verdicts without changing RNG or scientific reports. The
client captures raw/effective bytes before the call, persists them in the completion
transaction/journal, and reproduces complete saved outputs in a disposable context.
Native provenance and explicit reproduction reuse paused readers and joined workers.

## Findings and verification

Implementation follows supported REVIEW -> REPAIR registration. The source acceptance
command `.venv/Scripts/python.exe -B labs/game_loop/verify_era_execution.py source
--output .development/x5/application-02` passed 13 checks, including two connected
source-SDL reading/reproduction flows. The complete report and all ordered elite
records match after moving the actual copied corpus, covenant, readability model and
released files. Original footage is verified by the existing indexed recording reader;
all Keeper bytes remain unchanged. The prior application-01 report remains: its lone
failure was the instrument's incorrect `original_recordings/` directory assumption,
corrected to the actual verified `replays/` authority without lowering acceptance.

The separate client journey `.development/x5/client/source-journey-01/result.json`
uses actual native-source W -> E staging/evolution, records one admitted and one
refused release, selects a report-supported descendant, restarts after withdrawing
release files, and explicitly runs D reproduction. All 73 rendered frames, selected
occurrence evidence, screenshots and before/after Keeper hashes are retained.
These are source event and pixel observations, not OS keyboard automation.

### Actual RED/GREEN commands

All commands use this repository's `.venv/Scripts/python.exe -B`.

| Scope | Command after interpreter | Retained evidence |
| --- | --- | --- |
| Storage | `-m unittest discover -s labs/game_loop -p test_execution_store.py -v` | storage/red-01.txt: 13 tests, absent schema/API failures. green-01.txt: 13 pass. Independent contradiction control red-review-02.txt: 18 tests, 4 failures/4 errors; green-review-02.txt: all 18 pass. |
| Storage preservation/parity | `-m unittest discover -s labs/game_loop -p test_campaign_store.py -v`; same with `test_package_storage_parity.py`; `-m unittest discover -s packages/mecha_engine/tests -p "test_storage*contract.py" -v` | storage/handoff-02.json: 11 legacy, 3 parity and 11 package tests pass (including nested 18 execution probes); source/log hashes retained. |
| Runtime observer | `-m unittest discover -s labs/runtime_integration -p test_admission_observer.py -v` | runtime/handoff.json: pre-source full output pins, initial RED 10 tests with absent seams, portable-pin RED, lab-before-promotion 3 pass and observer 11 pass. |
| Runtime compatibility | `-m unittest discover -s labs/runtime_integration -p "test_*.py"`; package runtime contract command in handoff | 86 runtime-integration and 28 package runtime tests pass. |
| Game evidence/cache | `-m unittest discover -s game/tests -p test_execution.py` | game/red-02.log proves missing APIs and stale same-ID/content cache; green-03.log records 14 expanded controls including five weather modes. Further review repairs have separate runs. |
| Client | `-m unittest discover -s game/tests -p test_execution_client.py` | client/red.stderr.log: six absent APIs; green-01: six pass; green-02 retains unfinished runtime dependency failure; green-03: eleven pass including worker cancel/join, read-only ledger and corruption visibility. |

The runtime's first portable output pin incorrectly included the generated temporary
workshop path. The instrument now asserts that actual path separately and normalizes
only the known fixture-path field for portable hashing; complete observed/plain
outputs are compared at the same path. Both original RED and raw outputs survive.
The first game RED had an invalid test fixture key, corrected to actual
`cell.mutation_weight`; later Windows Temp cleanup failures were corrected by closing
SQLite handles, with every acceptance assertion retained.

### Independent review repairs and delivery identity

Storage initially accepted coherently rehashed founder verdicts contradicting the
report. Both writer and reader now bind ordered admitted IDs and rejection records,
including None-versus-empty report presence; synthetic storage tests alone had not
covered this semantic link. The original review probe and new RED remain retained.

An existing exact completed-era/restart test then caught input key-order loss through
legacy canonical elite storage. New evidence additionally retains the ordered full
elite output bytes, binds their decoded values to the old elite records and uses them
for subsequent founder inputs. Existing result assertions remain unchanged. Old
ledgers retain their historical behavior and absent evidence.

Review also identified raw imported-covenant provenance loss and loader-code identity
that could describe changed files while the process retained older functions. Those
repairs and independent re-review are pending at this dated checkpoint. No passing
artifact/full gate is claimed until their measured outcomes are recorded below.

The packaging RED `delivery/red-metadata-01.log` failed earlier than anticipated:
`importlib.metadata.version('mecha-engine')` was absent in the source environment,
not merely the frozen bundle. The player now ships the actual engine pyproject
as a manifest-covered resource. Execution identity uses declared project metadata
and engine code identity; it does not invent an installed distribution or install one.
Raw declaration bytes are retained separately from the effective execution payloads.

## First complete sweep and journal compatibility control

Full `20261006T023914-6aa24357` completed 2,983 tests / 24 suites with two
documented DR0034 zlib skips, 2307 valid JSON artifacts and zero source mutations.
Exactly one assertion failed: the old original-recording journal control expected
v2 from a result that now also contains immutable execution evidence. The
preregistered X5 contract requires v3 for that result; all other 626 game tests
and every other suite passed. The full RED remains intact under its run directory.

The scoped correction changes only
`game/tests/test_original_recordings.py::test_pending_original_journal_is_versioned_against_legacy_data_loss`.
It explicitly tests both current execution-plus-recording v3 and historical
recording-only v2. The latter fixture omits execution before journal/ledger creation;
it never removes stored evidence. Both arms retain recording interruption,
no-resimulation retry and idle-v1 assertions, and add exact execution/footage bytes,
recorded pointer SHA, prior-era evidence and read-only replay preservation checks.
No product code, scientific threshold or native artifact changes for this correction.
Focused GREEN passed 41 tests in 59.979 seconds across `test_original_recordings`,
`test_era_plan` and `test_campaign_recovery`. Actual command:
`.venv/Scripts/python.exe -B .development/x5/game/run_recording_regression.py`.
The exact command/log and before/after hashes are retained under
`.development/x5/game/recording-regression-09.log` and its handoff. A fresh full
remains required. Artifact02 and all runtime source hashes are unchanged.

## Preservation and remaining gates

Keep old rows/text blobs/footage bytes/hashes, explicit unavailable historical inputs,
R3 default refusal, separate E5 families/niches/genetic declarations/cared lives, and
original versus recomputed footage. No original recording pointer is replaced by
reproduction. No remote executor or exact-published-SHA cloud result is claimed.
Focused verification is iteration; X5 requires integrated acceptance and closing full,
artifact parsing, preservation/diff checks before local completion.

## Sources

- docs/development/cycle-38-immutable-era-inputs.md; sunsetted/TODO.md X5.
- research/decision_records/0016-evolve-founder-grids.md; 0022-storage-module.md; 0074-original-best-elite-recording.md.
- labs/game_loop/campaign_store.py; labs/runtime_integration/mecha_engine_runtime_loop.py.
- packages/mecha_engine/src/mecha_engine/{runtime/evolve.py,storage/store.py}.
- game/src/mecha_game/{campaign,era_plan,campaign_recovery,execution,app,contribute,era_review,recorded_review,repertoire}.py.
- .development/x5/baseline.json; .development/x4/preservation-final.json.
