================================================================================
SPEC-002: CFHM COMPONENT AUTOPSY (F2-A) — BINDING EXECUTION SPECIFICATION
Author: Ox-alpha. Relay: user. Executor: Manus. Version: 1.0.
Governing docs: SPEC-001 + R1–R7 + R8 (lean transmission). §0 executor rules
apply UNCHANGED: stop-and-record verbatim on ambiguity/failure; never improvise;
no seed dropped; no tuning after any result is seen.
================================================================================

A. SCOPE AND INPUTS
  A1. Analysis-only experiment. NO world generation. All inputs are the 100
      preserved files f1_v2/data/seed_{s}_{arm}.npz (s = 1000..1049,
      arm ∈ {A1, A2}) plus per-seed-arm selected_gamma from
      f1_v2/configs/seed_{s}_{arm}.json.
  A2. All outputs go to a NEW root f1_v2_autopsy/. The trees metrics/,
      predictions/, f1_v2/, and tag F1-v1-baseline remain byte-immutable.
  A3. Idempotency (lesson of DEVIATION-014): every output file is deleted and
      rewritten atomically at the START of each invocation; no append mode
      anywhere in this spec.

B. FITTED VARIANTS (per seed-arm case; identical training hyperparameters to
   F1-v2: Adam lr 1e-3, 50 epochs full-batch, lambda_1 = 0.01 fixed — the v2
   modal selection — targets weeks 2..104, torch seed = int(world_key)+4000,
   hazards/logits clipped as ratified):
   V-REFIT   CFHM-full, retrained from scratch on the saved world.
             Purpose: reproducibility anchor against v2's stored B4 rows.
   V-A0      CFHM with the transmission channel STRUCTURALLY ZEROED:
             all three taps of b_{tau,m} fixed identically to 0 and EXCLUDED
             from the optimizer. Everything else identical to V-REFIT.
             Purpose: "same architecture, same training path, no channel."
   V-ORAC    CFHM with fragility REPLACED BY GROUND TRUTH: the MLP output
             a_i is replaced by the frozen constant vector
             base_i = gamma_recorded + kappa * a*_i
             where a*_i = fragility_truth from the npz and gamma_recorded /
             kappa (=1.0) come from the v2 config JSON. Learnable parameters:
             b and c only. Purpose: with PERFECT fragility, can transmission
             be identified at all?
   V-B3R     B3 logistic regression refit on the same saved features/events
             (C=1.0, lbfgs, max_iter=1000). Purpose: pairing completeness.
   Total: 400 fits. CPU-scale.

C. METRICS PER VARIANT PER CASE
   C1. Precision@25 via the SHARED score_metrics.rank_desc / precision_at
       implementation (ascending-index tie-break). Labels from npz.
   C2. Transmission summary for every fit that contains b (V-REFIT, V-ORAC):
       per type tau in {major, minor, advisory}:
         S_tau  = SUM_m b_{tau,m}          (learned type amplitude)
       and the flattened Spearman rho between the 9-vector (b_{tau,m}) and
       the corresponding 9-vector of ground-truth amplitudes
       (for V-REFIT: b*_{tau,m}; for V-ORAC: b*_tau^A2 scalars broadcast to
       taps — use the per-type scalar repeated 3 times).

D. PRE-REGISTERED SUMMARY FORMULAS (executor computes; author classifies)
   D1. REPRODUCIBILITY GATE (evaluated FIRST, on all 100 cases):
       delta_s = | P25(V-REFIT) - P25_v2stored(B4) |
       Gate passes iff delta_s <= 0.08 in >= 90% of cases. If it FAILS:
       HALT the entire autopsy, transmit deltas verbatim, await author ruling.
       Nothing downstream is valid without this gate.
   D2. Channel-gap statistics (vs V-REFIT):
       g_arm = median over seeds of [ P25(V-A0) - P25(V-REFIT) ], per arm.
   D3. Collapse statistic (from V-REFIT fits):
       collapse_fraction = fraction of fits with S_tau <= 0.05 for ALL three
       types simultaneously.
   D4. Misidentification statistics (from V-REFIT fits, A2 arm):
       amp_fraction = fraction of fits with any S_tau > 0.15;
       rho_median   = median flattened Spearman rho (A2, V-REFIT).
   D5. Oracle-lift statistics:
       o_arm = median over seeds of [ P25(V-ORAC) - P25(V-REFIT) ], per arm;
       o_b3_arm = median over seeds of [ P25(V-ORAC) - P25(V-B3R) ], per arm.

E. TRANSMISSION TO AUTHOR (lean bundle; narration allowed but carries no
   evidentiary weight):
   T1. AUTOPSY_ROWS.csv verbatim: seed | arm | variant | p_at_25 | S_major |
       S_minor | S_advisory | spearman_rho   (400 rows + b-columns blank for
       V-A0/V-B3R).
   T2. Summary table verbatim: D1 pass rate and worst delta; g_A1, g_A2;
       collapse_fraction; amp_fraction; rho_median (A2); o_A1, o_A2, and the
       four o_b3 values.
   T3. DEVIATIONS.md (verbatim, new root) covering anything encountered,
       including any npz/config read failures.
   T4. sha256 manifest of f1_v2_autopsy/ contents.
   Classification labels (Section F vocabulary) MUST NOT appear anywhere in
   executor output. Evidence ends at T2; judgment begins with the author.

F. CLASSIFICATION VOCABULARY (AUTHOR-ONLY; listed here solely so the
   categories are public before results exist — preventing post-hoc relabeling)
   CHANNEL-HARMFUL / CHANNEL-INERT / MISIDENTIFIED / REGIME-STARVED /
   ARCHITECTURE-OVERHEAD / MIXED. Mapping thresholds live with the author and
   will be published WITH the verdict, applied to T1/T2 as transmitted.

G. EXECUTOR INSTRUCTIONS
   1. Create f1_v2_autopsy/spec/SPEC-002-authored.md with this document
      verbatim; provenance commit under the authorized identity.
   2. Implement; emit one STATUS.md ping at start and one at completion
      (this is a small job; no midpoint checkpoint).
   3. Produce T1-T4. Expected wall-clock is modest; if any single fit exceeds
      10 minutes, record it as a deviation and continue.
================================================================================
END SPEC-002
================================================================================
