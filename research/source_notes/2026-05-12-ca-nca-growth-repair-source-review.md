# CA/NCA Growth and Repair Source Review - 2026-05-12

## Primary Sources

- https://distill.pub/2020/growing-ca/
- https://distill.pub/selforg/2021/textures/

## Confirmed Facts

- Growing Neural Cellular Automata are framed around morphogenesis: growth from
  a seed cell, persistence, and regeneration after damage.
- The NCA model applies the same local update rule to each cell.
- Cell updates depend on immediate neighborhood state.
- Regenerating variants are trained with damage exposure, which improves repair
  behavior.
- Texture NCA work reinforces the same local-rule framing for pattern formation
  and emphasizes asynchronous/discrete grid updates.

## Mechagotchi Interpretation

Mechagotchi should not jump directly to ML-backed NCA. The first useful step is
an inspectable CA/NCA-inspired local rule that proves the measurement surface:
growth validity, repair validity, readability delta, SLIP alignment, and
lifecycle survival after repair.

The Stage 0 lab therefore uses a discrete local attractor. It is intentionally
not described as a trained neural CA.

The follow-up persistence benchmark keeps the same interpretation. Persistence
and regeneration in the source literature justify testing idle stability and
broader damage masks, but the current Mechagotchi implementation remains a
target-template baseline until learned rules or less-assisted repair exist.

The repeated stochastic damage benchmark extends that interpretation. The
source literature's regeneration framing justifies repeated damage exposure,
while the current implementation remains an assisted measurement baseline rather
than a trained regenerating NCA.
