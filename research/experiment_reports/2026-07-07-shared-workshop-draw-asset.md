# Experiment Report: The Shared Workshop Draw Asset (E2)

Date: 2026-07-07

## WHY

DR 0026's survey recorded the cleanup: the canvas packet-drawing loops
were duplicated inline JS — `drawPacket` in `preview.html`,
`drawReplayPacket` in `session.html`, plus each page's own copy of the
scrubber's wound overlay and body-resolution helper — with no shared
`.js` asset anywhere in the workshop. Duplication is drift waiting to
happen on the very surface whose rule is "the workshop draws the
packet; it never guesses."

## WHAT

`workshop/shared/draw.js` — one `MechaDraw` object, served automatically
by the workshop server's static root:

- `drawPacket(canvas, packet, opts)` — the packet loop verbatim
  (background from the packet's own palette, one rect per cell from its
  `visual`); `opts.showDamage` gates the red damage outline. The
  preview has ALWAYS stroked damage and the session drawer never did —
  the option pins each page's historical pixels exactly (the preview
  keeps a one-line wrapper opting the stroke on).
- `woundOverlay(canvas, packet, removedCells)` — the damage event's own
  `removed_cells` filled over the body (both scrubbers' inline copy).
- `bodyPacketAt(frames, index)` — the scrubber invariant (the body at
  frame i is the latest packet-bearing frame ≤ i), previously defined
  identically in both pages.

Both pages now `<script src="/shared/draw.js">` and their inline
duplicates are deleted. **Scope correction recorded**: DR 0026's note
counted the grid editor's `draw()` among the duplicates — the survey's
detail shows it is NOT one: it renders the editing MATRIX (token→color
mapping, anchor dot, mouth bar, override/inspection outlines), a
distinct authoring surface with different semantics. It deliberately
stays page-local, and the tests pin that distinction.

## Verification

```powershell
PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
Ran 52 tests in 86.575s
OK    # /shared/draw.js serves with the three helpers; /preview and
      # /session import it, carry no inline duplicates, and the preview
      # wrapper pins showDamage: true; the editor's draw() stays local
```

## Decision

Adopt — E2 developed to its description: de-duplication only, drawing
math unchanged, each page's pixel behavior pinned by the option it
opts into. One drawer now serves every packet surface.

## Sources

- `research/decision_records/0026-render-module-disposition.md` (the recorded cleanup)
- `workshop/shared/draw.js`
- `workshop/preview/preview.html`, `workshop/session/session.html`
- `workshop/grid_editor/grid_editor.html` (the distinct local surface)
- `workshop/tests/test_workshop_server.py` (`SharedDrawAssetTests`)
