window.MECHAGOTCHI_WORKSHOP_DATA = {
  "state": {
    "schema_version": "0.1.0",
    "editor_id": "workshop_editor_stage0",
    "grid_id": "mg_seed_001",
    "grid_size": [
      8,
      8
    ],
    "palette": {
      "palette_id": "lcd_green",
      "colors": [
        "#07140d",
        "#5dbb63",
        "#d8ffd6"
      ],
      "background_index": 0
    },
    "slip": {
      "profile_id": "slip_lcd_seed",
      "name": "LCD Seed Companion",
      "rules": {
        "slip_version": "0.1.0",
        "profile_id": "slip_lcd_seed",
        "name": "LCD Seed Companion",
        "grid": {
          "allowed_palettes": [
            "lcd_green"
          ],
          "body_mass_min": 4,
          "body_mass_max": 24,
          "required_organ_roles": [
            "sensor",
            "expression"
          ]
        },
        "mutation": {
          "cell_mutation_rate_max": 0.15,
          "organ_shift_rate_max": 0.05,
          "palette_shift_rate_max": 0.05,
          "symmetry_break_rate_max": 0.05
        },
        "behavior": {
          "curiosity": 0.6,
          "neediness": 0.4,
          "sleepiness": 0.5
        },
        "survival_weights": {
          "stability": 0.5,
          "novelty": 0.25,
          "bond": 0.25
        }
      }
    },
    "tools": {
      "erase": {
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty"
      },
      "body": {
        "token": "B",
        "role": "body",
        "organ": "core",
        "material": "hard"
      },
      "anchor": {
        "token": "A",
        "role": "body",
        "organ": "core",
        "material": "hard"
      },
      "sensor": {
        "token": "E",
        "role": "sensor",
        "organ": "sensors",
        "material": "glass"
      },
      "expression": {
        "token": "M",
        "role": "expression",
        "organ": "expression",
        "material": "soft"
      }
    },
    "cells": [
      {
        "x": 0,
        "y": 0,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 1,
        "y": 0,
        "token": "E",
        "role": "sensor",
        "organ": "sensors",
        "material": "glass",
        "visual": "#d8ffd6",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 2,
        "y": 0,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 3,
        "y": 0,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 4,
        "y": 0,
        "token": "E",
        "role": "sensor",
        "organ": "sensors",
        "material": "glass",
        "visual": "#d8ffd6",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 5,
        "y": 0,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 6,
        "y": 0,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 7,
        "y": 0,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 0,
        "y": 1,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 1,
        "y": 1,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 2,
        "y": 1,
        "token": "B",
        "role": "body",
        "organ": "core",
        "material": "hard",
        "visual": "#5dbb63",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 3,
        "y": 1,
        "token": "B",
        "role": "body",
        "organ": "core",
        "material": "hard",
        "visual": "#5dbb63",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 4,
        "y": 1,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 5,
        "y": 1,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 6,
        "y": 1,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 7,
        "y": 1,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 0,
        "y": 2,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 1,
        "y": 2,
        "token": "B",
        "role": "body",
        "organ": "core",
        "material": "hard",
        "visual": "#5dbb63",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 2,
        "y": 2,
        "token": "A",
        "role": "body",
        "organ": "core",
        "material": "hard",
        "visual": "#5dbb63",
        "mutation_weight": 0.1,
        "animation_anchor": true,
        "locked": false
      },
      {
        "x": 3,
        "y": 2,
        "token": "B",
        "role": "body",
        "organ": "core",
        "material": "hard",
        "visual": "#5dbb63",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 4,
        "y": 2,
        "token": "B",
        "role": "body",
        "organ": "core",
        "material": "hard",
        "visual": "#5dbb63",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 5,
        "y": 2,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 6,
        "y": 2,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 7,
        "y": 2,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 0,
        "y": 3,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 1,
        "y": 3,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 2,
        "y": 3,
        "token": "B",
        "role": "body",
        "organ": "core",
        "material": "hard",
        "visual": "#5dbb63",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 3,
        "y": 3,
        "token": "B",
        "role": "body",
        "organ": "core",
        "material": "hard",
        "visual": "#5dbb63",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 4,
        "y": 3,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 5,
        "y": 3,
        "token": "M",
        "role": "expression",
        "organ": "expression",
        "material": "soft",
        "visual": "#d8ffd6",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 6,
        "y": 3,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 7,
        "y": 3,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 0,
        "y": 4,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 1,
        "y": 4,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 2,
        "y": 4,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 3,
        "y": 4,
        "token": "B",
        "role": "body",
        "organ": "core",
        "material": "hard",
        "visual": "#5dbb63",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 4,
        "y": 4,
        "token": "B",
        "role": "body",
        "organ": "core",
        "material": "hard",
        "visual": "#5dbb63",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 5,
        "y": 4,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 6,
        "y": 4,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 7,
        "y": 4,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 0,
        "y": 5,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 1,
        "y": 5,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 2,
        "y": 5,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 3,
        "y": 5,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 4,
        "y": 5,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 5,
        "y": 5,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 6,
        "y": 5,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 7,
        "y": 5,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 0,
        "y": 6,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 1,
        "y": 6,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 2,
        "y": 6,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 3,
        "y": 6,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 4,
        "y": 6,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 5,
        "y": 6,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 6,
        "y": 6,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 7,
        "y": 6,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 0,
        "y": 7,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 1,
        "y": 7,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 2,
        "y": 7,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 3,
        "y": 7,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 4,
        "y": 7,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 5,
        "y": 7,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 6,
        "y": 7,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      },
      {
        "x": 7,
        "y": 7,
        "token": ".",
        "role": "empty",
        "organ": null,
        "material": "empty",
        "visual": "#07140d",
        "mutation_weight": 0,
        "animation_anchor": false,
        "locked": false
      }
    ],
    "mutation": {
      "cell_mutation_rate": 0.05,
      "organ_shift_rate": 0.02,
      "palette_shift_rate": 0.01,
      "symmetry_break_rate": 0.01
    },
    "metadata": {
      "source": "workshop_editor_lab",
      "seed_grid_id": "mg_seed_001"
    }
  },
  "exported_grid": {
    "grid_id": "workshop_export_stage0",
    "schema_version": "0.1.0",
    "parent_grid_id": "mg_seed_001",
    "grid_size": [
      8,
      8
    ],
    "cells": [
      {
        "x": 1,
        "y": 0,
        "visual": "#d8ffd6",
        "role": "eye",
        "material": "glass",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "sensors",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 4,
        "y": 0,
        "visual": "#d8ffd6",
        "role": "eye",
        "material": "glass",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "sensors",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 2,
        "y": 1,
        "visual": "#5dbb63",
        "role": "body",
        "material": "hard",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "core",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 3,
        "y": 1,
        "visual": "#5dbb63",
        "role": "body",
        "material": "hard",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "core",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 1,
        "y": 2,
        "visual": "#5dbb63",
        "role": "body",
        "material": "hard",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "core",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 2,
        "y": 2,
        "visual": "#5dbb63",
        "role": "body",
        "material": "hard",
        "mutation_weight": 0.1,
        "animation_anchor": true,
        "organ": "core",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 3,
        "y": 2,
        "visual": "#5dbb63",
        "role": "body",
        "material": "hard",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "core",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 4,
        "y": 2,
        "visual": "#5dbb63",
        "role": "body",
        "material": "hard",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "core",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 2,
        "y": 3,
        "visual": "#5dbb63",
        "role": "body",
        "material": "hard",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "core",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 3,
        "y": 3,
        "visual": "#5dbb63",
        "role": "body",
        "material": "hard",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "core",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 5,
        "y": 3,
        "visual": "#d8ffd6",
        "role": "mouth",
        "material": "soft",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "expression",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 3,
        "y": 4,
        "visual": "#5dbb63",
        "role": "body",
        "material": "hard",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "core",
        "stress": 0,
        "damage": 0,
        "locked": false
      },
      {
        "x": 4,
        "y": 4,
        "visual": "#5dbb63",
        "role": "body",
        "material": "hard",
        "mutation_weight": 0.1,
        "animation_anchor": false,
        "organ": "core",
        "stress": 0,
        "damage": 0,
        "locked": false
      }
    ],
    "organs": {
      "core": {
        "role": "body_core",
        "cells": [
          [
            2,
            1
          ],
          [
            3,
            1
          ],
          [
            1,
            2
          ],
          [
            2,
            2
          ],
          [
            3,
            2
          ],
          [
            4,
            2
          ],
          [
            2,
            3
          ],
          [
            3,
            3
          ],
          [
            3,
            4
          ],
          [
            4,
            4
          ]
        ],
        "required": true
      },
      "sensors": {
        "role": "sensor",
        "cells": [
          [
            1,
            0
          ],
          [
            4,
            0
          ]
        ],
        "required": true
      },
      "expression": {
        "role": "expression",
        "cells": [
          [
            5,
            3
          ]
        ],
        "required": false
      }
    },
    "palette": {
      "palette_id": "lcd_green",
      "colors": [
        "#07140d",
        "#5dbb63",
        "#d8ffd6"
      ],
      "background_index": 0
    },
    "mutation": {
      "cell_mutation_rate": 0.05,
      "organ_shift_rate": 0.02,
      "palette_shift_rate": 0.01,
      "symmetry_break_rate": 0.01
    },
    "lineage": {
      "generation": 1,
      "ancestor_ids": [
        "mg_seed_001"
      ],
      "mutation_events": [
        "workshop_semantic_authoring"
      ]
    },
    "metadata": {
      "source": "workshop_editor_lab",
      "slip_profile_id": "slip_lcd_seed",
      "seed_grid_id": "mg_seed_001"
    }
  },
  "report": {
    "lab_id": "workshop_editor_stage0",
    "source_grid_id": "mg_seed_001",
    "slip_profile_id": "slip_lcd_seed",
    "surfaces": [
      "semantic_grid_canvas",
      "semantic_brush_toolbar",
      "cell_metadata_inspector",
      "validator_panel",
      "json_export_panel"
    ],
    "metrics": {
      "profile_creation_success": 1,
      "validator_clarity": 1,
      "schema_error_rate": 0,
      "custom_profile_survival_rate": 1
    },
    "export_validation": {
      "valid": true,
      "errors": [],
      "slip_aligned": true,
      "slip_errors": []
    },
    "decision": {
      "status": "prototype",
      "reason": "A minimal semantic editor can export a valid, SLIP-aligned grid genome without embedding third-party editor code."
    }
  },
  "roundtrip": {
    "report": {
      "lab_id": "workshop_roundtrip_stage0",
      "source_grid_id": "mg_seed_001",
      "slip_profile_id": "slip_lcd_seed",
      "surfaces": [
        "semantic_grid_canvas",
        "json_import_panel",
        "json_export_panel",
        "roundtrip_diff_panel",
        "validator_panel"
      ],
      "metrics": {
        "roundtrip_success": 1,
        "semantic_fidelity": 1.0,
        "schema_error_rate": 0,
        "changed_cell_count": 0,
        "missing_cell_count": 0,
        "added_cell_count": 0,
        "import_export_fidelity": 1.0,
        "preview_accuracy": 1.0
      },
      "import_validation": {
        "valid": true,
        "errors": []
      },
      "export_validation": {
        "valid": true,
        "errors": [],
        "slip_aligned": true,
        "slip_errors": []
      },
      "semantic_diff": {
        "changed_cells": [],
        "missing_cells": [],
        "added_cells": []
      },
      "imported_state": {
        "schema_version": "0.1.0",
        "editor_id": "workshop_editor_stage0",
        "grid_id": "mg_seed_001",
        "grid_size": [
          8,
          8
        ],
        "palette": {
          "palette_id": "lcd_green",
          "colors": [
            "#07140d",
            "#5dbb63",
            "#d8ffd6"
          ],
          "background_index": 0
        },
        "slip": {
          "profile_id": "slip_lcd_seed",
          "name": "LCD Seed Companion",
          "rules": {
            "slip_version": "0.1.0",
            "profile_id": "slip_lcd_seed",
            "name": "LCD Seed Companion",
            "grid": {
              "allowed_palettes": [
                "lcd_green"
              ],
              "body_mass_min": 4,
              "body_mass_max": 24,
              "required_organ_roles": [
                "sensor",
                "expression"
              ]
            },
            "mutation": {
              "cell_mutation_rate_max": 0.15,
              "organ_shift_rate_max": 0.05,
              "palette_shift_rate_max": 0.05,
              "symmetry_break_rate_max": 0.05
            },
            "behavior": {
              "curiosity": 0.6,
              "neediness": 0.4,
              "sleepiness": 0.5
            },
            "survival_weights": {
              "stability": 0.5,
              "novelty": 0.25,
              "bond": 0.25
            }
          }
        },
        "tools": {
          "erase": {
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty"
          },
          "body": {
            "token": "B",
            "role": "body",
            "organ": "core",
            "material": "hard"
          },
          "anchor": {
            "token": "A",
            "role": "body",
            "organ": "core",
            "material": "hard"
          },
          "sensor": {
            "token": "E",
            "role": "sensor",
            "organ": "sensors",
            "material": "glass"
          },
          "expression": {
            "token": "M",
            "role": "expression",
            "organ": "expression",
            "material": "soft"
          }
        },
        "cells": [
          {
            "x": 0,
            "y": 0,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 1,
            "y": 0,
            "token": "E",
            "role": "sensor",
            "organ": "sensors",
            "material": "glass",
            "visual": "#d8ffd6",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 2,
            "y": 0,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 3,
            "y": 0,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 4,
            "y": 0,
            "token": "E",
            "role": "sensor",
            "organ": "sensors",
            "material": "glass",
            "visual": "#d8ffd6",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 5,
            "y": 0,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 6,
            "y": 0,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 7,
            "y": 0,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 0,
            "y": 1,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 1,
            "y": 1,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 2,
            "y": 1,
            "token": "B",
            "role": "body",
            "organ": "core",
            "material": "hard",
            "visual": "#5dbb63",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 3,
            "y": 1,
            "token": "B",
            "role": "body",
            "organ": "core",
            "material": "hard",
            "visual": "#5dbb63",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 4,
            "y": 1,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 5,
            "y": 1,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 6,
            "y": 1,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 7,
            "y": 1,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 0,
            "y": 2,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 1,
            "y": 2,
            "token": "B",
            "role": "body",
            "organ": "core",
            "material": "hard",
            "visual": "#5dbb63",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 2,
            "y": 2,
            "token": "A",
            "role": "body",
            "organ": "core",
            "material": "hard",
            "visual": "#5dbb63",
            "mutation_weight": 0.1,
            "animation_anchor": true,
            "locked": false
          },
          {
            "x": 3,
            "y": 2,
            "token": "B",
            "role": "body",
            "organ": "core",
            "material": "hard",
            "visual": "#5dbb63",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 4,
            "y": 2,
            "token": "B",
            "role": "body",
            "organ": "core",
            "material": "hard",
            "visual": "#5dbb63",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 5,
            "y": 2,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 6,
            "y": 2,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 7,
            "y": 2,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 0,
            "y": 3,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 1,
            "y": 3,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 2,
            "y": 3,
            "token": "B",
            "role": "body",
            "organ": "core",
            "material": "hard",
            "visual": "#5dbb63",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 3,
            "y": 3,
            "token": "B",
            "role": "body",
            "organ": "core",
            "material": "hard",
            "visual": "#5dbb63",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 4,
            "y": 3,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 5,
            "y": 3,
            "token": "M",
            "role": "expression",
            "organ": "expression",
            "material": "soft",
            "visual": "#d8ffd6",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 6,
            "y": 3,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 7,
            "y": 3,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 0,
            "y": 4,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 1,
            "y": 4,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 2,
            "y": 4,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 3,
            "y": 4,
            "token": "B",
            "role": "body",
            "organ": "core",
            "material": "hard",
            "visual": "#5dbb63",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 4,
            "y": 4,
            "token": "B",
            "role": "body",
            "organ": "core",
            "material": "hard",
            "visual": "#5dbb63",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 5,
            "y": 4,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 6,
            "y": 4,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 7,
            "y": 4,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 0,
            "y": 5,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 1,
            "y": 5,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 2,
            "y": 5,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 3,
            "y": 5,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 4,
            "y": 5,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 5,
            "y": 5,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 6,
            "y": 5,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 7,
            "y": 5,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 0,
            "y": 6,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 1,
            "y": 6,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 2,
            "y": 6,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 3,
            "y": 6,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 4,
            "y": 6,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 5,
            "y": 6,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 6,
            "y": 6,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 7,
            "y": 6,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 0,
            "y": 7,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 1,
            "y": 7,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 2,
            "y": 7,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 3,
            "y": 7,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 4,
            "y": 7,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 5,
            "y": 7,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 6,
            "y": 7,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          },
          {
            "x": 7,
            "y": 7,
            "token": ".",
            "role": "empty",
            "organ": null,
            "material": "empty",
            "visual": "#07140d",
            "mutation_weight": 0,
            "animation_anchor": false,
            "locked": false
          }
        ],
        "mutation": {
          "cell_mutation_rate": 0.05,
          "organ_shift_rate": 0.02,
          "palette_shift_rate": 0.01,
          "symmetry_break_rate": 0.01
        },
        "metadata": {
          "source": "workshop_roundtrip_import",
          "seed_grid_id": "mg_seed_001",
          "imported_grid_id": "mg_seed_001"
        }
      },
      "roundtrip_export": {
        "grid_id": "workshop_roundtrip_export_stage0",
        "schema_version": "0.1.0",
        "parent_grid_id": "mg_seed_001",
        "grid_size": [
          8,
          8
        ],
        "cells": [
          {
            "x": 1,
            "y": 0,
            "visual": "#d8ffd6",
            "role": "eye",
            "material": "glass",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "sensors",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 4,
            "y": 0,
            "visual": "#d8ffd6",
            "role": "eye",
            "material": "glass",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "sensors",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 2,
            "y": 1,
            "visual": "#5dbb63",
            "role": "body",
            "material": "hard",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 3,
            "y": 1,
            "visual": "#5dbb63",
            "role": "body",
            "material": "hard",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 1,
            "y": 2,
            "visual": "#5dbb63",
            "role": "body",
            "material": "hard",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 2,
            "y": 2,
            "visual": "#5dbb63",
            "role": "body",
            "material": "hard",
            "mutation_weight": 0.1,
            "animation_anchor": true,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 3,
            "y": 2,
            "visual": "#5dbb63",
            "role": "body",
            "material": "hard",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 4,
            "y": 2,
            "visual": "#5dbb63",
            "role": "body",
            "material": "hard",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 2,
            "y": 3,
            "visual": "#5dbb63",
            "role": "body",
            "material": "hard",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 3,
            "y": 3,
            "visual": "#5dbb63",
            "role": "body",
            "material": "hard",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 5,
            "y": 3,
            "visual": "#d8ffd6",
            "role": "mouth",
            "material": "soft",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "expression",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 3,
            "y": 4,
            "visual": "#5dbb63",
            "role": "body",
            "material": "hard",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": false
          },
          {
            "x": 4,
            "y": 4,
            "visual": "#5dbb63",
            "role": "body",
            "material": "hard",
            "mutation_weight": 0.1,
            "animation_anchor": false,
            "organ": "core",
            "stress": 0,
            "damage": 0,
            "locked": false
          }
        ],
        "organs": {
          "core": {
            "role": "body_core",
            "cells": [
              [
                2,
                1
              ],
              [
                3,
                1
              ],
              [
                1,
                2
              ],
              [
                2,
                2
              ],
              [
                3,
                2
              ],
              [
                4,
                2
              ],
              [
                2,
                3
              ],
              [
                3,
                3
              ],
              [
                3,
                4
              ],
              [
                4,
                4
              ]
            ],
            "required": true
          },
          "sensors": {
            "role": "sensor",
            "cells": [
              [
                1,
                0
              ],
              [
                4,
                0
              ]
            ],
            "required": true
          },
          "expression": {
            "role": "expression",
            "cells": [
              [
                5,
                3
              ]
            ],
            "required": false
          }
        },
        "palette": {
          "palette_id": "lcd_green",
          "colors": [
            "#07140d",
            "#5dbb63",
            "#d8ffd6"
          ],
          "background_index": 0
        },
        "mutation": {
          "cell_mutation_rate": 0.05,
          "organ_shift_rate": 0.02,
          "palette_shift_rate": 0.01,
          "symmetry_break_rate": 0.01
        },
        "lineage": {
          "generation": 1,
          "ancestor_ids": [
            "mg_seed_001"
          ],
          "mutation_events": [
            "workshop_semantic_authoring"
          ]
        },
        "metadata": {
          "source": "workshop_editor_lab",
          "slip_profile_id": "slip_lcd_seed",
          "seed_grid_id": "mg_seed_001"
        }
      },
      "decision": {
        "status": "prototype",
        "reason": "The semantic workshop can import a valid grid, export it again, and preserve semantic fidelity under the active SLIP profile."
      }
    },
    "imported_state": {
      "schema_version": "0.1.0",
      "editor_id": "workshop_editor_stage0",
      "grid_id": "mg_seed_001",
      "grid_size": [
        8,
        8
      ],
      "palette": {
        "palette_id": "lcd_green",
        "colors": [
          "#07140d",
          "#5dbb63",
          "#d8ffd6"
        ],
        "background_index": 0
      },
      "slip": {
        "profile_id": "slip_lcd_seed",
        "name": "LCD Seed Companion",
        "rules": {
          "slip_version": "0.1.0",
          "profile_id": "slip_lcd_seed",
          "name": "LCD Seed Companion",
          "grid": {
            "allowed_palettes": [
              "lcd_green"
            ],
            "body_mass_min": 4,
            "body_mass_max": 24,
            "required_organ_roles": [
              "sensor",
              "expression"
            ]
          },
          "mutation": {
            "cell_mutation_rate_max": 0.15,
            "organ_shift_rate_max": 0.05,
            "palette_shift_rate_max": 0.05,
            "symmetry_break_rate_max": 0.05
          },
          "behavior": {
            "curiosity": 0.6,
            "neediness": 0.4,
            "sleepiness": 0.5
          },
          "survival_weights": {
            "stability": 0.5,
            "novelty": 0.25,
            "bond": 0.25
          }
        }
      },
      "tools": {
        "erase": {
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty"
        },
        "body": {
          "token": "B",
          "role": "body",
          "organ": "core",
          "material": "hard"
        },
        "anchor": {
          "token": "A",
          "role": "body",
          "organ": "core",
          "material": "hard"
        },
        "sensor": {
          "token": "E",
          "role": "sensor",
          "organ": "sensors",
          "material": "glass"
        },
        "expression": {
          "token": "M",
          "role": "expression",
          "organ": "expression",
          "material": "soft"
        }
      },
      "cells": [
        {
          "x": 0,
          "y": 0,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 1,
          "y": 0,
          "token": "E",
          "role": "sensor",
          "organ": "sensors",
          "material": "glass",
          "visual": "#d8ffd6",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 2,
          "y": 0,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 3,
          "y": 0,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 4,
          "y": 0,
          "token": "E",
          "role": "sensor",
          "organ": "sensors",
          "material": "glass",
          "visual": "#d8ffd6",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 5,
          "y": 0,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 6,
          "y": 0,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 7,
          "y": 0,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 0,
          "y": 1,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 1,
          "y": 1,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 2,
          "y": 1,
          "token": "B",
          "role": "body",
          "organ": "core",
          "material": "hard",
          "visual": "#5dbb63",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 3,
          "y": 1,
          "token": "B",
          "role": "body",
          "organ": "core",
          "material": "hard",
          "visual": "#5dbb63",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 4,
          "y": 1,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 5,
          "y": 1,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 6,
          "y": 1,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 7,
          "y": 1,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 0,
          "y": 2,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 1,
          "y": 2,
          "token": "B",
          "role": "body",
          "organ": "core",
          "material": "hard",
          "visual": "#5dbb63",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 2,
          "y": 2,
          "token": "A",
          "role": "body",
          "organ": "core",
          "material": "hard",
          "visual": "#5dbb63",
          "mutation_weight": 0.1,
          "animation_anchor": true,
          "locked": false
        },
        {
          "x": 3,
          "y": 2,
          "token": "B",
          "role": "body",
          "organ": "core",
          "material": "hard",
          "visual": "#5dbb63",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 4,
          "y": 2,
          "token": "B",
          "role": "body",
          "organ": "core",
          "material": "hard",
          "visual": "#5dbb63",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 5,
          "y": 2,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 6,
          "y": 2,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 7,
          "y": 2,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 0,
          "y": 3,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 1,
          "y": 3,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 2,
          "y": 3,
          "token": "B",
          "role": "body",
          "organ": "core",
          "material": "hard",
          "visual": "#5dbb63",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 3,
          "y": 3,
          "token": "B",
          "role": "body",
          "organ": "core",
          "material": "hard",
          "visual": "#5dbb63",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 4,
          "y": 3,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 5,
          "y": 3,
          "token": "M",
          "role": "expression",
          "organ": "expression",
          "material": "soft",
          "visual": "#d8ffd6",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 6,
          "y": 3,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 7,
          "y": 3,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 0,
          "y": 4,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 1,
          "y": 4,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 2,
          "y": 4,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 3,
          "y": 4,
          "token": "B",
          "role": "body",
          "organ": "core",
          "material": "hard",
          "visual": "#5dbb63",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 4,
          "y": 4,
          "token": "B",
          "role": "body",
          "organ": "core",
          "material": "hard",
          "visual": "#5dbb63",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 5,
          "y": 4,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 6,
          "y": 4,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 7,
          "y": 4,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 0,
          "y": 5,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 1,
          "y": 5,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 2,
          "y": 5,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 3,
          "y": 5,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 4,
          "y": 5,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 5,
          "y": 5,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 6,
          "y": 5,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 7,
          "y": 5,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 0,
          "y": 6,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 1,
          "y": 6,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 2,
          "y": 6,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 3,
          "y": 6,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 4,
          "y": 6,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 5,
          "y": 6,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 6,
          "y": 6,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 7,
          "y": 6,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 0,
          "y": 7,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 1,
          "y": 7,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 2,
          "y": 7,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 3,
          "y": 7,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 4,
          "y": 7,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 5,
          "y": 7,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 6,
          "y": 7,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        },
        {
          "x": 7,
          "y": 7,
          "token": ".",
          "role": "empty",
          "organ": null,
          "material": "empty",
          "visual": "#07140d",
          "mutation_weight": 0,
          "animation_anchor": false,
          "locked": false
        }
      ],
      "mutation": {
        "cell_mutation_rate": 0.05,
        "organ_shift_rate": 0.02,
        "palette_shift_rate": 0.01,
        "symmetry_break_rate": 0.01
      },
      "metadata": {
        "source": "workshop_roundtrip_import",
        "seed_grid_id": "mg_seed_001",
        "imported_grid_id": "mg_seed_001"
      }
    },
    "roundtrip_export": {
      "grid_id": "workshop_roundtrip_export_stage0",
      "schema_version": "0.1.0",
      "parent_grid_id": "mg_seed_001",
      "grid_size": [
        8,
        8
      ],
      "cells": [
        {
          "x": 1,
          "y": 0,
          "visual": "#d8ffd6",
          "role": "eye",
          "material": "glass",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "sensors",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 4,
          "y": 0,
          "visual": "#d8ffd6",
          "role": "eye",
          "material": "glass",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "sensors",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 2,
          "y": 1,
          "visual": "#5dbb63",
          "role": "body",
          "material": "hard",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "core",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 3,
          "y": 1,
          "visual": "#5dbb63",
          "role": "body",
          "material": "hard",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "core",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 1,
          "y": 2,
          "visual": "#5dbb63",
          "role": "body",
          "material": "hard",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "core",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 2,
          "y": 2,
          "visual": "#5dbb63",
          "role": "body",
          "material": "hard",
          "mutation_weight": 0.1,
          "animation_anchor": true,
          "organ": "core",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 3,
          "y": 2,
          "visual": "#5dbb63",
          "role": "body",
          "material": "hard",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "core",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 4,
          "y": 2,
          "visual": "#5dbb63",
          "role": "body",
          "material": "hard",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "core",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 2,
          "y": 3,
          "visual": "#5dbb63",
          "role": "body",
          "material": "hard",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "core",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 3,
          "y": 3,
          "visual": "#5dbb63",
          "role": "body",
          "material": "hard",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "core",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 5,
          "y": 3,
          "visual": "#d8ffd6",
          "role": "mouth",
          "material": "soft",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "expression",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 3,
          "y": 4,
          "visual": "#5dbb63",
          "role": "body",
          "material": "hard",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "core",
          "stress": 0,
          "damage": 0,
          "locked": false
        },
        {
          "x": 4,
          "y": 4,
          "visual": "#5dbb63",
          "role": "body",
          "material": "hard",
          "mutation_weight": 0.1,
          "animation_anchor": false,
          "organ": "core",
          "stress": 0,
          "damage": 0,
          "locked": false
        }
      ],
      "organs": {
        "core": {
          "role": "body_core",
          "cells": [
            [
              2,
              1
            ],
            [
              3,
              1
            ],
            [
              1,
              2
            ],
            [
              2,
              2
            ],
            [
              3,
              2
            ],
            [
              4,
              2
            ],
            [
              2,
              3
            ],
            [
              3,
              3
            ],
            [
              3,
              4
            ],
            [
              4,
              4
            ]
          ],
          "required": true
        },
        "sensors": {
          "role": "sensor",
          "cells": [
            [
              1,
              0
            ],
            [
              4,
              0
            ]
          ],
          "required": true
        },
        "expression": {
          "role": "expression",
          "cells": [
            [
              5,
              3
            ]
          ],
          "required": false
        }
      },
      "palette": {
        "palette_id": "lcd_green",
        "colors": [
          "#07140d",
          "#5dbb63",
          "#d8ffd6"
        ],
        "background_index": 0
      },
      "mutation": {
        "cell_mutation_rate": 0.05,
        "organ_shift_rate": 0.02,
        "palette_shift_rate": 0.01,
        "symmetry_break_rate": 0.01
      },
      "lineage": {
        "generation": 1,
        "ancestor_ids": [
          "mg_seed_001"
        ],
        "mutation_events": [
          "workshop_semantic_authoring"
        ]
      },
      "metadata": {
        "source": "workshop_editor_lab",
        "slip_profile_id": "slip_lcd_seed",
        "seed_grid_id": "mg_seed_001"
      }
    }
  }
};
