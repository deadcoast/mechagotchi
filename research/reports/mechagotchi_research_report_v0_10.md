# Mechagotchi Research Report v0.10

Date: 2026-07-05

## Executive Summary

The repair-and-tooling wave. Two arcs, both closing long-standing open
items. **Engine arc**: the learned-repair stability blocker — open since
the first trained-repair benchmark — was diagnosed (overgrowth, 27.2% of
the agreement loss), attacked along its committed direction (retrieval
conditioning — a measured negative result that also bounded the whole
retrieved-template family at 0.785 agreement), and then cleared by a
reframing: the wound-site arm, which observes the damage event's destroyed
positions (an engine-native signal), never destroyed tokens, never a
template. With a validator-guarded token choice it meets the assisted
stability bar with margin (0.938462 overlap = agreement, validity 1.0);
the blind arm honestly stays below (0.862546 / 0.631871). Decision record
0006 (user-authorized) promoted `repair` as the sixth `mecha_engine`
module with bit-for-bit lab parity, and its observability contract is now
binding on every future damage surface.

**Tooling arc** (supportive layer — the standing identity constraint in
the root `README.md` was recorded this wave: this repository is NOT a CLI
application): the manual-calibration workflow went from "impossible to
execute" (samples existed only as JSON) to a generated visual rating tool,
then to one command — `mechas rate --creatures --autoexport` — via the new
`mechas` companion CLI (decision record 0007, Typer + Rich, binding design
charter). A same-day audit executed every command and failure path,
finding and fixing five defects; owner-designed batch-rating locks,
keyboard rating, project-progress display, and reviewer prefill followed,
each verified live in a browser. Manual calibration itself is **deferred
by owner decision** — the pipeline is ready, the evidence state is
honestly 0 of 63 rows, and it is not a constraint to chase while the
sample set may still change.

Test base: 520 lab + 163 package at v0.9 → **539 lab + 193 package + 15
CLI = 747, all green**. Promotion gate: 4 promotion-ready of 6 candidates;
scaffold gate 9/9 with 6 promoted modules.

This report consolidates and links the underlying experiment reports; it
does not replace them.

## Consolidated Reports (5) and Decision Records (2)

1. `research/experiment_reports/2026-07-04-ca-nca-repair-context-ablation.md`
   — negative result, first-class: retrieval-context features, self-play,
   and pruning all degrade the plain trained rule; exemplar ceiling 0.785
   bounds the retrieved-template family; in-artifact replication proves
   harness fidelity.
2. `research/experiment_reports/2026-07-04-ca-nca-wound-site-repair.md`
   — the wound-site arm meets the 0.9/0.9/0.9 assisted stability bar with
   no template; damage events now record destroyed positions; the
   promotion-gate blocker re-derived from the new evidence key; blind-arm
   verdict kept separate and unmet.
3. `research/experiment_reports/2026-07-04-ca-nca-wound-site-validity-guard.md`
   — validator-guarded token substitution closes the one validity failure
   (`mg_seed_046`); the target-free connectivity constraint alone
   recovered the correct token; arm moves to 0.938462 / 0.938462 / 1.0.
4. `research/experiment_reports/2026-07-05-mecha-engine-repair-promotion.md`
   — DR 0006 supersedes DR 0004's deferral; `repair` promoted with 29
   contract tests, bit-for-bit lab parity pins, both gates re-derived
   test-first; the template-assisted attractor deliberately NOT ported.
5. `research/experiment_reports/2026-07-05-slip-readability-rating-tool.md`
   (+ 3 addenda) — the calibration protocol made human-executable: the
   generated pixel-art rating tool; served-mode export through the mechas
   server; batch-rating locks, rate-all, keyboard rating (owner-designed
   QoL); the 21-row pass reclassified as a system test and calibration
   deferred by owner decision.

Decision records: `0006-create-mecha-engine-repair-target.md`,
`0007-mechas-companion-cli.md`. Governance additions this wave: the root
`README.md` (identity constraint, MIVIM doctrine), `TOOLS.md` cheat sheet,
`docs/cli/mechas-cli.md` + `mechas-cli-design.md` + `mechas-cli-audit.md`.

## Headline Metrics

- Wound-site repair (guarded): overlap 0.938462 = structural agreement,
  validity 1.0, lifecycle survival 1.0 (guard off: 0.930769 / 0.9).
- Blind trained arm (recorded, unmet): 0.862546 / 0.631871 / 1.0.
- Exemplar-retrieval ceiling: 0.785 mean agreement (family bound).
- `mecha_engine`: 6 promoted modules; promotion gate 4 of 6
  promotion-ready; scaffold gate 9/9.
- mechas CLI: v0.1.0; audit five findings, five fixes, all
  regression-tested; rating loop verified end-to-end twice with live
  browser passes.
- Manual calibration: 0 of 63 rows — deferred by owner decision;
  pipeline ready.

## Deliberately Open (next_sequence)

1. **Manual readability calibration — deferred by owner decision.** Not a
   constraint to chase; revisit when the sample set stabilizes. Still
   honestly gates the evaluation module, descriptor threshold locks, and
   profile-weighted evolution claims.
2. **Runtime integration lab** (recommended next engine step, no owner
   gate needed): compose the six promoted modules through the spec's
   cross-module MVP flow (validate → generate → simulate → damage →
   repair → archive → provenance) as a research lab, exercising the
   repair module's damage-event contract in a full loop and producing the
   evidence a future `runtime` surface would need.
3. **Learning module target** — design-ready; awaits the owner's go and a
   decision record (0008).
4. **mecha_workshop build track** — research done; awaits the owner
   explicitly starting the build.
5. mechas CLI roadmap (supportive layer only): `mechas gates`, `doctor`,
   `test`; per the identity constraint these never outrank engine work.

## Sources

- `research/reports/research_report_v0_10_manifest.json`
- `research/README.md`
- `docs/00-agent_onboarding.md`
- `README.md`
- the five consolidated experiment reports and two decision records above
