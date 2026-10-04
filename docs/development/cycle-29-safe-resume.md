# Cycle 29 S1: safe companion resume and explicit recovery

Preregistered 2026-10-04 after review of the complete Cycle 28 result and before
S1 RED. Use the actual repository and existing interpreter; no Git mutations.

Observed source gap: CompanionSession.load reconstructs GenerationModel from
unvalidated JSON fields. The generator only checks its class, allowing malformed
or wrong-size learned models to survive reload and fail later. The app also
has no explicit recovery path for its existing .bak.json file. Incumbent policy
status is implicit while Q-table status is shown. Policy is deliberately a
recorded life choice; keep conflict refusal and the default-adoption refusal.

Implement engine-owned structural model validation and parent-size compatibility
without changing valid model math, output or metadata. At the session boundary,
turn malformed save structures into clear ValueError messages before play or
writes. Preserve valid incumbent, Q-table, legacy-covenant and successor saves.

Add explicit --recover-backup in app and supportive launcher. Validate backup
and policy compatibility before any write. Retain the previous primary byte-for-
byte in a separate recovery archive; preserve the validated backup. Use atomic
replacement so failed writes do not truncate the primary. Refuse missing or bad
backups and conflicts with new-life/covenant options. Never auto-reset a pet or
silently choose another policy. Show the actual active policy in the existing
paged casing, including inactive Q-table state; keep existing UI structure.

RED pins: malformed/missing model fields, non-numeric/negative counts, unknown
strategy/token, wrong model dimensions, corrupt save root/required fields;
unchanged primary/backup on refusal; explicit recovery preserves old primary
and learned state; restore/save write failure preserves readable old bytes;
new/resume choices for both policies and old save compatibility. Validate real
source/CLI and native launches, plus a rendered casing. Run focused package/game/
CLI checks, then the full sweep and preservation audit before local completion.
No model retraining, scientific artifact rewrite, default promotion or new
policy algorithm belongs to this slice.
