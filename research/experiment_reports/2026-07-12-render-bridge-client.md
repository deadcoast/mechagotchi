# Experiment Report: The Render Bridge Consumed — Graph-Driven Clips + the Full Effects Contract (Cycle 14 · GAME · F3, first half)

Date: 2026-07-12

## WHY

The Phase-C gate shipped the bridge contract and named its unconsumed
remainders: live clip DRIVING through the transition graph is "the
client-side play loop… Phase F's consumption of this contract"
(remainder #3), and `lcd_ghosting`/the effects pipeline await a live
player (remainder #2, closed at F1). F3's charter adds the kept
fleet's game-side consumers; this report delivers the first half —
the bridge itself, consumed in full on the client side — and names
the fleet half honestly (it needs an engine promotion first).

## WHAT

**`game/src/mecha_game/clips.py` — the clip driver.** The C2 graph
mirrored verbatim (hub-and-spoke: idle the resting hub, self-loops
everywhere; measured validity 0.9877 ≥ 0.80 in cycle 11). The driving
rule derives from the metric itself: C2's PRE-REGISTERED validity
judges exactly one kind of cut — the LAST frame of the source to the
FIRST frame of the target — so the driver cuts ONLY at loop
boundaries (mid-clip, the animation always completes) and routes
illegal direct edges (e.g. beg→sleep) through the idle hub, which
reaches every clip. Pinned by test: over an adversarial target
script, every emitted step is an intra-clip advance, a self-loop
boundary, or a documented graph edge — nothing else can be emitted.

**The effects contract completed** (`rasterize.py`): `glitch` (the
ill display's odd-cell-row shear, shift `max(1, round(amplitude ·
cell_px · 0.5))`, amplitude IS the engine's stress number — C5) and
`crt_bloom` (the beg display's white halo at `intensity · 0.4` alpha)
join scanline + temporal `lcd_ghosting` in the pure compositor — all
four the shared drawer's exact math, applied in its order (glitch →
bloom → scanline) after grid-resolution ghosting. An unknown declared
effect is still reported, never dropped (pinned). The HUD's attention
ping now PINGS (lit on alternating 4-frame phases, deterministic).

**The window drives the graph**: each render frame the driver steps
toward the session's `desired_clip()` (the engine's own T16 selection
via a probe packet; beg while begging), and the packet is built at
the driver's exact (clip, frame) — succession resets the driver with
the new body.

**Measured** (`data/game_client/render_bridge_stage0.json`, status
complete): a 44-tick state script sweeping calm → hungry → stressed →
exhausted → calm over the real corpus creature drove all four state
clips (`beg`, `idle`, `ill`, `sleep`) with **zero illegal cuts**, and
the compositor rasterized the **full documented contract**
(`scanline`, `lcd_ghosting`, `crt_bloom`, `glitch`) with nothing
declared skipped. Twin runs byte-equal. A real window launched with
graph driving, exit 0.

## Verification

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 55 tests in 2.332s
OK
PS> uv run python -B game/evidence.py
wrote ...\data\game_client\render_bridge_stage0.json   # status: complete
PS> uv run python -B game/run_game.py --ticks 6 --keeper-dir <tmp>
# window with graph-driven clips, exit code 0
```

(RED for this increment: `test_clips.py` failed on the missing
`mecha_game.clips`; the prior `test_unimplemented_declared_effects…`
expectation was RETIRED deliberately — bloom/glitch are now
implemented, so the skip-reporting pin moved to an unknown effect
name, `vhs_wobble`.)

## HONEST REMAINDER

1. **The kept fleet's consumers are the second half of F3** — beg
   timing, clip choice, mood display need the five D6-kept threads as
   PACKAGE surfaces (`labs/micro_threads` is not importable from the
   game by boundary law). That promotion is its own gated engine
   change (spec + verbatim port + lab-side parity pins), queued next;
   F3 stays unchecked in the TODO until it lands.
2. **`blink` was not exercised by the bridge script** (it needs the
   age tic at a calm moment) — the driver's blink edges are pinned by
   the unit tests instead.
3. **Per-role limb/joint motion** remains the standing engine-side
   Phase-C remainder #1, untouched here.

## Sources

- `audits/TODO.md` (cycle 14 F3), `research/experiment_reports/2026-07-08-phase-c-gate.md` (remainders #2/#3)
- `research/experiment_reports/2026-07-08-transition-graph.md` (C2 — the graph and the metric this driver derives from)
- `labs/animation_system/transition_graph.py` (the mirrored edges), `workshop/shared/draw.js` (the effects math)
- `game/src/mecha_game/{clips,rasterize,hud,session,app}.py` (+ tests)
- `data/game_client/render_bridge_stage0.json` (evidence)
