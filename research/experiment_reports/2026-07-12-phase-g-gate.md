# Experiment Report: The Phase-G Gate — the Alpha Stands; the Gap Analysis Retires (Cycle 17 · SHARED · G6)

Date: 2026-07-12

## WHY

Phase G was the last documented phase: "Real-CuBFF corpus + the
transducer study; community asset/profile system; CI +
reproducibility; the M7 public alpha of BOTH builds." The gap
analysis — commissioned by the owner's 2026-07-07 course correction —
governs every cycle "until Phase G's alpha gate is green." This is
that gate.

## THE GATE

| Task | Result | Evidence |
| --- | --- | --- |
| **G1 · CI + reproducibility** | the sweep is ONE checked-in runner (verified locally under a classic-zlib venv — the strongest portability check this machine offers) + a two-runner workflow; the zlib sensitivity handled by DR 0034's conditional pins (named skips, content gates unconditional) | `2026-07-12-ci-reproducibility.md` |
| **G2 · the real CuBFF corpus** | THE OLDEST BLOCKER CLOSED WITH REAL DATA: upstream built at the audited commit (WSL2, `make CUDA=0`), one genuine run → nine byte-exact checkpoints; the gate flipped on its own judgment (`ingested_real_cubff_snapshots`, 9/0/0) | `2026-07-12-real-cubff-corpus.md` |
| **G3 · the transducer study** | the DOCUMENTED protocol over REAL states: 20 runs × the fixed epoch grid = 400 curated states; **gates MET (preference 400/400 > 60%, invalid 0/400 < 10%) → KEEP** — with the sweep's degeneracy scrutinized, not celebrated (both instruments saturate on early-phase soup) | `2026-07-12-real-transducer-study.md` |
| **G4 · real weather** | DR 0021's zero-seam-change promise VERIFIED: the ingested records drive an era verbatim, provenance ids flow per generation, client key 4 = REAL — and the measured truth recorded: early-phase real weather is MILD (0.77–0.85), nothing tuned to feel dramatic | `2026-07-12-real-weather.md` |
| **G5 · distribution decisions** | DR 0035: at alpha, packs travel as FILES and the GATES are the security model (data judged, never executed); signing deferred-with-reason; a registry is a post-alpha decision made WITH the owner | `0035-pack-distribution-at-alpha.md` |
| **G6 · this packet + gate** | `docs/alpha.md` (reproduce everything from one document) + the README's alpha section; evidence regen recorded as a deliberate act, not a CI job; the closing sweep below | this report |

## THE ALPHA CHECKLIST — both builds

**THE ENGINE** (`packages/mecha_engine/`): ten promoted modules, 295
contract tests + lab-side parity pins over full corpora; phases A–E
gated green at documented scale (16×16 foundation; WFC adopted by
bake-off; the animation system at 0.9877 transition validity; the
11-thread fleet with honest ablation verdicts; 20,480-evaluation
evolution runs with the four-clause archive gate judged and
dispositioned). Verified per push by the checked-in sweep.

**THE GAME** (`game/`): the full MVP ladder delivered and gated
(cycles 14–16) — installable (PyInstaller, resume verified on the
real bundle), the companion loop under the documented beg-mediated
model with measured stakes, eras with covenant progression, the
hatchery, the Contribute bridge, the Review replays, the
repertoire/lineage browsers, SLIP import/export, community packs
under three gate layers, campaign resume byte-identical to the
unbroken run — **fifteen stage-0 artifacts under
`data/game_client/`, every status complete**, 152 game tests.

**Shared truth discipline**: every displayed number an engine output;
negative results first-class (the GA-advantage refutation, the
fleet's ~0 decision-seam delta, the transducer sweep's degeneracy,
real weather's mildness — all recorded verbatim).

**The closing sweep** (`tools/ci/run_sweep.py`, full mode): 19 lab
suites + package 295 + workshop 60 + CLI 23 + game 152 — all OK;
2,211 JSON artifacts valid. **SWEEP GREEN.**

## HONEST REMAINDER (Phase G's own)

1. **The first green CLOUD CI run awaits a push** — the workflow is
   authored and its runner verified locally; commits are never
   pushed unasked.
2. **The real corpus is early-phase** — post-takeover soup (and the
   Python-callback export that lights the replication/lineage
   channels) are named increments the proven build path makes cheap.
3. **Distribution infrastructure is deliberately absent** (DR 0035) —
   files + gates at alpha; registry/signing re-open WITH the owner.
4. **The standing engine/product remainders carry as facts** (the
   cycle-17 standing note's list, unchanged).

## VERDICT

**The Phase-G alpha gate is GREEN.** Every documented phase (A–G) is
complete and gated: the research program (Stages 0–6), the ENGINE
track, the GAME track's full MVP ladder, and the late-stage
requireds — with the real-CuBFF requirement satisfied by genuine
upstream data. **`docs/gap-analysis.md` RETIRES as the cycle-planning
source, per its own charter.** Cycle 17 archives to
`audits/complete/17/`.

**What governs next is the OWNER'S decision** (the cycle-17 TODO
pre-registered this): the documentation still defines scope, and the
named remainders + the docs' unexhausted depths (workshop authoring
at 16×16, post-takeover corpora, community infrastructure, the
research plan's Stage-7 horizon) are candidate directions — but the
next planning source is chosen with the owner, not by momentum.

## Verification

```powershell
PS> uv run python -B tools/ci/run_sweep.py
# 19 labs OK · package OK · cli OK · game OK · workshop OK ·
# 2211 JSON artifacts valid · SWEEP GREEN
PS> # docs/alpha.md: install → sweep → play/build → share, from a fresh clone
```

## Sources

- `audits/TODO.md` (cycle 17, all six tasks) → `audits/complete/17/`
- `docs/gap-analysis.md` (the retired roadmap), `docs/alpha.md` (the packet)
- The five G-task records of 2026-07-12 (`ci-reproducibility`, `real-cubff-corpus`, `real-transducer-study`, `real-weather`, DR `0035`)
- The three Phase-F gates (cycles 14–16), the five engine-phase gates (cycles 09–13)
