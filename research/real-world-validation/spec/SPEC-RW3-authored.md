SPEC-RW3 v1.0: FINAL INTERFACE GENERALIZATION (BINDING)
Author: Ox-alpha. Relay: user. Executor: Manus. Version: 1.0.
§0 rules UNCHANGED. R2-002 enumeration rule STANDING. Deviations continue
from DEVIATION-081 (project ledger). Two-phase mandate: parity on
synthetic data FIRST, then real-world rerun. Work in maf_v3/ and
cfhm_v3/ (copies of maf_v2/ and cfhm_v2/). lhe_v2/ is already real-world
capable — no changes to LHE.
================================================================================

SECTION 0 — PRINCIPLE
  Remove the last two hardcoded synthetic-regime constraints. Generalize
  the container, never alter the mathematics. Prove behavior-neutrality
  on original synthetic cardinalities BEFORE touching real data.

================================================================================
SECTION M3 — MAF FEATURE WIDTH GENERALIZATION (maf_v3/)
================================================================================
  M3.1. CHANGE (enumerated, complete):
        a. Encoder input width: from fixed 5 to parameterized
           input_dim (set at model construction from the actual
           feature matrix width).
        b. All downstream layers sized from input_dim automatically.
  M3.2. UNCHANGED (verify by inspection): hidden=16, r=2, lambda1,
        weight_decay, encoder activation, beta init, U init, psi init,
        branch equations, do-mask, loss, optimizer, 300-epoch loop,
        forecast logic, misuse guards (not-fitted, tau validation,
        refit warning), environment-order enforcement.
  M3.3. PHASE-1 PARITY GATE (on original synthetic worlds):
        World 2000: rmse_holdout = 0.1118193525252465 +/- 1e-6,
        m_psi = 0.9082706766917292 +/- 1e-9, m_dauroc = 0.8 +/- 1e-9.
        World 2029: rmse_holdout = 0.1326847206438254 +/- 1e-6.
        PARITY FAIL => HALT.
  M3.4. PHASE-2 REAL-WORLD EXECUTION (SPEC-RW1 Section M, unchanged):
        M-RW-A LaLonde: PSID3 (8 features) as observational env;
          pilot NSW subsample as interventional env; MAF predicts
          NSW treatment effect; compare vs RCT ATE (1794.34) and
          three baselines. PASS: |MAF - RCT| <= 1000 in >= 60% of
          20 pilot seeds AND MAF closest to RCT in >= 50%.
        M-RW-B IHDP: 10 replications as environments; train on
          {1..7}, holdout {8,9,10}; PEHE vs mu1-mu0 truth.
          Baselines: pooled regression, per-env regression.
          PASS: MAF PEHE <= pooled PEHE. STRONG PASS: >= 10% reduction.
  M3.5. VERSION after acceptance: maf v1.3.0.

================================================================================
SECTION C3 — CFHM TEMPORAL GENERALIZATION (cfhm_v3/)
================================================================================
  C3.1. CHANGE (enumerated, complete):
        a. Total weeks: from fixed 130 to parameterized total_weeks
           (set at model construction from the actual event matrix).
        b. Train/test split: from fixed 104/26 to parameterized
           train_weeks / test_weeks (set from the data's temporal
           boundaries; must sum to total_weeks).
        c. All accumulator arrays, event matrices, and forecast
           horizons sized from total_weeks automatically.
  C3.2. UNCHANGED (verify by inspection): typed-edge recursion;
        transmission amplitudes b; recovery c; spectral-radius cap;
        3-tap geometric kernel; R6 gamma-bisection calibration;
        Bernoulli NLL loss; D4 collapse-gate semantics.
  C3.3. PHASE-1 PARITY GATE (on original synthetic worlds):
        World 1000 arm A1: all three amplitudes match certified values
        bit-for-bit (0.016286008171011557 / 0.016285802691637867 /
        0.016285407525629885). Spectral radius <= 0.95 + 1e-9.
        World 1000 arm A2: all three amplitudes match SPEC-002 T1 A2
        references bit-for-bit (0.016286579456825427 /
        0.01628656954388021 / 0.016286499458644653).
        Gamma: A1 = -4.02490234375, A2 = -3.712158203125, both
        within 1e-6.
        PARITY FAIL => HALT.
  C3.4. PHASE-2 REAL-WORLD EXECUTION (SPEC-RW1 Section C, unchanged):
        The preserved 8,507-node / 8,213-edge retraction citation
        network. Temporal split: train on retraction events before
        2020-01-01, test on events >= 2020-01-01. total_weeks and
        train/test split derived from actual data boundaries.
        Baselines: B-FRAG (logistic regression on features) and
        B-DEG (in-degree ranking). Metric: Precision@50 on test-window
        events, 5 temporal bootstrap replicates (seed 7100).
        PASS: CFHM P@50 >= 1.15 x B-FRAG P@50.
        COLLAPSE CHECK: if transmission amplitudes <= 0.05 after
        training => record as CONFIRMED negative result on real data.
        If amplitudes > 0.05 => record as DISCOVERY: the channel
        learns on real data even though it didn't on synthetic.
        Either outcome is a valid finding. Neither is a bug.
  C3.5. VERSION after acceptance: cfhm v0.2.0.

================================================================================
SECTION G — FAILURE POLICY
================================================================================
  G1. Tooling failures => fix + log deviation (from DEVIATION-081).
  G2. PHASE-1 parity failures => HALT, transmit verbatim, await author.
  G3. PHASE-2 threshold misses => document as findings per the
      pre-registered rules. No redesign. No retuning. No threshold
      changes.

================================================================================
SECTION T — TRANSMISSION
================================================================================
  T1. STATUS pings: start, after each Phase-1 gate, after Phase-2
      completion.
  T2. Final bundle: RW3_REPORT.md (Phase-1 parity tables + Phase-2
      real-world results per SPEC-RW1 Sections M and C), DEVIATIONS.md
      (from DEVIATION-081), sha256 manifests of maf_v3/ and cfhm_v3/.
  T3. Version bumps upon full acceptance: maf v1.3.0, cfhm v0.2.0.
      Tag and push to GitHub per established convention (green CI
      before tag).
================================================================================
END SPEC-RW3 v1.0
