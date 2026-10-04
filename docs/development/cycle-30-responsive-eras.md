# Cycle 30 T5: measured era responsiveness

Preregistered 2026-10-04 after T4 full closure and a direct product-readiness
delegation. Use the authoritative repo/.venv; preserve owner edits, saves and
scientific controls. No Git mutations or alternate source checkout.

REVIEW first: observe the actual pygame event loop with normal ERA_CONFIG
(6 generations x 16 candidates, two damage cycles, 16 ticks), then a larger
configuration earned by that real campaign (at most 12 x 32 candidates).
No fabricated unlocks. Bound each subprocess at 90 seconds and 512 MiB working
set; stop and record a limit hit rather than extending the workload. Record
actual evaluation counts, frame/event gaps, input handling, result/seed/history
and save integrity. Source SDL-dummy interaction is distinct from native keyboard.

If no defect is demonstrated, report the measurements and stop this investigation.
If event pumping blocks, make the existing foreground app responsive without a
new panel or scientific speed shortcut. Any optional observation/cancellation
seam must preserve seeded engine output byte-for-byte when uncancelled, retain
scientific controls, and follow lab/package parity. Progress must report actual
phases or completed work, never invented percentages. Cancellation/quit must
preserve staged inputs, campaign history, companion state and T4 completed-result
recovery; no detached worker may survive the foreground invocation. Pause care
and reject conflicting mutation inputs while computation owns the campaign.

Before RED, finish the measured defect report and specify the chosen bounded
execution/cancellation contract here. Test normal completion parity, observable
progress, input responsiveness, cancellation and shutdown, recovery faults,
conflicting inputs and both learning policies. Preserve baseline observations.
After executable changes, use focused iteration and one full closing gate on
final source; do not rerun unchanged T4 gates. Inspect actual app rendering and
source event flows, build the changed native client, and retain the native
keyboard limitation. Record exact commands, metrics, limits and next action in
research/experiment_reports/2026-10-04-era-responsiveness.md.

## Measured defect and implementation contract (before RED)

Actual bounded baseline: normal event gap 9.327s / larger 11.866s; Help waited
9.221s / 11.760s. Both eras saved correct consecutive seeds, 96 / 384 actual
evaluations and no pending journal. Actual worker peaks 64.555 / 75.043 MiB.
The first probe mistakenly sampled the Windows venv launcher; its preliminary
files remain, but only the corrected worker measurement is authoritative.

Use a single foreground-owned non-daemon computation thread for an explicitly
requested era. The main thread waits in a restricted pygame event/render loop,
keeping the existing paused panel and casing: real loading/computation/save
phases plus completed candidate counts. No new screen, engine acceleration,
percentage estimate, persistent worker, process service or unattended work.
Headless --eras keeps its existing synchronous contract. Main-thread-only pygame.

Promote a lab-proven optional progress_callback(completed, budget) on evolve:
zero before evolution and one notification after each candidate is fully
recorded. Fresh integer values only; callback exceptions propagate. None and an
observational callback must produce identical complete results, seeds and inputs.
Early extinction reports actual work below the budget, never invented completion.

Escape cancels before commit; F1 toggles busy help (Escape closes it first).
Close requests cancellation and then quits after the worker joins. Other play,
era, covenant and save inputs received while busy are consumed without execution
or later replay. Care, queued actions, replay and clip time remain paused. Cold
model loading has a cooperative boundary after loading; cancellation may wait
for that phase, with truthful status and continued event/render service.

Before T4 journal begin, cancellation discards only the isolated computation and
keeps preparation, seed, ledger and campaign state unchanged. The commit boundary
is atomic with cancellation acceptance. Once saving starts, cancellation cannot
discard the real completed result; close waits for that persistence attempt,
retaining T4 retry/restart semantics on failure. A finally path cancels and joins
on rendering/event exceptions, so no worker outlives the foreground call.

Observe normal/larger frame and input gaps <=0.5s under the stated resource
limits, actual progress counts and exact baseline report hashes. Do not infer
responsiveness for every unlocked maximum from this bounded study. Measure
cancel-to-stop separately for cold loading and active evaluation; preserve failed
or slow observations. Unit tests pin commit races/faults, event ordering, close,
mutating-input refusal, completed-result recovery and both policies. No old
acceptance threshold is weakened to accommodate concurrency.

Visual check before final RED: an E input received before the first ordinary
paint must still show the held companion/HUD during work, without advancing its
life or clip clock. Preserve the original blank-first-paint screenshots.

Already retrieved controls after E must retain their order: F1, Escape and
window-close are delivered to the restricted waiting loop. Duplicate E/care/
preparation inputs in that same batch remain ignored. A submitted close must
never be discarded merely because E preceded it in the SDL batch.

Closing review additionally pins a window close while model loading is blocked:
for both policies the main thread must continue painting, accept cancellation
before loading returns, join after the cooperative boundary, and preserve all
saved inputs. This is a bounded synchronization check, not a workload benchmark.
