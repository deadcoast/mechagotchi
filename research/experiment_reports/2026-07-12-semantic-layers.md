# Experiment Report: Semantic Layers — Authoring Depth Without a Second Truth (Cycle 18 · WORKSHOP · H2)

Date: 2026-07-12

## WHY

The gap table's Workshop row names layers first among the absent
authoring depth. The design constraint that matters is the
engine-truth law: layers must deepen AUTHORING without creating a
second source of truth beside the schema grid.

## WHAT

**The layer model is authoring state; the grid stays the single
truth.** Four semantic strata — body / organs / decoration / effects
— merge in precedence order (last non-empty token wins) into the ONE
matrix every engine-facing path reads (validate / save / preview /
export). Visibility is a VIEW concern only: hidden strata still merge
into the saved truth.

**The server side** (RED-first, 4 new suite tests): the save payload
optionally carries `layers`; the server VERIFIES THE HONESTY CLAIM —
the strata must merge to the posted matrix, or the save is refused
("the sidecar may not lie about the grid") with nothing written. An
accepted save writes `<name>.layers.json` beside the draft (the
workshop's sidecar idiom); a save WITHOUT layers deletes any stale
sidecar (a stale sidecar would lie); `GET /api/grids/<name>` reloads
the sidecar with the draft; **releases never carry the sidecar** —
a release is the grid (pinned).

**The editor side**: a layer bar (radio = the stratum you paint,
checkbox = view-only visibility), painting writes the active stratum
(the anchor-rehoming convenience scans every stratum), the canvas
renders the visible merge, resize preserves each stratum's top-left
region, load restores the sidecar (drafts without one split
deterministically: B/A → body, E/M → organs, the rest → decoration),
clear resets all strata. The page's 733 lines of script pass a node
syntax check.

## Verification

```powershell
PS> python -B -m unittest test_workshop_server.SemanticLayerTests   # (from workshop/tests)
Ran 4 tests ... FAILED (failures=3)   # RED: no sidecar, no reload, no shed
# after implementation:
Ran 4 tests ... OK
PS> python -B -m unittest test_workshop_server
Ran 64 tests ... OK                    # the whole server suite
PS> node --check <extracted editor script>
JS SYNTAX OK
```

## HONEST REMAINDER

1. **The strata are the fixed four** — user-defined layers would need
   their own shape rules; the documented depth names semantic strata,
   which these are.
2. **The browser UI is syntax-checked and server-verified, not
   click-tested** — the human-driven session is H5's gate; the
   honesty check means even a buggy client cannot save a lying
   sidecar.
3. **Onion skin and the timeline (H3) build on this layer plumbing** —
   the sidecar format deliberately leaves room for frame data.

## Sources

- `audits/TODO.md` (cycle 18 H2), the gap table's Workshop row, `docs/mecha-workshop/mecha-workshop-design.md`
- `workshop/server/workshop_server.py` (`_merge_layers`, the save/load/release changes) + `workshop/tests/test_workshop_server.py` (SemanticLayerTests)
- `workshop/grid_editor/grid_editor.html` (the layer bar + strata state)
