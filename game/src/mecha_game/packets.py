"""The hello-creature packet source — engine truth only (F1, DR 0033).

The client never draws a guess: adoption goes through the engine's own
gate (`mecha_engine.lifecycle.initial_state`, which refuses a
misaligned body/covenant pair with the validator's verbatim errors),
and every frame the window presents is one
`mecha_engine.genome.render_packet_v2` — the Phase-C bridge contract —
driving the idle clip frame by frame. F2 replaces the static hello
state with the live companion loop; the packet path stays this one.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from mecha_engine.genome import clip_frame_count, render_packet_v2
from mecha_engine.lifecycle import initial_state

# The frozen F1 research hello pair: the first 16x16 corpus creature under the
# LCD seed covenant — the engine accepts the pair (pinned by the F1
# tests over the real fixtures, never assumed).
HELLO_SEED = Path("data") / "seed_grids_16x16" / "mg_seed16_001_beetle.json"
HELLO_SLIP = Path("data") / "slips" / "valid" / "slip_lcd_seed.json"
# Q3 / DR 0064: new product lives use the measured adopted covenant.
# HELLO_SLIP remains the explicit historical experiment input.
DEFAULT_SLIP = Path("data") / "slips" / "valid" / "slip_v2_cleanliness.json"
HELLO_CLIP = "idle"


@dataclass(frozen=True)
class HelloCreature:
    """One adopted creature: the grid, its covenant, and the engine's
    initial lifecycle state (F2 will advance it; F1 renders it)."""

    grid: dict
    slip_profile: dict
    lifecycle_state: dict
    clip: str
    frame_count: int


def data_search_origins(start: Path | None = None) -> list[Path]:
    """Compatibility facade: exact declared roots, never ancestor searches."""
    from mecha_game.runtime_resources import resource_roots
    return resource_roots(start)


def default_fixture_paths(start: Path | None = None) -> tuple[Path, Path]:
    """Resolve new-life fixtures only in this source checkout/native payload."""
    from mecha_game.runtime_resources import validate_resource
    for base in data_search_origins(start):
        seed = base / HELLO_SEED
        slip = base / DEFAULT_SLIP
        if seed.is_file() and slip.is_file():
            validate_resource(seed)
            validate_resource(slip)
            return seed, slip
    raise FileNotFoundError(
        f"no {HELLO_SEED.as_posix()} corpus in this installation - "
        "use a complete Windows release or pass explicit seed/slip paths"
    )


def load_hello_creature(
    seed_path: str | Path,
    slip_path: str | Path | None = None,
    *,
    slip_profile: dict | None = None,
) -> HelloCreature:
    """Adopt a creature: the engine's own gate judges the pair.

    ``initial_state`` raises with the validator's or the covenant's
    verbatim errors when the body or the match is wrong — the client
    relays, never softens.
    """
    grid = json.loads(Path(seed_path).read_text(encoding="utf-8"))
    if slip_profile is None:
        if slip_path is None:
            raise ValueError("provide slip_path or slip_profile")
        slip_profile = json.loads(
            Path(slip_path).read_text(encoding="utf-8")
        )
    state = initial_state(grid, slip_profile)
    return HelloCreature(
        grid=grid,
        slip_profile=slip_profile,
        lifecycle_state=state,
        clip=HELLO_CLIP,
        frame_count=clip_frame_count(HELLO_CLIP),
    )


def hello_packet(creature: HelloCreature, tick: int) -> dict:
    """One frame of engine truth: ``render_packet_v2`` driving the
    clip, ``frame_index`` cycling with the client tick."""
    return render_packet_v2(
        creature.grid,
        creature.lifecycle_state,
        slip_profile=creature.slip_profile,
        clip=creature.clip,
        frame_index=tick % creature.frame_count,
    )
