# CA/NCA Repair Context Ablation Stage 0

Negative-result ablation for retrieval-context conditioning of the gradient-trained repair rule, under the exact trained-repair benchmark protocol.

- Training grids: 40
- Held-out targets: 10
- Cycles: 5 at dropout 0.2

| Config | Final overlap | Structural agreement | Validity |
| --- | ---: | ---: | ---: |
| plain_replication | 0.862546 | 0.631871 | 1.0 |
| context | 0.802656 | 0.615123 | 1.0 |
| context_self_play | 0.809249 | 0.590334 | 1.0 |
| context_self_play_prune | 0.801557 | 0.61331 | 1.0 |
| plain_self_play_prune | 0.838278 | 0.589837 | 1.0 |

- Exemplar oracle ceiling (mean agreement): 0.785
- Retrieved exemplar agreement (mean): 0.731124
- Decision: reject_context_conditioning

Retrieval-context conditioning, self-play retraining, and confidence pruning each fail to improve — and mostly degrade — held-out final overlap and structural agreement versus the plain trained rule. Leave-one-out retrieval is more reliable over the training corpus than for held-out variants, so the model over-trusts consensus features that mislead at evaluation time. The retrieval ceiling additionally bounds every exemplar-template strategy below the assisted stability bar on this corpus.
