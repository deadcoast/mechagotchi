# Qualified native learning rollout

Date: 2026-10-06. Source integration verified; final fresh-bundle and aggregate
verification belong to the integration owner and remain separate gates.

## Delivered behavior

Fresh native Keepers using the built-in seed and covenant now choose the measured
Q-table follower. Native New confirmation displays the effective policy and offers
an incumbent toggle without a terminal. Changing either input explicitly keeps
an omitted choice incumbent. An explicit policy remains authoritative.

Any valid prior primary or backup retains policy when New is selected without a
policy override. Resume, backup recovery, succession, hatching and elite adoption
preserve their recorded mode. Low-level CompanionSession and explicit_new_session
callers retain incumbent defaults, so historical constructor callers and studies
are not silently migrated. Old saves without a policy remain incumbent.

Current-life learning survives restart exactly. Every new life starts cold;
trained tables are not inherited. Resume conflicts refuse before save writes.
The source process journey observed actual no-care starvation at tick10 and an
age-zero successor with a new life identity, parent identity and empty table.
The change neither invents care nor lets the companion feed itself.

## Independent scientific review

All 1,500 stage1 receipts were independently checked against their manifest hash,
ordered plan, row payloads, previous receipt hashes and terminal receipt. The
164 recorded source hashes matched before this rollout changed the entry files.
The two attempt manifests retain identical founders, corpus, covenant, plan,
admissions, hatch seed and budgets. All 56 retained stage0 rows match stage1's
prefix exactly. Prior manifest/report hashes and the 15.608391-second debit validate.
Stage0 stays incomplete/REFUSE; stage1's recorded 100.608998 seconds includes that debit.

Five original synthetic Keeper policies each attempted 100 lives of 200 requested
ticks per arm. All 50 actual hatch founders from the ordered shipped 16x16 corpus
were admitted under exact slip_v2_cleanliness, hatch seed 20261006 and the original
paired RNG plan. Welfare includes zero after death through the requested horizon.
No new scientific cohort was run for this integration.

| Exact six-decimal row total /500 lives | Welfare sum | Follower gain |
| --- | ---: | ---: |
| Incumbent | 83.867185 | 11.7106982904% |
| Additive, consumer disabled | 83.596818 | 12.0719905870% |
| Full-confidence follower | 93.688618 | -- |

Both gains exceed the unchanged inclusive 5% rule. The original historical R3 rows,
refusals, Q1/parity binding and Q3 controls remain recorded. Q3's standard seed
survives 400 attentive ticks and starves at 10 without care. All 400 nonattentive
cohort lives die in every arm; this does not establish neglect rescue.

The aggregate gain is not a per-life guarantee. Follower improves 99 / worsens 3 / ties 398
paired lives versus incumbent, and improves 88 / worsens 2 / ties 410 versus additive.
Attentive life 88, founder 38, seed 20260797 dies of stress at 180 under follower while
both comparators survive 200. These observations do not fail the registered
aggregate gate and are preserved rather than removed. Follower produces 451 more
beg ticks and 415 more Keeper feeds than incumbent. The preexisting Cycle 28 product
stance accepts that measured tradeoff with voluntary care and incumbent opt-out;
human tolerance, attachment, individual personality and biological inheritance
remain unmeasured. Broader custom covenants do not inherit the cohort claim.

## Preregistered and executed verification

Contract: docs/development/cycle-38-qualified-learning-rollout.md, including native
New-only toggle clause 7, written before the corresponding RED tests. Commands use
the existing repository .venv/Scripts/python.exe 3.13.9 and -B.

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_learning_rollout.py -v
# RED: 13 tests, 1 failure / 12 errors: missing resolver and unchanged incumbent default.
# GREEN-01: 13 tests pass. GREEN-02: 14 tests pass, including four native source-event flows.
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_startup.py -v
# 20 tests pass.
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_native_entry.py -v
# 4 tests pass.
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_learning_policy.py -v
# 9 tests pass.
.venv/Scripts/python.exe -B labs/game_loop/verify_learning_rollout.py --output .development/x7-v2/learning/source-01
# Retained instrument failure: preparation was incorrectly assumed to pause care.
.venv/Scripts/python.exe -B labs/game_loop/verify_learning_rollout.py --output .development/x7-v2/learning/source-02
# 16 checks pass across 12 actual source-process invocations; 8.0974345 seconds.
```

Tests cover fresh/custom/default/explicit choices, both saved modes, valid backup
authority, invalid-history preservation, conflict refusal, cold hatch/elite/New/
succession, exact trained restart and actual keyboard-event consumption of the
native toggle. Injected source keyboard events are not OS keyboard automation.
Per-process native receipts retain their actual windows display driver. Two
intentional conflict refusals occur before a window; ten successful source launches
use Windows SDL. Save homes and working directories are isolated under the new run
directories. No live save or historical build was opened.

source-01's false assumption is retained in full: --view preparation explicitly
continues care and advanced the trained life 160 to 161. The verifier now compares
the actual first resumed tick against the complete expected state from the saved
life. No product semantics or scientific criterion changed. One explicitly
authorized corrected verifier run followed diagnosis. source-01 took 7.9631092 seconds,
source-02 took 8.0974345 seconds, cumulative 16.0605437 seconds. Both are within the 300-second total and 60-second
per-launch bounds; no automatic retry exists. The corrected report records unchanged
verification source during its run. All original reports and isolated saves remain.

## Remaining gates and boundaries

The integration owner must build a fresh bundle and execute:

```powershell
.venv/Scripts/python.exe -B labs/game_loop/verify_learning_rollout.py --output .development/x7-v2/learning/native-01 --bundle <fresh-folder>
```

Then complete final aggregate/artifact/preservation/diff verification against final
source. The source metric is an honest pre-bundle checkpoint. It does not rewrite
the scientific artifacts or claim remote CI. The meaningful-care descendant gate
and X8 scientific progression work remain independent. No trained-Q inheritance,
offline catch-up, hidden service, Git commit, sync or push was introduced.

## Independent review correction: stale inspection display

Review found that a save changed outside the entry window caused the confirmation
to refuse correctly, but its exception-driven refresh retained the old displayed
New policy. A subsequent untouched New used the new saved policy, contrary to the
display. The correction recomputes the displayed effective policy on that refresh,
matching directory selection and Retry. Save authority itself was not weakened.

The prospective appendix preceded a real view/entry/save event regression in both
directions. RED displayed [qtable, qtable] after an external incumbent save and
[incumbent, incumbent] after an external qtable save; both assertions failed.
The same command then passes all 15 rollout tests. It verifies the refused stale
confirmation preserves every external save byte, the refreshed New displays the
new policy and the next untouched confirmation creates that exact policy.

```powershell
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_learning_rollout.py -v
# refresh-red.log: 15 tests, 2 failing directional subcases.
# refresh-green.log: 15 tests pass in 2.261 seconds.
```

Current focused coverage is 48 tests (15 rollout +20 startup +4 native entry
+9 learning policy). The original source process reports and stage0 metric remain
unchanged prior snapshots; the final bundle verifier binds this correction and
the parent's subsequent UI width polish. No scientific cohort or full source
process verifier was rerun. data/game_client/learning_rollout_stage1.json records
this additive review repair and its exact log/source bindings.

## Sources

- docs/development/cycle-38-qualified-learning-rollout.md
- docs/development/cycle-28-learning-consumer.md
- research/decision_records/0088-qualified-native-learning-rollout.md
- research/algorithm_cards/qualified_native_learning_rollout.md
- data/game_client/learning_rollout_stage0.json
- data/game_client/product_learning_gate_stage0.json
- data/game_client/product_learning_gate_stage1.json
- .development/x7-v2/learning/independent-evidence.json
- .development/x7-v2/learning/red.log
- .development/x7-v2/learning/green-02.log
- .development/x7-v2/learning/source-01/report.json
- .development/x7-v2/learning/source-02/report.json
- game/src/mecha_game/startup.py
- game/src/mecha_game/entry.py
- game/tests/test_learning_rollout.py
- labs/game_loop/verify_learning_rollout.py
- data/game_client/learning_rollout_stage1.json
- .development/x7-v2/learning/refresh-red.log
- .development/x7-v2/learning/refresh-green.log
