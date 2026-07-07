# Experiment Report: The SLIP Visual-Grammar Gate Promoted into `render_packet_v2` (E1)

Date: 2026-07-07

## WHY

DR 0026 (D3) named a concrete `genome` follow-up: the workshop's live
preview still called the LAB `build_render_packet_v2` because only the
lab version carried the T3.5 `visual_grammar.animation_vocab` gate — the
last place a SHIPPED surface (the workshop server) depended on a lab
module for packet building. E1 closes it: port the gate into the
promoted `mecha_engine.genome.render_packet_v2`, then switch the
workshop to the package version.

## WHAT

- **The port** — `render_packet_v2` gains keyword-only
  `slip_profile: dict | None = None`, replicating the lab authority
  verbatim: the species' `visual_grammar.animation_vocab` (intersected
  with `ANIMATION_STATES`) bounds the reported vocabulary, and a
  selected state outside it falls back to a DISPLAYED `idle` while
  `mood` stays honest (a hunger-driven `beg` on a species with no beg
  shows idle + mood hungry). `slip_profile=None` is byte-identical to
  the pre-E1 contract.
- **Parity** — `labs/grid_genome/test_package_animation_parity.py`
  gained `SlipVocabGateParityTests` (bounded-vocabulary packets
  identical across seeds and lifecycle snapshots incl. the honest-idle
  fallback; out-of-vocab override identical; `None` byte-identical) —
  closing the "except the lab's SLIP-vocab extension" carve-out the
  parity file's own scope note had documented.
- **Contract** — the genome contract driver + `test_genome_contract.py`
  gained the gate probe (bounded vocab, fallback-to-idle, honest mood,
  ungated shows beg, `None` byte-identical).
- **The consumer switched** — `workshop/server/workshop_server.py`
  `/api/preview/render` now calls the promoted `render_packet_v2` with
  the resolved `slip_profile`, so the portrait's animation vocabulary
  reflects the species' grammar. The lab `build_render_packet_v2` import
  is gone from the server.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/grid_genome -p "test_package_animation_parity.py"
Ran 11 tests in 0.027s
OK

PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_genome_contract.py"
Ran 26 tests in 0.173s
OK

PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
OK    # render endpoint: no profile -> full vocab (byte-identical);
      # nocturne profile (vocab idle+sleep) -> packet bounded to idle+sleep
```

End-to-end proof: saving the nocturne zoo profile (vocab `[idle,
sleep]`) and rendering through `/api/preview/render` returns a packet
whose `animation_vocabulary` is exactly `["idle", "sleep"]` — the
promoted gate working through the shipped endpoint.

## Decision

Adopt — E1 developed to its description. The last shipped-surface
dependency on a lab for packet building is closed; the SLIP
visual-grammar gate is a promoted `genome` contract member with full
parity and contract coverage.

## Sources

- `research/decision_records/0026-render-module-disposition.md` (the named follow-up)
- `research/decision_records/0013-port-slip-v2-and-packet-v2.md` (the packet-v2 port pattern)
- `packages/mecha_engine/src/mecha_engine/genome/animation.py`
- `labs/grid_genome/animation_states.py` (the verbatim authority)
- `labs/grid_genome/test_package_animation_parity.py`
- `packages/mecha_engine/tests/test_genome_contract.py` (+ driver)
- `workshop/server/workshop_server.py`, `workshop/tests/test_workshop_server.py`
- `research/package_specs/mecha_engine_genome_contract_gate.md`
