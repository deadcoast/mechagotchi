# Experiment Report: The Structured Decoder — a Sharp Refutation That Sees the Phase (Cycle 20 · SHARED · J4)

Date: 2026-07-20

## WHY

I2 proved the transducer study's saturation belongs to the ARMS (the
raw direct arm 0-valid in every phase; the semantic arm
validator-gated by construction) and named the remainder: a DIFFERENT
direct arm — a structured tape decoder — with pre-registered gates
falsifiable both ways. J4 designs it, grounded in the tape's OWN
language rather than any tuned mapping.

## WHAT

**The decoder, recorded not improvised** (`structured_decoder.py`,
7 pins RED-first): bff_noheads's exact ten instruction bytes
(`bff.inc.h` at the audited commit) map to morphological tokens by
functional correspondence — copy-read → body (what replicates is
mass), copy-write → eye, loops → joints, head-0 motion → limbs,
head-1 motion → antenna/sensor, byte mutation → effects; all other
bytes empty. Byte index i lands at (i % 8, i // 8) — the tape's
structure IS the morphology's structure. The first copy-read carries
the anchor. NO fix-ups: no connectivity patching, no organ rescue —
the validator judges freely.

**The pre-registered gates over the committed I2 corpus (400 states,
386 early / 14 post):**

| Gate | Measured | Verdict |
| --- | --- | --- |
| validity_unsaturated (valid count > 0) | **0/400** | **FAILED** |
| readability_graded (non-flat) | min ≠ max, graded | MET |
| phase_sensitive | early ≠ post on every metric | MET |

**Verdict: `decoder_joins_the_refuted_record`** — by the
pre-registered rule (validity AND gradation required). And the
refutation is SHARP in a way the raw arm's never was:

- **The decoder sees the phase** — the first direct arm ever to:
  post-takeover tapes decode to **15.14 cells vs early's 7.13**
  (replicator instruction density visible as 2.1× denser morphology)
  with readability 0.327 vs 0.294. The information is IN the tape and
  the decoder extracts it.
- **Early soup warms up before the collapse**: random bytes predict
  ~2.5 instruction cells per tape; the early-phase corpus measures
  7.13 — instruction density accumulates well before takeover, and
  the decoder's cell count is now an instrument that shows it.
- **The failure is spatial coherence, not information**: scattered
  instruction positions cannot satisfy connectivity and the body-core
  floor. Fixing that requires spatial REARRANGEMENT — clustering,
  packing — at which point a decoder becomes a compiler, which is the
  semantic arm's territory. The boundary between decoding and
  compiling is now MEASURED, not asserted: the semantic transducer's
  necessity is a coherence theorem, not a corpus accident.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/cubff_transducer -p "test_structured_decoder.py"
ImportError: cannot import name ... from 'structured_decoder'   # RED
# after implementation (the table verbatim, position pins, the free-
# failure pin, determinism, study gates):
Ran 7 tests ... OK
PS> python -B labs/cubff_transducer/structured_decoder.py
# validity_unsaturated: false · readability_graded: true · phase_sensitive: true
# early: 386 states, 0 valid, mean cells 7.132 · post: 14 states, 0 valid, mean cells 15.143
# decoder_joins_the_refuted_record
```

## HONEST REMAINDER

1. **The refuted record grows by one honest entry** — and the entry
   carries the mechanism: validity is a spatial-coherence bar no
   position-preserving decoder clears; any "coherent decoder" is a
   compiler by another name (a future arm would need its own record
   arguing why rearrangement isn't smuggled compilation).
2. **The decoder's cell-count instrument** (instruction density as
   morphology) is a byproduct worth keeping — it measures soup
   warm-up without brotli.
3. **14 post-takeover states** — the phase sensitivity is clean but
   the subset is the I2 corpus's; a distributional claim would need
   more crossings.

## Sources

- `audits/TODO.md` (cycle 20 J4)
- `research/experiment_reports/2026-07-20-transducer-study-post-takeover.md` (I2 — the remainder this answers)
- `labs/cubff_transducer/structured_decoder.py` (+ `test_structured_decoder.py`)
- `data/cubff_transducer/structured_decoder_stage0.json`, `real_states_curated_i2.json` (the corpus)
- `~/cubff_g2/bff.inc.h` @ `f212e84` (the instruction set, verbatim)
