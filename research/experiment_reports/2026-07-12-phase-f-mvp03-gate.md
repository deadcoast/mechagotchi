# Experiment Report: The MVP 0.3 Gate — the Ladder Is Climbed; Phase F Closes (Cycle 16 · GAME · F18)

Date: 2026-07-12

## WHY

Cycle 16 climbed the MVP ladder's last named rung. MVP 0.3's own
sentence (validity §1.24): *"Add mecha_darwin archive. Add species
niches. Add import/export SLIP files. Add lineage browser. Add
community profile packs."* This gate judges it, and — because the
ladder's named rungs are now exhausted — dispositions Phase F itself.

## THE GATE — MVP 0.3's checklist, judged

| The documented element (§1.24) | Delivered | Where |
| --- | --- | --- |
| mecha_darwin archive | RUNNING since F4 (every era is a MAP-Elites run); **SURFACED at F13** — the repertoire browser pages the archive's own records, and A adopts the browsed elite | `repertoire_stage0` |
| Species niches | The descriptor's named axes on every browsed elite; niche mastery as a spendable unlock axis (F7); coverage/qd in species memory | `repertoire_stage0`, `covenant_spending_stage0` |
| Import/export SLIP files | The active covenant travels — export verbatim, import through the authority + the corpus-compatibility gate; an import is a new species contract | `covenant_io_stage0` |
| Lineage browser | The Keeper's story, every line a record field verbatim — origins, engine death causes, the growing ancestor chain (0→1→2 measured) | `lineage_story_stage0` |
| Community profile packs | The FORMAT rung: `mechagotchi_pack_v1` with three layers of engine gates; the committed starter pack measured end to end. Distribution honestly stays Phase G | `community_pack_stage0` |

Plus F17's carried remainders closed: replay persistence
(hash-verified, DR 0022's pointer rule), campaign resume (a resumed
continuation matches the unbroken run byte for byte — observed live
across two real processes), the windowed bundle launch-verified.

**The closing sweep**: 19 lab suites + package 295 + workshop 60 +
CLI 23 + **game 147** — all green. Fourteen stage-0 artifacts under
`data/game_client/`, every status `complete`.

## THE PHASE-F DISPOSITION

**Phase F's charter is MET.** The gap analysis asked for "a REAL user
front end: a game client a player launches and plays … the MVP ladder
(0.1 → 0.2 → 0.3) climbed as PRODUCT releases — installable,
launchable, with save files." All three rungs are delivered and gated
(cycles 14–16); the client is installable, resumable, and runs the
whole documented loop — companion, eras, covenant progression,
creation, contribution, review, browsing, sharing. **Phase F CLOSES.**

**Named Phase-F remainders** (they carry as facts, not blockers):
16×16 workshop authoring (the committed releases are 8×8-era pieces);
a ledger-backed repertoire page; the cross-era family lens (E5's
clustering stays lab math); a WFC hatchery trace seam; per-elite clip
playback in browsers; UI key-surface polish (the footer is dense);
pack signing (with Phase G's distribution decisions); the engine-side
standing remainders unchanged (DR 0032 re-openers, occupancy
saturation, behavior_neediness at 16×16, the scale-geometry seam —
still undemanded, per-role motion, clip-frame exports).

## VERDICT

**The Phase-F MVP 0.3 gate is GREEN and Phase F is COMPLETE.**
Cycle 16 archives to `audits/complete/16/`; **cycle 17 opens Phase G
from the gap analysis** — the shared late-stage requireds: the
real-CuBFF corpus + the documented transducer study (REQUIRED, owner
2026-07-07), CI + reproducibility, community distribution decisions,
and the M7 public alpha of BOTH builds. The gap analysis retires only
when Phase G's alpha gate is green.

## Verification

```powershell
PS> # the closing sweep (2026-07-12, at F17's commit)
# 19 lab suites (system python -B): all OK
# package 295 OK · workshop 60 OK · CLI 23 OK · game 147 OK
PS> uv run python -B game/evidence.py
# fourteen artifacts under data/game_client/, every status "complete"
PS> mechas game --play   # the product: play, evolve, spend, hatch,
#   release, review, browse, share — quit, and it all resumes
```

## Sources

- `audits/TODO.md` (cycle 16, all six tasks checked) → `audits/complete/16/`
- `docs/project-research/validity-research.md` (§1.24 — the judged sentence)
- `docs/gap-analysis.md` (Phase F's charter; Phase G — the opened scope)
- The six task reports of 2026-07-12 (`repertoire-browser`, `lineage-browser`, `covenant-io`, `community-packs`, `carried-remainders`, this gate)
- `data/game_client/` (the fourteen stage-0 artifacts)
