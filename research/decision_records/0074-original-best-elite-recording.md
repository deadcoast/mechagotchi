# DR 0074 - Original best-elite evaluation recording

2026-10-04. Implemented and locally verified after preregistration. Parent chose final best elite
only, preserving one replay per era. Extend DR0023 observation through actual
evolve evaluation, with lab/package parity and unchanged scientific outputs.
Use the existing frame format plus explicit original-evaluation provenance;
legacy post-era artifacts retain their labels. Recovery commits the actual
recorded result, never resimulates. Limits and acceptance are in
`docs/development/cycle-31-original-recordings.md`; no new selection mechanic.

Report: `research/experiment_reports/2026-10-04-original-era-recordings.md`.


Recording-bearing pending journals use mechagotchi_era_plan_v2 so older clients
refuse to clear fields they do not understand. U1 accepts existing v1 journals
and returns to v1 idle preparation only after completion. No campaign-ledger
schema or scientific report changes. This guards against old-client data loss.

Full `20261004T224746-6ccc82b0` passed 2,624 tests / 24 suites, two documented
zlib skips and 2,290 JSON artifacts with no mutations. Original capture leaves
complete scientific reports unchanged; eleven native launches and 25 source
flows support recovery, cancellation and playback. Published-SHA CI remains
separate and unmet. No default-policy change or Git mutation.
