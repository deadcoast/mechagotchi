# W3 - constrained hatch preview and saved origin

2026-10-05. Cycle 35, DR0078. Continued in the requested source tree and its
existing Python 3.13.9 environment at owner HEAD 64bea16f10c8. No agent Git
mutations, environments, source mirrors, security changes or unattended services.

## Application result

H now pauses care and shows the actual generated founder under the active
covenant, including one imported through I. Enter explicitly replaces the
current companion with that displayed candidate; N requests another; H/Escape
returns without adopting. O reopens the saved companion birth genome and its
recorded origin after restart. Both incumbent and experimental qtable retain
their selected policy. R3's default-adoption refusal remains unchanged.

Space plays/pauses the engine's animation, comma/period step, and brackets select
permitted clips. These are render_packet_v2 frames with no lifecycle state,
not a life simulation. The first page exposes replacement consequences and
controls; later pages show recorded parent, accepted/attempted proposals, seed,
generation and every field returned by explain_generation. No value or event is
reconstructed. Missing trace metadata remains explicitly unavailable. F1 pauses
playback; paging does not reset as animation advances. O writes no new schema.

Adoption rechecks the campaign state and exact covenant snapshot, then constructs
the candidate through the existing initial_state gate before checkpointing.
Failures preserve the candidate/old companion or follow the existing paused
Ctrl+S recovery when the new in-memory session's save fails. Closing-event
batches and repeated Enter/N keys cannot leak care or unintended rerolls.

## RED, repair and measured application checks

Preregistered cycle-35 contract and workflow registration before RED:

```powershell
& .\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_hatch_preview.py -v
```

Original RED: 8 tests in 2.467s, 7 failures / 3 errors (subcases), captured in
`.development/w3-red.log`: H saved a replacement before confirmation, O had no
reader and the pure view did not exist. Initial GREEN: 8 tests / 1.857s. Expanded
and final GREEN: **13 tests / 2.935s**. Save-failure tests intentionally print
the original/new save lock diagnostics; these are observed recovery cases.

The first demonstration stopped at screenshot export because the harness
converted a relative path against an absolute root. Its log/image are retained
in `.development/w3-demo.log` / `w3-ui`. Only path normalization changed. No
application failure or acceptance threshold was hidden. The packet test's key
was corrected from `clip` to the documented `animation` before implementation's
first GREEN. Contract wording was clarified to attribute the consumer selection
to the direct delegation; F8 defines the existing trace and WFC boundary.

```powershell
& .\.venv\Scripts\python.exe -B game/build_release.py --dist game/dist/w3-hatch-preview-final --work .development/w3-final-build-work --windowed
& .\.venv\Scripts\python.exe -B labs/game_loop/verify_hatch_preview.py --fixtures .development/w3-final-demo --screenshots .development/w3-final-ui --bundle game/dist/w3-hatch-preview-final/Mechagotchi/Mechagotchi.exe --output .development/w3-observed-final.json
```

**48 application checks passed: 10 source pygame flows, 208 rendered frames,
four separate native load/resume launches.** Both policies cover cold preview,
animation/help/cancel, named import -> preview -> adoption -> restart -> full
origin paging, absent provenance and failed-new-save retry. Maximum observed
source polling gap: **0.0505134s**. All rendered lines fit. The view/adopted genome
and explanation match direct fixed-seed generation exactly; both policies share
the same grid and trace hashes. Read-only paths retain every fixture file byte;
the import inbox remains unchanged and no evolution-model cache is created.

Native launches load the source-adopted hatch and resume it while retaining its
exact grid, trace and policy; they are process/save checks, not native keyboard
automation. Source keyboard behavior is injected through pygame's real event
loop. Visually inspected final import/summary, resumed origin, unavailable trace
and save-failure screens at scale 16. Small scale 1 is covered by source tests.

Native candidate: `game/dist/w3-hatch-preview-final/Mechagotchi/Mechagotchi.exe`,
with adjacent `_internal`. SHA256:
`455d67a060144653b2b4b839c3f7c2bd277909abab0ac28c2363a35d69eb361f`.
The metric artifact includes exact source hashes and a reusable generated grid,
covenant and explanation example: `data/game_client/hatch_preview_release_stage0.json`.

## Local verification and preservation

Focused `20261005T130101-77bfb545`: **875 tests**, game 415 / package 324 / CLI 44 /
game-loop lab 92, 2,297 JSON artifacts, no mutations. Later discovery text, final
summary and artifact additions are covered by the closing full run below.
Full `20261005T130951-59a1cc56` passed **2,679 tests / 24 suites**, 2 documented DR0034 zlib skips; **2298 JSON artifacts valid**. No source mutations; local completion only.

```powershell
$env:PYTHONPATH = (Resolve-Path tools/mechas_cli/src).Path
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify focused
& .\.venv\Scripts\python.exe -B -m mechas_cli.app develop --verify full
& .\.venv\Scripts\python.exe -B .development/w3-audit.py
git diff --check
```

The full pass supplies the current passing check for the final POLISH transition;
no duplicate unchanged sweep is needed. Narrative closure updates are outside
the executable/contract fingerprint, and the final audit reviews them separately.

Preservation: all 3,346 prior lab/data files, 77 engine files, 42 existing game
tests, 20 prior native executables and two live keeper files retain their hashes.
W2's closed report/card/decision are unchanged. The only existing code changes
are app.py and footer.py, plus the new pure generation_view consumer. No engine,
lab algorithm, existing assertion, scientific control or historical metric moved.
Observed source/native hashes remain exact and `git diff --check` passes.
Closure evidence: `.development/w3-full.json`, `.development/w3-preservation.json`,
`.development/w3-closed.json`, `.development/w3-live-handoff.json`. The handoff
records the final HEAD, dirty-file hashes and no active worker. Next action:
read-only `develop --status`, review W3, then preregister any separate WFC trace
scope against its actual lab/package contracts. Commits/sync/push remain user-owned.


## Exact remaining scope

This is the constrained generator consumer. Its historical strategy enum includes
`wfc_style`; that does not make it a WFC collapse trace. WFC is the separate
DR0031 production rich-alphabet generator, whose current code returns only
`wfc_wave_collapsed` without detailed observations. The next source-backed seam
is optional observational collapse/propagation/restart/finish trace capture in
the established lab and package WFC implementation, with identical fixed-seed
outputs and RNG decisions before a separate client consumer. No WFC event is
fabricated here and no WFC instrumentation contract is yet registered.

Per-launch hatch seeds still reset, as F8 documents. Native keyboard/human
usability, maximum scale, remote execution and exact-published-SHA Windows/Ubuntu
CI remain unverified. Parent owns remote setup and single-writer coordination;
no remote executor is configured. Read the closing handoff/status before
registering any further scope; preserve all owner edits and historical evidence.

## Sources

- docs/development/cycle-35-hatch-preview.md
- research/decision_records/0078-constrained-hatch-preview.md
- research/algorithm_cards/hatch_preview.md
- game/src/mecha_game/{app,generation_view,footer,hatchery}.py
- game/tests/test_hatch_preview.py
- labs/game_loop/verify_hatch_preview.py
- data/game_client/hatch_preview_release_stage0.json
- research/experiment_reports/2026-07-12-hatchery.md
- research/decision_records/0031-wfc-generation-adoption.md
