(function () {
  const fallback = {
    state: {
      grid_size: [8, 8],
      palette: {
        palette_id: "lcd_green",
        colors: ["#07140d", "#5dbb63", "#d8ffd6"],
        background_index: 0
      },
      slip: {
        profile_id: "slip_lcd_seed",
        name: "LCD Seed Companion",
        rules: {
          mutation: {
            cell_mutation_rate_max: 0.15,
            organ_shift_rate_max: 0.05,
            palette_shift_rate_max: 0.05,
            symmetry_break_rate_max: 0.05
          },
          grid: {
            allowed_palettes: ["lcd_green"],
            body_mass_min: 4,
            body_mass_max: 24,
            required_organ_roles: ["sensor", "expression"]
          }
        }
      },
      mutation: {
        cell_mutation_rate: 0.05,
        organ_shift_rate: 0.02,
        palette_shift_rate: 0.01,
        symmetry_break_rate: 0.01
      },
      metadata: {
        seed_grid_id: "fallback"
      },
      cells: []
    }
  };

  for (let y = 0; y < 8; y += 1) {
    for (let x = 0; x < 8; x += 1) {
      fallback.state.cells.push(emptyCell(x, y));
    }
  }

  const data = window.MECHAGOTCHI_WORKSHOP_DATA || fallback;
  const state = JSON.parse(JSON.stringify(data.state));
  let activeTool = "body";
  let selectedCell = state.cells[0];

  const gridElement = document.getElementById("semantic-grid");
  const profileLine = document.getElementById("profile-line");
  const statusStrip = document.getElementById("status-strip");
  const details = document.getElementById("cell-details");
  const validationList = document.getElementById("validation-list");
  const exportJson = document.getElementById("export-json");
  const exportSummary = document.getElementById("export-summary");

  const toolMap = {
    erase: { token: ".", role: "empty", organ: null, material: "empty" },
    body: { token: "B", role: "body", organ: "core", material: "hard" },
    anchor: { token: "A", role: "body", organ: "core", material: "hard" },
    sensor: { token: "E", role: "sensor", organ: "sensors", material: "glass" },
    expression: { token: "M", role: "expression", organ: "expression", material: "soft" }
  };

  document.querySelectorAll(".tool").forEach((button) => {
    button.addEventListener("click", () => {
      activeTool = button.dataset.tool;
      document.querySelectorAll(".tool").forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
    });
  });

  function renderGrid() {
    profileLine.textContent = `${state.slip.name} / ${state.palette.palette_id}`;
    gridElement.innerHTML = "";
    state.cells.forEach((cell) => {
      const button = document.createElement("button");
      button.className = "grid-cell";
      button.type = "button";
      button.dataset.x = String(cell.x);
      button.dataset.y = String(cell.y);
      button.dataset.token = cell.token;
      button.style.setProperty("--cell-color", cellColor(cell));
      button.title = `${cell.x},${cell.y} ${cell.role}`;
      button.textContent = cell.token;
      button.addEventListener("click", () => {
        paintCell(cell.x, cell.y, activeTool);
      });
      gridElement.appendChild(button);
    });
    updateInspector(selectedCell);
    validateExport();
  }

  function paintCell(x, y, tool) {
    const brush = toolMap[tool];
    if (tool === "anchor") {
      state.cells.forEach((cell) => {
        cell.animation_anchor = false;
        if (cell.token === "A") {
          cell.token = "B";
        }
      });
    }
    const cell = state.cells.find((item) => item.x === x && item.y === y);
    cell.token = brush.token;
    cell.role = brush.role;
    cell.organ = brush.organ;
    cell.material = brush.material;
    cell.animation_anchor = tool === "anchor";
    selectedCell = cell;
    renderGrid();
  }

  function exportGenome() {
    const colors = state.palette.colors;
    const body = [];
    const sensors = [];
    const expression = [];
    const cells = state.cells
      .filter((cell) => cell.token !== ".")
      .map((cell) => {
        const token = cell.token;
        const organ = token === "E" ? "sensors" : token === "M" ? "expression" : "core";
        const role = token === "E" ? "eye" : token === "M" ? "mouth" : "body";
        const gridCell = {
          x: cell.x,
          y: cell.y,
          visual: token === "E" || token === "M" ? colors[2] : colors[1],
          role,
          material: token === "E" ? "glass" : token === "M" ? "soft" : "hard",
          mutation_weight: 0.1,
          animation_anchor: token === "A",
          organ,
          stress: 0,
          damage: 0,
          locked: false
        };
        if (organ === "core") {
          body.push([cell.x, cell.y]);
        } else if (organ === "sensors") {
          sensors.push([cell.x, cell.y]);
        } else {
          expression.push([cell.x, cell.y]);
        }
        return gridCell;
      });

    const organs = {
      core: { role: "body_core", cells: body, required: true },
      sensors: { role: "sensor", cells: sensors, required: true }
    };
    if (expression.length > 0) {
      organs.expression = { role: "expression", cells: expression, required: false };
    }

    return {
      grid_id: "workshop_live_export",
      schema_version: "0.1.0",
      parent_grid_id: state.grid_id || state.metadata.seed_grid_id,
      grid_size: state.grid_size,
      cells,
      organs,
      palette: state.palette,
      mutation: state.mutation,
      lineage: {
        generation: 1,
        ancestor_ids: [state.metadata.seed_grid_id],
        mutation_events: ["workshop_semantic_authoring"]
      },
      metadata: {
        source: "workshop_editor_lab",
        slip_profile_id: state.slip.profile_id,
        seed_grid_id: state.metadata.seed_grid_id
      }
    };
  }

  function validateExport() {
    const exported = exportGenome();
    const errors = [];
    const bodyMass = exported.organs.core.cells.length;
    const roles = Object.values(exported.organs).map((organ) => organ.role);
    if (!exported.cells.some((cell) => cell.animation_anchor)) {
      errors.push("missing animation anchor");
    }
    if (bodyMass < state.slip.rules.grid.body_mass_min || bodyMass > state.slip.rules.grid.body_mass_max) {
      errors.push("body mass outside SLIP bounds");
    }
    state.slip.rules.grid.required_organ_roles.forEach((role) => {
      if (!roles.includes(role)) {
        errors.push(`${role} organ missing`);
      }
    });
    const ok = errors.length === 0;
    statusStrip.textContent = ok ? "Valid" : "Invalid";
    statusStrip.classList.toggle("is-invalid", !ok);
    validationList.innerHTML = "";
    (ok ? ["export passes local semantic checks"] : errors).forEach((text) => {
      const item = document.createElement("li");
      item.className = ok ? "ok" : "bad";
      item.textContent = text;
      validationList.appendChild(item);
    });
    exportJson.value = JSON.stringify(exported, null, 2);
    exportSummary.textContent = `${exported.cells.length} cells / ${bodyMass} core`;
    return ok;
  }

  function updateInspector(cell) {
    details.innerHTML = [
      ["X", cell.x],
      ["Y", cell.y],
      ["Role", cell.role],
      ["Organ", cell.organ || "none"]
    ]
      .map(([label, value]) => `<dt>${label}</dt><dd>${value}</dd>`)
      .join("");
  }

  function cellColor(cell) {
    if (cell.token === ".") {
      return state.palette.colors[0];
    }
    if (cell.token === "E" || cell.token === "M") {
      return state.palette.colors[2];
    }
    return state.palette.colors[1];
  }

  function emptyCell(x, y) {
    return {
      x,
      y,
      token: ".",
      role: "empty",
      organ: null,
      material: "empty",
      animation_anchor: false,
      locked: false
    };
  }

  window.MechagotchiWorkshop = {
    renderGrid,
    validateExport,
    exportGenome
  };

  renderGrid();
})();
