# Cycle 38: qualified native learning rollout

Preregistered 2026-10-06 before RED. This is product integration of the completed
X7 product-learning comparison, not a new experiment or retrospective revision.
Owner checkout remains phase-l-gate at d4b4337d0dacbdfa816d990297c03a5da2d0cdca;
preserve all source work, historical evidence, live saves and previous builds.
Commits, sync and push remain the owner's.

## Evidence and decision boundary

Independent read-only validation checked all 1,500 stage1 chained receipts against
their exact manifest and plan; all 164 source bindings matched at review. Stage0
is retained incomplete/REFUSE. Its exact frozen corpus, founders, covenant and plan
match stage1, all 56 prior rows reproduce, and its 15.608391s debit is included in
stage1's 100.608998s cumulative runtime. No trial or scientific retry is proposed.

The six-decimal per-life welfare sums are 93.688618 follower, 83.867185 incumbent,
83.596818 additive: +11.7106982904% and +12.0719905870%, exceeding the unchanged
inclusive 5% gate against BOTH comparators. Five synthetic Keeper policies, 100
lives each, 200 requested ticks, all 50 admitted hatch founders at hatch seed
20261006, exact slip_v2_cleanliness, and paired original seeds define the finding.
The Q3 actual default seed survives 400 attentive ticks; no-care still starves at
tick10. All 400 nonattentive cohort lives die in every arm. Follower improves99,
worsens3 and ties398 lives versus incumbent; improves88, worsens2 and ties410 versus
additive. Attentive life 88/founder 38/seed 20260797 dies of stress at 180 while both
comparators live at 200. This aggregate ADOPT is not per-life nonregression.

Additional451 beg ticks and 415 Keeper feeds versus incumbent remain explicit.
The existing Cycle 28 product stance allows extra begging for a qualified welfare
gain with voluntary feeding and incumbent opt-out. No attachment, biological
inheritance, human tolerance, automatic feeding, neglect rescue or general benefit
across other covenants is claimed. Historical DR0066 remains REFUSE.

## Prospective implementation contract

1. Keep CompanionSession's omitted constructor policy and the low-level explicit
   new-session helper's omitted policy incumbent. Parser default remains None.
   Resolve the product default only in native entry creation.
2. An explicit requested policy remains authoritative. With no explicit policy,
   any valid prior primary or backup means continuity: explicit New keeps that
   prior policy. Resume, backup recovery, succession, hatching and elite adoption
   retain existing policy and saved per-life trained state where applicable.
3. A native fresh Keeper with neither valid prior snapshot, both seed and slip
   options omitted, and therefore the built-in input choice defaults to qtable.
   Either custom input option keeps omitted policy incumbent. An explicit qtable
   choice remains available for custom inputs without borrowing the cohort claim.
4. Every new life starts with no trained Q-table, including explicit New, hatch,
   elite adoption and genuine-death succession. Restart retains the exact current
   table. Policy conflict on resume/recovery refuses before any save write.
5. Only Keeper feed actions fill hunger. No care still causes observed starvation;
   no fixture may fabricate death to establish that journey. The scientific gate,
   reward, confidence, action mapping, lifecycle and care selector remain unchanged.
6. UI labels distinguish per-life learning from inherited morphology and species
   covenant. Parent integration owns app/UI text and final bundle/full verification.
7. Native New confirmation offers a visible incumbent/Q-table choice. It starts
   by displaying the effective fresh default or saved prior policy. Only a user's
   explicit toggle overrides the saved policy for this newly created life; resume
   and recovery do not migrate it. Selecting a different directory resets the
   displayed default to that directory's authority. Incumbent opt-out must not
   require a terminal. Parent owns native_ui.py and its direct UI tests; this lane
   passes the selected New-only policy through entry creation.

## RED/GREEN and acceptance plan

Add game/tests/test_learning_rollout.py, first run against the missing native
resolver, then implement only startup.py and entry.py. Cover built-in/custom
omitted choice, explicit options, valid primary/backup continuity, malformed input
refusal, inspection without writes, low-level incumbent compatibility, exact warm
restart, both policy conflicts, real no-care death/cold child, and cold hatch/elite
adoption. Preserve prior snapshots byte-for-byte in these isolated paths.

Run focused rollout/startup/native-entry/learning-policy tests using repository
.venv/Scripts/python.exe -B, with logs under .development/x7-v2/learning. A bounded
source/native verifier runs actual app processes against new isolated homes and
retains each command, returncode and launch receipt: fresh built-in, restart,
explicit incumbent, custom input, conflict, genuine death then automatic child,
and warm table restart. Per-launch limit60s, whole verifier limit300s, no retries;
failure preserves its partial report. No live save or prior bundle is opened.

The parent builds a fresh native folder, runs the verifier against it, and closes
with aggregate tests, JSON artifact validation, preservation and diff review.
No publication or exact-published-SHA Windows/Ubuntu CI result is implied.

## Sources

- docs/development/cycle-38-lived-care-and-thought.md
- docs/development/cycle-38-learning-instrument-repair.md
- docs/development/cycle-28-learning-consumer.md
- data/game_client/product_learning_gate_stage0.json
- data/game_client/product_learning_gate_stage1.json
- research/decision_records/0066-playable-qtable-opt-in.md
- game/src/mecha_game/startup.py
- game/src/mecha_game/entry.py

## Independent review repair, before RED

The entry exception path correctly rejects a stale inspection but refreshed only
the save facts, leaving the displayed New policy from the previous inspection.
Preregister the correction: every exception-driven inspection refresh recomputes
the displayed effective policy from the new primary/backup authority, just like
directory selection and Retry. A source-event regression changes the save policy
between New display and confirmation, proves refusal preserves the external save,
then proves the next untouched New displays and creates the same newly inspected
policy in both directions. No policy migration, scientific rerun or threshold
change is authorized by this correction. Keep RED/GREEN logs and original source
verification as prior snapshots; final bundle verification binds the correction.

## Review correction sources

- game/src/mecha_game/entry.py
- game/tests/test_learning_rollout.py
- data/game_client/learning_rollout_stage1.json
