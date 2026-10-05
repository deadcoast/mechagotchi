# Development TODO - Cycles 30-32: connected Keeper and recorded history

Cycle 29 S1/S2 are locally complete and reviewed. Archive:
`sunsetted/complete/TODO/29/TODO.md`. S2's single full gate
`20261004T173915-19f22122` passed 2,537 tests / 24 suites with two documented
skips, 2,276 valid JSON artifacts and no source mutations.

- [x] **T1 - Recorded era review as a player surface.** Locally complete. Browse outcomes,
  progression facts and weather after restart while companion care is paused;
  return to the current covenant/next era through established controls.
  Contract: `docs/development/cycle-30-era-review.md`. Use stored engine facts;
  preserve all prior science and incumbent/default policy boundaries.
  Report: `research/experiment_reports/2026-10-04-era-review.md`; 11 targeted
  checks and 14 actual native/source checks passed. Focused runner
  `20261004T181301-70fcba95` passed 666 tests / 2,279 valid JSON artifacts with
  no source mutations. Full run `20261004T181855-269f5dbc` passed 2,548 tests /
  24 suites, two documented skips, 2,279 valid JSON artifacts and no mutations.
  Reviewed repeated navigation, restart, 24 eras and small windows.

- [x] **T2 - Saved archive browsing and adoption.** Locally complete and reviewed. B opens saved creatures after restart and from the selected T era;
  A uses the current covenant's validation and S2 checkpoints. C controls are
  visible on the first small-window page. Contract:
  `docs/development/cycle-30-saved-archive.md`; report:
  `research/experiment_reports/2026-10-04-saved-archive.md`.
  Focused `20261004T185147-cb5b0431`: 769 tests / 2,282 valid JSON, no mutations.
  Final candidate: 22 application checks, four native launches, 13 source pygame
  flows on both policies / 24-era histories. Full `20261004T185738-2f3b4168`:
  2,563 tests / 24 suites, two documented skips, 2,282 JSON, no mutations.
  Additional adoption review passed 12 checks / six native launches / six
  source flows; covenant unchanged, invalid selections refused, both policies
  survive adoption/restart and incompatible-policy refusal.

- [x] **T3 - Saved replay review.** Locally complete and reviewed. Source scope from
  DR 0021/0022/0023: reopen recordings after restart/from selected era reports,
  preserving provenance and stating missing/corrupt recordings explicitly.
  Contract: `docs/development/cycle-30-saved-replays.md`; report:
  `research/experiment_reports/2026-10-04-saved-replays.md`.
  Observed 17 application checks / six native launches / eight source pygame
  flows (72 rendered frames), both policies. Focused `20261004T192539-c157294c`
  passed 690 tests. Full `20261004T192757-866fdf0f` passed 2,576 tests / 24
  suites, two documented skips, 2,283 JSON, no mutations. Final runner closure:
  `.development/t3-closed.json`; no further scope is started.

Use the existing workflow in the authoritative repo and .venv. No Git mutations.
Do not repeat unchanged completed gates. Native keyboard remains blocked by the
missing node_repl/@oai/sky runtime; do not seek an alternate control route.

T1-T3 are locally closed and reviewed. The next explicit delegation selected
one source-backed integration milestone after observing lost preparation:

- [x] **T4 - Durable next-era preparation and completion.** Locally complete. Keep explicit
  contributions, weather and covenant decisions across restart; finish an era's
  saved result once after interrupted persistence; show real founder outcomes
  through the existing connected play loop. Contract:
  `docs/development/cycle-30-durable-era-plan.md`; report/code handoff:
  `research/experiment_reports/2026-10-04-keeper-loop.md`. Fourteen targeted
  tests and 25 application checks (ten native launches, nine source flows /
  71 frames, tiny eras) pass. Focused `20261004T201806-79255b52`: 704 tests.
  Full `20261004T202052-aaa63dd1`: 2,590 tests / 24 suites, two documented
  skips, 2,286 valid JSON artifacts, no mutations. Closure:
  `.development/t4-closed.json`. No new scientific mechanics, default adoption
  or separate player panel. All four contracted Cycle 30 tasks are locally closed.

No further feature list is created. No Git or publication action is authorized.

The established-remainder review and consolidated product checkpoint are in
`research/experiment_reports/2026-10-04-keeper-loop.md`. It distinguishes
future engine recording/family consumers, optional polish and DR 0035's owner
hosting decision from the four met contracts. Offline simulation was explicitly
dispositioned by the earlier five-notices audit; it is not a new requirement.
No next RED or competing process has been started.

- [x] **T5 - Measure and keep era computation responsive.** Locally complete. Direct delegation
  after T4 closure: bounded normal and earned larger-era source observations;
  fix only demonstrated blocking, preserving deterministic results and T4 saves.
  Contract: `docs/development/cycle-30-responsive-eras.md`.
  Report: `research/experiment_reports/2026-10-04-era-responsiveness.md`.

  T5 implementation/source/native observations and preservation are complete.
  Focused `20261004T213006-5d5985a6` passed 784 tests / 2,288 JSON, no mutations.
  Closing review added only the uncovered cold-load close check (both policies).
  Full `20261004T214405-8fe7b9f8` passed 2,606 tests / 24 suites, two documented
  skips and 2,288 JSON artifacts without mutations. Closure and exact restart:
  `.development/t5-closed.json`, `.development/t5-live-handoff.json`. All five
  accepted Cycle 30 contracts are locally closed; no next scope or Git action.
  The T5 report consolidates the current build and established design remainder.

## Cycle 31 - Original evaluation review

- [x] **U1 - Original best-elite recording and playback.** Locally complete. Parent selected one
  final best elite per era. Capture actual evaluation, explicit provenance and
  unavailable other selections; preserve science, T4 journal and T5 cancellation.
  Contract: `docs/development/cycle-31-original-recordings.md`.
  Report: `research/experiment_reports/2026-10-04-original-era-recordings.md`.
  Morphological family/hosted sharing remain separate. No Git mutations.

U1 focused `20261004T224313-a113b1ed` passed 895 tests. Full
`20261004T224746-6ccc82b0` passed 2,624 tests / 24 suites, two documented zlib
skips and 2,290 valid JSON artifacts with no mutations. Actual observations:
33 connected checks, eleven native launches, 25 source flows / 1,365 frames.
Closure: `.development/u1-closed.json`; exact restart:
`.development/u1-live-handoff.json`. Read-only `develop --status` is next;
do not rerun unchanged gates or start another RED. The U1 report distinguishes
the completed recording seam from family/hosting scope and measured limits.

## Cycle 32 - Recorded niche history

- [x] **V1 - Recorded niche history and campaign story.** Locally complete. Parent selected exact
  saved seven-axis occurrences across eras and recorded predecessor campaigns;
  preserve missing/incompatible history explicitly, current-covenant adoption
  and U1 replay provenance. Contract: `docs/development/cycle-32-niche-history.md`.
  Report: `research/experiment_reports/2026-10-04-niche-history.md`.
  No E5 projection, inferred founders, new mechanics or Git mutations.

V1 focused `20261004T234239-c31e7659` passed 740 tests. Full
`20261004T234803-5750f659` passed 2,636 tests / 24 suites, two documented zlib
skips and 2,292 valid JSON artifacts with no source mutations. Demonstration:
21 checks, four native launches, seven source flows / 59 frames over 24 actual
tiny eras, three linked campaigns and 204 elites, on both policy fixtures.
Closure: `.development/v1-closed.json`; restart: `.development/v1-live-handoff.json`.
Next: read-only `develop --status` and review this result. No active worker, next
RED or Git action. E5 projection, new mechanics and hosting remain deferred.

## Cycle 33 - Connected import inboxes

- [ ] **W1 - Select and apply named covenant/pack files.** Current delegation
  authorizes development after V1 review. F15's named picker remainder closes
  the observed F16 pack-to-covenant disconnect. Contract:
  `docs/development/cycle-33-import-inboxes.md`. Preserve all prior results,
  native builds, live saves and scientific definitions. No Git actions.
