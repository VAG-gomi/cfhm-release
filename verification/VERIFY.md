# CFHM SPEC-C1 v1.1 Verification Report

**Package:** `cfhm` 0.1.0

**Branch:** `cfhm-artifact`

**Base commit:** `d88ec4a8551184572d7b1a0d8d521e70e5b23468`

**Specification:** `spec/SPEC-C1-authored.md`

**Status:** `PASS`

## F1 — Fresh installation and import

A fresh Python 3.12 virtual environment installed the package from outside the package root with the exact bound runtime pins already available. The installed import returned:

```text
installed_version 0.1.0
```

F1: **PASS**.

## F2 — Four tests, zero skips

The required test files were executed:

```text
tests/test_generator.py
tests/test_graph_constraint.py
tests/test_stability_cap.py
tests/test_collapse_signature.py
```

Result:

```text
4 passed, 0 skipped
```

F2: **PASS**.

## F3 — Generator anchors

`generate_world(1000, "A1")` reproduced the bound values:

```text
gamma_calibrated=-4.024902343750
train_rate=0.040048076923
```

`generate_world(1000, "A2")` reproduced:

```text
gamma_calibrated=-3.712158203125
```

Repeated A1 generation produced identical arrays for features, events, and labels. F3: **PASS**.

## F4 — Model constraints and scientific collapse gate

The actual `CFHMModel` implementation is in `src/cfhm/model.py`. The four tests verified:

| Gate | Result |
|---|---|
| D2 structural zero for undeclared edges | **PASS** |
| D3 spectral-radius cap `<= 0.95 + 1e-9` | **PASS** |
| D4 collapse signature | **PASS** |

The bound D4 run used world `1000`, arm `A1`, 50 epochs, and `lambda1=0.01`. The observed amplitudes were:

```text
major=0.016286008171011557
minor=0.016285802691637867
advisory=0.016285407525629885
```

All three values are `<= 0.05`. The observed structural radius was:

```text
0.016286008171011557
```

No scientific repair, tuning, rerun, or result-driven change was applied. F4: **PASS**.

## F5 — Closed-world files and documentation bindings

The package contains the required public source modules, four tests, data table, example, documentation, verification file, and specification chain. The exact E1 string is present in `README.md`; `docs/AUTOPSY.md` is a byte-exact extraction of Section 0 from the registered specification; `docs/EMPIRICAL_RECORD.md` contains all three stages; and `docs/FAVORABLE_REGIME.md` labels the favorable-regime memo `UNTESTED`.

The 400-row T1 table is preserved at `data/autopsy_rows.csv` and matches `f1_v2_autopsy/AUTOPSY_ROWS.csv` byte-for-byte. The SPEC-001 R1–R6 files and SPEC-002 handoff are preserved in `spec/` byte-for-byte. F5: **PASS**.

## F6 — SHA-256 manifest

`ARTIFACT_MANIFEST.sha256` covers every regular file under `cfhm_release/` except the manifest itself, including the `spec/` subtree. The final clean package contains 30 regular files including the manifest, and the manifest contains 29 entries. The self-entry is excluded only under the accepted D-052 non-recursive convention. F6: **PASS**.

## F7 — Prior-tree spot checks

The following pre-existing files were present and unchanged:

```text
f1_v2_autopsy/SUMMARY.csv
lhe_v1/SUMMARY.csv
maf_v1/SUMMARY.csv
```

Their hashes were checked from the clean pre-package repository state and no changes were made to any prior experiment tree. F7: **PASS**.

## Acceptance conclusion

All SPEC-C1 acceptance criteria F1–F7 pass. The artifact remains a negative result: the transmission channel collapses in the shipped regime and the package is not a working hazard predictor. Completion actions under §I remain separate from this local acceptance record.
