/* MechaDraw — the one packet drawer every workshop page shares (E2).
 *
 * The workshop draws the engine's render packet; it never guesses. This
 * asset de-duplicates the canvas loops that preview.html and
 * session.html each carried inline (DR 0026's recorded cleanup) —
 * drawing math unchanged, pixel output identical:
 *
 * - drawPacket(canvas, packet, opts): background from the packet's own
 *   palette, one filled rect per cell from its `visual`; with
 *   opts.showDamage, damaged cells wear the red outline (the preview's
 *   historical behavior — the replay/session drawer never stroked).
 * - woundOverlay(canvas, packet, removedCells): the damage event's own
 *   removed_cells (engine observability truth) filled over the body.
 * - bodyPacketAt(frames, index): the scrubber invariant — the body at
 *   frame i is the latest packet-bearing frame <= i.
 *
 * The grid editor's draw() is NOT this function: it renders the editing
 * MATRIX (tokens, anchor dot, mouth bar, override/inspection outlines),
 * a distinct authoring surface, and deliberately stays page-local.
 */

const MechaDraw = {
  drawPacket(canvas, packet, opts = {}) {
    const [w] = packet.grid_size;
    const ctx = canvas.getContext("2d");
    const cell = canvas.width / w;
    ctx.fillStyle = packet.palette.colors[packet.palette.background_index] || "#000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    for (const c of packet.cells) {
      ctx.fillStyle = c.visual;
      ctx.fillRect(c.x * cell, c.y * cell, cell, cell);
      if (opts.showDamage && c.damage > 0) {
        ctx.strokeStyle = "rgba(200,60,40,0.9)";
        ctx.lineWidth = 2;
        ctx.strokeRect(c.x * cell + 1, c.y * cell + 1, cell - 2, cell - 2);
      }
    }
  },

  woundOverlay(canvas, packet, removedCells) {
    const [w] = packet.grid_size;
    const cell = canvas.width / w;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "rgba(200,60,40,0.75)";
    for (const [x, y] of removedCells) {
      ctx.fillRect(x * cell, y * cell, cell, cell);
    }
  },

  bodyPacketAt(frames, index) {
    for (let i = index; i >= 0; i--) {
      if (frames[i].packet) return frames[i].packet;
    }
    return null;
  },
};
