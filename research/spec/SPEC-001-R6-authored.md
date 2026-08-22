================================================================================
SPEC-001-R6: AUTHOR RESOLUTION — RATE GATE REPAIR AND F1-v1 CLOSURE (BINDING)
Reissued intact for F1-v2. Supersedes conflicting text in SPEC-001/R1–R5.
================================================================================

AUTHOR-ERR-005 (context): R-003 bound "no intercept term." Consequence: at
week 1, lambda = sigmoid(kappa * a*_i); a* is symmetric around zero, so the
median hazard is 0.5 for every kappa. The [3%, 5%] gate was unsatisfiable by
construction. F1-v1 (all 100 seed-arm cases RATE-EXCLUDED) is therefore
classified VOID-BY-DESIGN: a generator-validation outcome, not a CFHM
hypothesis failure. No claim about transmission ranking is supported or
refuted by F1-v1.

R6-001 — GROUND-TRUTH INTERCEPT (supersedes R-003's "no intercept" clause):
  Hazard becomes:
    lambda_i(t+1) = sigma( GAMMA + kappa*a*_i + msg_i(t) - c*_i*R_i(t) )
  GAMMA = -3.2, FIXED constant, applied identically in arms A1 and A2.
  GAMMA sits OUTSIDE the kappa scaling: kappa continues to modulate fragility
  spread only. All other ground-truth distributions unchanged (R-003, R2, R3).
  Model side UNCHANGED: CFHM's MLP bias absorbs an intercept naturally;
  B3 logistic regression has an intercept by construction; B1/B2 unaffected;
  evaluation and C6 verdict arithmetic untouched.

R6-002 — CALIBRATION LADDER WITH DETERMINISTIC FALLBACK:
  Primary path (unchanged): run the bound kappa ladder {0.125, 0.25, 0.5, 1,
  2, 4, 8} at GAMMA = -3.2; select the SMALLEST kappa whose train-window rate
  lies in [3%, 5%].
  Fallback path (only if NO kappa lands in band for that seed): deterministic
  per-seed calibration by bisection on GAMMA in [-8, -1], 12 iterations,
  kappa frozen at 1.0, same seed and streams, selecting the GAMMA whose
  train-window rate is closest to 4% among iterates landing in [3%, 5%].
  Rate is monotone increasing in GAMMA, so the bisection terminates
  deterministically. Seeds are never re-rolled.
  RECORD PER SEED which path was used and the final (kappa, gamma) pair.

R6-003 — BOOKKEEPING:
  1. F1-v1 artifacts are immutable. Tagged baseline: F1-v1-baseline at
     commit 594c6793a4a71ce55f164865ef9525b54d9678eb. Never modified.
  2. New work proceeds as F1-v2 under this amendment. New experiment version,
     new commits; no overwriting of v1 artifacts.
  3. DEVIATION-007/-008 cross-referenced to AUTHOR-ERR-005: SATISFIED as
     filed; no duplicate entries required.
  4. Carried requirement: the final artifact package must include
     verdict_recomputed.json computed over the COMPLETE seed_status.json,
     and both rate_excluded_seeds arrays pasted in full (see R7 section 5).

EXECUTOR INSTRUCTIONS:
  1. Append verbatim as spec/SPEC-001-R6-authored.md; provenance commit.
  2. Apply the minimal diff: add GAMMA = -3.2; insert GAMMA into the single
     ground-truth hazard line. NOTHING else changes.
  3. Re-run the seed-1000 smoke command. Expected: train-window rate near
     band at some kappa (registered prediction: ~4-7% at kappa=1 including
     contagion feedback; A2 slightly higher from maintainer forcing).
  4. On smoke pass: emit STATUS.md ping, then proceed to the full 50-seed
     run under HANDOFF PART 2 as amended by R1-R7.
================================================================================
END SPEC-001-R6
================================================================================
