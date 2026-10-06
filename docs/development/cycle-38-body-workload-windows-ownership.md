# Body workload Windows owned-tree delivery repair

Preregistered 2026-10-06 after full run `20261006T130949-31acbf23` and retained synthetic diagnostics; before the new repair RED tests. This is an operational delivery-instrument correction. The fixed scientific cohort is closed and will not be repeated.

## Evidence and scope

The full sweep completed 3622 tests in 24 suites, with two skips and 2321 valid JSON artifacts. Its sole failure was an unsupported startup-output assertion under a synthetic 0.2-second timeout. The proposed test-only repair retained timeout, cleanup and process-reaping requirements and independently tested successful stdout/stderr retention. That new positive fixture then failed the strict immediate-root-exit ownership check with both the virtual-environment launcher and the same underlying interpreter image. Both failed owner runs and the independent failed run remain unchanged.

A fixed three-probe, 15-second maximum diagnostic completed in 0.7446121 seconds with all owned processes closed. One distinct descendant had exit code 0 but was not yet signaled after its root returned, then disappeared within 10.188 ms. Deliberately long-lived descendants remained active and required termination. This does not establish the exact cause of any earlier individual failure or of the original build guard refusal.

Diagnostic: `.development/body-workload/delivery/job-accounting-diagnosis-01/report.json`, SHA256 241424b54454d42d0c7fc669140cd17bb0eeabf912226b7a07d9aca2ebbae151.

Only `labs/game_loop/verify_body_workload_delivery.py` and its test module may change. The verifier format advances from v1 to v2. The game, engine, evaluator, scientific coordinators, measured source archives, immutable inputs, all prior receipts and the 354-file Windows artifact remain unchanged. No new care pair, original production era, extinction trial, model fitting or selection is authorized here.

## Prospective completion rule

Delivery completion means that the entire owned process tree is empty within the existing work allocation. Root exit alone is insufficient. This prospectively replaces the immediate-root-exit classification for the delivery verifier; it does not reinterpret old failures or change scientific-coordinator semantics.

Compute one total deadline and its existing cleanup reserve when the stage starts. Both root waiting and owned-tree draining use the same work deadline, equal to total deadline minus that reserve. After the root exits, reap/query the owned tree until it becomes empty or the work deadline is reached. Do not grant a separate grace period or extend either deadline. If any process remains, terminate the owned tree, confirm closure inside the existing cleanup reserve, and refuse the stage. Query or cleanup uncertainty must refuse. A stage can succeed only with zero owned processes and closed log handles. Existing per-stage and total delivery budgets remain unchanged.

## RED, GREEN and delivery checks

Before source repair, add deterministic tests for transient owned processes reaching zero within the work deadline, persistent processes exhausting that deadline, no deadline extension or cleanup-reserve consumption, and uncertainty refusal. Retain the actual timeout/reap test and long-lived-descendant refusal test. Exact successful stdout/stderr and exit-code checks must pass through both the repository launcher and the already-running interpreter image. Include an actual short-lived descendant completing while still owned. All fixtures are synthetic stdlib processes; the test driver remains the repository Python 3.13.9.

Retain RED logs, implement the narrow verifier change, and obtain independent exact-diff review. Run the targeted suite, then bind a fresh operational source manifest. Execute one new detached operational verification against the same artifact and same immutable source-era record in a fresh output directory, under the unchanged 480-second total cap. Its reproduction verifies an existing era; it is not a new scientific trial. Preserve any failure without automatic retry. All 45 original delivery predicates must still pass; process closure and artifact/source-save preservation remain required.

Update the final report/metric with the actual operational disposition. Freeze the final verification closure, run the complete DR0062 sweep, then audit all protected files, source archives and artifact hashes. Local completion and scientific refusal remain separate; overall care and population extinction remain open.
