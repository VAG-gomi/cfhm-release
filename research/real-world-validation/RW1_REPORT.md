# SPEC-RW1 v1.0 — Real-World Validation Report

> **Author:** Ox-alpha  
> **Relay:** user  
> **Executor:** Manus  
> **Execution date:** 2026-08-24 UTC  
> **Status:** **INCOMPLETE / BLOCKED BY CERTIFIED INTERFACE COMPATIBILITY**  
> **Scientific HALT-class claim/evidence mismatch:** **NONE FOUND**

## Executive result

SPEC-RW1 was registered verbatim and its thresholds were frozen before any model touched the copied real-data inputs. The exact DS-1 raw files were reused without re-download. The MAF and CFHM real-data fits could not start because the authored real-world dataset cardinalities are incompatible with the certified package interfaces: MAF requires at least 20 training environments, while SPEC-RW1 binds 7 IHDP training environments and 2 LaLonde environments; CFHM requires exactly 200 nodes, while the bound 500-paper citation construction produced 8,507 nodes. LHE completed one Air Quality seed-8000 paired smoke but then hit the certified acquisition fallback runtime error before the full 20-seed battery could complete.

These are **reportable execution/interface findings**, not scientific PASS or FAIL verdicts. No threshold was changed, no baseline was invented, no model was redesigned, and no source repository or preserved DS-1 raw file was modified. The detailed deviation record is in the external report-side [`DEVIATIONS.md`](DEVIATIONS.md); it does not alter the earlier project ledger.

## Pre-run conditions

| Condition | Bound state | Recorded evidence |
|---|---|---|
| Authored specification | Registered verbatim; 157 body lines, 9,372 bytes | `spec/SPEC-RW1-authored.md` |
| Raw source | Existing DS-1 raw files copied; no re-download | `raw/` and `evidence/SPEC_RW1_registration.txt` |
| Raw payload budget | 98,241,693 bytes, below 524,288,000-byte limit | `RUN_METADATA.json` and manifest |
| MAF hyperparameters | `hidden=16`, `r=2`, `lambda1=1e-3` | `evidence/MAF_preflight.txt` |
| Locked thresholds | Frozen before model execution | `spec/SPEC-RW1-authored.md` |
| Repository changes | None | Model repositories and DS-1 raw sources were read only |

## Section M — MAF on real data

### Bound inputs

For IHDP, SPEC-RW1 enumerates the ten DS-B replications, using replications 1–7 as training environments and 8–10 as holdout evaluation. Each replication contains 747 rows and unit-level `mu0`/`mu1` values, with the bound target `tau_i = mu1_i - mu0_i`. For LaLonde, PSID3 is the observational environment and the 185 NSW treated plus 260 NSW control rows form the interventional environment.

### Pre-model ground-truth calculation

The LaLonde RCT reference was computed directly from the preserved NSW files before any model fit:

| Quantity | Value |
|---|---:|
| NSW treated rows | 185 |
| NSW control rows | 260 |
| Mean `RE78` treated | 6349.14353027027 |
| Mean `RE78` control | 4554.801126 |
| RCT ATE | **1794.34240427027** |

### Compatibility finding

The certified `MAFModel.fit()` contract rejects fewer than 20 training environments. The exact preflight errors were:

```text
MAF_PREFLIGHT|IHDP_train_reps_1_to_7|ValueError|fit requires at least 20 training environments
MAF_PREFLIGHT|LaLonde_environments_PSID3_NSW|ValueError|fit requires at least 20 training environments
```

No MAF model fit occurred. Consequently, IHDP pooled/per-environment/MAF PEHE, the MAF-vs-pooled threshold, LaLonde model estimates, psi norms, and confounding-proxy correlation are all `UNAVAILABLE` rather than imputed. The M-section real-world claim is **not evaluated**.

## Section C — CFHM on the retraction citation network

### Bound network construction

The Retraction Watch CSV supplied 69,174 rows with a valid `OriginalPaperDOI`. A uniform sample of 500 rows was drawn with seed 7000. Duplicate DOI values were retained when selected because the bound sampling unit is a CSV row; the sample contained 29 repeated DOI selections after case-insensitive normalization. OpenCitations v2 was queried once per sampled row with at least one second between calls and one retry on transient failures. All 500 response files were preserved.

| Network quantity | Observed value |
|---|---:|
| Sampled retracted rows | 500 |
| OpenCitations response files | 500 |
| Nodes from sampled papers plus fetched citing records | **8,507** |
| Unique citing-to-cited edges | **8,213** |
| Sampling seed | 7000 |

The exact sampled rows, response files, call log, and deduplicated edge table are under `cfhm_network/`.

### Compatibility finding

The certified CFHM model is fixed to `n_nodes=200`. The required real network has 8,507 nodes. The exact preflight error was:

```text
CFHM_PREFLIGHT|ValueError|n_nodes must be 200
```

The network was not truncated, padded, or re-encoded to force compatibility. No CFHM or fragility-only fit occurred. Therefore held-out precision@50, the learned transmission coefficient, and all C4 threshold decisions are `UNAVAILABLE`; the C-section model claim is **not evaluated**. Network construction itself is preserved as a completed partial section.

## Section L — LHE on dense real processes

### Bound preprocessing

The copied UCI Air Quality archive was parsed with semicolon delimiters, comma decimals converted to dots, `-200` treated as missing, and 114 delimiter-only blank rows dropped. Rows with missing or invalid `T` or `CO(GT)` were also dropped. The resulting `T` → `CO(GT)` pair table contains **7,344 usable rows**, giving the bound 10% query budget of **734**.

The copied Appliances Energy archive was parsed with leading-space tolerance. No missing or invalid `T1` or `Appliances` values were found. The resulting pair table contains **19,735 usable rows**, giving the bound 10% query budget of **1,973**. Raw ZIP bytes remain unchanged under `raw/DS-F/`; derived pair tables are under `data/`.

### Partial smoke evidence

One Air Quality paired smoke for seed 8000 completed before the LHE path failed on the Appliances dataset:

| Dataset | Method | Seed | Holdout RMSE | Result |
|---|---|---:|---:|---|
| Air Quality | V-LHE | 8000 | 1.4478283552 | Did not beat B-PASS |
| Air Quality | B-PASS | 8000 | 1.43889788338 | Lower RMSE in smoke |

This one smoke is not promoted to the pre-registered 20-run win fraction.

### Compatibility/runtime finding

The certified LHE acquisition implementation exhausted its fixed 0.0–10.0 grid and then failed its continuous fallback search at the larger real-data budget. The exact error was:

```text
RuntimeError: unable to find continuous fallback query
```

No fallback rule, candidate domain, budget, family set, threshold, or machinery was changed. The full 20 paired seeds for both datasets were therefore not run. The L-section labels and overall LHE real-world label are **not evaluated**.

## Transmission summary

The exact row-wise transmission table is [`RW1_RESULTS.csv`](RW1_RESULTS.csv). The locked summary row set is [`SUMMARY.csv`](SUMMARY.csv). Because both `13a` and `13b` are required for the two LHE datasets, the physical CSV contains 15 rows: rows 1–12, 13a, 13b, and row 14 overall label. `UNAVAILABLE`, `BLOCKED`, and `INCOMPLETE` are explicit classifications, not missing-data substitutions.

| Component | Final classification | Reason |
|---|---|---|
| MAF real-data validation | **NOT EVALUATED** | Certified fit requires ≥20 environments; bound inputs provide 7 or 2. |
| CFHM real-data validation | **PARTIAL / NOT EVALUATED** | Network construction completed; certified model requires 200 nodes, observed network has 8,507. |
| LHE real-data validation | **PARTIAL / NOT EVALUATED** | One Air Quality smoke completed; bound acquisition fallback failed before full paired battery. |
| Overall SPEC-RW1 scientific label | **NOT EVALUATED** | The authored prerequisites for all three section-level threshold decisions were not executable without redesign. |

## Failure-policy application

The five report-side deviations are recorded in [`DEVIATIONS.md`](DEVIATIONS.md): DEVIATION-069 for the MAF environment-cardinality incompatibility, DEVIATION-070 for the LHE acquisition fallback runtime failure, DEVIATION-071 for CFHM node-cardinality incompatibility, DEVIATION-072 for the retained UCI Air Quality source-row format discrepancy, and DEVIATION-073 for the initially mis-targeted report-finalizer guard. DEVIATION-073 is closed as corrected; the first four remain report-only pending author ruling. No finding is classified as a scientific claim/evidence mismatch, so no scientific HALT-class finding is declared.

## Provenance and read-only boundary

All successful raw downloads originated in the earlier DS-1 preservation area and were copied into `rw1/raw/` without re-download. Raw payload hashes are listed in the manifest. Generated RW1 outputs are outside the model repositories. No file, tag, release, visibility setting, or source package in the MAF, CFHM, or LHE repositories was modified by this run.

## Output map

| Artifact | Purpose |
|---|---|
| `spec/SPEC-RW1-authored.md` | Verbatim binding specification body |
| `raw/` | Exact copied DS-1 raw payloads used by RW1 |
| `data/` | LHE feature-target derived tables created by bound preprocessing |
| `cfhm_network/` | Seeded sample, API responses, call log, and citation edges |
| `RW1_RESULTS.csv` | Row-wise section/dataset/model/metric transmission |
| `SUMMARY.csv` | Exact summary metrics and explicit statuses |
| `DEVIATIONS.md` | External report-side deviation ledger, continuing at 069 |
| `STATUS.md` | Start, section, and completion status record |
| `RW1_MANIFEST.sha256` | Hash manifest for all RW1 files except the manifest itself |
