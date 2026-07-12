# Experiment Report: The Phase-F MVP 0.1 Gate — The Game Exists (Cycle 14 · GAME · F6)

Date: 2026-07-12

## WHY

Cycle 14 was the first GAME-track cycle: the build the engine exists
to showcase — a client a player launches and plays, NOT the
dev-served workshop pages. Its rung was MVP 0.1, judged against the
founding document's own sentence (validity §1.22/§1.34): *"A 16×16
monochrome grid creature that is generated from a genome, has
hunger/energy/mood/age, changes expression by state, logs
interactions, mutates after death, produces a child using parent
traits, saves a lineage file. This proves the entire thesis."*

## THE GATE — MVP 0.1's own checklist, judged

| The documented element (validity §1.22) | Delivered | Evidence |
| --- | --- | --- |
| Generate one companion from a grid genome | the corpus founder adopts through `initial_state`; every successor is `generate_candidate` from the dead parent's genome | `companion_loop_stage0` |
| Display it in a pixel grid | the pygame-ce window over `render_packet_v2`, the pure compositor, the full LCD identity | `front_end_skeleton_stage0` |
| Simulate hunger, energy, mood, age | the engine's own lifecycle tick; bars/mood/age displayed verbatim | `companion_loop_stage0` |
| Allow feed/play/sleep interactions | F/P/S = the engine's `ACTIONS`, queued to the tick; the documented beg-mediated model (only the keeper feeds) | `companion_loop_stage0` |
| Log survival data | the interaction log + per-life lineage records (born/died/cause) | `companion_loop_stage0` |
| Mutate next generation | `generate_candidate` (validator-gated, deterministic seed chain) | `companion_loop_stage0` |
| Save lineage | `keeper_lineage_v1` — verbatim engine lineage blocks | `companion_loop_stage0` |
| Load one SLIP profile | the LCD covenant governs adoption, vocabulary, generation, and eras | every artifact |

§1.34's framing holds: 16×16 (the ratified scale), expression changes
by state (graph-driven clips), death → mutation → child with parent
traits, the lineage file saved. **The rung's own sentence is met.**

Phase F's charter demanded more than the sentence, and cycle 14
delivered it:

| Task | Result | Evidence |
| --- | --- | --- |
| **F1 · the technology + skeleton** | DR 0033 (pygame-ce — engine in-process, packets verbatim); the launchable client; `lcd_ghosting` first implemented (Phase-C remainder #2 closed) | `2026-07-12-front-end-client-skeleton.md` |
| **F2 · the companion loop** | the documented beg-mediated model with MEASURED stakes: neglect starves at age 10; the attentive keeper survives the 400-tick budget (79 feeds); succession + lineage | `2026-07-12-companion-loop-product.md` |
| **F3 · the bridge + the fleet** | graph-driven clips (zero illegal cuts), the full effects contract, and the D6-kept five streaming through the new public fleet surface (begs-soon / bandit clip choice / HMM felt mood); the "needs promotion" claim CORRECTED and recorded | `2026-07-12-render-bridge-client.md`, `2026-07-12-fleet-consumers.md` |
| **F4 · the Keeper/era loop** | one era = one promoted evolve run at A4 scale; founder spine; nine unlock facts across all five axes in the measured campaign; ledger persistence; **the era's best elite adopts as the companion** | `2026-07-12-keeper-era-loop.md` |
| **F5 · the installable release** | `keeper_session_v1` save/resume (byte-identical continuation pinned); PyInstaller onedir; the REAL exe verified install→launch→play→quit→RESUME (age 4→7) | `2026-07-12-installable-release.md` |
| **F6 · this gate** | 19 lab suites + package 295 + workshop 60 + CLI 21 + **game 83** — all green | below |

Two additive engine exports entered under the full discipline
(RED-first, spec section + contract pin updated together):
`learning.{observe_fleet, fleet_signals, FLEET_THREAD_NAMES}` and
`runtime.learned_readability_score` — behavior unchanged, frozen
paths byte-identical, both consumed by the named GAME consumers.

## HONEST REMAINDER (what Phase F still owes beyond MVP 0.1)

1. **The 0.2/0.3 rungs** (validity §1.23–1.24) decompose into cycle 15
   FROM THE GAP ANALYSIS: the visual editor + preview reach the
   product (the workshop bridge / DR 0021's Contribute step —
   `released_grids` is the consumed seam), generation surfacing,
   covenant SPENDING (the earned unlock budget applied — the lab's
   `covenant_budget` is the proven source), then 0.3's archive/
   lineage-browser/community surfaces.
2. **The Review step shows summaries, not replays** — the R5 scrubber
   remains the named consumer (G3).
3. **The bandit's warmth needs real play**; the fleet's decision-seam
   divergence is 0 (D6's ~0, reconfirmed) — its value is display/
   timing/choice, as the Phase-D gate said.
4. **Standing engine remainders unchanged**: DR 0032's re-openers,
   occupancy saturation, behavior_neediness at 16×16, the unpromoted
   scale-geometry seam (F4 did NOT demand it — recorded), the hybrid
   re-opener, per-role motion, clip-frame exports, dropped threads
   stay out.
5. **Phase G stays late-stage**: real-CuBFF ingest (REQUIRED), CI/
   packaging matrices/signing, community, the M7 public alpha.

## VERDICT

**The Phase-F MVP 0.1 gate is GREEN.** The application the documents
describe exists at its first rung as a PRODUCT: a player installs a
41 MB bundle, launches it, raises a real 16×16 engine creature that
begs and starves and dies and passes its genome on, runs evolution
eras whose elites they can adopt, quits, and resumes the same life.
Phase F CONTINUES (the ladder's 0.2/0.3 rungs); cycle 14 archives to
`audits/complete/14/`; cycle 15 opens from the gap analysis.

## Verification

```powershell
PS> # the closing sweep (2026-07-12)
# 19 lab suites (system python -B): all OK
# package 295 OK · workshop 60 OK · CLI 21 OK · game 83 OK
PS> uv run python -B game/evidence.py
# six artifacts under data/game_client/, every status "complete"
PS> .\game\dist\Mechagotchi\Mechagotchi.exe   # the product, playable
```

## Sources

- `audits/TODO.md` (cycle 14, all six tasks checked) → `audits/complete/14/`
- `docs/project-research/validity-research.md` (§1.22, §1.34 — the judged sentence)
- `docs/gap-analysis.md` (Phase F; the governing roadmap)
- The five task reports of 2026-07-12 (`front-end-client-skeleton`, `companion-loop-product`, `render-bridge-client`, `fleet-consumers`, `keeper-era-loop`, `installable-release`)
- `research/decision_records/0033-game-front-end-technology.md`
- `data/game_client/` (the six stage-0 artifacts)
