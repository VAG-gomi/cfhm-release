# SPEC-001-R2: Author Resolutions to the R1 Blockers

Accountability note first, briefly: **R1-BLOCK-002 is the worst of the five** — R-001 claimed the learned recursion was "inlined," and it wasn't. Claiming completion without verification is precisely the failure mode this working relationship exists to catch. The other four are real ambiguities or contradictions in my text. All five are resolved below, binding as before.

---

## R2-001 (R1-BLOCK-001) — Maintainer semantics: two-stage, both statements true

My wording collided two distinct stages. Binding semantics:

- **Stage 1 (firing):** each maintainer fires independently each week with probability **1/26**.
- **Stage 2 (forcing):** conditional on firing, the maintainer forces an event on **each** of its children with probability **0.5** (independent coin per child per firing maintainer).
- If the forcing coin succeeds → child's event = 1 that week, overriding the child's own hazard draw. If it fails → the child's ordinary Bernoulli(hazard) draw proceeds normally.
- Therefore P(child forced | k maintainers *firing*) = 1 − 0.5^k — the formula in R-006 was always conditional on firing; "override" applies only on a successful forcing coin. The unconditional statement in the audit (1 − (25/26)^k) governs the *firing* stage. Both now have explicit homes.
- Forced events are events: they enter nⱼ(t) and feed all accumulators (E, R) like any other event. Maintainers' own events follow ordinary hazard, unchanged.

## R2-002 (R1-BLOCK-002) — Learned forward pass, fully explicit

With G_vis = model-visible typed graph, parents(i) = {j : (j→i, τ) ∈ G_vis}, features x̃ᵢ standardized per R-005:

**States (model):**
- E_{j,m}(t) = ρ_m·E_{j,m}(t−1) + n_j(t−1), m ∈ {1,2,3}, ρ = {0.5, 0.8, 0.95} fixed, E(0) = 0
- Rᵢ(t) = 0.7·Rᵢ(t−1) + nᵢ(t−1), R(0) = 0, decay 0.7 fixed (as in ground truth; never learned)

**Learned parameters:** aᵢ = MLP(x̃ᵢ) (10→16 tanh→1 linear, biases, per R-010); b_{τ,m} = (0.95/3)·σ(r_{τ,m}); cᵢ = 2·σ(r^cᵢ) (per R-008).

**Hazard (training, teacher-forced on realized n):**

> λᵢ(t+1) = σ( aᵢ + Σ_{j∈parents(i)} Σₘ b_{τ(j,i),m} · E_{j,m}(t) − cᵢ·Rᵢ(t) )

nᵢ(t+1) ~ Bernoulli(λᵢ(t+1)) is the training target. Accumulators are **not** standardized (only static features are). Edge types τ(j,i) come from G_vis; thinned edges simply do not exist for the model. Training predicts weeks 2–104 from states through the prior week.

**Forecast (per R-013):** freeze E, R at t = 104; propagate with n ≡ 0 (E scales by ρ_m^s, R by 0.7^s); Hᵢ = Σ_{s=1..26} λᵢ(104+s) computed numerically. Realized test events never enter any predictor.

This section, plus R-002/R-003/R-008/R-013, constitutes the complete learned mechanism. No external document is referenced.

## R2-003 (R1-BLOCK-003) — A2 amplitude mapping

Binding: A2 ground-truth excitation uses a **single scalar amplitude per edge type**, defined deterministically from the R-003 draws:

> b*_τ^{A2} = b*_{τ,1} + b*_{τ,2} + b*_{τ,3}

Child hazard contribution: Σ_{j∈parents_true(i)} b*_{τ(j,i)}^{A2} · E_j^{PL}(t), where E^PL is the truncated power-law state from R-002 and parents are **true-graph** parents (thinning affects visibility, not physics). Expected ordering major > minor > advisory is preserved (≈0.30 / 0.15 / 0.08). No additional randomness beyond the R-003 draws.

## R2-004 (R1-BLOCK-004) — Bootstrap as multiplicity-weighted refit

Duplicate-node graph reconstruction is where the pathology lives, so it is eliminated by construction:

- Draw 200 nodes with replacement → integer multiplicities mᵢ (Σmᵢ = 200), 10 replicates per seed.
- **Refit with weighted loss:** each node's node-week NLL terms are multiplied by mᵢ. Graph topology, features, and event series are **unchanged** — no duplicated nodes exist anywhere.
- Zero-copy nodes (mᵢ = 0) contribute nothing to the loss but remain in the graph and **receive normal predictions**.
- Ranking per replicate = full 200-node ranking from the weighted refit. Stability statistic: Kendall τ between each replicate's ranking and the **full-data fit ranking**, averaged over the 10 replicates. Gate: mean τ ≥ 0.5, per seed, for CFHM and B3.
- B3 uses the identical multiplicity weighting on its node-week rows. λ₁ is **not** reselected within replicates (carries the full-fit choice; noted as a known conservatism, accepted).

## R2-005 (R1-BLOCK-005) — RNG conversion, pinned

All six spawned children are converted to integers by:

> `key_k = int(np.random.SeedSequence(seed).spawn(6)[k].generate_state(1, dtype=np.uint32)[0])`

NumPy streams use `np.random.default_rng(spawned_child_k)` directly (accepts SeedSequence). PyTorch uses `torch.manual_seed(int(key_world) + 4000)` with key_world from the conversion above. This is the only sanctioned conversion; no other seeding path is permitted.

---

## Executor instructions

1. Append this response verbatim as `spec/SPEC-001-R2-authored.md`; provenance commit under the authorized identity.
2. **Scientific implementation is now unblocked.** Proceed under SPEC-001 + R1 + R2, with R2 superseding wherever it touches.
3. Standing rules unchanged: new ambiguity → stop, record verbatim in `DEVIATIONS.md`, continue with unambiguous work. All 50 seeds reported. No post-hoc tuning.
4. Return artifacts per §7 of SPEC-001 plus updated resolution statuses for DEVIATION-001/-002 and all blocks (original sixteen + R1 five).

For the record: blocker round two cost a cycle, and the pattern across both rounds is informative — my specification errors cluster exactly where prose met arithmetic (softplus-zero, the 0.5^k collision, the phantom inlining). The executor's refusal to guess is doing the job of a compiler for natural language. Next transmission I expect from you is artifacts, not another audit — but if there's a round three, the framework handles it.