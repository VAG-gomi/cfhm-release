# SPEC-002 CFHM Component Autopsy — Evidence Handoff

> **Originated by:** Ox-alpha. **Relayed by:** User. **Executed by:** Manus. This document transmits evidence only; no author-only classification is applied.

## Execution status

The analysis-only autopsy completed on all **100 preserved seed-arm cases** using only the saved `f1_v2/data/*.npz` files and corresponding `selected_gamma` configuration values. The four prescribed variants produced **400 fits** in total: 100 each for V-REFIT, V-A0, V-ORAC, and V-B3R. The prior `f1_v2/` tree and `F1-v1-baseline` remain unchanged.

The D1 reproducibility gate was evaluated first. All 100 cases passed the bound delta threshold, so downstream variants were executed. The D1 pass fraction was **1.0**, and the worst observed delta was **0.0**.

## T1 — AUTOPSY_ROWS.csv

The complete 400-row table is attached separately as `AUTOPSY_ROWS.csv`. Its exact schema is:

```text
seed,arm,variant,p_at_25,S_major,S_minor,S_advisory,spearman_rho
```

The transmission table contains 100 rows per variant. The S-columns and Spearman field are blank for V-A0 and V-B3R, as specified.

## T2 — Exact eleven-row summary

| statistic | value |
|---|---:|
| d1_gate_pass_fraction | 1.0 |
| d1_worst_delta | 0.0 |
| g_A1 | 0.0 |
| g_A2 | 0.0 |
| collapse_fraction | 1.0 |
| amp_fraction | 0.0 |
| rho_median_A2 | -0.675 |
| o_A1 | 0.19999999999999996 |
| o_A2 | 0.24 |
| o_b3_A1 | 0.0 |
| o_b3_A2 | 0.039999999999999925 |

The verbatim CSV rendering is attached separately as `SUMMARY.csv`.

## T3 — DEVIATIONS.md

The complete deviation ledger is attached separately as `DEVIATIONS.md`. It records the resolved T2-count ambiguities and the two shell-level launch/bookkeeping events. No input read failure or individual fit failure occurred, and no prior experiment tree was modified.

## T4 — SHA-256 manifest

The complete manifest of `f1_v2_autopsy/` is attached separately as `AUTOPSY_MANIFEST.sha256`. It covers the authored specifications, relay artifacts, implementation, status, raw T1/T2 tables, D1 deltas, input manifest, result records, and this handoff document; the manifest file itself is excluded to avoid recursive hashing.

## Supporting raw evidence

The D1 case-level deltas are transmitted in `D1_DELTAS.csv`. The start/completion execution status is in `STATUS.md`. The implementation is in `run_autopsy.py`, and the binding author amendments are preserved under `spec/`.

## References

[1]: AUTOPSY_ROWS.csv — complete T1 fit-by-case transmission table.
[2]: SUMMARY.csv — verbatim T2 eleven-row summary.
[3]: DEVIATIONS.md — complete T3 deviation ledger.
[4]: AUTOPSY_MANIFEST.sha256 — complete T4 SHA-256 manifest.
[5]: D1_DELTAS.csv — case-level reproducibility deltas.
[6]: STATUS.md — start/completion status record.
