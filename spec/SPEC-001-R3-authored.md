# SPEC-001-R3: Author Resolution to DEVIATION-003

One blocker this round, and it's legitimately mine: §2 listed three numbers without saying how they combine. Binding below — including the knock-on consequences the executor hasn't hit yet but would have next round, which I'm closing preemptively.

---

## R3-001 (DEVIATION-003) — Typed-edge sampling: **independent per-type draws**

For each ordered pair i < j, draw three independent Bernoulli variables with probabilities {0.04, 0.08, 0.05} for types {major, minor, advisory}. Each success creates a distinct typed edge. **Parallel typed edges between the same pair are permitted** (expected in ~0.9% of pairs at these rates).

Rationale for the choice, so the record shows it wasn't arbitrary:
1. **Literal reading.** The spec wrote P(edge) = {0.04, 0.08, 0.05} — three numbers. Independent per-type draws use them exactly as written.
2. **No new parameters.** The exclusive alternative (edge-or-not, then categorical type) requires a total edge probability that exists nowhere in the specification. Resolving one ambiguity by introducing an unspecified quantity is not resolution.
3. **Semantics.** Multi-typed coupling is realistic (a library can be simultaneously a runtime dependency and a licensing/advisory coupling) and is *within CFHM's expressiveness by construction* — provided the recursions are edge-indexed, which they now are (see R3-002).

## R3-002 — Recursions restated as typed-edge-indexed (binding patch to R2-002 and ground truth)

The R2-002 formula summed over `j ∈ parents(i)` with `b_{τ(j,i),m}` — undefined when τ(j,i) is non-unique. All hazard sums, ground truth and learned, are hereby indexed by **typed edge**, not by parent:

> λᵢ(t+1) = σ( aᵢ + Σ_{e=(j→i,τ) ∈ G} Σ_{m=1..3} b_{τ,m} · E_{j,m}(t) − cᵢ·Rᵢ(t) )

A pair carrying two types contributes twice, once per channel, using that type's amplitudes. Identical indexing applies to the A1 ground truth (b*_{τ,m}) and to A2 (b*_τ^{A2} scalar per typed edge, power-law state E^PL). Parents' accumulator states E_{j,m} remain per-node — shared across the types of its outgoing edges.

## R3-003 — Knock-on definitions forced by R3-001 (binding)

- **In-degree feature (refines R-005):** number of **distinct incoming neighbors** (union over types) in the model-visible graph. Distinct, not edge-counted — the feature measures structural prominence, and double-counting parallel types would inflate it arbitrarily.
- **Maintainer selection (refines R-006):** candidates = 30 highest **distinct-children out-degree** in the **true** graph; ties broken by ascending node index (same convention as R-015).
- **Thinning (confirms R-007):** operates on the multiset of typed edges; |E_true| counts typed edges; each typed edge is independently thinnable.
- **RNG consumption order (extends R-016):** typed-edge draws consume `rng_world` in lexicographic order over pairs (i<j), types in fixed order (major, minor, advisory) within each pair. Consumption order is part of the specification; any other order changes the world.

## Status

- DEVIATION-001: closed (identity configured as authorized).
- Scientific implementation remains unblocked under SPEC-001 + R1 + R2 + R3, with R3 superseding wherever it touches.

## Executor instructions

1. Append verbatim as `spec/SPEC-001-R3-authored.md`; provenance commit.
2. Proceed. Standing rules unchanged: new ambiguity → stop, record verbatim, continue with unambiguous work; all seeds reported; no post-hoc tuning.
3. Return artifacts per §7 plus resolution statuses for all blocks (16 + 5 + 1).

---

For the record: blocker trajectory 16 → 5 → 1, and the error classes migrated as they fell — arithmetic error (softplus-zero), then internal contradiction (0.5^k), now pure underspecification (sampling convention). That's the expected convergence shape of this loop: the remaining ambiguities are the ones that only surface when every earlier layer is pinned. If the next transmission is artifacts, my audit will be against §6 verdict arithmetic and §7 raw tables — summaries will be returned unread.
