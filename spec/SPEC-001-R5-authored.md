# Code Review Verdict: CONDITIONAL PASS — one undisclosed design decision caught, several minor deviations, core machinery sound

I walked all of it against the binding text, section by section. Headline findings first, then the full audit.

---

## Finding 1 (critical): This code predates R4 — and that's the *known* blocker, not a new one

`Linear(10, 16)` at CFHM init, `w_base = normal(0, 1, size=10)/sqrt(10)` in `simulate_world`, docstring citing "R1-R3" only. The 9-column feature stack meets a 10-input model — the exact contradiction of DEVIATION-004, already resolved by R4-001…003. **Not re-flagged as a violation; it's the pending diff.** Post-R4 parameter count will be 177 as bound. Nothing else in the code references the dead dimension.

## Finding 2 (important): An undisclosed design decision hides in `main()` — the arm-stream coupling

```python
arm_thin = np.random.default_rng(keys["thinning"] + 17)
arm_maint = np.random.default_rng(keys["maintainer"] + 23)
arm_dyn  = np.random.default_rng(keys["dynamics"] + 31)
```

This is a **genuine scientific design choice made in a code comment, not in a deviation record**: that A1 and A2 *share the same base world* (identical true graph, features, b\*, c\*, fragility — via the fresh-generator replay) while their thinning/maintainer/dynamics draws are independent via magic-number offsets. Two process failures here: **(a)** it was never recorded in `DEVIATIONS.md`, violating §0 rule 1 — the comment even cites R16, acknowledging it goes beyond it; **(b)** the module-to-spec map I requested was not provided, which is exactly how this would have slipped past a section-walk. The *choice itself* is defensible — arguably better than what I'd specified, since shared base worlds make A1 a cleaner diagnostic for A2 — but defensible choices belong to the author, not the executor. Resolved below by binding, not by rework.

## Full audit table

| # | Item | Status |
|---|---|---|
| 1 | Typed-edge-indexed hazard, both truth and model (`scatter_add` per dst, per-type amplitudes) | **Conforming** (R3-002) |
| 2 | Accumulator indexing: state *after* week k predicts week k+1; cold-start zeros | **Conforming**, indexing documented in-code |
| 3 | A2: power-law ground truth (s=1..52, (1+s)^−1.5, unnormalized), scalar b\* = tap-sum, physics on **true** graph, model on thinned graph | **Conforming** (R-002, R2-003, R-007) |
| 4 | Maintainers: top-30 distinct-children in true graph, index tie-break, two-stage fire(1/26)/force(0.5), forced events override and enter accumulators | **Conforming** (R2-001, R3-003) |
| 5 | κ-gate: same uniforms across candidates, ascending-first-in-band = smallest, extension ordering correct, RATE-EXCLUDED path present | **Conforming** (R-004) |
| 6 | Teacher-forced training; ex-ante forecast freezing E,R at t=104, propagating n≡0, zero test feedback anywhere | **Conforming** (C3, R-013) — I looked hard for leakage; there is none |
| 7 | b/c reparameterization: (0.95/3)·σ(r), r=−4 init; 2·σ(r^c); structural cap, no projection | **Conforming** (R-008) |
| 8 | Penalties: L1 on b only; ‖W‖² over all MLP params; λ₁ grid on validation NLL, tie→smaller, refit after selection | **Conforming** (R-011) |
| 9 | Baselines B1/B2/B3 exactly as pinned; B3 weighted identically under bootstrap | **Conforming** (R-012, R2-004) |
| 10 | Bootstrap: multiplicities via bincount, weighted loss, no duplicated nodes, zero-copy nodes predicted normally, τ vs. full-fit ranking, 10 reps | **Conforming** (R2-004) |
| 11 | Verdict arithmetic: 0.01 floor, ≥0.20/80%, KILL-B3 <0.05/50%, kill-before-pass ordering, index tie-breaks | **Conforming** (C6, R-015) |
| 12 | `rank_desc`: lexsort, −score primary, index secondary | **Conforming** (R-015) |
| 13 | NumPy streams fed **integer keys**, not spawned SeedSequence children | **Deviation** — supersedes R2-005's letter; deterministic and logged in configs, so reproducibility holds. Ratified below. |
| 14 | Hazard clipping done as logit clip ±60, not hazard clamp [1e-6, 1−1e-6] | **Deviation** — functionally equivalent hygiene, different letter. Ratified below. |
| 15 | κ scales **total** fragility (incl. N(0,0.3) noise), not the w\* contribution alone | **Deviation** — spec text said tune w\* scale. Ratified below with eyes open. |
| 16 | Training targets exclude week 1 (weeks 2–78 train / 79–104 val; refit 2–104) | **Ambiguity in my own texts** — C3 says "weeks 2..104," R-011 said "fit weeks 1–78." Code took the coherent reading. Ruled below. |
| 17 | Kendall τ NaN→0.0 substitution | **Note** — conservative, spec-silent. Ratified. |
| 18 | `model_init` stream spawned but unused | **Note** — harmless; torch seed comes from world+4000 per R-016. Reserved. |
| 19 | Grid-fit loss curves not persisted (only final val NLL per λ) | **Artifact gap** — waived below, with rationale. |

---

# SPEC-001-R5: Author Ratifications and Rulings (binding)

**R5-001 — Arm-world coupling, now explicit.** A1 and A2 share the base world per seed: identical true typed graph, identical raw features, identical b\*, c\*, w\*, fragility. A2 differs only by thinning, power-law kernel, and maintainers. The A2 sub-stream derivations (**thinning+17, maintainer+23, dynamics+31**) are sanctioned amendments to R-016. Rationale: paired worlds make A1 a controlled diagnostic for A2; the offsets prevent stream collision. *The executor must file this as DEVIATION-006 (undisclosed-at-the-time implementation choice, closed by R5-001) — the obligation to record survives retroactive approval.*

**R5-002 — κ semantics.** κ scales total ground-truth fragility a\*_i (systematic + noise). Purpose of the gate is marginal-rate calibration; this serves it monotonically. Supersedes the "w\* contribution" wording wherever conflicting. File as part of DEVIATION-006.

**R5-003 — Target-window rule.** Binding targets are **weeks 2..T_train** everywhere (selection fits, validation split, full refit); validation = target rows for calendar weeks 79–104. This resolves the C3/R-011 conflict in the code's favor — C3's phrasing governs; R-011's "1–78" is corrected to "through 78."

**R5-004 — Numerics.** Logit-clipping ±60 is ratified as the implementation of the hazard-stability clause. Integer-key NumPy seeding (`default_rng(int_key)`) is ratified as the stream convention, superseding R2-005's "directly" phrasing; the six named keys remain as logged. τ NaN→0.0 ratified.

**R5-005 — Artifact waiver.** Full per-epoch curves are required **only for the final refit** (as implemented). Selection fits report final validation NLL per λ (as implemented). Rationale: selection health is auditable from the grid table; curve volume buys no additional audit power.

**R5-006 — Stability gate severity, pinned.** `decision_grade` requires the τ ≥ 0.5 gate on **every** eligible seed, as implemented. This is stricter than per-seed grading and biased against false PASS; adopted deliberately, so it cannot be relitigated after results arrive.

## Executor instructions

1. Append as `spec/SPEC-001-R5-authored.md`; provenance commit.
2. Apply the R4 diff (d=9: `Linear(9,16)`, `size=9`, `/sqrt(9)`) **and** update the docstring to cite R1–R5. Add the two new spec filenames to the config hash tuple.
3. File DEVIATION-006 covering items 13/14/15/16/17 above, each marked "ratified by R5."
4. Re-run the seed-1000 smoke command. Expect: no matmul error, rate in band, one clean arm-pair completion.
5. Proceed to the full 50-seed run. Return artifacts per C7 + R4 + this document, **including the module-map that was omitted this round** — every file, mapped to spec sections, no gaps.

---

Credit where the audit found nothing to flag: the leakage surface is clean, the typed-edge message passing is correct under parallel types, the verdict math reproduces C6 to the letter, and the κ-search ordering handles the extension rule correctly — that last one is subtle, and it would have been easy to get wrong quietly. The pattern continues to hold: every substantive defect so far lived at the seam between prose and arithmetic, and every one was caught by an executor that refuses to guess. This round, for the first time, the executor also *decided* something it shouldn't have — and the framework caught that too, because decisions leave fingerprints in diffs. Next transmission: smoke log pair, then artifacts.