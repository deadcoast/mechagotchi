# Cycle 38 X5: immutable era inputs and recorded founder provenance

Preregistered 2026-10-06 after measured X4 local closure; actual full and preservation
evidence are pinned in .development/x5/baseline.json. Authority: direct
delegation, TODO X5, DR0016/0021/0022/0074 and X1 recovery. Use the requested tree/Python
3.13.9 .venv; record actual root/branch/HEAD and dirty/source identities in .development/x5.
Preserve owner work. No Git mutation, mirror, new environment, security change, unattended
process or credentials.

## Reviewed gap and fixed boundaries

Current campaign inputs preserve ordered loaded objects but discard source identities. Weather
persistence records forecast/snapshot IDs rather than input snapshots. Repair cache keys
contain grid IDs/epochs/seed rather than contents. X3 writes uniquely attributable founders;
duplicate IDs are omitted because v1's primary key cannot distinguish occurrences. Existing
replay tests supply external inputs. Historical W5 evidence remains 2 eras/23 elites/2
replays/0 founder rows; X3's partial improvement does not rewrite that observation or close
X5.

Preserve the exact scientific reports, elite records, admission decisions, RNG consumption,
generator/default arms, calibration thresholds and learned scores. R3 default adoption remains
refused; saved per-life policies and all negative findings survive. Genetic declarations,
morphology families, seven-axis niche occurrences and actual cared lives remain distinct. This
slice changes evidence capture/storage/reproduction, not mutation permissions or care
inheritance.

## Immutable execution bundle

Capture one execution snapshot immediately before the actual evolve invocation. Use those
captured objects for that invocation; do not read input paths again after execution to claim
they describe what ran. Resolve weather exactly once. The effective input encoding is UTF-8
JSON with object insertion order retained; hash the exact encoded bytes. Canonical manifest
JSON may sort its own keys, but must not reorder effective model weights or lists when
reconstructing inputs. learned_readability_score currently sums weights in insertion order.

Execution bundle v1 is a JSON-compatible object with manifest and blobs fields:

- manifest: format=mechagotchi_era_execution_v1; campaign_id; era_index; rng_seed;
  execution_contract; effective_config; inputs; sources; founder_occurrences;
  calibration_sha256; report_sha256; elites_sha256.
- inputs: seed_corpus_sha256; covenant_sha256; generation_model_sha256;
  repair_model_sha256; readability_model_sha256; readability_selection_sha256;
  founder_mode (none/list); founder_sha256 ordered blob-reference list; weather_mode
  (none/list); ordered_weather_sha256 when present. Empty lists are not None.
- blobs: SHA256-keyed records containing media_type and data_base64. Decoding
  yields the immutable bytes hashed by the key. The ledger stores those bytes
  as BLOBs; base64 exists only to transport them in the pending JSON journal.
- sources: recorded roles, ordered corpus/release positions, available relative
  labels and raw-byte digests. Retain raw input bytes when loaded from files,
  including the adopted readability artifact, alongside effective model payloads.
  In-memory inputs are identified as such; never invent a filename or author.

Retain complete ordered seed genomes, actual covenant, GenerationModel payload, actual repair
weights/model metadata, learned weights/reference features and effective selection blend.
Reuse dataclasses.asdict/GenerationModel(**data) and its validator; reproduction never
retrains. Capture preparation's known repair training subset/order/recipe; external models
retain their declared provenance. Keep GenerationModel.metadata.seed_corpus_sha256's
historical IDs-only meaning; add a distinctly named full-content identity.

Retain exact weather payloads: calm=None; stable_soup/storm's ordered generated records;
real/callback's actual loaded records in their execution order. Capture all effective evolve
parameters, including existing defaults and seed arithmetic. Calibration bytes identify
descriptor mode/names/edges, area scaling, fitness weights, calibration status, pressure
constants and generator/admission policies. Use a versioned supported execution contract and
recorded runtime identity. Runtime identity records normalized loaded code-object
content (including constants, flags and exception tables; excluding filenames/line
tables) across the declared execution module closure, plus Python major/minor and
engine version. Source/frozen equivalence must be measured; an unavailable loader
is not a compatibility claim. Calibration globals remain independently captured.
Changed or unsupported semantics/calibration refuse reproduction
explicitly; never silently substitute current constants or modify module globals to replay.

## Ordered founder evidence and shared runtime interface

Lab-first optional evolve(..., admission_callback=None) observes each founder immediately
after the existing admission decision. Call once per submitted occurrence, in input order,
with an isolated dictionary containing submission_index, grid_id, admitted and
rejection_errors (None on admission). Use actual engine errors, including size mismatch.
Exceptions propagate through existing foreground cancellation/error handling. No new
scientific report fields, RNG draws or changed admission algorithm. The legacy lab
workshop-directory arm retains its existing measured behavior. A mutually exclusive
optional lab founder_grids input proves the already-promoted package admission/size
semantics, including duplicate-ID occurrences, without changing that legacy arm.

Game capture joins observer events by ordinal to exact captured genomes. Each founder
occurrence records ordinal, grid_id, grid_sha256, source_kind, source_position, admitted and
rejection_errors; era_elite sources additionally retain available
campaign_id/era_index/niche_key. Repeated IDs remain separate, even with unequal payloads or
verdicts; never deduplicate/reorder to satisfy old storage. Preserve the old founder_records
projection. Declared lineage does not prove release origin; descendant joins use actual
evidence and retain duplicate-ID ambiguity.

## Shared storage interface and migration

Existing mecha_engine.storage remains the sole ledger authority. Add optional record_era(...,
execution=None) and public load_era_execution(conn, campaign_id, era_index) -> bundle | None.
Add pure validate_execution(bundle) -> None for structural/hash/reference/ordinal checks; it
performs no simulation or file I/O. The writer also binds identity/profile/report/elites to
its actual era arguments. Readers verify hashes and all references before returning
independent copies. None means historical evidence was not recorded, never an empty execution.

Schema v2 adds execution_blobs(sha256 PRIMARY KEY, media_type, payload BLOB),
era_executions(campaign_id, era_index PRIMARY KEY pair, manifest_json, manifest_sha256) and
founder_occurrences(campaign_id, era_index, ordinal PRIMARY KEY triple, occurrence_json). Era
tables use the existing era foreign key. Blobs are deduplicated by exact bytes; an existing
hash with conflicting bytes or media type refuses. Manifest-authoritative occurrence
projections must match; no UPDATE/REPLACE of execution evidence. execution_contract is an object with named
contract, runtime identity and policy fields; calibration_sha256 references retained
JSON. Effective input digests always reference blobs, including JSON null where
applicable; source raw-byte references use raw_sha256. Result digests use existing
storage canonical_json UTF-8 bytes of the complete report and full ordered elite list.
Keep ordinary history/query shapes unchanged when execution evidence is absent.

Migration is forward-only additive DDL in one transaction, advancing user_version only on
success; old blobs stay exact and missing execution rows stay absent. New evidence commits
inside record_era with profile/report/elites/unlocks; retain the campaign-status transaction
boundary/recovery rules. Implement lab-first in campaign_store.py and mirror exactly. Update
the source-parity marker without narrowing its region; extend behavior parity while retaining
old-table assertions.

## Journal, old-state acceptance and content-sensitive cache

Execution-bearing pending results use mechagotchi_era_plan_v3 so old clients refuse to discard
fields. Include the complete bundle inside the hashed pending result. Source-bearing staged
preparation also uses v3 before a result exists so older clients cannot discard source
metadata; v3 permits pending=None and validates ordered release_sources alignment. Continue accepting v1/v2
journals; missing inputs stay unavailable. EraPlan.finish commits recorded bytes only, then
follows existing original-footage, state and checkpoint ordering. Retry compares execution
evidence as well as the existing report/elites/profile before treating an already committed
era as equal. Failure retains the pending journal and every conflicting artifact for
inspection.

Export SUPPORTED_READ_SCHEMA_VERSIONS=(1,2). Read-only consumers accept supported
ledger versions 1 and 2 without migration:
campaign_recovery, EraReview and recorded_review must share this policy. Older paired recovery
snapshots remain inspectable/restorable as v1. Migration occurs only through the ordinary
authorized writer. Unsupported future schemas refuse. Old missing inputs are reported as
missing; no fixture/path-based backfill.

Version the repair cache envelope/key from full ordered effective training subset bytes,
available raw-source identities, all trainer options and contract identity. Verify the cached
model digest before use. Changed inputs cannot hit old ID-only entries; preserve those files.
Corrupt/conflicting cache bytes are retained and reported, never silently used or overwritten.
Pin cached/fresh model equality and preserve with_models=False/foreground cancellation;
inspection never trains/writes.

## Reproduction consumer and ownership

Game execution.py also provides inspect_execution(bundle), a read-only structural/
compatibility status without simulation or fixture/model loading. Game execution.py
owns capture_execution(campaign_id, era_index, effective_inputs,
source_records) -> bundle; finalize_execution(bundle, admissions, report, elites) -> bundle;
and reproduce_era(conn, campaign_id, era_index, *, progress_callback=None) -> result.
effective_inputs contains the exact runtime arguments and serialized scorer/model values
listed above. Capture precedes evolve; finalize adds admissions and result hashes. Reproduction
reconstructs models from verified ledger bytes, runs the supported engine in disposable
memory/context, and returns report/elites/full equality. It never consults current
loaders/trainers/releases/live campaign. Missing bytes or unsupported contract gives a named
unavailable reason; inequality is a failed reproduction with diagnostic paths, never a
replacement of recorded results. Result status is matched, mismatch or unavailable, with
the named reason/differing paths and complete reproduced report/elites when available.

Expose an explicit command through the native/source entry: --keeper-dir DIR
--reproduce-era N --campaign-id ID --output NEW_DIR, backed by the same reproduction API.
It opens a read-only ledger, requires a new disposable output directory, writes comparison
and complete recomputed results there, and reports mismatch/unavailability distinctly.
Native era/archive review displays recorded provenance/availability; opening it never runs
simulation. An explicit native Reproduce action runs the same API through the
existing joined foreground worker, with real progress/cancel and a result notice.
Connection ownership stays inside that worker; reading a view never starts it.
Keep existing era-worker defaults/behavior, care pause and same-frame guards.
Reproduction never advances/saves a Keeper. Preserve original final-best footage
and legacy replay labels/hashes; recomputation never writes the original recording pointer
or replaces report/history/care/admission facts. No automatic UI simulation.

Disjoint owners: storage (lab/package/parity); runtime (lab/package observer and
unchanged-output controls); game (execution/campaign/cache/journal/recovery/tests); app
(native review/command/demonstration); lead (registration/report/card/DR/metric/ledger,
acceptance/sole runner). Agree interfaces; no shared-file writers or full sweep while source
writers remain active.

## Falsifiable verification and preservation

Record exact RED then GREEN commands/output; retain each failed run and original diagnostic
artifact under a unique path. Do not overwrite a failed result with success, weaken
assertions, relabel controls or regenerate historical evidence.

1. Changed corpus bytes with unchanged IDs/order misses cache; unchanged inputs
   hit it and equal fresh training; changed/tampered model bytes cannot be reused.
2. Observer off/on yields equal complete reports/elites and unmodified inputs;
   lab/package events match for admission/refusal/size rejection/duplicate IDs.
3. Ordered founders with duplicate unequal payloads/verdicts survive journal,
   commit and restart exactly; None/list semantics and source order are pinned.
4. Record admitted and refused releases; change/remove original input paths;
   reproduce full report and every full elite record from retained bytes only.
   Exercise all five weather modes and trap any default-loader/trainer fallback.
5. Alter/reorder a retained input or corrupt a blob/reference/calibration identity:
   verification/reproduction fails explicitly; original outputs/footage stay exact.
6. Inject migration/era transaction and later footage/state/checkpoint failures:
   rollback or exact retry, retained journal/conflicts, no second evolve call.
7. Populated v1 ledger migration and old snapshot recovery preserve old text blobs,
   rows, footage bytes and recorded hashes; historical missing evidence stays absent.
8. Native release -> admission -> supported descendant inspection -> restart, then
   explicit source/packaged reproduction proves the consumer and ambiguous-link notices.

Close only after independent review, focused controls, source/native demonstrations, full
sweep/artifact parsing, preservation audit and diff review. Register slice
x5-immutable-era-inputs with game/package/lab:game_loop/lab:runtime_integration focused
suites; full retains all suites. Keep code/contract/report/card/DR/metric/ research ledger
together. X4 failures and controls survive untouched. Publication, remote execution, OS
keyboard and human usability claims remain separately evidenced.

## Sources

- AGENTS.md; ONBOARDING.md; CLAUDE.md; sunsetted/TODO.md X5; docs/development/
  local-cycle.md; workflow.json; cycle-38-selected-keeper-creation.md.
- research/reports/2026-10-05-product-design-implementation-checkpoint.md X5.
- research/decision_records/0016-evolve-founder-grids.md; 0022-storage-module.md;
  0074-original-best-elite-recording.md; 0081-keeper-continuity-and-faithful-authoring.md.
- game/src/mecha_game/{campaign,era_plan,campaign_recovery,session,era_review,
  recorded_review,original_recording,niche_history}.py.
- packages/mecha_engine/src/mecha_engine/runtime/evolve.py; runtime/_readability.py;
  generation/model.py; repair/train.py; archive/descriptors.py; archive/scoring.py.
- labs/game_loop/campaign_store.py; test_package_storage_parity.py.
