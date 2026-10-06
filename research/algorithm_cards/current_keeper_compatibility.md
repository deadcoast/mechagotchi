# Current Keeper write compatibility

Operational persistence boundary; not a scientific algorithm or adoption result.

Inputs: validated target campaign/model, selected native session when available,
current companion file, captured preparation/era and existing checkpoint authorities.
Output: compatible write authorization under the Keeper publication lock, or a
readable refusal before mutation. Unknown models and unrelated histories still refuse.
Standalone/lab writers without a native companion retain their existing workflow.

Native model choice is per new life; campaign model remains immutable. The shared
boundary rereads the companion at publication and protects delayed workers, recovery,
preparation, era persistence, imports, authoring and release. Expected companion bytes
also protect stale care/lineage checkpoints without changing serialized save formats.
Read-only compatible or mismatched historical inspection never grants write authority.

Verification includes actual RED failures, complete-directory byte comparisons,
interrupted/repeated/restarted operations, inverse model choices, stale contexts,
Windows cross-process locking and compatible idempotence. Limits: local operational
verification is separate from scientific qualification and exact-published-SHA CI.

See DR0092 and research/experiment_reports/2026-10-06-body-compatibility.md.
