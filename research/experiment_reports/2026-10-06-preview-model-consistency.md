# Selected Keeper preview model consistency

Date: 2026-10-06. Cycle 38, approved X3/X5 integration repair. Locally qualified.

## WHY

The retained previous-slice HTTP probe demonstrated that both live and recomputed
replay previews omitted the compatible workload Keeper's body model. The original
probe substituted engine results and established dispatch only, not physiology.

## WHAT

Registered `preview-model-consistency` before RED in
`docs/development/cycle-38-preview-consistency.md`. Work stayed in the requested
checkout on `phase-l-gate`, owner HEAD `c15bdff771959a5a45ca470429e7327be979dd01`.
Six incoming modifications were preserved byte-exact. Independent backend and
replay implementation lanes, separate browser evidence and independent source/
closing review supported one integrator. The repository has no `.agents/` tree;
the user-home superpowers junction has no target. No new environment or checkout,
memory edits, commits, sync, push or protected-source restoration occurred.

## FINDINGS

- Current Keeper context exposes its validated versioned body model. Both live
  and replay routes resolve it freshly, validate context/model assertions, and
  recheck after simulation. Untrusted fields cannot override authority. Standalone
  remains legacy; supported new-life choices and read-only inspection survive.
- Actual HTTP live reports and recomputed replay frames match explicit-model
  engine outputs on fixed deterministic fixtures. The browser beetle fixture's
  episode need balance was **0.83407 workload-v1 versus 0.838109 legacy**. These
  are software regression observations, not new scientific qualification.
- New recomputed replay IDs use `preview-v2-` and bind full genome, profile,
  repair model, body model and effective options. Workshop preview identities also
  bind context and selected document. Generation/repair training cache remains
  model-independent; no model-sensitive simulation result cache is shared.
- Shared context arbitrates overlapping refreshes, invalidates pending requests
  and displayed previews immediately, and performs a fresh authority read before
  displaying delayed responses. Result/error/settings races and repeated replay
  timers are covered. Model and snapshot provenance are visible. A displayed
  preview is a snapshot, not a continuous observation of future disk changes.
- The original `replay_from_lived` formatter remains exact against entry/HEAD;
  recorded footage keeps its stored model, frames and IDs. Native playback labels
  recorded provenance. Recording publication now preserves existing footage on
  conflict and can finish the same interrupted publication safely. Concurrent
  different-model writers cannot replace one another's saved evidence.

## Verification

Exact retained commands and hashes are in backend-lane-result.json,
replay-lane-result.json, independent-source-review.json and browser-review.json
under `.development/preview-consistency`. The same RED/GREEN commands were:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s workshop/tests -p test_preview_model_consistency.py -v
.\.venv\Scripts\python.exe -B -m unittest discover -s game/tests -p test_preview_replay_identity.py
node --test workshop/tests/authoring_frontend.test.js
node workshop/tests/preview_browser_check.js .development/preview-consistency/browser-03
```

Retained real results:

```text
Backend corrected RED: Ran 11 tests; FAILED (failures=26, errors=1)
Backend GREEN03: Ran 11 tests in 37.095s; OK
Replay RED: Ran 13 tests in 2.195s; FAILED (failures=7, errors=2)
Replay affected GREEN: Ran 55 tests in 45.795s; OK (16 dedicated regressions)
Frontend RED: tests 25; pass 18; fail 7
Frontend final GREEN / independent check: tests 26; pass 26; fail 0
Browser final03: 15 checks passed; JavaScript exceptions []
Focused 20261006T160507-120bd725: 1788 tests / 5 suites; passed; changed_files []
Full 20261006T161657-fb5c2348: 3682 tests / 24 suites / 2 documented skips; passed; changed_files []
```

The registered runner used repository Python 3.13.9 through the retained
`run_preview_gate.py` driver and `mechas_cli.development.verify`; exact full child:

```powershell
.\.venv\Scripts\python.exe -B tools/ci/run_sweep.py --log-dir .development/runs/20261006T161657-fb5c2348
```

The full summary records 2,323 valid JSON artifacts, dependency availability and each suite;
source/result fingerprints and diff checks are retained with the run. Independent
source review reran 53 checks and bound all eight affected runtime files. Two review
findings were repaired: truthful engine profile-refusal feedback, and visible
failed-refresh feedback. Browser evidence covers both models, standalone default,
delayed results/errors, model switches, refresh ordering/failure/unavailable/retry,
settings changes, repeated playback, native-select input, keyboard scrubbing and
narrow layouts. Eleven final screenshots were inspected; isolated endpoints closed.

### Additive Windows delivery and retained failures

Delivered `game/dist/preview-consistency-01/Mechagotchi/Mechagotchi.exe`, with its
adjacent `_internal` and manifest. The source manifest binds the owner HEAD plus
245 exact runtime files, including the uncommitted implementation. Baseline45 and
fixed retained-era reproduction passed; packaged HTTP checks exercised both models
and real physiology, identities, stale/malformed/forged inputs and read-only retries.
The separate native historical lane passed 22 checks and retained footage/ledger
bytes across a current-model switch. Exact final shutdown adjudication, check
counts, artifact hashes and process cleanup are in delivery-closing.json and the
independent review. The 159 accepted operational checks comprise baseline45,
functional HTTP66, historical22 and bounded shutdown26. The failed combined
delivery03 report remains failed; its missing shutdown obligation passed the
separately preregistered probe. No native OS-keyboard or human-usability claim is made.

Failed attempts are evidence, never relabeled: initial backend RED discovery
duplicated imported fixtures; an initial edit script stopped before server install;
a test helper argument collided with a forged nested-context test field. Browser01
mistook structural final_state for physiological need balance; browser02 selected
an incompatible standalone profile. Both were instrument corrections, preserving
the fixture rather than searching seeds. Deliberately canceled HTTP requests can
leave connection-abort diagnostics; final browser had zero JavaScript exceptions.

Delivery01/02 instruments exhausted their process budgets; delivery03 retained its
strict generic zero-exit failure after an intentional external model switch. The
actual native stale-save guard must refuse that write. A separately registered
short shutdown probe and independent adjudication require named refusal evidence,
natural process termination and persisted whole-Keeper before/after hashes; a
generic nonzero exit cannot qualify. The delivery lane's initial assertion that
windowed output omitted stderr was contradicted by the actual recorded guard text
and corrected. No second build was needed for that mistaken inference; all prior
attempts and the exact tested artifact remain retained.

The first short shutdown control also retained a failed initial-to-final equality:
the first Creator opening legitimately attached the companion chronicle to its
existing campaign. Independent diff confirmed that link and backups only; the
post-ready-to-exit inventory was already exact. The corrected fixture primes that
same native one-frame Creator before copying either probe, retaining every strict
assertion. This is fixture initialization, not a relaxed preservation requirement.

The broad premium static scan included dependencies and preserved historical
payloads, so a scoped audit used the existing design ownership. Its eleven button
warnings are parser false positives for the `$` event-handler alias, individually
source-verified by independent review; the preview-page controls were exercised
in browser. The failed raw audit remains recorded. No unrelated UI redesign was
made to satisfy the parser.

## Preservation, disposition and next action

Final protection and source archive/diff evidence live in preservation-final.json,
final-source-manifest.json and final-scoped.diff. The 23,856 protected path entries
include duplicate absolute/relative spellings; no protected file or incoming edit
may differ. Earlier builds, live saves, studies and recorded history remain intact.
Final closing/resume records and independent-closing-review.json govern completion.
The metric is deliberately fixed focused evidence and points to that closing gate;
it does not claim subsequent gates by itself.

Overall care remains **REFUSE**: 9/30 pristine changes, 4/30 morphology changes with
pair28 welfare failure. Extinction remains **OPEN**. Equations, food, full repair,
death limits, cohorts, sampling, criteria and defaults are unchanged. No scientific
study or production-era hunt was run. Legacy body and care-off defaults remain.

This review identified no additional confirmed software defect from the approved
integration queue awaiting implementation. Existing X6 operative qualification,
X7 meaningful care and X8 genuine extinction/progression remain scientific outcome
boundaries, not permission to rerun studies or invent new product scope. Owner
review and Git publication remain separate. Exact-published-SHA native Windows and
Ubuntu CI is unobserved; local completion makes no publication claim.

## Sources

- docs/development/cycle-38-preview-consistency.md
- sunsetted/TODO.md
- research/decision_records/0093-preview-model-consistency.md
- research/algorithm_cards/preview_model_consistency.md
- data/game_client/preview_model_consistency_stage0.json
- game/src/mecha_game/keeper_context.py
- workshop/server/workshop_server.py
- workshop/shared/authoring.js
- workshop/preview/preview.html
- workshop/grid_editor/grid_editor.html
- game/src/mecha_game/replay.py
- game/src/mecha_game/campaign.py
- game/src/mecha_game/app.py
- .development/preview-consistency/closing.json
- .development/preview-consistency/entry.json
- .development/body-compatibility/next-preview-boundary.json
