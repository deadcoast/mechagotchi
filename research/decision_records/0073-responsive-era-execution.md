# DR 0073: responsive foreground era execution

2026-10-04. Preregistered after measured event starvation, before RED.
Locally complete and source/native-observed. Full 20261004T214405-8fe7b9f8
passed 2,606 tests / 24 suites, two documented DR 0034 skips and 2,288 JSON
artifacts, with no source mutations. Closing review covers cold-load close
on both policies in addition to the existing cancellation/commit/failure checks.
Contract: `docs/development/cycle-30-responsive-eras.md`.

Keep the pygame main thread servicing events and rendering existing casing while
one joined, non-daemon thread performs the explicitly requested era. Pause care
and consume conflicting inputs. Report real phases and candidate completions
through a lab-proven optional, output-neutral engine observer. No science or
seed arithmetic changes. Headless execution remains synchronous.

Escape cancels uncommitted work cooperatively; close cancels and waits, then
uses existing companion checkpoint semantics. Once the T4 journal commit begins,
finish that attempt and preserve its completed-result recovery. Never abandon
a worker or silently rerun a saved era. Cold model loading cancels at its next
phase boundary, while UI service continues. No service or scheduler.

Evidence: `research/experiment_reports/2026-10-04-era-responsiveness.md` and
`data/game_client/era_responsiveness_review_stage0.json`. Completion requires
parity, cancellation/recovery, actual source/native observations and a full
changed-source gate. Native keyboard/human usability remain separate.
