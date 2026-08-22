# Author's Response to the Execution-Layer Audit

First, the assessment you're owed: **this audit is correct, and it's the system working as designed.** Sixteen blockers raised, sixteen verified against the spec text — all sixteen legitimate. Manus stopped instead of improvising, which is precisely what §0 rule 1 demanded. Two catches deserve individual mention:

- **BLOCK-008 is a genuine mathematical error of mine.** softplus(0) = ln 2 ≈ 0.693, not zero. I wrote a contradictory parameterization. Logged below as AUTHOR-ERR-002.
- **BLOCK-004 caught a real internal contradiction** between the all-seeds rule and the rate gate. Also mine.

Additionally, while verifying BLOCK-010 I found a third error independently: my "≈350 parameters" claim. Actual count of 10→16→1 with biases: 160+16+16+1 = **193**. Logged as AUTHOR-ERR-001. No design impact; the estimate was slop.

Accepting all sixteen is not deference — each ruling below traces to specific spec text. Here are the author's bindings.

---

# SPEC-001-R1: Author Resolutions (binding, supersede SPEC-001 where they conflict)

## Procedural

**DEVIATION-001 — AUTHORIZED.** Configure repository-local identity `CFHM-CI <noreply@localhost>` solely for provenance commits. No global config, no spec changes.

**BLOCK-001 — Resolved by inlining.** The complete learned forward pass is now specified in R-002/R-003/R-008/R-013 below. No external document is referenced anywhere in this revision.

## World generator

**R-002 (BLOCK-002) — Kernel definitions.**
Taps m ∈ {1,2,3}. Tap state: `E_{j,m}(t) = ρ_m·E_{j,m}(t−1) + n_j(t−1)`, with `E(0) = 0` (cold start; identical treatment in ground truth and model). Effective kernel ψ_m(s) = ρ_m^s for s ≥ 1, else 0.
**A2:** ground-truth excitation is a *single-channel truncated power-law*: `E_j(t) = Σ_{s=1..52} (1+s)^{−1.5} · n_j(t−s)`, unnormalized, cold-start zeros. **The model architecture is unchanged in A2** — it still uses 3-tap geometric. The kernel mismatch is deliberate; A2 exists to violate the model's baked-in assumptions (declared limitation #5 of the design).

**R-003 (BLOCK-003) — Ground-truth values.**
Per seed: `b*_{τ,m}` ~ LogNormal(ln μ_τ, 0.2) with type scales μ = {major: 0.30, minor: 0.15, advisory: 0.08} and within-type tap shares {0.5, 0.35, 0.15}. `c*ᵢ` ~ Uniform[0.2, 1.0]. `w*` ~ N(0,1)/√10 per dimension. **No intercept term** — fragility heterogeneity comes from features plus the 𝒩(0, 0.3) noise only.

**R-004 (BLOCK-004) — Rate gate without re-rolling.**
Deterministic scale search on the *same seed*: κ ∈ {0.25, 0.5, 1, 2, 4}; select the smallest κ giving train-window event rate ∈ [3%, 5%]. If none succeeds, extend to {0.125, 8}. If still none: mark seed **RATE-EXCLUDED**, record realized rates, exclude from the 50. Seeds are never re-rolled; the procedure is fully deterministic and reproducible.

**R-005 (BLOCK-005) — Features.**
age ~ U[0.5, 20] → log-age; popularity ~ LogNormal(0, 1); complexity ~ U[0,1]; field ~ Categorical(uniform, 5). Generation order: true graph → A2 thinning → features → dynamics. **In-degree is computed from the model-visible (thinned, in A2) graph**, since it is a model input. Standardization across nodes using train-window statistics.

**R-006 (BLOCK-006) — Maintainers.**
Candidates: 30 highest-out-degree nodes in the **true** graph (maintainers are hidden structure); sample 5 uniformly. They are among the 200 scored nodes. Their own events follow ordinary hazard. Firing: Bernoulli(1/26) per week, independent per maintainer. Forced child events **override** the child's Bernoulli draw that week (event = 1 regardless of hazard). Multiple maintainers: child has an event if any firing maintainer targets it (effective p = 1 − 0.5^k).

**R-007 (BLOCK-007) — Thinning.**
Uniform random subset of true edges, size ⌊0.85·|E_true|⌋, types retained, drawn once per seed after graph generation. **Ground truth runs on the full graph; the model sees the thinned graph.** Unrecorded conduits carrying real transmission is the adversarial mechanism.

## Model

**R-008 (BLOCKS-008/009) — Reparameterization, replacing both the softplus and zero-init wordings.**
Author error acknowledged (AUTHOR-ERR-002). Binding form:
- `b_{τ,m} = (0.95/3) · σ(r_{τ,m})`, raw params `r` initialized at **−4.0** ⇒ b ≈ 0.006 at init; Σₘ b ≤ 0.95 holds *structurally*, no projection, no post-update step.
- `cᵢ = 2 · σ(r^cᵢ)`, `r^c` init −4.0 ⇒ c ≈ 0.036.
Near-zero initialization intent preserved; cap guaranteed by construction.

**R-010 (BLOCK-010) — MLP details.**
Final layer linear (logit). Biases everywhere. PyTorch default init except r-parameters (−4.0). Corrected count: **193 parameters** (AUTHOR-ERR-001).

**R-011 (BLOCK-011) — Penalties and validation.**
‖W‖² covers all MLP weights and biases. L1 covers `b` only (all types, all taps), not `c`. Validation window: weeks 79–104 (final quarter of train); fit on 1–78; select λ₁ by validation NLL; **refit on full weeks 1–104** with the chosen λ₁ before test scoring. Grid ties → smaller λ₁.

## Baselines and evaluation

**R-012 (BLOCK-012) — Baselines pinned.**
B1: descending in-degree, model-visible graph. B2: descending z(log-age) + z(popularity). B3: sklearn `LogisticRegression(C=1.0, lbfgs, max_iter=1000)` on node-week rows (weeks 1–104), per-node static score = predicted probability at that node's covariate vector; refit per seed. All methods rank the same 200 nodes.

**R-013 (BLOCK-013) — Ex-ante forecast protocol.**
Freeze E, R at t = 104. Propagate decays with n ≡ 0 through t = 130. Predicted hazard mass = Σ λᵢ(t) over test weeks. **Realized test events never enter any predictor.** This is a true pre-event forecast.

**R-014 (BLOCK-014) — Stability procedure.**
Node-level bootstrap: resample 200 nodes with replacement, 10 refits per seed (same λ₁, series rebuilt for the sampled multiset; prediction for original node i = mean over its copies). Kendall τ on the 200-length rank vectors, averaged over refits. Gate applies to **CFHM and B3** (B1/B2 are deterministic). Threshold unchanged: mean τ ≥ 0.5 or not decision-grade.

**R-015 (BLOCK-015) — Verdict arithmetic.**
Best baseline per seed = max P@25 over B1–B3. Relative improvement = (P@25_CFHM − P@25_base) / max(P@25_base, 0.01). PASS: rel ≥ 0.20 in ≥ 80% of non-excluded A2 seeds. KILL-B3: rel over B3 specifically < 0.05 in ≥ 50% of seeds. Ranking ties broken by ascending node index.

**R-016 (BLOCK-016) — RNG streams.**
`SeedSequence(seed).spawn(6)` → keys for [world, thinning, maintainer, dynamics, model-init, bootstrap], consumed by `numpy.default_rng`. `torch.manual_seed(world_key + 4000)`.

---

## Executor instructions

1. Proceed to implementation under SPEC-001 + R-001…R-016. R-resolutions are binding amendments, not suggestions.
2. Append this response verbatim to `spec/` as `SPEC-001-R1-authored.md`; create the provenance commit under the authorized identity.
3. Any *new* ambiguity discovered during implementation: same rule as before — stop, record, continue with what remains unambiguous.
4. Return artifacts unchanged from §7 of the original spec, plus `DEVIATIONS.md` updated with resolution statuses for DEVIATION-001 and all sixteen blocks.

---

One observation for the record, since this conversation has been an exercise in epistemic hygiene: the audit you relayed just demonstrated the exact behavior the whole framework was built to elicit — **an executor that refuses to guess**. Sixteen blockers is not obstruction; a spec with sixteen silent implementation choices would have produced results I couldn't distinguish from whatever the executor happened to prefer. Now every degree of freedom is either pinned or named. When the artifacts come back, the audit standard stands: raw tables, not summaries.