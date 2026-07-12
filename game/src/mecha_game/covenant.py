"""Covenant spending — the progression is FELT (F7, DR 0021 step 2).

The session lab's proven `covenant_budget`/`apply_covenant_change`
semantics (labs/game_loop/session_runner.py — mirrored, never
imported): the Keeper's spendable budget is a PURE function of the
campaign's BASE covenant, its base engine parameters, and the earned
unlock facts; palettes unlock per niche-mastery tier, thinking depth
per bloodline tier on the authority's real 2-tick floor,
population/generation caps double per quality-diversity tier, and the
legibility blend steps with its tiers. Over-budget requests are
rejected with named violations and NOTHING is applied; every accepted
covenant passes `mecha_engine.slip.validate_slip` (the authority's
refusals verbatim). Deferred axes are named, never silently dropped.
"""

from __future__ import annotations

import json

from mecha_engine.slip import validate_slip

from mecha_game.campaign import legibility_blend_for

# Mirrored session-lab tuning data (DR 0021's progression table).
PALETTE_UNLOCK_ORDER = (
    "amber_terminal",
    "crt_blue",
    "pocket_plum",
)
DELIBERATION_CONFIDENCE_DEFAULT = 0.72


def _max_tier(unlock_state: list[dict], axis: str) -> int:
    return max(
        (fact["tier"] for fact in unlock_state if fact["axis"] == axis),
        default=0,
    )


def covenant_budget(
    base_profile: dict,
    base_engine_parameters: dict,
    unlock_state: list[dict],
) -> dict:
    """The Keeper's spendable budget — a pure function of base
    covenant + base parameters + earned facts."""
    niche_tier = _max_tier(unlock_state, "niche_mastery")
    bloodline_tier = _max_tier(unlock_state, "bloodline_depth")
    qd_tier = _max_tier(unlock_state, "quality_diversity")
    base_palettes = list(base_profile["grid"]["allowed_palettes"])
    unlocked = [
        palette
        for palette in PALETTE_UNLOCK_ORDER[:niche_tier]
        if palette not in base_palettes
    ]
    return {
        "allowed_palettes": base_palettes + unlocked,
        # The authority's deliberation floor is 2 ticks (R1's schema):
        # tier 1 unlocks the minimum thinking depth, each further tier
        # deepens it by one — DR 0021's "+1 per tier" on the real floor.
        "deliberation_max_ticks": (
            bloodline_tier + 1 if bloodline_tier >= 1 else 0
        ),
        "population_cap": base_engine_parameters["population"]
        * 2**qd_tier,
        "generation_cap": base_engine_parameters["generations"]
        * 2**qd_tier,
        "legibility_blend": legibility_blend_for(unlock_state),
        "deferred": {
            "organ_role_budget": (
                "awaiting an allowed_roles SLIP field (DR 0011 ladder "
                "candidate) — the axis unlocks palettes only for now"
            ),
            "harsher_forecasts": (
                "storm_record tiers await weather sources beyond the "
                "three shipped forecasts (real CuBFF exports included)"
            ),
        },
    }


def apply_covenant_change(
    keeper_campaign,
    *,
    allowed_palettes: list[str] | None = None,
    deliberation_max_ticks: int | None = None,
    population: int | None = None,
    generations: int | None = None,
) -> dict:
    """Adjust the ACTIVE campaign's covenant within the EARNED budget.

    Enforced by the same authority validator as every covenant;
    over-budget requests are rejected with named violations and
    NOTHING is applied. Past eras stay reproducible — the ledger
    stores each era's profile verbatim.
    """
    budget = keeper_campaign.budget()
    violations: list[str] = []
    if allowed_palettes is not None:
        for palette in allowed_palettes:
            if palette not in budget["allowed_palettes"]:
                violations.append(
                    f"palette {palette} is not in the earned budget"
                )
        if not allowed_palettes:
            violations.append("the covenant needs at least one palette")
    if deliberation_max_ticks is not None and (
        deliberation_max_ticks > budget["deliberation_max_ticks"]
        or deliberation_max_ticks < 0
        or deliberation_max_ticks == 1  # below the authority's floor of 2
    ):
        violations.append(
            f"deliberation_max_ticks {deliberation_max_ticks} exceeds the "
            f"earned budget {budget['deliberation_max_ticks']} (0 = none; "
            "the authority's floor is 2)"
        )
    if population is not None and not (
        1 <= population <= budget["population_cap"]
    ):
        violations.append(
            f"population {population} exceeds the earned cap "
            f"{budget['population_cap']}"
        )
    if generations is not None and not (
        1 <= generations <= budget["generation_cap"]
    ):
        violations.append(
            f"generations {generations} exceeds the earned cap "
            f"{budget['generation_cap']}"
        )
    if violations:
        return {"ok": False, "violations": violations, "budget": budget}

    profile = json.loads(
        json.dumps(keeper_campaign.campaign["slip_profile"])
    )
    if allowed_palettes is not None:
        profile["grid"]["allowed_palettes"] = list(allowed_palettes)
    if deliberation_max_ticks is not None:
        if deliberation_max_ticks == 0:
            profile.pop("deliberation", None)
        else:
            profile["slip_version"] = "0.2.0"
            profile["deliberation"] = {
                "max_ticks": deliberation_max_ticks,
                "confidence_threshold": DELIBERATION_CONFIDENCE_DEFAULT,
            }
    verdict = validate_slip(profile)
    if not verdict.ok:
        return {
            "ok": False,
            "violations": [
                f"the authority rejects the covenant: {error}"
                for error in verdict.errors
            ],
            "budget": budget,
        }
    keeper_campaign.campaign["slip_profile"] = profile
    if population is not None:
        keeper_campaign.era_config["population"] = population
    if generations is not None:
        keeper_campaign.era_config["generations"] = generations
    return {
        "ok": True,
        "covenant": profile,
        "engine_parameters": dict(keeper_campaign.era_config),
        "budget": budget,
    }


# -- one-key spends (the client's covenant mode, F7) ---------------------


def spend_next_palette(keeper_campaign) -> dict:
    """Spend the next earned-but-unspent palette into the covenant."""
    budget = keeper_campaign.budget()
    active = keeper_campaign.campaign["slip_profile"]["grid"][
        "allowed_palettes"
    ]
    for palette in budget["allowed_palettes"]:
        if palette not in active:
            return apply_covenant_change(
                keeper_campaign, allowed_palettes=[*active, palette]
            )
    return {
        "ok": False,
        "violations": ["no unspent palette in the earned budget"],
        "budget": budget,
    }


def spend_deliberation_to_budget(keeper_campaign) -> dict:
    """Deepen the covenant's thinking to the earned maximum."""
    budget = keeper_campaign.budget()
    earned = budget["deliberation_max_ticks"]
    current = (
        keeper_campaign.campaign["slip_profile"]
        .get("deliberation", {})
        .get("max_ticks", 0)
    )
    if earned == 0 or earned <= current:
        return {
            "ok": False,
            "violations": [
                "no deeper thinking in the earned budget "
                f"(earned {earned}, covenant {current})"
            ],
            "budget": budget,
        }
    return apply_covenant_change(
        keeper_campaign, deliberation_max_ticks=earned
    )


def spend_population_to_cap(keeper_campaign) -> dict:
    budget = keeper_campaign.budget()
    if keeper_campaign.era_config["population"] >= budget["population_cap"]:
        return {
            "ok": False,
            "violations": [
                "population already at the earned cap "
                f"{budget['population_cap']}"
            ],
            "budget": budget,
        }
    return apply_covenant_change(
        keeper_campaign, population=budget["population_cap"]
    )


def spend_generations_to_cap(keeper_campaign) -> dict:
    budget = keeper_campaign.budget()
    if (
        keeper_campaign.era_config["generations"]
        >= budget["generation_cap"]
    ):
        return {
            "ok": False,
            "violations": [
                "generations already at the earned cap "
                f"{budget['generation_cap']}"
            ],
            "budget": budget,
        }
    return apply_covenant_change(
        keeper_campaign, generations=budget["generation_cap"]
    )
