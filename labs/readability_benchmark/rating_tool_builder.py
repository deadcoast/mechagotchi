"""Generate the visual reviewer tool for manual readability calibration.

The calibration protocol needs three humans to rate 21 sample grids on five
1-5 questions, but the samples only exist as grid-genome JSON — nothing a
reviewer can look at. This lab renders the exact 21-sample set the
calibration gate scores (same loader, same order as the reviewer template
CSV) into a single self-contained HTML page: each grid drawn as pixel art
on its native palette, five rating scales per sample, multi-reviewer
passes, and a CSV export matching the template header byte-for-byte.

Honesty constraints baked in: the page shows raw pixels only — no organ
labels, roles, anchors, or proxy readability scores that could bias the
rating (the protocol requires rating before seeing proxy values).

Filled CSVs go to data/readability/slip_readability_calibration_ratings.csv
and are consumed by slip_readability_calibration_gate.py.
"""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from slip_readability_calibration_gate import (  # noqa: E402
    build_slip_long_horizon_readability_benchmark,
)


DEFAULT_OUTPUT_DIR = ROOT / "data" / "readability"
TOOL_FILENAME = "slip_readability_calibration_rating_tool.html"
ARTIFACT_ID = "slip_readability_rating_tool_stage0"
CSV_HEADER = (
    "sample_id,grid_id,source,reviewer_id,silhouette,organ_clarity,"
    "palette_contrast,animation_readiness,companion_appeal,notes"
)
RATINGS_FILENAME = "slip_readability_calibration_ratings.csv"


def collect_rating_samples() -> list[dict]:
    """The 21 calibration samples with render payloads, in template order.

    Deliberately excludes proxy readability scores and per-cell role/organ
    annotations beyond what the pixels show — reviewers must judge the raw
    sprite.
    """
    grids: dict[str, dict] = {}
    benchmark = build_slip_long_horizon_readability_benchmark(
        grid_collector=grids
    )
    samples = []
    for entry in benchmark["samples"]:
        grid = grids[entry["sample_id"]]
        samples.append(
            {
                "sample_id": entry["sample_id"],
                "grid_id": entry["grid_id"],
                "source": entry["source"],
                "grid_size": grid["grid_size"],
                "palette": {
                    "palette_id": grid["palette"]["palette_id"],
                    "colors": grid["palette"]["colors"],
                    "background_index": grid["palette"].get(
                        "background_index", 0
                    ),
                },
                "cells": [
                    {"x": cell["x"], "y": cell["y"], "visual": cell["visual"]}
                    for cell in grid["cells"]
                ],
            }
        )
    return samples


def build_rating_tool_html(samples: list[dict]) -> str:
    payload = json.dumps(samples, separators=(",", ":"))
    return _TOOL_TEMPLATE.replace("__SAMPLES__", payload)


def build_rating_tool_report(samples: list[dict], html: str) -> dict:
    return {
        "lab_id": ARTIFACT_ID,
        "date": "2026-07-05",
        "purpose": (
            "Render the frozen 21-sample calibration set as a "
            "self-contained visual rating page so human reviewers can "
            "produce the 63-row manual ratings CSV the calibration gate "
            "requires."
        ),
        "sample_count": len(samples),
        "reviewers_required": 3,
        "expected_completed_rows": len(samples) * 3,
        "rating_scale": [1, 2, 3, 4, 5],
        "questions": [
            "silhouette",
            "organ_clarity",
            "palette_contrast",
            "animation_readiness",
            "companion_appeal",
        ],
        "csv_header": CSV_HEADER,
        "ratings_destination": f"data/readability/{RATINGS_FILENAME}",
        "tool_file": f"data/readability/{TOOL_FILENAME}",
        "tool_bytes": len(html.encode("utf-8")),
        "bias_controls": [
            "no proxy readability scores in the page payload",
            "no role/organ/anchor annotations rendered",
            "sample order fixed to the reviewer template CSV",
            "duplicate reviewer ids rejected for independent passes",
        ],
        "source_artifacts": [
            "data/readability/slip_readability_calibration_template.csv",
            "data/readability/slip_readability_calibration_reviewer_packet.md",
            "labs/readability_benchmark/slip_readability_calibration_gate.py",
        ],
        "closed_states": ["reviewer_samples_viewable_as_pixel_art"],
        "blocked_states": [
            "manual_readability_calibration_absent_until_63_rows_collected"
        ],
        "decision": {
            "status": "rating_tool_available",
            "reason": (
                "Reviewers previously had only grid-genome JSON to look "
                "at; the calibration protocol is now executable by a "
                "human. Calibration itself stays blocked until the filled "
                "CSV exists and passes the gate."
            ),
        },
        "next_research_step": (
            "Collect 3 independent reviewer passes with the tool, save "
            f"the exported CSV to data/readability/{RATINGS_FILENAME}, "
            "and rerun slip_readability_calibration_gate.py."
        ),
    }


def write_rating_tool_artifacts(
    output_dir: Path, report: dict, html: str
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / TOOL_FILENAME).write_text(html, encoding="utf-8")
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )


_TOOL_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mechagotchi Readability Rating</title>
<style>
  :root {
    --ground: #e8e6dd;
    --panel: #f2f1ea;
    --ink: #26291f;
    --ink-soft: #5c6052;
    --line: #cfcdc0;
    --accent: #3f8f4a;
    --accent-ink: #ffffff;
    --bezel: #31352b;
    --amber: #c98a2b;
    --danger: #a8442e;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --ground: #1a1d18;
      --panel: #22261f;
      --ink: #dfe3d3;
      --ink-soft: #9aa08c;
      --line: #383d33;
      --accent: #5dbb63;
      --accent-ink: #10240f;
      --bezel: #0d0f0b;
      --amber: #d9a04a;
      --danger: #d1705a;
    }
  }
  :root[data-theme="dark"] {
    --ground: #1a1d18;
    --panel: #22261f;
    --ink: #dfe3d3;
    --ink-soft: #9aa08c;
    --line: #383d33;
    --accent: #5dbb63;
    --accent-ink: #10240f;
    --bezel: #0d0f0b;
    --amber: #d9a04a;
    --danger: #d1705a;
  }
  :root[data-theme="light"] {
    --ground: #e8e6dd;
    --panel: #f2f1ea;
    --ink: #26291f;
    --ink-soft: #5c6052;
    --line: #cfcdc0;
    --accent: #3f8f4a;
    --accent-ink: #ffffff;
    --bezel: #31352b;
    --amber: #c98a2b;
    --danger: #a8442e;
  }

  * { box-sizing: border-box; }
  html, body { margin: 0; }
  body {
    background: var(--ground);
    color: var(--ink);
    font-family: system-ui, "Segoe UI", sans-serif;
    font-size: 16px;
    line-height: 1.5;
  }
  .mono { font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace; }

  .shell { max-width: 860px; margin: 0 auto; padding: 28px 20px 80px; }

  header.top {
    display: flex; align-items: baseline; justify-content: space-between;
    gap: 16px; flex-wrap: wrap; margin-bottom: 6px;
  }
  header.top h1 {
    font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
    font-size: 1.15rem; font-weight: 600; letter-spacing: 0.02em; margin: 0;
  }
  header.top h1 .dim { color: var(--ink-soft); font-weight: 400; }
  .rowcount {
    font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
    font-size: 0.85rem; color: var(--ink-soft);
    font-variant-numeric: tabular-nums;
  }
  .rowcount strong { color: var(--ink); font-weight: 600; }

  .card {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 22px;
    margin-top: 16px;
  }

  .intro p { max-width: 62ch; margin: 0 0 12px; }
  .intro p:last-of-type { margin-bottom: 0; }
  .intro .qlist { margin: 14px 0 0; padding: 0; list-style: none; display: grid; gap: 8px; }
  .intro .qlist li { display: grid; grid-template-columns: 172px 1fr; gap: 12px; align-items: baseline; }
  .intro .qlist .qname {
    font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
    font-size: 0.82rem; color: var(--accent); font-weight: 600;
  }
  .intro .qlist .qtext { color: var(--ink-soft); font-size: 0.95rem; }
  @media (max-width: 560px) { .intro .qlist li { grid-template-columns: 1fr; gap: 2px; } }

  label.fieldlabel {
    display: block; font-size: 0.78rem; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--ink-soft); margin: 18px 0 6px;
  }
  input[type="text"], textarea {
    width: 100%; padding: 10px 12px;
    border: 1px solid var(--line); border-radius: 6px;
    background: var(--ground); color: var(--ink);
    font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
    font-size: 0.95rem;
  }
  input[type="text"]:focus-visible, textarea:focus-visible, button:focus-visible {
    outline: 2px solid var(--accent); outline-offset: 1px;
  }

  button {
    font: inherit; cursor: pointer; border-radius: 6px;
    border: 1px solid var(--line); background: var(--panel); color: var(--ink);
    padding: 10px 18px;
  }
  button.primary {
    background: var(--accent); color: var(--accent-ink);
    border-color: var(--accent); font-weight: 600;
  }
  button:disabled { opacity: 0.45; cursor: not-allowed; }

  .dots { display: flex; gap: 5px; flex-wrap: wrap; margin: 18px 0 4px; }
  .dots button {
    width: 22px; height: 22px; padding: 0; border-radius: 5px;
    border: 1px solid var(--line); background: var(--ground);
    font-size: 0; line-height: 0;
  }
  .dots button.done { background: var(--accent); border-color: var(--accent); }
  .dots button.current { outline: 2px solid var(--amber); outline-offset: 1px; }

  .stage { display: grid; grid-template-columns: minmax(260px, 340px) 1fr; gap: 26px; align-items: start; }
  @media (max-width: 720px) { .stage { grid-template-columns: 1fr; } }

  .device {
    background: var(--bezel); border-radius: 14px; padding: 18px;
    display: grid; gap: 10px; justify-items: center;
  }
  .device canvas {
    width: 100%; max-width: 300px; aspect-ratio: 1;
    image-rendering: pixelated; border-radius: 4px; display: block;
  }
  .device .tag {
    font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
    font-size: 0.75rem; color: #b9bfae; letter-spacing: 0.06em;
    font-variant-numeric: tabular-nums;
  }

  .rateall {
    display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    margin: 0 0 14px; padding: 10px 12px;
    background: var(--ground); border: 1px solid var(--line); border-radius: 8px;
  }
  .rateall .label {
    font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
    font-size: 0.8rem; color: var(--ink-soft);
  }
  .lock-btn {
    padding: 4px 10px; font-size: 0.72rem;
    font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
    background: transparent; color: var(--ink-soft);
  }
  .lock-btn[aria-pressed="true"] {
    color: var(--amber); border-color: var(--amber); font-weight: 700;
  }
  .scale button.locked {
    border-color: var(--amber);
    box-shadow: inset 0 0 0 1px var(--amber);
  }
  .hintline {
    font-size: 0.76rem; color: var(--ink-soft); margin: 6px 0 14px;
  }

  .questions { display: grid; gap: 14px; }
  .qrow { display: grid; gap: 5px; }
  .qrow .qhead { display: flex; align-items: baseline; gap: 10px; }
  .qrow .qname {
    font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
    font-size: 0.85rem; font-weight: 600;
  }
  .qrow .qhint { font-size: 0.85rem; color: var(--ink-soft); }
  .scale { display: flex; gap: 6px; }
  .scale button {
    width: 42px; height: 38px; padding: 0;
    font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
    font-size: 0.95rem; font-variant-numeric: tabular-nums;
    background: var(--ground);
  }
  .scale button[aria-pressed="true"] {
    background: var(--accent); color: var(--accent-ink);
    border-color: var(--accent); font-weight: 700;
  }
  .scale-ends {
    display: flex; justify-content: space-between; width: 234px;
    font-size: 0.72rem; color: var(--ink-soft);
  }

  .nav { display: flex; justify-content: space-between; gap: 12px; margin-top: 22px; }
  .nav .spacer { flex: 1; }

  .notice { font-size: 0.9rem; color: var(--ink-soft); margin-top: 10px; }
  .notice.warn { color: var(--danger); }

  .reviewer-list { margin: 12px 0 0; padding: 0; list-style: none; display: grid; gap: 6px; }
  .reviewer-list li {
    display: flex; justify-content: space-between; align-items: center;
    font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace;
    font-size: 0.9rem; padding: 8px 12px;
    background: var(--ground); border: 1px solid var(--line); border-radius: 6px;
  }
  .reviewer-list .rows { color: var(--ink-soft); font-variant-numeric: tabular-nums; }
  .reviewer-list button.remove {
    padding: 2px 10px; font-size: 0.8rem; color: var(--danger); border-color: var(--line);
    background: transparent;
  }
  pre.path {
    background: var(--ground); border: 1px solid var(--line); border-radius: 6px;
    padding: 10px 12px; overflow-x: auto; font-size: 0.85rem; margin: 8px 0 0;
  }
  .hidden { display: none; }

  @media (prefers-reduced-motion: no-preference) {
    button { transition: background-color 120ms ease, border-color 120ms ease; }
  }
</style>
</head>
<body>
<div class="shell">
  <header class="top">
    <h1>Mechagotchi <span class="dim">/ readability rating</span></h1>
    <div class="rowcount" id="row-count"></div>
  </header>

  <section class="card intro" id="screen-intro">
    <p>You are about to look at <strong>21 tiny pixel creatures</strong> and rate how readable
    each one is — whether a person can tell what they're looking at. Each creature gets five
    ratings on a 1&ndash;5 scale (1&nbsp;=&nbsp;not at all, 5&nbsp;=&nbsp;clearly yes):</p>
    <ul class="qlist">
      <li><span class="qname">silhouette</span><span class="qtext">Can you recognize a creature body from the outline alone?</span></li>
      <li><span class="qname">organ_clarity</span><span class="qtext">Can you spot eyes/sensors, a mouth, and a main body?</span></li>
      <li><span class="qname">palette_contrast</span><span class="qtext">Do the colors separate body, features, and background?</span></li>
      <li><span class="qname">animation_readiness</span><span class="qtext">Is there an obvious feature that could move or blink?</span></li>
      <li><span class="qname">companion_appeal</span><span class="qtext">Does it read as a plausible little companion, not noise?</span></li>
    </ul>
    <p style="margin-top:14px;">Go with your gut — first impressions are exactly what this
    calibration needs. The full set needs <strong>3 reviewers</strong> (63 rows total). Each
    person does one pass; you can hand this page to someone else for the next pass. Progress
    is saved in this browser, so you can close and come back.</p>
    <label class="fieldlabel" for="reviewer-id">Your reviewer name or initials</label>
    <input type="text" id="reviewer-id" placeholder="e.g. ryan" maxlength="40" autocomplete="off">
    <p class="notice warn hidden" id="reviewer-error"></p>
    <div class="nav">
      <span class="spacer"></span>
      <button class="primary" id="start-btn">Start rating &rarr;</button>
    </div>
  </section>

  <section class="card hidden" id="screen-rate">
    <div class="dots" id="dots"></div>
    <div class="stage">
      <div class="device">
        <canvas id="grid-canvas" width="400" height="400"></canvas>
        <div class="tag" id="sample-tag"></div>
      </div>
      <div>
        <div class="rateall" id="rateall"></div>
        <p class="hintline">a locked rating carries across creatures until you
        unlock it &middot; keys: <span class="mono">1&ndash;5</span> rate,
        <span class="mono">Enter</span> next,
        <span class="mono">&larr;/&rarr;</span> move</p>
        <div class="questions" id="questions"></div>
        <label class="fieldlabel" for="notes">Notes (optional)</label>
        <textarea id="notes" rows="2" placeholder="anything odd or notable about this one"></textarea>
      </div>
    </div>
    <div class="nav">
      <button id="prev-btn">&larr; Back</button>
      <span class="spacer"></span>
      <button class="primary" id="next-btn">Next &rarr;</button>
    </div>
    <p class="notice" id="rate-notice"></p>
  </section>

  <section class="card hidden" id="screen-finish">
    <p id="finish-headline" style="font-weight:600; margin:0 0 8px;"></p>
    <p style="max-width:62ch; margin:0;">Completed reviewer passes in this browser:</p>
    <ul class="reviewer-list" id="reviewer-list"></ul>
    <p class="notice" id="finish-notice"></p>
    <div class="nav">
      <button id="another-btn">+ Add another reviewer</button>
      <span class="spacer"></span>
      <button class="primary" id="download-btn">Download CSV</button>
    </div>
    <div id="manual-export-help">
      <p style="max-width:62ch;">When all three passes are done, download the CSV and save it into the
      project as:</p>
      <pre class="path mono">data\readability\slip_readability_calibration_ratings.csv</pre>
      <p style="max-width:62ch;">then tell Claude the ratings are in — the calibration gate takes it
      from there.</p>
    </div>
    <p id="served-export-help" class="hidden" style="max-width:62ch;">Saving puts the CSV straight
    into the project — nothing to move by hand. When all three passes are saved, the calibration
    gate can run.</p>
  </section>
</div>

<script>
const SAMPLES = __SAMPLES__;

const QUESTIONS = [
  ["silhouette", "outline reads as a creature?"],
  ["organ_clarity", "eyes / mouth / body identifiable?"],
  ["palette_contrast", "colors separate the parts?"],
  ["animation_readiness", "something could clearly move?"],
  ["companion_appeal", "plausible little companion?"],
];
const CSV_HEADER = "sample_id,grid_id,source,reviewer_id,silhouette,organ_clarity,palette_contrast,animation_readiness,companion_appeal,notes";
const STORE_KEY = "mechagotchi_readability_ratings_v1";

let state = load() || { completed: [], current: null };
if (state.current) {
  // Older saved passes predate the batch-rating locks.
  state.current.locks = state.current.locks || {};
  if (!("lockAll" in state.current)) state.current.lockAll = null;
  if (!("lastAll" in state.current)) state.current.lastAll = null;
}

function load() {
  try { return JSON.parse(localStorage.getItem(STORE_KEY)); } catch { return null; }
}
function save() { localStorage.setItem(STORE_KEY, JSON.stringify(state)); }

// Batch-rating locks: fill this creature's unset questions from the
// per-question locks first, then the rate-all lock. Set values are never
// overwritten — individual overrides always win.
function applyLocks(cur, idx) {
  let changed = false;
  const row = cur.rows[idx] || {};
  for (const [q] of QUESTIONS) {
    if (Number.isInteger(row[q])) continue;
    const value = Number.isInteger(cur.locks[q]) ? cur.locks[q] : cur.lockAll;
    if (Number.isInteger(value)) {
      row[q] = value;
      changed = true;
    }
  }
  if (changed) cur.rows[idx] = row;
  return changed;
}

const $ = (id) => document.getElementById(id);
const screens = { intro: $("screen-intro"), rate: $("screen-rate"), finish: $("screen-finish") };
function show(name) {
  for (const key of Object.keys(screens)) screens[key].classList.toggle("hidden", key !== name);
  updateRowCount();
}

function totalRows() {
  let n = state.completed.length * SAMPLES.length;
  if (state.current) n += Object.values(state.current.rows).filter(isRowComplete).length;
  return n;
}
function isRowComplete(row) {
  return row && QUESTIONS.every(([q]) => Number.isInteger(row[q]));
}
function updateRowCount() {
  $("row-count").innerHTML = "rows <strong>" + totalRows() + "</strong> / " + (SAMPLES.length * 3);
}

function drawSample(sample) {
  const canvas = $("grid-canvas");
  const ctx = canvas.getContext("2d");
  const [w, h] = sample.grid_size;
  const cell = canvas.width / w;
  const bg = sample.palette.colors[sample.palette.background_index] || "#000";
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (const c of sample.cells) {
    ctx.fillStyle = c.visual;
    ctx.fillRect(c.x * cell, c.y * cell, cell, cell);
  }
  ctx.strokeStyle = "rgba(0,0,0,0.18)";
  ctx.lineWidth = 1;
  for (let i = 1; i < w; i++) {
    ctx.beginPath(); ctx.moveTo(i * cell + 0.5, 0); ctx.lineTo(i * cell + 0.5, canvas.height); ctx.stroke();
  }
  for (let j = 1; j < h; j++) {
    ctx.beginPath(); ctx.moveTo(0, j * cell + 0.5); ctx.lineTo(canvas.width, j * cell + 0.5); ctx.stroke();
  }
}

function setRating(q, n) {
  const cur = state.current;
  cur.rows[cur.index] = cur.rows[cur.index] || {};
  cur.rows[cur.index][q] = n;
  // Re-locking follows the user: changing a locked question's value moves
  // the lock to the new value instead of fighting it.
  if (Number.isInteger(cur.locks[q])) cur.locks[q] = n;
  save();
  renderStep();
  updateRowCount();
}

function renderRateAll() {
  const cur = state.current;
  const wrap = $("rateall");
  wrap.innerHTML = "";
  const label = document.createElement("span");
  label.className = "label";
  label.textContent = "rate all";
  wrap.appendChild(label);
  const scale = document.createElement("div");
  scale.className = "scale";
  scale.setAttribute("role", "group");
  scale.setAttribute("aria-label", "rate all five questions");
  for (let n = 1; n <= 5; n++) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = n;
    btn.setAttribute("aria-pressed", cur.lastAll === n ? "true" : "false");
    if (cur.lockAll === n) btn.classList.add("locked");
    btn.addEventListener("click", () => {
      cur.rows[cur.index] = cur.rows[cur.index] || {};
      // A per-question lock is a held judgment: rate-all fills around it
      // instead of stomping it, matching how locks carry to the next
      // creature.
      for (const [q] of QUESTIONS) {
        cur.rows[cur.index][q] = Number.isInteger(cur.locks[q])
          ? cur.locks[q]
          : n;
      }
      cur.lastAll = n;
      if (cur.lockAll !== null) cur.lockAll = n;
      save();
      renderStep();
      updateRowCount();
    });
    scale.appendChild(btn);
  }
  wrap.appendChild(scale);
  const lock = document.createElement("button");
  lock.type = "button";
  lock.className = "lock-btn";
  lock.setAttribute("aria-pressed", cur.lockAll !== null ? "true" : "false");
  lock.textContent = cur.lockAll !== null ? "locked " + cur.lockAll : "lock";
  lock.title = "carry this rate-all value across creatures";
  lock.addEventListener("click", () => {
    if (cur.lockAll !== null) {
      cur.lockAll = null;
    } else if (Number.isInteger(cur.lastAll)) {
      cur.lockAll = cur.lastAll;
    } else {
      $("rate-notice").textContent = "Pick a rate-all value first, then lock it.";
      return;
    }
    save();
    renderStep();
    updateRowCount();
  });
  wrap.appendChild(lock);
}

function renderStep() {
  const cur = state.current;
  const idx = cur.index;
  const sample = SAMPLES[idx];
  if (applyLocks(cur, idx)) save();
  drawSample(sample);
  $("sample-tag").textContent = "creature " + String(idx + 1).padStart(2, "0") + " / " + SAMPLES.length + " · " + sample.palette.palette_id;

  renderRateAll();
  const row = cur.rows[idx] || {};
  const qwrap = $("questions");
  qwrap.innerHTML = "";
  for (const [q, hint] of QUESTIONS) {
    const div = document.createElement("div");
    div.className = "qrow";
    const head = document.createElement("div");
    head.className = "qhead";
    head.innerHTML = '<span class="qname">' + q + '</span><span class="qhint">' + hint + "</span>";
    const lock = document.createElement("button");
    lock.type = "button";
    lock.className = "lock-btn";
    const lockedValue = cur.locks[q];
    lock.setAttribute(
      "aria-pressed", Number.isInteger(lockedValue) ? "true" : "false"
    );
    lock.textContent = Number.isInteger(lockedValue) ? "locked " + lockedValue : "lock";
    lock.title = "carry this question's rating across creatures";
    lock.addEventListener("click", () => {
      if (Number.isInteger(cur.locks[q])) {
        delete cur.locks[q];
      } else if (Number.isInteger((cur.rows[idx] || {})[q])) {
        cur.locks[q] = cur.rows[idx][q];
      } else {
        $("rate-notice").textContent = "Rate " + q + " first, then lock it.";
        return;
      }
      save();
      renderStep();
      updateRowCount();
    });
    head.appendChild(lock);
    div.appendChild(head);
    const scale = document.createElement("div");
    scale.className = "scale";
    scale.setAttribute("role", "group");
    scale.setAttribute("aria-label", q);
    for (let n = 1; n <= 5; n++) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = n;
      btn.setAttribute("aria-pressed", row[q] === n ? "true" : "false");
      if (cur.locks[q] === n) btn.classList.add("locked");
      btn.addEventListener("click", () => setRating(q, n));
      scale.appendChild(btn);
    }
    div.appendChild(scale);
    const ends = document.createElement("div");
    ends.className = "scale-ends";
    ends.innerHTML = "<span>not at all</span><span>clearly yes</span>";
    div.appendChild(ends);
    qwrap.appendChild(div);
  }

  $("notes").value = (row.notes || "");
  $("prev-btn").disabled = idx === 0;
  $("next-btn").textContent = idx === SAMPLES.length - 1 ? "Finish pass →" : "Next →";
  $("rate-notice").textContent = "reviewer: " + cur.reviewer;
  renderDots();
}

function renderDots() {
  const cur = state.current;
  const wrap = $("dots");
  wrap.innerHTML = "";
  SAMPLES.forEach((_, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.title = "creature " + (i + 1);
    b.textContent = i + 1;
    if (isRowComplete(cur.rows[i])) b.classList.add("done");
    if (i === cur.index) b.classList.add("current");
    b.addEventListener("click", () => { commitNotes(); cur.index = i; save(); renderStep(); });
    wrap.appendChild(b);
  });
}

function commitNotes() {
  const cur = state.current;
  if (!cur) return;
  const text = $("notes").value.trim();
  if (text) {
    cur.rows[cur.index] = cur.rows[cur.index] || {};
    cur.rows[cur.index].notes = text;
  } else if (cur.rows[cur.index]) {
    delete cur.rows[cur.index].notes;
  }
}

$("prev-btn").addEventListener("click", () => {
  commitNotes();
  state.current.index = Math.max(0, state.current.index - 1);
  save(); renderStep();
});

$("next-btn").addEventListener("click", () => {
  const cur = state.current;
  commitNotes();
  if (!isRowComplete(cur.rows[cur.index])) {
    $("rate-notice").textContent = "Rate all five questions before moving on.";
    return;
  }
  if (cur.index < SAMPLES.length - 1) {
    cur.index += 1;
    save(); renderStep();
  } else {
    const incomplete = SAMPLES.findIndex((_, i) => !isRowComplete(cur.rows[i]));
    if (incomplete !== -1) {
      cur.index = incomplete;
      save(); renderStep();
      $("rate-notice").textContent = "Creature " + (incomplete + 1) + " still needs ratings.";
      return;
    }
    state.completed.push({ reviewer: cur.reviewer, rows: cur.rows });
    state.current = null;
    save();
    renderFinish();
    show("finish");
    if (AUTO_EXPORT) { exportCsv(true); }
  }
});

$("start-btn").addEventListener("click", () => {
  const id = $("reviewer-id").value.trim();
  const err = $("reviewer-error");
  if (!id) {
    err.textContent = "Enter a reviewer name first.";
    err.classList.remove("hidden");
    return;
  }
  if (state.completed.some((c) => c.reviewer === id)) {
    err.textContent = '"' + id + '" already finished a pass — use a different name for an independent pass.';
    err.classList.remove("hidden");
    return;
  }
  err.classList.add("hidden");
  // Fresh locks per pass: reviewer independence means no lock state may
  // leak from one reviewer into the next.
  state.current = {
    reviewer: id, rows: {}, index: 0,
    locks: {}, lockAll: null, lastAll: null,
  };
  save();
  show("rate");
  renderStep();
});

// Keyboard rating: 1-5 rates the next unanswered question, Enter
// advances, arrows move between creatures. Never active while typing.
document.addEventListener("keydown", (event) => {
  if (screens.rate.classList.contains("hidden")) return;
  const target = event.target;
  if (target && (target.tagName === "TEXTAREA" || target.tagName === "INPUT")) return;
  const cur = state.current;
  if (!cur) return;
  if (event.key >= "1" && event.key <= "5") {
    const row = cur.rows[cur.index] || {};
    const next = QUESTIONS.find(([q]) => !Number.isInteger(row[q]));
    if (next) {
      event.preventDefault();
      setRating(next[0], Number(event.key));
    }
  } else if (event.key === "Enter") {
    event.preventDefault();
    $("next-btn").click();
  } else if (event.key === "ArrowRight") {
    event.preventDefault();
    $("next-btn").click();
  } else if (event.key === "ArrowLeft") {
    if (!$("prev-btn").disabled) {
      event.preventDefault();
      $("prev-btn").click();
    }
  }
});

function renderFinish() {
  const list = $("reviewer-list");
  list.innerHTML = "";
  state.completed.forEach((c, i) => {
    const li = document.createElement("li");
    const name = document.createElement("span");
    name.textContent = c.reviewer;
    const rows = document.createElement("span");
    rows.className = "rows";
    rows.textContent = SAMPLES.length + " rows";
    const rm = document.createElement("button");
    rm.className = "remove";
    rm.textContent = "remove";
    rm.addEventListener("click", () => {
      if (confirm('Remove reviewer "' + c.reviewer + '" and their ' + SAMPLES.length + " rows?")) {
        state.completed.splice(i, 1);
        save(); renderFinish(); updateRowCount();
      }
    });
    li.append(name, rows, rm);
    list.appendChild(li);
  });
  const n = state.completed.length;
  $("finish-headline").textContent = n >= 3
    ? "All " + n * SAMPLES.length + " rows collected — ready to export."
    : "Pass complete. " + n + " of 3 reviewers done.";
  $("finish-notice").textContent = n >= 3
    ? ""
    : "The calibration gate needs 3 independent reviewers (" + (3 - n) + " more pass" + (3 - n === 1 ? "" : "es") + " to go). You can download a partial CSV, but the gate stays blocked until all 63 rows exist.";
  $("download-btn").disabled = n === 0;
}

$("another-btn").addEventListener("click", () => {
  $("reviewer-id").value = "";
  show("intro");
});

function csvField(value) {
  const s = String(value == null ? "" : value);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

// Served by the mechas CLI (http/https) -> POST the CSV to /api/export so
// it lands directly in the project; opened as a plain file -> download.
const SERVED = location.protocol === "http:" || location.protocol === "https:";
const AUTO_EXPORT = new URLSearchParams(location.search).get("autoexport") === "1";

function buildCsv() {
  const lines = [CSV_HEADER];
  for (const pass of state.completed) {
    SAMPLES.forEach((sample, i) => {
      const row = pass.rows[i];
      lines.push([
        sample.sample_id, sample.grid_id, sample.source, pass.reviewer,
        row.silhouette, row.organ_clarity, row.palette_contrast,
        row.animation_readiness, row.companion_appeal, row.notes,
      ].map(csvField).join(","));
    });
  }
  return lines.join("\n") + "\n";
}

function downloadCsv(csv) {
  const blob = new Blob([csv], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "slip_readability_calibration_ratings.csv";
  a.click();
  URL.revokeObjectURL(a.href);
}

async function exportCsv(auto) {
  const csv = buildCsv();
  const notice = $("finish-notice");
  if (SERVED) {
    try {
      const response = await fetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "text/csv" },
        body: csv,
      });
      if (response.ok) {
        const result = await response.json();
        notice.textContent = (auto ? "Auto-saved" : "Saved") +
          " into the project (" + result.rows + " rows) — " + result.saved_to;
        return;
      }
    } catch (error) {
      /* endpoint unavailable — fall through to download */
    }
    if (auto) {
      notice.textContent = "Auto-save failed — use the Export button to download instead.";
      return;
    }
  }
  downloadCsv(csv);
}

$("download-btn").addEventListener("click", () => { exportCsv(false); });

if (SERVED) {
  $("download-btn").textContent = "Save to project";
  $("manual-export-help").classList.add("hidden");
  $("served-export-help").classList.remove("hidden");
}

updateRowCount();
if (state.current) {
  show("rate");
  renderStep();
} else if (state.completed.length > 0) {
  renderFinish();
  show("finish");
} else {
  show("intro");
}
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the visual manual-readability rating tool."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR
    )
    args = parser.parse_args()
    samples = collect_rating_samples()
    html = build_rating_tool_html(samples)
    report = build_rating_tool_report(samples, html)
    write_rating_tool_artifacts(args.output_dir, report, html)
    print(
        json.dumps(
            {
                "sample_count": report["sample_count"],
                "tool_file": report["tool_file"],
                "tool_bytes": report["tool_bytes"],
                "decision": report["decision"]["status"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
