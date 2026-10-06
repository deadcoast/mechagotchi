# Earned preparation: prefreeze compatibility clarification

2026-10-06, before model setup, source freeze or any qualification trial.
This supplements `cycle-38-earned-preparation.md` without changing its scientific
criteria, inputs, seeds, six era slots or resource limits.

The first registered focused run, `20261006T095701-88f5b14f`, exposed the existing
`test_import_inboxes.ImportInboxTests.test_covenant_state_write_failure_is_visible_and_retries_without_changing_pet`
contract: an interrupted covenant import visibly says `Import not completed`,
and a fresh Enter in that same inbox explicitly finishes the import. Restore
this compatibility without repeating the import or covenant spend.

Only the exact current inbox selection, preview digest, captured import result
and pending preparation journal digest authorize that fresh Enter retry. A
changed selection/preview/journal refuses. Duplicate events from the original
press do not retry. Reopening or restarting uses the general explicit C/E or
`--finish-preparation` flow. The notice must say writes await finish and cannot
claim that all bytes remain unchanged. Original journal evidence survives.

The source lane adds assertions for these identities and repeat-input behavior;
the original import regression test is retained unchanged. Independent review
and a fresh passing focused sweep precede the immutable measurement freeze.
