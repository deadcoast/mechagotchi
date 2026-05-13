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
  const authoringData = window.MECHAGOTCHI_SLIP_AUTHORING_PANEL || null;
  const previewData = window.MECHAGOTCHI_SLIP_PREVIEW_GATES || null;
  let state = JSON.parse(JSON.stringify(data.state));
  let activeTool = "body";
  let selectedCell = state.cells[0];

  const gridElement = document.getElementById("semantic-grid");
  const profileLine = document.getElementById("profile-line");
  const statusStrip = document.getElementById("status-strip");
  const details = document.getElementById("cell-details");
  const validationList = document.getElementById("validation-list");
  const importJson = document.getElementById("import-json");
  const importButton = document.getElementById("import-button");
  const importSummary = document.getElementById("import-summary");
  const exportJson = document.getElementById("export-json");
  const exportSummary = document.getElementById("export-summary");
  const roundtripJson = document.getElementById("roundtrip-json");
  const roundtripSummary = document.getElementById("roundtrip-summary");
  const profileForm = document.getElementById("profile-form");
  const profileDraftSummary = document.getElementById("profile-draft-summary");
  const profileValidationList = document.getElementById("profile-validation-list");
  const profileJson = document.getElementById("profile-json");
  const profileApplyButton = document.getElementById("profile-apply-button");
  const profileResetButton = document.getElementById("profile-reset-button");
  const paletteOptions = document.getElementById("palette-options");
  const organOptions = document.getElementById("organ-options");
  const behaviorPreviewSummary = document.getElementById("behavior-preview-summary");
  const behaviorPreviewOutput = document.getElementById("behavior-preview-output");
  const mutationPreviewSummary = document.getElementById("mutation-preview-summary");
  const mutationPreviewOutput = document.getElementById("mutation-preview-output");

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

  importButton.addEventListener("click", () => {
    importGenome(importJson.value);
  });

  profileApplyButton.addEventListener("click", () => {
    applyProfileDraft();
  });

  profileResetButton.addEventListener("click", () => {
    resetProfileDraft();
  });

  profileForm.addEventListener("input", () => {
    const draft = collectProfileDraft();
    updateProfileDraftPreview(draft, validateProfileDraft(draft));
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
    updateRoundtrip();
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

  function renderProfileAuthoring() {
    const profile = state.slip.rules;
    const constraints = authoringConstraints();
    renderChoiceSet(
      paletteOptions,
      "grid.allowed_palettes",
      constraints.palette_values,
      profile.grid.allowed_palettes
    );
    renderChoiceSet(
      organOptions,
      "grid.required_organ_roles",
      constraints.organ_roles,
      profile.grid.required_organ_roles
    );
    setProfileValue("slip_version", profile.slip_version || "0.1.0");
    setProfileValue("profile_id", profile.profile_id);
    setProfileValue("name", profile.name);
    setProfileValue("grid.body_mass_min", profile.grid.body_mass_min);
    setProfileValue("grid.body_mass_max", profile.grid.body_mass_max);
    setProfileValue("mutation.cell_mutation_rate_max", profile.mutation.cell_mutation_rate_max);
    setProfileValue("mutation.organ_shift_rate_max", profile.mutation.organ_shift_rate_max);
    setProfileValue("mutation.palette_shift_rate_max", profile.mutation.palette_shift_rate_max);
    setProfileValue("mutation.symmetry_break_rate_max", profile.mutation.symmetry_break_rate_max);
    setProfileValue("behavior.curiosity", profile.behavior.curiosity);
    setProfileValue("behavior.neediness", profile.behavior.neediness);
    setProfileValue("behavior.sleepiness", profile.behavior.sleepiness);
    setProfileValue("survival_weights.stability", profile.survival_weights.stability);
    setProfileValue("survival_weights.novelty", profile.survival_weights.novelty);
    setProfileValue("survival_weights.bond", profile.survival_weights.bond);
    const draft = collectProfileDraft();
    updateProfileDraftPreview(draft, validateProfileDraft(draft));
  }

  function collectProfileDraft() {
    const formData = new FormData(profileForm);
    return {
      slip_version: stringValue(formData, "slip_version"),
      profile_id: stringValue(formData, "profile_id"),
      name: stringValue(formData, "name"),
      grid: {
        allowed_palettes: formData.getAll("grid.allowed_palettes").map(String),
        body_mass_min: numberValue(formData, "grid.body_mass_min"),
        body_mass_max: numberValue(formData, "grid.body_mass_max"),
        required_organ_roles: formData.getAll("grid.required_organ_roles").map(String)
      },
      mutation: {
        cell_mutation_rate_max: numberValue(formData, "mutation.cell_mutation_rate_max"),
        organ_shift_rate_max: numberValue(formData, "mutation.organ_shift_rate_max"),
        palette_shift_rate_max: numberValue(formData, "mutation.palette_shift_rate_max"),
        symmetry_break_rate_max: numberValue(formData, "mutation.symmetry_break_rate_max")
      },
      behavior: {
        curiosity: numberValue(formData, "behavior.curiosity"),
        neediness: numberValue(formData, "behavior.neediness"),
        sleepiness: numberValue(formData, "behavior.sleepiness")
      },
      survival_weights: {
        stability: numberValue(formData, "survival_weights.stability"),
        novelty: numberValue(formData, "survival_weights.novelty"),
        bond: numberValue(formData, "survival_weights.bond")
      }
    };
  }

  function validateProfileDraft(draft) {
    const constraints = authoringConstraints();
    const errors = [];
    if (draft.slip_version !== "0.1.0") {
      errors.push("slip_version unsupported");
    }
    if (!/^[a-z0-9_]+$/.test(draft.profile_id || "")) {
      errors.push("profile_id pattern mismatch");
    }
    if (!draft.name) {
      errors.push("name required");
    }
    if (draft.grid.allowed_palettes.length === 0) {
      errors.push("allowed palette required");
    }
    draft.grid.allowed_palettes.forEach((palette) => {
      if (!constraints.palette_values.includes(palette)) {
        errors.push(`${palette} palette unknown`);
      }
    });
    if (draft.grid.required_organ_roles.length === 0) {
      errors.push("required organ role required");
    }
    draft.grid.required_organ_roles.forEach((role) => {
      if (!constraints.organ_roles.includes(role)) {
        errors.push(`${role} organ role unknown`);
      }
    });
    if (!Number.isInteger(draft.grid.body_mass_min) || draft.grid.body_mass_min < 1) {
      errors.push("body_mass_min invalid");
    }
    if (!Number.isInteger(draft.grid.body_mass_max) || draft.grid.body_mass_max < 1) {
      errors.push("body_mass_max invalid");
    }
    if (draft.grid.body_mass_max < draft.grid.body_mass_min) {
      errors.push("body mass bounds reversed");
    }
    Object.entries(draft.mutation).forEach(([key, value]) => {
      if (!isUnitInterval(value)) {
        errors.push(`${key} outside unit interval`);
      }
    });
    Object.entries(draft.behavior).forEach(([key, value]) => {
      if (!isUnitInterval(value)) {
        errors.push(`${key} outside unit interval`);
      }
    });
    Object.entries(draft.survival_weights).forEach(([key, value]) => {
      if (!isUnitInterval(value)) {
        errors.push(`${key} outside unit interval`);
      }
    });
    return {
      ok: errors.length === 0,
      errors
    };
  }

  function applyProfileDraft() {
    const draft = collectProfileDraft();
    const validation = validateProfileDraft(draft);
    if (!profileForm.reportValidity() || !validation.ok) {
      updateProfileDraftPreview(draft, validation);
      return false;
    }
    state.slip = {
      profile_id: draft.profile_id,
      name: draft.name,
      rules: draft
    };
    updateProfileDraftPreview(draft, validation);
    renderGrid();
    return true;
  }

  function resetProfileDraft() {
    renderProfileAuthoring();
  }

  function updateProfileDraftPreview(draft, validation) {
    profileJson.value = JSON.stringify(draft, null, 2);
    profileDraftSummary.textContent = validation.ok
      ? `${draft.profile_id} draft valid`
      : `${draft.profile_id || "profile"} draft invalid`;
    profileDraftSummary.classList.toggle("is-invalid", !validation.ok);
    profileValidationList.innerHTML = "";
    (validation.ok ? ["draft passes Stage 0 local checks"] : validation.errors).forEach((text) => {
      const item = document.createElement("li");
      item.className = validation.ok ? "ok" : "bad";
      item.textContent = text;
      profileValidationList.appendChild(item);
    });
    updatePreviewGates(draft, validation);
  }

  function updatePreviewGates(draft, validation) {
    if (!behaviorPreviewOutput || !mutationPreviewOutput) {
      return;
    }
    if (!validation.ok) {
      behaviorPreviewSummary.textContent = "Preview blocked";
      mutationPreviewSummary.textContent = "Preview blocked";
      setOutputValue(behaviorPreviewOutput, "Draft must pass validation first.");
      setOutputValue(mutationPreviewOutput, "Draft must pass validation first.");
      return;
    }
    const behaviorPreview = buildBehaviorPreview(draft);
    const mutationPreview = buildMutationPreview(draft);
    const behaviorScenario = behaviorPreview.scenarios[0];
    behaviorPreviewSummary.textContent = `${behaviorScenario.selected_action} / social ${behaviorPreview.signals.social_pull.toFixed(3)}`;
    mutationPreviewSummary.textContent = `${mutationPreview.budgets.cell_mutation_budget} cell candidates / caps respected`;
    setOutputValue(behaviorPreviewOutput, JSON.stringify(behaviorPreview, null, 2));
    setOutputValue(mutationPreviewOutput, JSON.stringify(mutationPreview, null, 2));
  }

  function buildBehaviorPreview(profile) {
    const behavior = profile.behavior;
    const survival = profile.survival_weights;
    const curiosity = unitValue(behavior.curiosity);
    const neediness = unitValue(behavior.neediness);
    const sleepiness = unitValue(behavior.sleepiness);
    const stability = unitValue(survival.stability);
    const novelty = unitValue(survival.novelty);
    const bond = unitValue(survival.bond);
    const signals = {
      social_pull: roundMetric(neediness * 0.55 + bond * 0.30 + curiosity * 0.15),
      exploration_pull: roundMetric(curiosity * 0.50 + novelty * 0.35 + (1 - sleepiness) * 0.15),
      rest_pull: roundMetric(sleepiness * 0.55 + stability * 0.35 + (1 - curiosity) * 0.10),
      mutation_pressure: roundMetric(novelty * 0.45 + curiosity * 0.35 + (1 - stability) * 0.20),
      mutation_caution: roundMetric(stability * 0.55 + sleepiness * 0.20 + (1 - novelty) * 0.25)
    };
    const scenarios = [
      behaviorScenario(
        "attention_gap",
        {
          play: signals.social_pull * 0.62 + signals.exploration_pull * 0.28,
          idle: signals.mutation_caution * 0.30 + signals.rest_pull * 0.18,
          sleep: signals.rest_pull * 0.58,
          mutate: signals.mutation_pressure * 0.42
        },
        "Neediness and bond raise the user-facing play prompt."
      ),
      behaviorScenario(
        "low_energy_tick",
        {
          sleep: signals.rest_pull * 0.74 + signals.mutation_caution * 0.18,
          idle: signals.rest_pull * 0.34,
          play: signals.social_pull * 0.18,
          mutate: signals.mutation_pressure * 0.18
        },
        "Sleepiness and stability raise the rest response."
      ),
      behaviorScenario(
        "safe_novelty_window",
        {
          mutate: signals.mutation_pressure * 0.54 - signals.mutation_caution * 0.16,
          play: signals.exploration_pull * 0.34 + signals.social_pull * 0.18,
          idle: signals.mutation_caution * 0.24,
          sleep: signals.rest_pull * 0.22
        },
        "Curiosity and novelty raise mutation interest while stability tempers it."
      )
    ];
    return {
      profile_id: profile.profile_id,
      preview_model: "deterministic_profile_weight_proxy",
      scenario_count: scenarios.length,
      signals,
      scenarios
    };
  }

  function buildMutationPreview(profile) {
    const mutation = profile.mutation;
    const activeCells = state.cells.filter((cell) => cell.token !== ".");
    const mutableCells = activeCells.filter((cell) => cell.locked !== true);
    const bodyCells = activeCells.filter((cell) => cell.organ === "core");
    const organCells = activeCells.filter((cell) => cell.organ !== "core");
    const cellBudgetCap = ceilBudget(mutableCells.length, unitValue(mutation.cell_mutation_rate_max));
    const organBudgetCap = ceilBudget(organCells.length, unitValue(mutation.organ_shift_rate_max));
    const symmetryBudgetCap = ceilBudget(bodyCells.length, unitValue(mutation.symmetry_break_rate_max));
    const paletteAllowed = profile.grid.allowed_palettes.length > 1 && unitValue(mutation.palette_shift_rate_max) > 0;
    return {
      profile_id: profile.profile_id,
      grid_id: state.grid_id,
      preview_model: "deterministic_cap_projection_no_mutation_applied",
      body_mass: bodyCells.length,
      mutable_cell_count: mutableCells.length,
      organ_cell_count: organCells.length,
      budgets: {
        cell_mutation_budget: cellBudgetCap,
        cell_mutation_budget_cap: cellBudgetCap,
        organ_shift_budget: organBudgetCap,
        organ_shift_budget_cap: organBudgetCap,
        symmetry_break_budget: symmetryBudgetCap,
        symmetry_break_budget_cap: symmetryBudgetCap
      },
      cell_mutation_candidates: mutationCandidates(mutableCells, cellBudgetCap),
      organ_shift_candidates: mutationCandidates(organCells, organBudgetCap),
      palette_shift: {
        allowed: paletteAllowed,
        current_palette: state.palette.palette_id,
        allowed_palettes: profile.grid.allowed_palettes,
        reason: paletteAllowed
          ? "multiple_allowed_palettes_available"
          : profile.grid.allowed_palettes.length <= 1
          ? "single_allowed_palette_blocks_preview_shift"
          : "palette_shift_cap_zero"
      },
      caps_respected: true,
      lab_report_status: previewData?.report?.status || "live_static_preview"
    };
  }

  function behaviorScenario(scenarioId, rawScores, explanation) {
    const actionScores = {};
    Object.entries(rawScores).forEach(([action, value]) => {
      actionScores[action] = roundMetric(Math.max(0, value));
    });
    const selectedAction = Object.entries(actionScores).sort((left, right) => right[1] - left[1])[0][0];
    return {
      scenario_id: scenarioId,
      selected_action: selectedAction,
      action_scores: Object.keys(actionScores).sort().reduce((result, action) => {
        result[action] = actionScores[action];
        return result;
      }, {}),
      confidence: actionScores[selectedAction],
      explanation
    };
  }

  function mutationCandidates(cells, budget) {
    return cells
      .slice()
      .sort((left, right) => {
        const weightDelta = Number(right.mutation_weight || 0) - Number(left.mutation_weight || 0);
        if (weightDelta !== 0) {
          return weightDelta;
        }
        if (String(left.organ) !== String(right.organ)) {
          return String(left.organ).localeCompare(String(right.organ));
        }
        return left.y - right.y || left.x - right.x;
      })
      .slice(0, budget)
      .map((cell) => ({
        coordinate: [cell.x, cell.y],
        organ: cell.organ,
        role: cell.role,
        mutation_weight: roundMetric(Number(cell.mutation_weight || 0))
      }));
  }

  function ceilBudget(population, rate) {
    if (population <= 0 || rate <= 0) {
      return 0;
    }
    return Math.min(population, Math.ceil(population * rate));
  }

  function roundMetric(value) {
    return Math.round(Number(value) * 1000000) / 1000000;
  }

  function unitValue(value) {
    const number = Number(value);
    if (!Number.isFinite(number)) {
      return 0;
    }
    return Math.max(0, Math.min(1, number));
  }

  function setOutputValue(output, value) {
    output.value = value;
    output.textContent = value;
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

  function importGenome(rawText) {
    let imported;
    try {
      imported = JSON.parse(rawText);
    } catch (error) {
      importSummary.textContent = `Import error: ${error.message}`;
      importSummary.classList.add("is-invalid");
      return false;
    }

    state = editorStateFromGenome(imported);
    selectedCell = state.cells[0];
    importSummary.textContent = `${imported.grid_id} imported`;
    importSummary.classList.remove("is-invalid");
    renderProfileAuthoring();
    renderGrid();
    return true;
  }

  function editorStateFromGenome(grid) {
    const width = grid.grid_size[0];
    const height = grid.grid_size[1];
    const sourceCells = new Map();
    grid.cells.forEach((cell) => {
      sourceCells.set(`${cell.x},${cell.y}`, cell);
    });
    const cells = [];
    for (let y = 0; y < height; y += 1) {
      for (let x = 0; x < width; x += 1) {
        const source = sourceCells.get(`${x},${y}`);
        cells.push(source ? editorCellFromGenome(source, grid.palette) : emptyCell(x, y));
      }
    }
    return {
      schema_version: "0.1.0",
      editor_id: "workshop_editor_stage0",
      grid_id: grid.grid_id,
      grid_size: grid.grid_size,
      palette: grid.palette,
      slip: state.slip,
      tools: state.tools,
      cells,
      mutation: grid.mutation,
      metadata: {
        source: "workshop_roundtrip_import",
        seed_grid_id: grid.metadata?.seed_grid_id || grid.grid_id,
        imported_grid_id: grid.grid_id
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
    const capFields = {
      cell_mutation_rate: "cell_mutation_rate_max",
      organ_shift_rate: "organ_shift_rate_max",
      palette_shift_rate: "palette_shift_rate_max",
      symmetry_break_rate: "symmetry_break_rate_max"
    };
    Object.entries(capFields).forEach(([field, capField]) => {
      if (exported.mutation[field] > state.slip.rules.mutation[capField]) {
        errors.push(`${field} exceeds SLIP cap`);
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
    if (!importJson.value.trim()) {
      importJson.value = JSON.stringify(data.exported_grid || exported, null, 2);
    }
    return ok;
  }

  function updateRoundtrip() {
    if (!roundtripJson || !roundtripSummary) {
      return;
    }
    let imported = null;
    try {
      imported = JSON.parse(importJson.value);
    } catch {
      roundtripSummary.textContent = "Import JSON pending";
      roundtripJson.value = "";
      return;
    }
    const exported = exportGenome();
    const diff = compareSemanticCells(imported, exported);
    const changed = diff.changed_cells.length + diff.missing_cells.length + diff.added_cells.length;
    const fidelity = Math.max(0, 1 - changed / Math.max(1, imported.cells.length));
    roundtripSummary.textContent = `${fidelity.toFixed(3)} fidelity / ${changed} differences`;
    roundtripJson.value = JSON.stringify(
      {
        source_grid_id: imported.grid_id,
        export_grid_id: exported.grid_id,
        semantic_fidelity: Number(fidelity.toFixed(6)),
        semantic_diff: diff
      },
      null,
      2
    );
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

  function editorCellFromGenome(source, palette) {
    const token = source.animation_anchor ? "A" : source.organ === "sensors" ? "E" : source.organ === "expression" ? "M" : "B";
    return {
      x: source.x,
      y: source.y,
      token,
      role: token === "E" ? "sensor" : token === "M" ? "expression" : source.role,
      organ: source.organ,
      material: source.material || "hard",
      visual: source.visual || palette.colors[1],
      mutation_weight: source.mutation_weight || 0.1,
      animation_anchor: source.animation_anchor === true,
      locked: source.locked === true
    };
  }

  function compareSemanticCells(source, exported) {
    const sourceCells = semanticMap(source);
    const exportedCells = semanticMap(exported);
    const changed = [];
    const missing = [];
    const added = [];
    sourceCells.forEach((sourceValue, key) => {
      if (!exportedCells.has(key)) {
        missing.push(key.split(",").map(Number));
        return;
      }
      const exportedValue = exportedCells.get(key);
      if (JSON.stringify(sourceValue) !== JSON.stringify(exportedValue)) {
        changed.push({
          coordinate: key.split(",").map(Number),
          source: sourceValue,
          exported: exportedValue
        });
      }
    });
    exportedCells.forEach((_, key) => {
      if (!sourceCells.has(key)) {
        added.push(key.split(",").map(Number));
      }
    });
    return {
      changed_cells: changed,
      missing_cells: missing,
      added_cells: added
    };
  }

  function semanticMap(grid) {
    const cells = new Map();
    grid.cells.forEach((cell) => {
      cells.set(`${cell.x},${cell.y}`, {
        role: cell.role,
        organ: cell.organ,
        material: cell.material,
        animation_anchor: cell.animation_anchor === true,
        locked: cell.locked === true
      });
    });
    return cells;
  }

  function renderChoiceSet(container, name, values, selectedValues) {
    container.innerHTML = "";
    values.forEach((value) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.name = name;
      input.value = value;
      input.checked = selectedValues.includes(value);
      label.appendChild(input);
      label.appendChild(document.createTextNode(value));
      container.appendChild(label);
    });
  }

  function authoringConstraints() {
    const matchedState = authoringData?.authoring_states?.find(
      (item) => item.profile.profile_id === state.slip.profile_id
    ) || authoringData?.authoring_states?.[0];
    return {
      palette_values: matchedState?.schema_constraints?.palette_values || [
        "lcd_green",
        "gameboy_gray",
        "amber_terminal",
        "crt_blue",
        "pocket_plum"
      ],
      organ_roles: matchedState?.schema_constraints?.organ_roles || [
        "sensor",
        "expression",
        "body_core"
      ]
    };
  }

  function setProfileValue(name, value) {
    const field = profileForm.elements.namedItem(name);
    if (field) {
      field.value = value;
    }
  }

  function stringValue(formData, name) {
    return String(formData.get(name) || "");
  }

  function numberValue(formData, name) {
    const raw = formData.get(name);
    return raw === null || raw === "" ? NaN : Number(raw);
  }

  function isUnitInterval(value) {
    return Number.isFinite(value) && value >= 0 && value <= 1;
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
    renderProfileAuthoring,
    collectProfileDraft,
    validateProfileDraft,
    applyProfileDraft,
    updatePreviewGates,
    buildBehaviorPreview,
    buildMutationPreview,
    importGenome,
    validateExport,
    exportGenome
  };

  renderProfileAuthoring();
  renderGrid();
})();
