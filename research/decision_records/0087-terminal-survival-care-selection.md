# DR 0087: correct terminal-survival ordering without promoting ineffective care

Date: 2026-10-06. Status: correction implemented; product adoption REFUSED.

## Context

X7 v1's complete care study found no care-dependent structural descendants.
Retained pair 22 additionally exposed a rank defect: a candidate dying on its
last requested tick and a candidate alive afterward both have 10 elapsed ticks.
Welfare-first selection preferred the dead candidate. That diagnosis requires a
versioned correction; it does not justify rewriting v1's criteria or refusal.

## Decision

Add explicit observed_care_selection_v2, preserving v1 and off behavior exactly.
Use the same eight-candidate legacy pool and cold evaluation, with terminal alive
as the first rank component before unchanged welfare, elapsed ticks and earliest
index. Preserve full source-bound evaluation trajectories and newborn pristine
state. Keep species covenant priors distinct from individual variation; no
biological inheritance, trained-Q inheritance, attachment or personality claim.

The original welfare and elapsed-survival nonregression bars remain mandatory,
alongside new terminal nonregression and live-option selection. The known pair 22
is a regression only. Qualify a separately preregistered original product cohort
of founders 10â€“19 with three disjoint seed pools and both named evaluators, under
30-second setup/pair and 300-second cumulative limits. Preserve every attempted
trial and refuse failed/incomplete work without automatic retries or seed hunting.

## Evidence and consequences

The correction selects live index 0 instead of dead index 4 in the retained
neglected archive-probe regression. All four retained pair 22 v1 receipts reproduce exactly.
Both complete 30-pair fresh cohorts REFUSE solely for 0/30 structural descendant
differences; every other gate passes. All 240 fed candidates survive and all 240
neglected candidates die from starvation per evaluator, leaving no live
neglected holdout option for terminal ordering to distinguish. Welfare changes,
and the probe selects nonzero indices in 21/30 pairs, but complete rankings stay
the same across paired histories. No acceptance threshold changed.

Keep v2 explicit and experimental; default care selection remains off. Meaningful
care-driven descendants remain OPEN. Product integration can expose and preserve
the corrected option without claiming the unqualified desired effect. Any new
mechanism requires its own contract and evidence. This decision does not replace
DR0086/v1's negative finding, alter learning rollout evidence or authorize Git
publication. Final build, native journeys, full aggregate and live-save
preservation are the integration owner's independent closing gates.

## Sources

- docs/development/cycle-38-terminal-survival-care.md
- research/decision_records/0086-lived-care-context-and-visible-thought.md
- research/experiment_reports/2026-10-06-terminal-survival-care.md
- research/algorithm_cards/terminal_survival_care.md
- data/game_client/observed_care_selection_stage0.json
- data/game_client/care_v2_terminal_survival_stage0.json
- labs/runtime_integration/observed_care_v2_gate.py
- packages/mecha_engine/src/mecha_engine/runtime/care.py
