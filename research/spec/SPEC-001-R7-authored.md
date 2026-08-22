================================================================================
SPEC-001-R7: TRANSMISSION FORMAT AMENDMENT (BINDING)
Governs all author<->executor traffic from F1-v2 onward.
================================================================================

R7-001 — TWO-DOCUMENT PROTOCOL:

DOC-1  STATUS.md (<= 40 lines), emitted at three checkpoints:
       post-smoke, after ~25 seeds, at completion. Contents ONLY:
       stage reached; seeds completed/total; anomalies encountered;
       calibration-path usage so far (kappa-ladder vs R6-002 bisection).

DOC-2  HANDOFF_REPORT.md — the complete evidence bundle, fixed sections:
  S1  Provenance: commit hashes (specs + code), env versions, runtime,
      commands. Verbatim.
  S2  Status ledger, 100 rows: seed | arm | status | kappa OR
      gamma-bisection path + final value | train rate.
  S3  per_seed_metrics.csv — VERBATIM, COMPLETE (~400 rows).
  S4  stability.csv — VERBATIM, COMPLETE (~100 rows).
  S5  verdict.json AND verdict_recomputed.json verbatim, plus an explicit
      consistency check between them, plus BOTH rate_excluded_seeds arrays
      pasted IN FULL (expected: 50 entries each).
  S6  Independent recomputation: run score_prediction_csv over the FULL
      predictions CSV; report max absolute delta vs S3 and row-count
      reconciliation (expected 80,000 rows).
  S7  Spot-slices: seeds {1000, 1025, 1049}, both arms, methods B3 and B4:
      top-25 nodes each as (node, label, score). ~600 rows total.
  S8  Loss summaries per fit type: run count, median/min/max final train
      and validation NLL, count of non-finite values.
  S9  DEVIATIONS.md — verbatim, complete.
  S10 Smoke pair: failing line from the pre-R4 log + tail of the passing
      post-R6 log.
  S11 sha256 manifest of every artifact file in the repository.
  Estimated size < ~1000 lines. Split only at section boundaries if needed.

R7-002 — REPO-ONLY ARTIFACTS: Full predictions CSV, .npz worlds, per-epoch
  curves, plots are NOT transmitted. They are evidenced by the S11 manifest.
  If the author disputes anything, the author names an exact slice (file,
  seed, arm, method, rows); the executor extracts only that slice, whose
  hash must match the manifest.

R7-003 — EARLY-STATUS BOUNDARY: Partial results seen at checkpoints may
  trigger only VOID/crash declarations, never scientific adjustments. This
  restates executor rule R-ii: no parameter may change after any test data
  has been seen, including early peeks.

R7-004 — LEDGER COLUMN: The S2 status ledger records which calibration path
  each seed used (kappa-ladder vs R6-002 gamma-bisection, with final gamma
  if bisected).

EXECUTOR INSTRUCTIONS:
  1. Append verbatim as spec/SPEC-001-R7-authored.md; provenance commit.
  2. Proceed per R6 executor instructions. Final transmission to the author
     is HANDOFF_REPORT.md per S1-S11, including MODULE_MAP.md coverage with
     no gaps.
================================================================================
END SPEC-001-R7
================================================================================
