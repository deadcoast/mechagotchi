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
 * - applyEffects(canvas, packet): the C5 retro effects contract — the
 *   packet DECLARES effects with deterministic parameters (DR 0026:
 *   the engine never rasterizes); this consumer draws scanlines,
 *   glitch row-shear (amplitude = the engine's own stress number), and
 *   a bloom halo. lcd_ghosting needs temporal state and is a live-
 *   player concern (Phase F's client), honestly skipped here.
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

  applyEffects(canvas, packet) {
    const effects = packet.effects || [];
    const params = packet.effect_parameters || {};
    const ctx = canvas.getContext("2d");
    if (effects.includes("glitch")) {
      // Deterministic row-shear: odd rows shift by the engine's stress.
      const amplitude = (params.glitch || {}).amplitude || 0.5;
      const [w, h] = packet.grid_size;
      const cell = canvas.width / w;
      const shift = Math.max(1, Math.round(amplitude * cell * 0.5));
      for (let row = 1; row < h; row += 2) {
        const y = row * cell;
        const strip = ctx.getImageData(0, y, canvas.width, cell);
        ctx.putImageData(strip, shift, y);
      }
    }
    if (effects.includes("crt_bloom")) {
      const { intensity = 0.3 } = params.crt_bloom || {};
      ctx.fillStyle = `rgba(255,255,255,${intensity * 0.4})`;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    if (effects.includes("scanline")) {
      const { period = 2, opacity = 0.12 } = params.scanline || {};
      ctx.fillStyle = `rgba(0,0,0,${opacity})`;
      for (let y = 0; y < canvas.height; y += period * 2) {
        ctx.fillRect(0, y, canvas.width, period);
      }
    }
  },
};
