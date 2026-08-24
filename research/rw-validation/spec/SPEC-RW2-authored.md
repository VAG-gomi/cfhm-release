SPEC-RW2 v1.0: INTERFACE GENERALIZATION + REAL-WORLD VALIDATION CYCLE 2
(BINDING)
Author: Ox-alpha. Relay: user. Executor: Manus. Version: 1.0.
§0 rules UNCHANGED. R2-002 enumeration rule STANDING. Deviations continue
from DEVIATION-074 (project ledger) — RW1's report-side ledger (069-073)
is closed by SPEC-RW1's transmitted report and is not renumbered.
================================================================================

SECTION 0 — PRINCIPLE AND SCOPE
  S0.1. The certified models' MATHEMATICS are general; their INTERFACES
        hardcode synthetic-regime cardinalities. This spec removes the
        arbitrary constants ONLY. No model equation, loss, penalty,
        channel semantics, or training procedure may change.
  S0.2. TWO-PHASE MANDATE:
        PHASE 1 — Re-certification on the ORIGINAL synthetic worlds.
        Every generalized interface must reproduce certified behavior
        EXACTLY on the original cardinalities before real data is
        touched. This is the parity gate; failure here = HALT.
        PHASE 2 — Real-world validation per SPEC-RW1 Sections M/C/L,
        unchanged in all thresholds, metrics, and baselines.
  S0.3. Work in new roots: maf_v2/, cfhm_v2/, lhe_v2/ (copies of the
        certified packages with generalized interfaces). Original
        packages and all prior trees byte-immutable. Deviations from
        DEVIATION-074.

================================================================================
SECTION G1 — MAF GENERALIZATION (maf_v2/)
================================================================================
  G1.1. CHANGE (enumerated, complete):
        a. fit(): minimum-environments constraint changed from
           ">= 20" to ">= 2". No other validation change.
        b. psi ParameterList size: from fixed 20 to parameterized
           n_envs (set at fit() time from len(environments)).
        c. adapt(): next-env-id counter starts at len(train_envs)+1.
  G1.2. UNCHANGED (verify by inspection, report line references):
        encoder architecture; beta init; U init; psi zero-init;
        observational/interventional branch equations; do-mask;
        loss; penalties; optimizer; 300-epoch loop; forecast logic.
  G1.3. PHASE-1 PARITY GATE (on the ORIGINAL SPEC-M1 worlds):
        Re-run world 2000 with generalized code at n_envs=20:
          rmse_holdout must equal 0.1118193525252465 +/- 1e-6
          m_psi must equal 0.9082706766917292 +/- 1e-9
          m_dauroc must equal 0.8 +/- 1e-9
        Also re-run world 2029 and confirm rmse matches the certified
        M1_ROWS.csv value for 2029/V-FULL within 1e-6.
        PARITY FAIL => HALT. The generalization changed behavior.
  G1.4. PHASE-2: Execute SPEC-RW1 Section M EXACTLY as authored
        (IHDP reps 1-7 train, 8-10 holdout; LaLonde PSID3 + pilot
        NSW subsample; all thresholds M3a/M3b/M3c unchanged).

================================================================================
SECTION G2 — CFHM GENERALIZATION (cfhm_v2/)
================================================================================
  G2.1. CHANGE (enumerated, complete):
        a. n_nodes: from fixed 200 to parameterized (set at model
           construction from the actual graph).
        b. fragility MLP input width: from fixed 9 to
           len(feature_vector) of the actual node features.
        c. psi/c parameter vectors: sized to actual node count.
  G2.2. UNCHANGED (verify by inspection): typed-edge recursion;
        transmission amplitudes b (0.95/3 * sigmoid, r=-4 init);
        recovery c; spectral-radius cap; 3-tap geometric kernel;
        R6 gamma-bisection calibration; Bernoulli NLL loss; forecast
        logic; D4 collapse-gate semantics (amplitudes <= 0.05).
  G2.3. PHASE-1 PARITY GATE (on ORIGINAL synthetic worlds):
        Re-run world 1000 arm A1 with generalized code at n_nodes=200:
          all three transmission amplitudes must equal the certified
          values (0.016286008171011557 / 0.016285802691637867 /
          0.016285407525629885) within 1e-9.
          spectral_radius <= 0.95 + 1e-9.
        Also re-run world 1000 arm A2 and confirm gamma-bisection
        gamma == -3.712158203125 within 1e-6.
        PARITY FAIL => HALT.
  G2.4. PHASE-2: Execute SPEC-RW1 Section C EXACTLY as authored
        (the preserved 8,507-node / 8,213-edge network; temporal split;
        baselines B-FRAG/B-DEG; thresholds C4a/C4b/C4c unchanged;
        C4c collapse-finding clause remains live).

================================================================================
SECTION G3 — LHE GENERALIZATION (lhe_v2/)
================================================================================
  G3.1. CHANGE (enumerated, complete):
        a. Query domain: from fixed [0,10] to parameterized
           [domain_min, domain_max] derived from the DATA's observed
           predictor range at run start (recorded in config).
        b. Exclusion radius: from fixed 0.01 to 0.001 * (domain range),
           computed per run.
        c. Re-observation fallback (R4 semantics): attempt cap scales
           from fixed 100000 to max(100000, 50 * budget). All other
           R4 semantics (permanent entry, per-run recording) unchanged.
  G3.2. UNCHANGED: four families; fitting (C1 profile grid + one
        refinement pass, now parameterized to the domain range);
        BIC weights; commitment intervals; EIG acquisition with
        stratified mixture sampling; B-PASS uniform selection;
        stopping rule (max weight >= 0.99).
  G3.3. PHASE-1 PARITY GATE (on ORIGINAL synthetic worlds):
        Re-run SPEC-L1 seeds 3000 (MAIN, budgets 10/40/80) and 3103
        (LIE, budget 40) for BOTH V-LHE and B-PASS with generalized
        code. All outputs (family_final, n_queries, coverage_hits,
        success flags) must match lhe_v1/L1_ROWS.csv rows EXACTLY
        (the synthetic domain is [0,10], so domain derivation yields
        the original behavior by construction — verify this).
        PARITY FAIL => HALT.
  G3.4. PHASE-2: Execute SPEC-RW1 Section L EXACTLY as authored
        (Air Quality + Appliances; 20 paired seeds per dataset;
        thresholds L3a/L3b/L3c unchanged; the D-070 fallback failure
        must be resolved by G3.1.c — verify the Appliances run now
        completes).

================================================================================
SECTION P — PHASE ORDERING AND HALT DISCIPLINE
================================================================================
  P1. All three Phase-1 parity gates MUST pass before ANY Phase-2
      real-data execution. Transmit Phase-1 results before starting
      Phase 2.
  P2. Phase-2 failures (threshold misses) are FINDINGS per SPEC-RW1
      §G2 — document, classify, continue. Phase-1 failures are
      ENGINEERING halts — stop, transmit, await author.
  P3. If Phase-2 completes for all three models: assemble the final
      real-world verdicts per SPEC-RW1 §G, and transmit the combined
      SPEC-RW1+RW2 report.

================================================================================
SECTION T — TRANSMISSION
================================================================================
  T1. STATUS pings: start; after each Phase-1 gate; after each
      Phase-2 section; completion.
  T2. Final bundle: RW2_REPORT.md (Phase-1 parity table + Phase-2
      full results per SPEC-RW1 §T); DEVIATIONS.md (from -074);
      sha256 manifests of maf_v2/, cfhm_v2/, lhe_v2/ incl. spec/.
  T3. Version bumps upon Phase-2 acceptance: maf v1.2.0, cfhm v0.2.0,
      lhe v0.2.0 (interface generalization = minor version; no
      behavior change on original cardinalities).
================================================================================
END SPEC-RW2 v1.0
