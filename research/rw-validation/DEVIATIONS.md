# DEVIATIONS.md — SPEC-RW1 external audit ledger

This is the **report-side RW1 deviation ledger**. It continues from the author-specified DEVIATION-069 sequence but does not modify `/home/ubuntu/cfhm_f1/DEVIATIONS.md` or any project repository.

## DEVIATION-069 — MAF real-data environment cardinality blocks the bound fit

**Stage:** SPEC-RW1 M-section preflight, before any MAF model fit.

**Bound requirement:** IHDP environments are replications 1–7 for training; LaLonde environments are `{PSID3, NSW}`. The certified MAF package requires at least 20 training environments.

**Exact observed errors:**

```text
MAF_PREFLIGHT|IHDP_train_reps_1_to_7|ValueError|fit requires at least 20 training environments
MAF_PREFLIGHT|LaLonde_environments_PSID3_NSW|ValueError|fit requires at least 20 training environments
```

**Classification:** Binding implementation/interface compatibility failure. The execution layer did not duplicate, split, pool, or invent environments. No MAF model fit, PEHE, ATE estimate, psi norm, or calibration correlation was claimed.

**Scientific impact:** The M-section real-world claim is **not evaluated** under the authored enumeration; this is not a PASS or FAIL result.

## DEVIATION-070 — LHE acquisition fallback cannot complete the bound Appliances budget

**Stage:** SPEC-RW1 L-section smoke/full attempt, after one Air Quality paired smoke and before the full two-dataset 20-seed battery was complete.

**Observed preprocessing:** Air Quality produced 7,344 usable rows after dropping 114 blank rows and 2,013 rows with missing/invalid `T` or `CO(GT)`. Appliances produced 19,735 usable rows with zero missing/invalid `T1` or `Appliances`. The 10% budgets are therefore 734 and 1,973.

**Exact runtime error:**

```text
RuntimeError: unable to find continuous fallback query
```

**Classification:** Certified acquisition/runtime compatibility failure. The bound LHE acquisition implementation exhausts its fixed 0.0–10.0 grid and then cannot find a continuous fallback candidate under its 0.01 separation rule at the larger real-data budget. No fallback rule, budget, threshold, family set, or machinery was changed.

**Observed partial evidence:** Air Quality seed 8000 completed one paired smoke: V-LHE RMSE `1.4478283552`; B-PASS RMSE `1.43889788338`; V-LHE did not win that smoke. This is not promoted to the pre-registered 20-run win fraction.

**Scientific impact:** L-section overall label is **not evaluated**. The runtime condition is recorded, not repaired.

## DEVIATION-071 — CFHM real-network cardinality blocks the bound model

**Stage:** SPEC-RW1 C-section after the bound network construction and before any CFHM fit.

**Observed network:** 500 valid retracted papers were sampled with seed 7000, all 500 OpenCitations calls returned response files, and the resulting graph contained 8,507 nodes and 8,213 unique citation edges.

**Exact observed error:**

```text
CFHM_PREFLIGHT|ValueError|n_nodes must be 200
```

**Classification:** Binding implementation/interface compatibility failure. The execution layer did not truncate the network, pad it, change the certified MLP input contract, or create an unrequested model variant.

**Scientific impact:** Precision@50, the transmission coefficient, and the C4 thresholds are **not evaluated**. Network construction evidence remains preserved.

## DEVIATION-072 — UCI Air Quality source row-format discrepancy retained verbatim

**Stage:** L-section preprocessing, before model execution.

The UCI Air Quality archive contains 9,471 physical data lines after the header, including 114 delimiter-only blank rows and 9,357 nonblank date/time rows. Applying the authored missing-value rule leaves 7,344 usable `T`/`CO(GT)` pairs. The source page’s stated instance count differs from the physical downloaded CSV; no rows were silently synthesized or normalized.

**Classification:** Source-format/data-cleaning observation. Preprocessing-only handling was applied exactly as bound.

**Scientific impact:** None beyond the explicitly reported usable-row count; no causal conclusion was drawn from this dataset.

## DEVIATION-073 — Initial RW1 manifest finalizer targeted a staging tree

**Stage:** RW1 final manifest verification, before manifest creation.

The first finalizer guard targeted `/home/ubuntu/cfhm_f1/maf_release`, which was not the exact MAF audit clone. It found branch `cfhm-artifact`, head `b92154508e0ece614ff4e086cf4e15e0ab411e21`, and untracked sibling paths. The guard stopped before generating the manifest. The exact observed guard line was:

```text
REPOSITORY_SIDE_EFFECT: /home/ubuntu/cfhm_f1/maf_release head=b92154508e0ece614ff4e086cf4e15e0ab411e21 clean=False
```

The condition was diagnosed and corrected without reset, cleanup, or repository mutation. The rerun used `/tmp/maf-release-canonical-inspect`, `/tmp/cfhm-release-code-review`, and `/home/ubuntu/cfhm_f1/lhe_release`; all matched their expected heads and were clean.

**Classification:** Execution bookkeeping/path-selection failure in the report finalizer. No scientific result or project repository was changed.

## Resolution status

DEVIATION-073 is **CLOSED as corrected**. DEVIATIONS-069 through 072 remain **OPEN / REPORT-ONLY** pending author ruling or a separate binding amendment. No repository, source package, tag, release, visibility setting, or preserved raw file was modified.
