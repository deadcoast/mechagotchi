# CTM Source Review - 2026-05-12

## Primary Sources

- https://pub.sakana.ai/ctm/
- https://github.com/SakanaAI/continuous-thought-machines
- https://arxiv.org/abs/2505.05522

## Confirmed Facts

- Continuous Thought Machines introduce an internal temporal axis for reasoning.
- CTM uses neuron-level temporal processing and synchronization as a central
  representation.
- The public repository is Apache-2.0 licensed.
- The released code is a research implementation for reproducing CTM results,
  not a small companion-engine dependency.

## Mechagotchi Interpretation

Mechagotchi should not adopt CTM as a model dependency. The useful idea is
narrower: uncertain switchboard decisions can spend extra internal ticks before
acting, while confident decisions should act immediately.

The Stage 0 adaptation is therefore a lightweight confidence-gated tick wrapper
around the existing micro-switchboard. It measures action accuracy, confidence
gain, tick count, and explanation traces without reusing CTM code.
