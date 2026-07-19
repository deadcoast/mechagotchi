# Experiment Report: The Phase-H Gate — The Authoring Depth Is Real (Cycle 18 · WORKSHOP · H6)

Date: 2026-07-19

## WHY

Cycle 18 opened the WORKSHOP track from the gap table's Workshop row —
the largest measured gap never phase-gated: *"Semantic pixel editor
with layers, onion skin, animation timeline, behavior editor;
community asset/profile system; ≤45-min first-session creature+SLIP."*
H6 consolidates the ladder and closes the cycle.

## THE LADDER

| Task | What is now true | Report |
| --- | --- | --- |
| **H1 · 16×16 authoring end to end** | A NEW creature (the glow lantern) authored through the REAL pipeline at the ratified default scale, released, and ADMITTED into a game era through the F9 gates — the cross-track blocker closed | `2026-07-12-16x16-authoring.md` |
| **H2 · Semantic layers** | Four strata as authoring state over the ONE schema-valid grid; the honesty-checked `.layers.json` sidecar ("the sidecar may not lie about the grid"); releases never carry it | `2026-07-12-semantic-layers.md` |
| **H3 · Onion skin + the timeline** | The timeline scrubs the engine's clip frames for the UNSAVED draft (trait overrides riding); onion skin + per-frame engine anchors; **clip-frame exports** (the Phase-C named remainder closed): APNG/spritesheet carry the engine's projections as a DR 0013 additive rung, the codec bound relaxed 2→16 with the foreign-fixture consequence handled honestly | `2026-07-19-onion-skin-timeline.md` |
| **H4 · The behavior editor** | Deliberation depth (DR 0017's confidence-gated thinking, the covenant's thinking-depth axis) authored visually beside the long-standing behavior/survival/mutation authoring, under the live authority loop with refusals verbatim | `2026-07-19-behavior-editor.md` |
| **H5 · The first-session gate** | The whole documented journey (blank → creature + SLIP → release → animated share) proven against the live server: 8/8 steps, 10 interactions, scripted-proxy honestly labeled, the human pass prepared-not-blocking | `2026-07-19-first-session-gate.md` |

## THE CLOSING SWEEP

19 labs + package 295 + workshop 83 + game 153 (5 documented skips) +
CLI 23 (15 documented env skips) — **GREEN**; **2,213 JSON artifacts
under `data/`, 0 invalid**; both authored pages node-syntax-checked.

## HONEST REMAINDERS (named, not smuggled)

1. **The community asset/profile system** — the Workshop row's last
   clause — is HANDED BACK to DR 0035's post-alpha scope by that
   record's own words: packs travel as files at alpha; a
   registry/sharing service is a post-alpha product decision made WITH
   the owner. Not built here, and not forgotten: re-opened by any
   hosted-distribution proposal.
2. **`visual_grammar` and `species_class`** remain un-authored ladder
   fields in the slip creator (named in H4).
3. **The human first-session pass** stays prepared-not-blocking (the
   calibration pattern; H5's artifact carries the protocol).
4. **Browser click-testing** — every panel is server-verified and
   syntax-checked; live-browser passes ride the human protocol.
5. **Per-clip choreography and per-role motion** (limb/joint/
   decoration — DR 0015's named future increment) are ENGINE
   increments with their own DR path, not workshop drift.
6. **Standing engine remainders unchanged**: DR 0032 re-openers,
   occupancy saturation, behavior_neediness at 16×16, the
   scale-geometry seam.

## VERDICT

**Phase H is green.** The workshop is no longer the "single-layer,
single-frame" measured gap: it authors at the default scale with
semantic layers, a real animation timeline over the engine's own clip
model, clip-carrying exports, the covenant's thinking-depth axis, and
a proven first-session path. Cycle 18 archives to
`audits/complete/18/`; cycle 19 is planned FROM THE DOCUMENTATION by
the developer — the named post-takeover science (G2/G3/G4 remainders)
plus the named engine motion/scale remainders.

## Verification

```powershell
PS> for d in labs/*/: python -B -m unittest discover -s $d -p "test_*.py"   # 19/19 OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 295 tests ... OK
PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
Ran 83 tests ... OK
PS> python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 153 tests ... OK (skipped=5)
PS> python -B -m unittest discover -s tools/mechas_cli/tests -p "test_*.py"
Ran 23 tests ... OK (skipped=15)
PS> # every data/**/*.json parsed: 2213 artifacts, 0 invalid
```

## Sources

- `audits/TODO.md` (cycle 18), `audits/complete/18/TODO.md` (the archive)
- The five H-task reports listed above
- `docs/mecha-workshop/mecha-workshop.md` (the Phase-H depth log), `docs/mecha-workshop/mecha-workshop-design.md`
- `research/decision_records/0035-pack-distribution-at-alpha.md` (the community hand-back), `0015` (per-role motion), `0017` (deliberation), `0013` (the additive rung)
- `research/experiment_reports/2026-07-12-phase-g-gate.md` (the candidates cycle 19 draws from)
