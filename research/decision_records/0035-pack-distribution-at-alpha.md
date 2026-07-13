# Decision Record 0035: Pack Distribution at the Alpha — Files, Gates, and Deferred Infrastructure

Date: 2026-07-12

## Status

**Accepted** (cycle 17 · Phase G, task G5). Dispositions the F16
remainder (distribution/registry/signing) at the scope the M7 public
alpha actually needs — and NO further. Implementation follows this
record; nothing here mandates new code.

## Context

F16 shipped the community CARRIER: `mechagotchi_pack_v1` (SLIPs +
creatures + provenance in one importable file) with three layers of
engine gates — the builder refuses invalid content verbatim, import
re-judges every item (tamper pinned by test) and stages only accepted
ones, and the era admission gates judge staged creatures a third time
at run. What F16 deliberately deferred: HOW packs travel between
Keepers, and whether provenance needs cryptographic integrity.

The M7 alpha (gap analysis, Phase G) is a public-repository alpha:
reproducible from the docs, both builds playable from a checkout or
the built bundle. There is no hosted service in the documented alpha
scope.

## Decision

1. **At the alpha, packs travel as FILES over ordinary channels** —
   repository checkouts, releases, or direct exchange between
   Keepers. The committed starter pack
   (`data/packs/mechagotchi_starter_pack.json`) is the canonical
   example and the format's reference fixture. No registry, no
   hosting service, no upload surface ships at alpha.
2. **The security model at alpha is the GATES, not trust in the
   file**: imported pack content is DATA judged by the engine's
   validators — never code, never executed. A malicious or corrupted
   pack can at worst present items the gates reject verbatim (the
   tamper path is pinned by test). This is the honest protection
   boundary, and it already exists.
3. **Provenance stays DECLARATIVE at alpha** (author/source/license/
   date, as F16 shipped). Cryptographic signing is DEFERRED, with the
   reason recorded: a signature scheme without distribution
   infrastructure changes ceremony, not the threat model — there is
   no registry to anchor identity against, and the gates already
   bound the blast radius of tampered content. Signing gets its own
   decision record WHEN a hosted distribution surface is proposed.
4. **A registry/sharing service is a POST-ALPHA product decision made
   WITH the owner** — community infrastructure shapes the project's
   public face (moderation, identity, hosting costs); it is not an
   agent-side call. The documented community system remains in scope
   (the gap analysis names it); this record sequences it after the
   alpha proves the file path.
5. **The alpha packet (G6) documents the pack path**: how to export a
   covenant, build a pack, hand the file over, and import it through
   the gates — the user-facing sentence of this record.

## Consequences

- G6 can write the alpha packet against a settled distribution story
  with zero new implementation risk.
- The F16 remainder ("pack signing … with Phase G's distribution
  decisions") is dispositioned: deferred-with-reason, not forgotten —
  re-opened by any hosted-distribution proposal.
- The alpha's community loop is honest about its size: Keepers share
  files; the engine judges contents; nothing pretends to be a
  platform.

## Sources

- `research/experiment_reports/2026-07-12-community-packs.md` (F16 — the carrier and its named remainders)
- `data/packs/mechagotchi_starter_pack.json` (the reference fixture), `game/src/mecha_game/packs.py` (the three gate layers)
- `docs/gap-analysis.md` (Phase G: the community system + the M7 alpha)
- `audits/TODO.md` (cycle 17 G5)
