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

## DEVIATION-067 — Readable T1 rendering was absent after evidence-stage rebuild

**Stage:** Four-repository staging, before GitHub repository creation.

**Observed issue:** The rebuilt evidence staging tree contained the authoritative raw `AUTOPSY_ROWS.csv` but not the separately generated `AUTOPSY_ROWS_READABLE.md`. A copy guard stopped before any repository creation or remote mutation.

**Resolution:** Regenerate the complete 400-row Markdown rendering directly from the actual raw CSV, verify the row count, and copy it to both evidence views. The raw CSV remains authoritative and unchanged.

**Classification:** Staging/documentation bookkeeping failure under §G1, not a scientific or model change.

**Scientific impact:** None observed. No raw evidence or package source was changed.

**Status:** Resolved by deterministic rendering from the preserved CSV.

## DEVIATION-068 — Initial four-repository README advertised a nonexistent runner path

**Stage:** Post-creation live repository audit.

**Observed issue:** The initial canonical README advertised `research/maf-spec-m1/run_maf.py`, which was a copied MAF-pattern path and did not exist in the CFHM repository. The actual preserved CFHM F1-v2 runner is the outer-workspace file `run_experiment.py`; the actual SPEC-002 runner is `f1_v2_autopsy/run_autopsy.py`.

**Resolution:** Add the actual preserved F1-v2 runner and metric runner under `research/f1_v2/` in the canonical repository and under `evidence/source/` in both evidence views. Correct all README/catalog/reproduction links to those paths. No model behavior, raw evidence, or authored specification is changed.

**Classification:** Documentation/path bookkeeping failure under §G1, not a scientific or model change.

**Scientific impact:** None observed. The files added are preserved source copies, and representative hashes are checked against the outer workspace.

**Status:** Resolved by path correction and source-file preservation.

## DEVIATION-069 — Staged mirrors retained stale MAF-derived documentation paths

**Stage:** Four-repository link audit after initial CFHM repository creation.

**Observed issue:** The copied CFHM package README still contained the earlier MAF-derived `research/maf-spec-m1/run_maf.py` reference, and the staged evidence catalog retained an obsolete relative runner link. The advertised paths did not exist in the newly created CFHM repositories.

**Resolution:** Correct the canonical package README, the evidence catalog, and all staged mirror copies to point to the actual CFHM F1-v2 runner at `research/source/run_experiment.py` and the actual SPEC-002 runner at `f1_v2_autopsy/run_autopsy.py`. Preserve the raw source files byte-for-byte and regenerate affected manifests. No model behavior or scientific result is changed.

**Classification:** Documentation/path bookkeeping failure under §G1, not a scientific or model change.

**Scientific impact:** None observed. The correction only makes existing actual source files discoverable.

**Status:** Resolved by path correction and link audit.

## DEVIATION-070 — Canonical staging initially replaced the package manifest scope

**Stage:** Four-repository staging, before GitHub correction push.

**Observed issue:** The first canonical staging pass regenerated `ARTIFACT_MANIFEST.sha256` across the entire canonical repository, which would have replaced the SPEC-C1 package manifest’s intended 30-file package scope.

**Resolution:** Restore `ARTIFACT_MANIFEST.sha256` byte-for-byte from the accepted local package and use a separate `REPOSITORY_MANIFEST.sha256` for the broader canonical repository tree. The package manifest and repository manifest now have distinct scopes.

**Classification:** Provenance/manifest-scope bookkeeping failure under §G1, not a scientific or model change.

**Scientific impact:** None observed. No source, data, specification, or model behavior changed.

**Status:** Resolved before the correction push.

## DEVIATION-071 — Correction staging attempted a self-copy

**Stage:** Four-repository correction staging.

**Observed issue:** A refresh loop attempted to copy `cfhm-spec-c1-evidence/ARTIFACT_CATALOG.md` onto the same path, causing `cp` to stop. The command made no GitHub mutation.

**Resolution:** Remove the redundant self-copy case and rerun the staging refresh. The source, raw evidence, and repository contents are unaffected.

**Classification:** Local staging command bookkeeping failure under §G1, not a scientific or model change.

**Scientific impact:** None observed.

**Status:** Resolved by corrected staging command.

## DEVIATION-072 — Active-link scanner flagged historical deviation prose

**Stage:** Post-correction remote verification.

**Observed issue:** A broad grep treated the old MAF-derived path quoted inside DEVIATION-068 and DEVIATION-069 historical records as an active stale link and stopped the verification pass. The remote repository had no active broken reference at that point.

**Resolution:** Rerun link verification against active README/catalog/reproduction links while allowing historical deviation records to retain their exact incident descriptions. No remote repository mutation occurred during the false-positive check.

**Classification:** Verification-tooling false positive under §G1, not a scientific or model change.

**Scientific impact:** None observed.

**Status:** Resolved by scoped active-link verification.

## DEVIATION-073 — Local provenance refresh shell had an unterminated final quote

**Stage:** Final package-copy refresh before GitHub correction push.

**Observed issue:** The refresh command’s final `printf` string ended with a double quote instead of a single quote, leaving the shell waiting for continuation. The local package-manifest work and provenance commit completed before the shell was terminated; the command did not push or mutate GitHub.

**Resolution:** Terminate the waiting shell, inspect the local commit and staged repository manifests, and continue using a corrected command. No scientific files or remote state are affected.

**Classification:** Shell-command bookkeeping failure under §G1, not a scientific or model change.

**Scientific impact:** None observed.

**Status:** Resolved by shell cleanup and corrected verification.
