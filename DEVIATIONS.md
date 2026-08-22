# CFHM Release Deviations

This ledger records packaging and execution deviations for SPEC-C1 v1.1. The first new entry continues the authorized sequence from DEVIATION-063. Existing CFHM experiment ledgers remain immutable outside `cfhm_release/`.

## DEVIATION-063 — SPEC-C1 source path differs from the preserved workspace layout

**Stage:** SPEC-C1 package construction, before acceptance execution.

**Bound reference:** SPEC-C1 §A2 names `f1_v2/run_experiment.py` as the source-of-truth behavior.

**Observed workspace state:** No file exists at `/home/ubuntu/cfhm_f1/f1_v2/run_experiment.py`. The preserved `f1_v2/` directory contains the completed evidence subdirectories and a symlinked `spec/` directory. The actual R6/R7 implementation is the repository-root file `/home/ubuntu/cfhm_f1/run_experiment.py`, present at bound current HEAD `d88ec4a8551184572d7b1a0d8d521e70e5b23468`.

**Resolution:** The package implementation was extracted from the actual preserved root implementation and its bound SPEC-001/R5/R6 semantics. No new scientific rule was selected, no historical tree was modified, and the path mismatch is disclosed rather than silently hidden. The package’s public modules are split according to SPEC-C1 §B; the original root implementation remains preserved outside `cfhm_release/`.

**Classification:** Tooling/layout bookkeeping deviation. This is an implementation necessity under G1, not a scientific redesign.

**Scientific impact:** None observed. The seed-1000 generator anchors and D4 collapse gate are tested against the prescribed values before proceeding to downstream acceptance work.

**Status:** Resolved for package construction; retained as provenance.

## DEVIATION-064 — Fresh install generated unbound build artifacts inside cfhm_release

**Stage:** Initial fresh-install acceptance run.

**Observed issue:** Running `pip install .` from the package root generated `build/`, `src/cfhm.egg-info/`, and `__pycache__/` files inside `cfhm_release/`. These paths are not listed in SPEC-C1 §B’s closed-world package layout and must not enter the release manifest.

**Resolution:** The generated installation artifacts will be removed from `cfhm_release/` before acceptance manifest generation. The fresh install itself passed; the package will be installed from outside the package root for the clean acceptance rerun. No scientific source or historical tree is changed.

**Classification:** Tooling/build bookkeeping failure under §G1, not a scientific or model change.

**Scientific impact:** None observed. The isolated tests and D4 collapse gate passed before the cleanup.

**Status:** Resolved by clean-tree cleanup and external-root installation rerun.

**Follow-up observation:** The clean external-root install avoided build and egg-info pollution in `cfhm_release`, but running pytest from the package source recreated local `__pycache__` files. These are also excluded by cleanup before the manifest and are not release artifacts.

## DEVIATION-065 — Pytest cache entered the package tree during acceptance

**Stage:** Final local acceptance audit.

**Observed issue:** Running pytest from the package root created `.pytest_cache/` with five transient files. This directory is not part of the SPEC-C1 §B closed-world layout and must not be shipped.

**Resolution:** The transient cache is removed before the final manifest is generated. Future acceptance invocations use an external working directory or disable the cache provider. The four test results and D4 output remain valid; no scientific source or prior tree is altered.

**Classification:** Tooling/test-runner bookkeeping failure under §G1, not a scientific or model change.

**Scientific impact:** None observed.

**Status:** Resolved by cleanup and final manifest regeneration.

## DEVIATION-066 — Final acceptance command used an unsupported pytest cache option

**Stage:** Final acceptance rerun.

**Observed issue:** The command used `pytest --cache-dir=...`, but pytest does not expose that option. The test command exited before collecting tests. The same command also attempted a source-root install, which recreated transient build metadata in `cfhm_release` before the test invocation.

**Resolution:** The unsupported option is replaced with pytest’s supported `-o cache_dir=...` setting. The final clean verification will run from outside the package tree without installing from the source root, then remove and verify any transient files before manifest finalization.

**Classification:** Tooling/command bookkeeping failure under §G1, not a scientific or model change.

**Scientific impact:** None observed. The prior four-test run and D4 collapse output remained unchanged; this failed command did not execute the acceptance tests.

**Status:** Resolved by corrected external-root acceptance command and clean-manifest rerun.
