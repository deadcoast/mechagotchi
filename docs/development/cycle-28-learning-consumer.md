# Cycle 28 / Phase R: the measured learner reaches the playable companion

Status: PLANNED, NOT STARTED. Prepared at Q5 on 2026-10-04.
Track: ENGINE first, then GAME. Review this completed consolidation before R1.
Source: DR 0060, Q1's unchanged artifact, DR 0063–0065, and the Phase-Q report.
Use the authoritative repository and its existing Python 3.13.9 environment.

## The actual missing integration

Q1's +7.355% is lab-tier eligibility under the extended full_fleet condition,
not a gain measured in the current game. The promoted package registry has
11 threads and lacks qtable_policy. Its decide function lacks qtable_consumer.
The game enables five incumbent threads; it has neither Q-table observation
nor the follower. Strict SLIP learning_switches currently admits only the four
original switchboard keys. Adding a consumer flag to a covenant today is invalid.
Thus porting the consumer branch alone would never produce a live recommendation.
Do not confuse the lab's extended fleet with the game's five-thread roster.

## R1 — promote the bounded Q-table and follower, defaults off (ENGINE)

Port only the existing qtable_policy observe/signal behavior and its required
helpers from labs/micro_threads/thread_fleet.py into promoted learning, plus
labs/grid_genome/micro_switchboard.py's full-confidence consumer semantics.
Keep the original ACTIONS order, reward math, bounded table/history, bucket
semantics, QTABLE_CONFIDENT_VISITS=12, rounding and deliberation record behavior.
Do not import labs, add sys.path, port unrelated discarded threads or introduce
new constants. Preserve explicit-True opt-in; absent/false/non-True remain off.
The observation/decision order must match the lab. No SLIP schema extension is
part of R1: the state seam is explicit runtime opt-in, not an invalid profile key.

Before RED, preregister parity vectors and complete off-mode instruments. Pins:
committed switchboard scenarios; pure input/no mutation; off/cold/warm states;
visits immediately below/at/above the existing floor; ties; missing thread;
recommended action differing from additive action; deliberation preserving the
consumer provenance; reward updates over complete episodes. Compare full lab
and public-package decisions and thread state, not just selected actions.
Reproduce Q1's complete committed instrument records before trusting a new gate.
The new artifact answers package parity; it does not overwrite Q1.

## R2 — an opt-in playable consumer with honest persistence (GAME)

Add an explicit experimental new-session choice for the package consumer.
Enable only the Q-table producer and its consumer alongside the five kept
threads; do not opt the entire extended lab roster into the game. Fleet-off
remains inert. The user selects a policy for a new life; an explicit option
that conflicts with an existing save must be refused before writing it.
Persist the effective choice and learned state across quit/resume. Existing
saves without this choice retain the incumbent. Preregister succession: retain
the chosen mode, start the child's learned table cold as episode-scoped learning,
and keep parent provenance; do not silently inherit trained parent rewards.

Test actual CompanionSession ticks and source-CLI/native launches with isolated
saves: opt-in, opt-out, cold-to-warm, resume, death/succession, corrupt or invalid
policy input and fleet-off. Preserve all covenant/default-cleanliness behavior.
An autonomous feed decision is still a beg executed as idle; only the keeper
feeds. Surface existing decision provenance, never an invented learning score.
Expose and document the choice in the app and supportive launcher together.

## R3 — price default adoption under the actual game (ENGINE + GAME)

Preregister before measurement, with ADOPT/REFUSE both legitimate. Use three
paired arms on the current v0.2 cleanliness covenant and actual game session:
(A) five-thread incumbent, (B) same plus Q-table additive signal, (C) same plus
full-confidence follower. Everything else stays fixed. Inherit Q1's documented
five keepers, 100 lifecycles per keeper, 200 ticks, seed base 20260709 and corpus;
record exact chosen action/keeper mappings before running. C vs B isolates the
consumer; C vs A prices the shipped-product change. Do not quote the old extended
full_fleet numbers as this experiment's baseline. Reproduce historical Q1 and
Q3 instruments separately and preserve their original covenants and definitions.

Gate: complete instruments/parity and actual game/save checks must pass; the
consumer must fire; welfare gain must meet the inherited +5% bar against BOTH
A and B, with the complete per-keeper/survival/care/beg tables reported. A zero
or incomparable denominator withholds adoption. No reward/threshold/keeper
retuning to manufacture clearance. Existing welfare remains its documented
need-balance measure; cleanliness/care counts are separate, not a new dirt-aware
metric. Reproduce Q3's 400-tick attentive and neglect controls under the chosen
candidate, showing any delta rather than rewriting the incumbent artifact.

Beg design stance, declared before measurement: extra engine beg displays are
an acceptable price for this documented welfare clearance only while feeding
stays voluntary and keeper-mediated, no alerts or forced care are added, and
incumbent opt-out remains available. Record exact additional begs and feeds.
This is a product decision, not a claim of human preference or tolerance.
If a mandatory gate fails, retain the experimentally useful opt-in and REFUSE
the default. A graded follower is a different policy and is outside this cycle.

## R4 — land the chosen product behavior and its release (GAME)

Only after the R3 record: ADOPT applies to new lives/campaigns; existing saves
retain their recorded mode, and an explicit incumbent option remains available.
REFUSE leaves the new-life default untouched. Retain historical covenants and
explicit study call-site bindings. Enumerate the exact affected artifact set;
old defect/eligibility measurements are never regenerated onto new semantics.
Verify readable controls/provenance, care, help pause, long notices, actual
launcher examples, independent saves, and the one-folder native release outside
repo cwd. No dependency/environment churn unless capability evidence requires it.

## R5 — close the evidence, preserve the next question (SHARED)

One consolidated report, complete full sweep/artifact/preservation audit and
cycle archive. Record scientific remainders separately from remote CI/signing
and owner-deferred human work. Commits and current-branch pushes follow the
user's 2026-10-04 authorization after verification; no history rewrite.

## Explicitly outside this cycle

No six-hidden-axis displays or aliasing of bond/fitness. No attention calibration
claim, new health/happiness definition, default autonomous grooming, animation
roster promotion, archive-loop changes, hosted registry, broad UI redesign,
new agent service or background automation. Those retain their named records.
The live queue is this plan, not permission to start before Q5 is reviewed.
