# Cycle 30 T4: keep the Keeper's next-era decisions

Preregistered 2026-10-04 after T3 full closure/review, before RED.
GAME consumer/persistence track. DR 0021's connected session is Review ->
Covenant -> Contribute -> Weather -> Run -> Collect. F17 promises resume of
spent covenant and campaign position. Actual T3-app observation in
`.development/t4-loop-review.json` selected storm and released the current pet,
saved/quit/restarted, then ran a calm era without that contribution. Reading
source also shows covenant changes reach disk only through a later era run.

Make the existing loop durable, without another panel or new simulation rule.
Persist explicit R/W contribution staging and weather choices atomically in a
keeper-owned next-era plan; retain full grids/order, reject malformed staging,
and make exact repeated staging idempotent. A conflicting same-id grid must be
refused visibly. The engine still judges compatibility at era execution; do not
pre-admit a staged creature or change its covenant to force admission.

Persist successful covenant spending/imports immediately through existing
campaign state, preserving old bytes on failure and keeping care/save/policy
semantics. Expose pending weather/contribution state and current-pet identity
through existing care/report/covenant casing. Permit preparation from the report
without unpausing care; preserve meaning of covenant spend keys. Show admitted
founder IDs as well as existing verbatim rejections in outcomes. Archive/adoption
and replay remain connected to that exact completed era through existing keys.

An explicit E runs once from a copy of the existing campaign. Before ledger/
state writes, durably journal the real completed era plus its campaign state.
Retry/restart finishes an interrupted persistence step idempotently, without
another evolve call or duplicated founders/era/seed. Clear staged contributions
only after ledger/state completion. Refuse conflicting external state or corrupt
plans/journals without replacing them; care and read-only reviews stay usable.
The journal is a foreground application save record, not a service/scheduler.
Existing save directories with no plan stay lazy and unchanged by viewing.

Use the same engine APIs/inputs/outputs and existing atomic file writer; no
engine/lab math, thresholds, scientific artifacts, defaults or policies change.
No offline simulation, generalized task framework, menus or broad new backlog.
RED pins: preparation/restart, exact order/dedup/refusal, atomic failures,
covenant persistence, simulation failure, journal/ledger/state/final-clear fault
points and restart with no re-simulation, conflicting-state refusal, exact
unbroken/resumed engine outcome parity, paused report preparation and connected
care->contribute->era->outcome->archive/adoption->replay behavior on both policies.
Observe actual source input/render flows and bounded native create/resume;
retain native keyboard limitation. Targeted tests during implementation; run
focused and the required full gate only on the final milestone. Preserve all
previous evidence/builds; no Git mutations. Leave an exact code/queue handoff.

F7 source review adds a specific covenant continuity pin before implementation:
base_parameters must survive newly written state, so restart cannot compound an
already spent population/generation cap. Old states lacking this information
retain their established load behavior; do not fabricate historical base values.

Preparation must remain reversible before execution: Backspace unstages copies
without deleting source creatures. A completed result awaiting persistence cannot
be discarded by that key. Stage structurally valid genomes via the existing
public validator; compatibility remains the era engine's own admission verdict.

Visual finish gate from the first actual candidate: a normal 384-pixel era
report must keep its outcome, niche count and QD on page one. While an actual
completed result awaits persistence, do not advertise preparation keys that
are disabled. These are existing facts/actions, with no new player panel.
