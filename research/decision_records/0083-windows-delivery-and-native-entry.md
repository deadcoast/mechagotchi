# Decision Record 0083: complete Windows delivery and native entry

2026-10-06, Cycle38 X4. Implement the approved complete-application milestone
using the existing pygame player, save/recovery authority and source data.
Target Windows x64 one-directory delivery with explicit manifests, dependency
notices and exact frozen resource resolution. Preserve source developer launch;
do not claim an incomplete standalone wheel is a complete installation.

Place independent read-only save inspection before default asset resolution or
care. Show applicable Resume, backup inspection, guarded Restore/New, directory
selection and retry in a native window even when no companion can be loaded.
Use explicit confirmation and captured save bytes through the existing recovery
authority. Preserve original files; cancel writes no saves. Actual write failures
remain visible. No probe-write establishes entry permissions.

Expose existing native actions with focusable contextual controls and resizable
integer creature pixels. Keep mode/pause/closing-frame/worker lifetime semantics.
Provide isolated public-engine and executable care-to-era examples; separate
observed application, artifact and cloud readiness from historical calibration.

Source tests and staged assets cannot establish standalone delivery. Build and
relocate only the artifact, exercise every advertised weather and creator route,
verify resource/import roots and actual save/review/restart behavior. Source-event
checks cannot establish OS keyboard or human usability. Publication is separate;
the local runner cannot mark exact-published-SHA Windows/Ubuntu CI green.

At registration this decision selects implementation; final local gates remain
pending. The report records actual RED/GREEN and subsequent gate outcomes.

Artifact-verified bounded checkpoint (2026-10-06): the new windowed build passed
241 detached checks across 43 actual executable invocations, plus four Windows SDL
launches and the source connected visible-control/adoption/restart journey. Exact
source/content IDs and evidence are in data/game_client/windows_delivery_stage0.json
and the report. X4 full sweep/closing preservation remain pending at the parent's
requested handoff; this is not local completion or publication.


## Local closure (2026-10-06 UTC)

Full 20261006T015224-25e2b473 passed **2,919 tests / 24 suites**, 2 documented DR0034 zlib skips, 2306 JSON artifacts valid, with zero source mutations.
Exact completion and JSON artifact counts are recorded in
.development/runs/20261006T015224-25e2b473/summary.json and result.json.
The source invocation was .venv/Scripts/python.exe -B -m mechas_cli.app develop
--verify full, with PYTHONPATH=tools/mechas_cli/src and PYTHONIOENCODING=utf-8;
.development/x4/full-invocation-02.log retains its output. Supported ENHANCE and
POLISH transitions use this current pass. Final source, delivered artifact,
live-save preservation and diff review are .development/x4/preservation-final.json
and final-source-state.json. The 142 incoming handoff dirty identities survive.
X4 is locally complete; the original pre-full handoff below remains dated evidence.
241 detached checks / 43 executable invocations, four actual Windows SDL launches
and the connected source-event journey remain separate evidence. No OS keyboard,
human usability, remote execution or exact-published-SHA cloud CI is claimed.
The complete folder contains 353 files / 61826456 bytes, including the 96496-byte
artifact-manifest.json. The metric artifact_files/artifact_bytes values describe
the 352 manifest-covered payload files and exclude that self-describing manifest.
X5 reproducible inputs is the next approved milestone; Git actions remain the owner's.


## Sources

- docs/development/cycle-38-windows-delivery.md; sunsetted/TODO.md X4.
- data/game_client/windows_delivery_stage1.json.
- game/src/mecha_game/{app,entry,startup,native_ui,runtime_resources,launch_info}.py.
- game/build_release.py; game/release_payload.py; labs/game_loop/verify_detached_release.py.
- .development/x4/{baseline,resume,preservation-final,final-source-state}.json.
- .development/runs/20261006T015224-25e2b473/{summary,result}.json.
