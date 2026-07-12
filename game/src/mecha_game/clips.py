"""Live clip driving — the C2 graph consumed (F3, Phase-C remainder #3).

The engine's transition graph is hub-and-spoke (`labs/animation_system/
transition_graph.py`, measured valid at 0.9877 ≥ 0.80 in cycle 11 C2):
``idle`` is the resting hub, every state clip enters from and returns
to it, and every clip loops on itself. The PRE-REGISTERED validity
metric judges exactly one kind of cut — the LAST frame of the source
to the FIRST frame of the target — so this driver cuts ONLY at loop
boundaries and routes illegal direct edges through the idle hub:
every step it emits is an intra-clip advance, a self-loop boundary,
or a measured graph edge. Pure, deterministic, engine vocabulary only.
"""

from __future__ import annotations

# The C2 graph, mirrored verbatim (hub-and-spoke plus self-loops).
TRANSITIONS: tuple[tuple[str, str], ...] = (
    ("idle", "idle"),
    ("idle", "blink"),
    ("blink", "idle"),
    ("blink", "blink"),
    ("idle", "sleep"),
    ("sleep", "idle"),
    ("sleep", "sleep"),
    ("idle", "beg"),
    ("beg", "idle"),
    ("beg", "beg"),
    ("idle", "ill"),
    ("ill", "idle"),
    ("ill", "ill"),
)
HUB = "idle"


class ClipDriver:
    """Walks the graph frame by frame toward a requested target clip."""

    def __init__(
        self, frame_counts: dict[str, int], *, initial_clip: str = HUB
    ) -> None:
        if initial_clip not in frame_counts:
            raise ValueError(f"unknown clip: {initial_clip}")
        self.frame_counts = dict(frame_counts)
        self._clip = initial_clip
        self._frame = 0

    def step(self, target: str) -> tuple[str, int]:
        """Emit the frame to display now, then advance toward ``target``.

        Mid-clip the animation always completes (the metric never
        measured a mid-clip cut); at the loop boundary the driver takes
        the graph edge to ``target`` when one exists, else the edge to
        the idle hub (which reaches every clip).
        """
        if target not in self.frame_counts:
            raise ValueError(f"unknown clip: {target}")
        display = (self._clip, self._frame)
        if self._frame < self.frame_counts[self._clip] - 1:
            self._frame += 1
        else:
            desired = (
                target
                if (self._clip, target) in TRANSITIONS
                else HUB
            )
            self._clip = desired
            self._frame = 0
        return display

    @property
    def current(self) -> tuple[str, int]:
        return (self._clip, self._frame)
