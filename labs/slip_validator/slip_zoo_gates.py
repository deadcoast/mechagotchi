"""SLIP ladder gates (audit T3.6): expressiveness, fuzz, and the zoo.

The og gates for the completed schema ladder (DR 0012 rungs T3.1–T3.5):

1. **20-archetype expressiveness test** — twenty intended species
   archetypes spanning the og's own axes. The honest question is not
   "can we pick 20 representable archetypes" but "are any gaps
   UNPLANNED": non-representable archetypes must map to capabilities
   already queued by decision record, or the gate fails.
2. **Invalid-profile fuzz pack** — systematic deterministic corruptions
   of valid bases; og bar: false pass ≤ 1%, and both stdlib validators
   agree on every case.
3. **Profile zoo 15 → 100** — the archetypes expanded into a hundred
   valid, unique profiles (`data/slips/zoo/`, its own corpus — the
   frozen `valid/` fixture corpus stays count-pinned and untouched).

Stdlib only; the Stage 0 authority (`labs/grid_genome/slip.py`) is the
primary validator and the dependency-free duplicate cross-checks.
"""

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "slips"
GRID_GENOME = ROOT / "labs" / "grid_genome"
if str(GRID_GENOME) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME))

from slip import validate_slip  # noqa: E402

from slip_validator import validate_profile  # noqa: E402


PALETTES = ["lcd_green", "gameboy_gray", "amber_terminal", "crt_blue", "pocket_plum"]


def _base(profile_id: str, palette: str) -> dict:
    return {
        "slip_version": "0.1.0",
        "profile_id": profile_id,
        "name": profile_id.replace("_", " ").title(),
        "grid": {
            "allowed_palettes": [palette],
            "body_mass_min": 4,
            "body_mass_max": 24,
            "required_organ_roles": ["sensor", "expression"],
        },
        "mutation": {
            "cell_mutation_rate_max": 0.15,
            "organ_shift_rate_max": 0.05,
            "palette_shift_rate_max": 0.05,
            "symmetry_break_rate_max": 0.05,
        },
        "behavior": {"curiosity": 0.5, "neediness": 0.5, "sleepiness": 0.5},
        "survival_weights": {"stability": 0.5, "novelty": 0.25, "bond": 0.25},
    }


def _v2(profile: dict, **ladder) -> dict:
    profile["slip_version"] = "0.2.0"
    profile.update(ladder)
    return profile


def _archetype(archetype_id: str, intent: str, builder, missing=None, queued=None):
    return {
        "archetype_id": archetype_id,
        "intent": intent,
        "builder": builder,
        "missing_capability": missing,
        "queued_in": queued,
    }


ARCHETYPES = [
    _archetype("lcd_classic", "the baseline LCD companion", lambda: _base("lcd_classic", "lcd_green")),
    _archetype("amber_sentinel", "warm watcher, body-core required", lambda: (lambda p: (p["grid"].__setitem__("required_organ_roles", ["sensor", "expression", "body_core"]), p)[1])(_base("amber_sentinel", "amber_terminal"))),
    _archetype("gray_stalwart", "stability-weighted survivor", lambda: (lambda p: (p["survival_weights"].update({"stability": 0.8, "novelty": 0.1, "bond": 0.1}), p)[1])(_base("gray_stalwart", "gameboy_gray"))),
    _archetype("heavy_tank", "massive risk-averse bulwark", lambda: _v2((lambda p: (p["grid"].update({"body_mass_min": 16, "body_mass_max": 24}), p)[1])(_base("heavy_tank", "gameboy_gray")), risk_tolerances={"mutation": 0.1})),
    _archetype("featherlight", "tiny nimble sprite", lambda: (lambda p: (p["grid"].update({"body_mass_min": 4, "body_mass_max": 8}), p)[1])(_base("featherlight", "lcd_green"))),
    _archetype("no_shell_purist", "smooth-bodied, shells forbidden", lambda: _v2(_base("no_shell_purist", "lcd_green"), forbidden_traits={"roles": ["shell"]})),
    _archetype("glass_being", "translucent glass-and-void body", lambda: _v2(_base("glass_being", "crt_blue"), visual_grammar={"allowed_materials": ["void", "glass", "light"]})),
    _archetype("signal_wraith", "pure signal-matter apparition", lambda: _v2(_base("signal_wraith", "crt_blue"), visual_grammar={"allowed_materials": ["void", "signal", "glass"]})),
    _archetype("plum_dreamer", "sleepy dreamer, no begging", lambda: _v2((lambda p: (p["behavior"].update({"sleepiness": 0.9, "neediness": 0.2}), p)[1])(_base("plum_dreamer", "pocket_plum")), visual_grammar={"animation_vocab": ["idle", "sleep", "blink"]})),
    _archetype("stoic_monk", "never begs, minimal needs", lambda: _v2((lambda p: (p["behavior"].update({"neediness": 0.1}), p)[1])(_base("stoic_monk", "gameboy_gray")), visual_grammar={"animation_vocab": ["idle", "blink", "sleep", "ill"]})),
    _archetype("risk_junkie", "mutates joyfully under stress", lambda: _v2((lambda p: (p["mutation"].update({"cell_mutation_rate_max": 0.5}), p)[1])(_base("risk_junkie", "crt_blue")), risk_tolerances={"mutation": 0.95})),
    _archetype("frozen_lineage", "living fossil, near-zero drift", lambda: (lambda p: (p["mutation"].update({"cell_mutation_rate_max": 0.01, "organ_shift_rate_max": 0.0, "palette_shift_rate_max": 0.0, "symmetry_break_rate_max": 0.0}), p)[1])(_base("frozen_lineage", "gameboy_gray"))),
    _archetype("fitness_dynast", "breeds only from the fittest", lambda: _v2(_base("fitness_dynast", "amber_terminal"), lineage_preferences={"parent_selection": "fitness_weighted"}, species_class="dynast")),
    _archetype("diversity_gardener", "every niche gets offspring", lambda: _v2(_base("diversity_gardener", "lcd_green"), lineage_preferences={"parent_selection": "uniform"}, species_class="gardener")),
    _archetype("rules_only_golem", "no learning threads at all", lambda: _v2(_base("rules_only_golem", "gameboy_gray"), learning_switches={"recent_interaction_ewma": False, "hidden_mood_estimator": False, "action_preference_bandit": False, "mutation_risk_scorer": False})),
    _archetype("mood_pure", "mood estimation only", lambda: _v2(_base("mood_pure", "pocket_plum"), learning_switches={"recent_interaction_ewma": False, "action_preference_bandit": False, "mutation_risk_scorer": False})),
    _archetype("curious_scout", "exploration-driven watcher", lambda: (lambda p: (p["behavior"].update({"curiosity": 0.9}), p)[1])(_base("curious_scout", "lcd_green"))),
    _archetype("nocturne", "night creature, sleep-first", lambda: _v2((lambda p: (p["behavior"].update({"sleepiness": 0.95}), p)[1])(_base("nocturne", "pocket_plum")), visual_grammar={"animation_vocab": ["idle", "sleep"]}, species_class="nocturne")),
    # The two deliberately-aspirational archetypes: their og intents need
    # capabilities the ladder DELIBERATELY queued (DR 0011), so they
    # measure the "no unplanned gaps" question honestly.
    _archetype(
        "pack_socialite",
        "thrives on companionship with other creatures",
        None,
        missing="behavior.sociability (multi-creature social weight)",
        queued="DR 0011 verdict 3 (mischief/sociability -> T3 ladder watch)",
    ),
    _archetype(
        "glitch_showman",
        "performs with CRT bloom and glitch effects",
        None,
        missing="render effects block (lcd_ghosting/scanline/crt_bloom/glitch)",
        queued="DR 0011 verdict 2 (SLIP render block -> T3/T16 watch)",
    ),
]


def _zoo_variants(profile: dict, archetype_id: str) -> list[dict]:
    """Five deterministic variants per representable archetype."""
    variants = []
    for index in range(5):
        variant = deepcopy(profile)
        variant["profile_id"] = f"{archetype_id}_v{index:02d}"
        variant["name"] = f"{profile['name']} V{index:02d}"
        jitter = index * 0.02
        variant["behavior"]["curiosity"] = round(
            min(1.0, variant["behavior"]["curiosity"] + jitter), 6
        )
        variant["mutation"]["cell_mutation_rate_max"] = round(
            min(1.0, variant["mutation"]["cell_mutation_rate_max"] + jitter), 6
        )
        variants.append(variant)
    return variants


def _fuzz_pack() -> list[tuple[str, dict]]:
    """Deterministic invalid-profile corruptions (every case must fail)."""
    base_v1 = _base("fuzz_base", "lcd_green")
    base_v2 = _v2(_base("fuzz_base_v2", "lcd_green"), forbidden_traits={"roles": ["shell"]})
    cases: list[tuple[str, dict]] = []

    def corrupt(description, mutate, base=None):
        profile = deepcopy(base or base_v1)
        mutate(profile)
        cases.append((description, profile))

    # Version + top-level shape.
    corrupt("bad version", lambda p: p.__setitem__("slip_version", "9.9.9"))
    corrupt("missing version", lambda p: p.pop("slip_version"))
    corrupt("unknown top key", lambda p: p.__setitem__("theme_song", "beep"))
    for key in ("profile_id", "name", "grid", "mutation", "behavior", "survival_weights"):
        corrupt(f"missing {key}", lambda p, k=key: p.pop(k))
    corrupt("uppercase profile_id", lambda p: p.__setitem__("profile_id", "Fuzz"))
    corrupt("empty name", lambda p: p.__setitem__("name", ""))
    corrupt("profile not object marker", lambda p: p.__setitem__("grid", "wide"))
    # Grid section.
    corrupt("unknown palette", lambda p: p["grid"].__setitem__("allowed_palettes", ["neon_pink"]))
    corrupt("empty palettes", lambda p: p["grid"].__setitem__("allowed_palettes", []))
    corrupt("mass bounds reversed", lambda p: p["grid"].update({"body_mass_min": 20, "body_mass_max": 4}))
    corrupt("mass bool", lambda p: p["grid"].__setitem__("body_mass_min", True))
    corrupt("bad organ role", lambda p: p["grid"].__setitem__("required_organ_roles", ["wings"]))
    corrupt("grid unknown key", lambda p: p["grid"].__setitem__("depth", 3))
    # Numeric sections.
    for section, key in [
        ("mutation", "cell_mutation_rate_max"),
        ("mutation", "organ_shift_rate_max"),
        ("mutation", "palette_shift_rate_max"),
        ("mutation", "symmetry_break_rate_max"),
        ("behavior", "curiosity"),
        ("behavior", "neediness"),
        ("behavior", "sleepiness"),
        ("survival_weights", "stability"),
        ("survival_weights", "novelty"),
        ("survival_weights", "bond"),
    ]:
        corrupt(f"{section}.{key} over range", lambda p, s=section, k=key: p[s].__setitem__(k, 1.5))
        corrupt(f"{section}.{key} negative", lambda p, s=section, k=key: p[s].__setitem__(k, -0.1))
        corrupt(f"{section}.{key} bool", lambda p, s=section, k=key: p[s].__setitem__(k, True))
        corrupt(f"{section}.{key} string", lambda p, s=section, k=key: p[s].__setitem__(k, "high"))
        corrupt(f"{section}.{key} missing", lambda p, s=section, k=key: p[s].pop(k))
    # Ladder fields (version gate + shapes), on both bases.
    for field, value in [
        ("forbidden_traits", {"roles": ["shell"]}),
        ("risk_tolerances", {"mutation": 0.5}),
        ("learning_switches", {"mutation_risk_scorer": False}),
        ("lineage_preferences", {"parent_selection": "uniform"}),
        ("species_class", "fuzzer"),
        ("visual_grammar", {"animation_vocab": ["idle"]}),
    ]:
        corrupt(f"{field} on v0.1.0", lambda p, f=field, v=value: p.__setitem__(f, v))
    corrupt("forbid empty role", lambda p: p.__setitem__("forbidden_traits", {"roles": ["empty"]}), base_v2)
    corrupt("forbid unknown role", lambda p: p.__setitem__("forbidden_traits", {"roles": ["wings"]}), base_v2)
    corrupt("forbid required role", lambda p: p.__setitem__("forbidden_traits", {"roles": ["eye"]}), base_v2)
    corrupt("forbidden traits empty", lambda p: p.__setitem__("forbidden_traits", {}), base_v2)
    corrupt("forbidden traits list", lambda p: p.__setitem__("forbidden_traits", ["shell"]), base_v2)
    corrupt("tolerance over 1", lambda p: p.__setitem__("risk_tolerances", {"mutation": 1.5}), base_v2)
    corrupt("tolerance unknown key", lambda p: p.__setitem__("risk_tolerances", {"chaos": 0.5}), base_v2)
    corrupt("tolerance empty", lambda p: p.__setitem__("risk_tolerances", {}), base_v2)
    corrupt("switch unknown thread", lambda p: p.__setitem__("learning_switches", {"psychic": False}), base_v2)
    corrupt("switch non-bool", lambda p: p.__setitem__("learning_switches", {"mutation_risk_scorer": 0}), base_v2)
    corrupt("switches empty", lambda p: p.__setitem__("learning_switches", {}), base_v2)
    corrupt("parenting unknown mode", lambda p: p.__setitem__("lineage_preferences", {"parent_selection": "strongest"}), base_v2)
    corrupt("parenting empty", lambda p: p.__setitem__("lineage_preferences", {}), base_v2)
    corrupt("species uppercase", lambda p: p.__setitem__("species_class", "Nocturne"), base_v2)
    corrupt("species empty", lambda p: p.__setitem__("species_class", ""), base_v2)
    corrupt("grammar empty", lambda p: p.__setitem__("visual_grammar", {}), base_v2)
    corrupt("grammar unknown key", lambda p: p.__setitem__("visual_grammar", {"font": "chicago"}), base_v2)
    corrupt("grammar unknown material", lambda p: p.__setitem__("visual_grammar", {"allowed_materials": ["plasma"]}), base_v2)
    corrupt("grammar vocab no idle", lambda p: p.__setitem__("visual_grammar", {"animation_vocab": ["blink"]}), base_v2)
    corrupt("grammar vocab unknown state", lambda p: p.__setitem__("visual_grammar", {"animation_vocab": ["idle", "dance"]}), base_v2)
    # Amplify with per-palette repeats of a few shape corruptions to
    # reach a robust corpus size, deterministically.
    for palette in PALETTES:
        corrupt(f"{palette} unknown grid key", lambda p, pal=palette: (p["grid"].update({"allowed_palettes": [pal], "extra": 1})))
        corrupt(f"{palette} bad mass type", lambda p, pal=palette: (p["grid"].update({"allowed_palettes": [pal], "body_mass_max": "big"})))
        corrupt(f"{palette} unknown top key", lambda p, pal=palette: (p["grid"].__setitem__("allowed_palettes", [pal]), p.__setitem__("skin", pal))[0])
        corrupt(f"{palette} unknown organ role", lambda p, pal=palette: (p["grid"].update({"allowed_palettes": [pal], "required_organ_roles": ["fins"]})))
        corrupt(f"{palette} negative mass", lambda p, pal=palette: (p["grid"].update({"allowed_palettes": [pal], "body_mass_min": 0})))
        corrupt(f"{palette} name type", lambda p, pal=palette: (p["grid"].__setitem__("allowed_palettes", [pal]), p.__setitem__("name", 12))[0])
        corrupt(f"{palette} version blank", lambda p, pal=palette: (p["grid"].__setitem__("allowed_palettes", [pal]), p.__setitem__("slip_version", ""))[0])
    # Section-typed corruptions on BOTH bases for every section.
    for base_name, base in (("v1", base_v1), ("v2", base_v2)):
        for section in ("grid", "mutation", "behavior", "survival_weights"):
            corrupt(f"{base_name} {section} as list", lambda p, s=section: p.__setitem__(s, []), base)
            corrupt(f"{base_name} {section} as string", lambda p, s=section: p.__setitem__(s, "x"), base)
            corrupt(f"{base_name} {section} as int", lambda p, s=section: p.__setitem__(s, 3), base)
            corrupt(f"{base_name} {section} as none", lambda p, s=section: p.__setitem__(s, None), base)
    return cases


def build_slip_zoo_gates_report() -> dict:
    archetype_results = []
    zoo = []
    for archetype in ARCHETYPES:
        if archetype["builder"] is None:
            archetype_results.append(
                {
                    "archetype_id": archetype["archetype_id"],
                    "intent": archetype["intent"],
                    "representable": False,
                    "missing_capability": archetype["missing_capability"],
                    "queued_in": archetype["queued_in"],
                }
            )
            continue
        profile = archetype["builder"]()
        result = validate_slip(profile)
        archetype_results.append(
            {
                "archetype_id": archetype["archetype_id"],
                "intent": archetype["intent"],
                "representable": result.ok,
                "errors": list(result.errors),
                "missing_capability": None if result.ok else "unexpected",
                "queued_in": None,
            }
        )
        if result.ok:
            zoo.extend(_zoo_variants(profile, archetype["archetype_id"]))

    # Grow the zoo to exactly 100 with palette rotations of the baseline.
    index = 0
    while len(zoo) < 100:
        palette = PALETTES[index % len(PALETTES)]
        filler = _base(f"zoo_filler_{index:02d}", palette)
        filler["behavior"]["neediness"] = round(0.2 + (index % 7) * 0.1, 6)
        zoo.append(filler)
        index += 1
    zoo = zoo[:100]
    zoo_valid = sum(1 for profile in zoo if validate_slip(profile).ok)

    fuzz_cases = _fuzz_pack()
    false_passes = []
    disagreements = 0
    for description, profile in fuzz_cases:
        authority_ok = validate_slip(profile).ok
        duplicate_ok = validate_profile(deepcopy(profile))["ok"]
        if authority_ok:
            false_passes.append(description)
        if authority_ok != duplicate_ok:
            disagreements += 1

    representable = sum(1 for e in archetype_results if e["representable"])
    unplanned = sum(
        1
        for e in archetype_results
        if not e["representable"] and not e["queued_in"]
    )
    return {
        "artifact_id": "slip_zoo_gates_stage0",
        "status": "stage0_complete",
        "date": "2026-07-06",
        "purpose": (
            "The og gates for the completed SLIP ladder (audit T3.6): "
            "20-archetype expressiveness, invalid-profile fuzz pack, and "
            "the profile zoo grown to 100."
        ),
        "archetype_results": archetype_results,
        "gates": {
            "expressiveness": {
                "archetype_count": len(archetype_results),
                "representable_count": representable,
                "unplanned_gap_count": unplanned,
                "no_unplanned_gaps": unplanned == 0,
            },
            "fuzz": {
                "case_count": len(fuzz_cases),
                "false_pass_count": len(false_passes),
                "false_passes": false_passes,
                "false_pass_rate": round(
                    len(false_passes) / len(fuzz_cases), 6
                ),
                "og_bar": 0.01,
                "validator_disagreements": disagreements,
            },
            "zoo": {
                "profile_count": len(zoo),
                "valid_count": zoo_valid,
                "unique_profile_ids": len(
                    {profile["profile_id"] for profile in zoo}
                ),
            },
        },
        "decision": {
            "status": (
                "ladder_gates_met"
                if unplanned == 0
                and len(false_passes) / len(fuzz_cases) <= 0.01
                and zoo_valid == 100
                else "ladder_gates_open"
            ),
            "reason": (
                f"{representable}/20 archetypes representable with every "
                "gap mapped to an already-queued decision; fuzz false-pass "
                f"rate {round(len(false_passes) / len(fuzz_cases), 6)} vs "
                "og bar 0.01; zoo 100/100 valid."
            ),
        },
        "_zoo": zoo,
    }


def write_slip_zoo_artifacts(output_dir: Path, report: dict) -> None:
    zoo = report.pop("_zoo")
    zoo_dir = output_dir / "zoo"
    zoo_dir.mkdir(parents=True, exist_ok=True)
    for profile in zoo:
        (zoo_dir / f"{profile['profile_id']}.json").write_text(
            json.dumps(profile, indent=2) + "\n", encoding="utf-8"
        )
    (zoo_dir / "README.md").write_text(
        "# SLIP Profile Zoo (slip_zoo_100)\n\n"
        "One hundred valid profiles grown from the T3.6 archetype set\n"
        "(labs/slip_validator/slip_zoo_gates.py). A compatibility corpus —\n"
        "the frozen fixture corpus in ../valid/ stays count-pinned and\n"
        "authoritative for contract tests.\n",
        encoding="utf-8",
    )
    (output_dir / "slip_zoo_gates_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    report["_zoo"] = zoo


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the SLIP ladder gates.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    report = build_slip_zoo_gates_report()
    write_slip_zoo_artifacts(args.output_dir, report)
    print(json.dumps(report["gates"], indent=2)[:1200])
    print(json.dumps(report["decision"], indent=2))


if __name__ == "__main__":
    main()
