SPEC-RW1 v1.0: REAL-WORLD VALIDATION OF MAF / CFHM / LHE (BINDING)
Author: Ox-alpha. Relay: user. Executor: Manus.
§0 rules UNCHANGED. R2-002 enumeration rule STANDING. Deviations continue
from DEVIATION-069. Datasets: use EXACTLY the raw files already preserved
under /home/ubuntu/ds1_raw/ (hashes recorded in DS-1) — no re-downloads.
================================================================================

PRINCIPLE: Real-world data has no planted answer key. Correctness is
defined against the strongest available real ground truth. ALL
thresholds below are locked BEFORE any model touches any dataset.
On any failure: document per §G; authorized fixes are PREPROCESSING
ONLY; redesign, retuning-to-fit, and threshold changes are prohibited
in this cycle.

DECLARED ADAPTATIONS (bound before execution):
  AD-1: IHDP contains no interventional training rows. MAF is therefore
        tested in its multi-environment observational form: does the
        per-environment quarantine improve the mechanism channel's
        treatment-effect estimation versus non-quarantined baselines?
        This is a scoped variant of the certified synthetic claim and is
        labeled as such in all outputs.
  AD-2: LHE's certified machinery is 1-D family selection. Real tests use
        one feature-target pair per dataset. No machinery redesign.
  AD-3: CFHM's real test uses the retraction citation network instead of
        npm (DS-D timeline partially unobtainable). Retraction = adverse
        event; citation = transmission edge; paper features = fragility.

================================================================================
SECTION M — MAF ON REAL DATA
================================================================================
M1. DATASETS (enumerated):
    M1a. IHDP primary: 10 replications from DS-B. Environments :=
         replications 1..7 (train), 8..10 (holdout-eval). Rows: all 747
         per replication. Treatment column = observational (biased by
         benchmark construction). Ground truth per replication: tau_i =
         mu1_i - mu0_i.
    M1b. LaLonde demonstration: PSID3 (128 rows) = observational
         environment; NSW treated+control (445 rows) = interventional
         environment (randomized assignment). Ground truth = ATE
         computed FROM THE NSW DATA ITSELF: mean(RE78 | treated) -
         mean(RE78 | control), computed by the executor and reported
         before any model runs.
M2. MODELS (enumerated, identical training budget each):
    M2a. Pooled regression: linear regression on [x, tau], all train
         environments pooled, no environment structure.
    M2b. Per-environment regression: separate linear fit per train
         environment; held-out env uses its own fit (no pooling).
    M2c. MAF: the certified maf v1.1.1 package, default hyperparameters
         (hidden=16, r=2, lambda1=1e-3), fit() per R3-001 semantics.
         IHDP: environments = replications 1..7. LaLonde: environments =
         {PSID3, NSW}; NSW rows routed to the interventional branch
         (randomized assignment = intervention), PSID3 rows to the
         observational branch.
M3. METRICS AND PRE-REGISTERED THRESHOLDS:
    M3a. IHDP primary: for each holdout replication r in {8,9,10}:
         sqrt(PEHE_r) = sqrt(mean((tau_hat(x_i) - tau_i)^2)) over all
         747 rows, where tau_hat = interventional prediction difference
         (tau=1 minus tau=0). Report per-rep and mean.
         THRESHOLD: mean holdout sqrt(PEHE) of M2c must be >= 10%
         LOWER than M2a (pooled). Secondary report: vs M2b.
    M3b. LaLonde demonstration: MAF interventional ATE estimate =
         mean over NSW rows of [pred(tau=1) - pred(tau=0)]. Report
         absolute distance from the RCT ATE for: M2a-on-PSID3-only,
         M2a-on-NSW (oracle reference), and M2c. THRESHOLD: M2c
         distance < M2a-on-PSID3 distance (demonstration criterion).
    M3c. Calibration: report per-env psi norms and their correlation
         with a per-environment confounding proxy (absolute difference
         between env-specific naive tau-estimate and the RCT/true tau).

================================================================================
SECTION C — CFHM ON THE RETRACTION CITATION NETWORK
================================================================================
C1. NETWORK CONSTRUCTION (bound procedure):
    C1a. Sample 500 retracted papers uniformly at random (seed
         7000, stream WORLD) from the Retraction Watch CSV rows having
         a valid OriginalPaperDOI.
    C1b. For each sampled paper, query OpenCitations v2 for incoming
         citations (rate limit: >= 1 second between calls; retry once
         on transient error; log every call).
    C1c. Nodes := sampled retracted papers + all fetched citing papers.
         Edges := citing -> cited. Event := retraction date (from CSV)
         for retracted nodes. Citing papers that are themselves in the
         Retraction Watch CSV also carry retraction events.
    C1d. Features per node (enumerated): log(1+citation count),
         log(1+age at window start), retraction-count of citation
         parents BEFORE window start, publication year (scaled),
         field-category one-hot (top 5 categories from CSV).
C2. TASK: weekly-binned hazard of RETRACTION for non-yet-retracted
    nodes over a 52-week window; train on first 60% of the timeline,
    test on the final 40% (temporal split, no leakage).
C3. MODELS: C3a fragility-only (logistic regression on features);
    C3b CFHM full (typed-edge transmission: edge type := citing-paper
    is-already-retracted vs not, two types).
C4. PRE-REGISTERED THRESHOLDS:
    C4a. C3b must beat C3a on held-out precision@k (k = 50) by >= 10%
         relative, mean over 5 temporal bootstrap replicates (seed 7100).
    C4b. Learned transmission coefficient for
         "citation-parent retracted" edges must be POSITIVE.
    C4c. IF the transmission channel again collapses to initialization
         (all amplitudes <= 0.05 after training): record verbatim =>
         this CONFIRMS the synthetic negative result on real data and
         is itself a reportable finding, not a packaging failure.
================================================================================
SECTION L — LHE ON DENSE REAL PROCESSES
================================================================================
L1. DATASETS AND PAIRS (enumerated):
    L1a. Air Quality: target = CO(GT) (comma decimal -> dot; -200 =
         missing per UCI documentation, rows with missing target or
         missing chosen feature dropped; 114 blank rows dropped).
         Feature = T (temperature). Report final usable row count.
    L1b. Appliances: target = Appliances, feature = T1 (no missing
         values expected; report if any found).
L2. PROCEDURE (per dataset, per seed):
    20 paired seeds (main seeds 8000..8019). Per seed: shuffle rows
    (seeded); budget := 10% of rows for queries; V-LHE selects query
    rows via certified EIG machinery; B-PASS selects uniformly at
    random; both start from the same 50-row seed set; final fit =
    best-weighted family on revealed rows; metric = RMSE on the
    remaining unrevealed rows.
L3. PRE-REGISTERED THRESHOLDS:
    L3a. LHE beats B-PASS on final RMSE in >= 60% of the 20 paired
         runs per dataset => component PASS.
    L3b. LHE loses in >= 60% => component FAIL (real-data negative).
    L3c. Between => INCONCLUSIVE for that dataset. Overall LHE
         real-world label: PASS if both datasets PASS; FAIL if both
         FAIL; else INCONCLUSIVE.
================================================================================
SECTION G — FAILURE POLICY (all sections)
================================================================================
  G1. Preprocessing failures (parse errors, encoding) => fix + log
      deviation from DEVIATION-069.
  G2. THRESHOLD FAILURES (a model misses its pre-registered bar) =>
      NOT fixable this cycle. Document, classify per the pre-registered
      rule, continue with remaining sections. A failed model is a
      FINDING, not a bug.
  G3. No threshold may be changed after any model has touched any
      dataset. No redesign. No additional baselines invented mid-run.

================================================================================
SECTION T — TRANSMISSION
================================================================================
  T1. STATUS pings: start, after each section (M/C/L), completion.
  T2. RW1_RESULTS.csv: one row per (section, dataset, model, metric)
      with values verbatim.
  T3. SUMMARY table — EXACT ROW SET (enumerated, 14 rows):
      1. m_ihdp_pehe_pooled  2. m_ihdp_pehe_perenv  3. m_ihdp_pehe_maf
      4. m_ihdp_maf_vs_pooled_pct  5. m_lalonde_rct_ate
      6. m_lalonde_pooled_est  7. m_lalonde_maf_est
      8. c_nodes_total  9. c_edges_total  10. c_prec50_fragonly
      11. c_prec50_cfhm  12. c_transmission_coefficient
      13. l_airq_winfrac + l_appl_winfrac (two rows if needed —
      enumerate as 13a/13b)
      14. overall_label (per-model labels, computed)
  T4. DEVIATIONS.md verbatim (from DEVIATION-069).
  T5. sha256 manifest of rw1/ incl. spec/ and raw-data copies.
================================================================================
END SPEC-RW1 v1.0
