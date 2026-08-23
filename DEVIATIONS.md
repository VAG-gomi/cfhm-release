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

## DEVIATION-074 — Preserved F1-v2 nested manifest was internally invalid

**Stage:** Read-only deep code and provenance review of the live canonical repository.

**Observed issue:** `research/f1_v2/metrics/artifact_manifest.sha256` contained 561 entries but, when evaluated from its declared `research/f1_v2/` scope, 338 entries were missing and 212 had checksum mismatches. The file combined an unprefixed path family with a second `f1_v2/`-prefixed path family. The preserved F1-v2 payload files themselves were not changed by this review.

**Resolution:** The exact pre-correction manifest bytes are preserved in the new provenance record `research/provenance/f1_v2-metrics-artifact_manifest.invalid-original.sha256`. The active nested manifest is regenerated from the actual dereferenced `research/f1_v2/` tree, excluding only `HANDOFF_REPORT.md` under the historical S11 statement and the manifest being written. The regenerated file is checked from `research/f1_v2/` and all listed files must verify.

**Classification:** Provenance/manifest bookkeeping correction under G1; not a scientific redesign.

**Scientific impact:** None. No model source, configuration, seed, log, raw table, prediction, or historical result file is changed.

**Status:** Resolved by the production-readiness correction pass; active manifest verification passed on the correction branch.

## DEVIATION-075 — Preserved autopsy manifest contained a stale temporary-file entry

**Stage:** Read-only deep code and provenance review of the live canonical repository.

**Observed issue:** `research/f1_v2_autopsy/AUTOPSY_MANIFEST.sha256` contained the entry `AUTOPSY_MANIFEST.sha256.tmp` with the SHA-256 of an empty file, but no such file existed. The remaining 16 autopsy payload entries verified successfully from the autopsy root.

**Resolution:** The exact pre-correction manifest bytes are preserved in `research/provenance/f1_v2_autopsy-AUTOPSY_MANIFEST.invalid-original.sha256`. The active autopsy manifest is regenerated from the actual autopsy tree, excluding only the manifest being written and transient `.tmp` files. The regenerated file is checked from `research/f1_v2_autopsy/` and all listed files must verify.

**Classification:** Provenance/manifest bookkeeping correction under G1; not a scientific redesign.

**Scientific impact:** None. The autopsy source, raw rows, summary, configs, and recorded results remain byte-unchanged.

**Status:** Resolved by the production-readiness correction pass; active manifest verification passed on the correction branch.

## DEVIATION-076 — Packaged AUROC is not historical-scorer equivalent on ties

**Stage:** Read-only deep code review; no metric implementation was changed.

**Observed issue:** The package metric implementation assigns ordinal ranks for tied scores and does not match the historical scorer’s average-tie-rank AUROC semantics. On the preserved 400 seed-arm-method groups, Precision@25 and Precision@10 matched, but AUROC differed in 218 groups; 99 differences exceeded `1e-12`, with maximum absolute difference `0.0047979797979798011`.

**Resolution:** No code or evidence was changed. This entry requests an author ruling on whether package metrics must be historically compatible or are intentionally a separate diagnostic API. The package remains unchanged pending that ruling.

**Classification:** Reproducibility/protocol ambiguity; no scientific redesign made.

**Scientific impact:** No change to D1–D4 or the historical runner, which continues to use the preserved historical scorer.

**Status:** Awaiting author ruling.

## DEVIATION-077 — Undocumented additional public model method

**Stage:** Read-only public-API review; no model implementation was changed.

**Observed issue:** `CFHMModel.interventional_hazard_mass()` is callable but is not listed in SPEC-C1 §C or `docs/API.md`, while SPEC-C1 defines the public API as closed-world (“nothing else public”).

**Resolution:** No method was removed or modified. This entry requests an author ruling on whether the diagnostic method is authorized, should be documented as part of the API, or should be removed under the closed-world rule.

**Classification:** Public-surface/provenance ambiguity; not a scientific redesign.

**Scientific impact:** None observed; the method is not used by D1–D4.

**Status:** Awaiting author ruling.

## DEVIATION-078 — Package fit scope differs from complete historical execution scope

**Stage:** Read-only package-versus-runner review; no source implementation was changed.

**Observed issue:** `CFHMModel.fit` performs the SPEC-C1 full 103-target-row bound fit but does not expose the historical runner’s lambda-selection split, validation reporting, baseline execution, or bootstrap stability procedure.

**Resolution:** The historical runner remains preserved under `research/source/run_experiment.py`; the package remains a compact D4-oriented research-artifact API. This scope distinction is recorded so the package is not represented as a bit-identical replacement for the full historical experiment.

**Classification:** Documentation/scope clarification under G1; not a scientific redesign.

**Scientific impact:** None. Representative package-versus-historical fits differed only at floating-point operation-order scale (maximum forecast-mass delta `3.552713678800501e-15`).

**Status:** Documented; no code change authorized or required pending any future author scope ruling.


## DEVIATION-079 — Evidence-view root-manifest refresh initially included `.git` metadata

**Stage:** Production-readiness correction pass, evidence-view post-commit verification.

**Observed issue:** The first local refresh command for the two evidence-view root manifests omitted the `.git/` exclusion. The resulting manifests verified before the local commits but failed afterward because four mutable Git metadata paths (`.git/index`, `.git/logs/HEAD`, `.git/logs/refs/heads/main`, and `.git/refs/heads/main`) had been hashed. This was a local manifest-generation bookkeeping error; no remote mutation occurred and no scientific or historical evidence payload was changed.

**Resolution:** Regenerate both evidence-view root manifests from worktree files while excluding `.git/`, the active root manifest, and transient `.tmp` files. Re-run all nested, package, input, and root manifest checks after the corrected commits.

**Classification:** Verification-tooling/manifest bookkeeping correction under G1; not a scientific redesign.

**Scientific impact:** None.

**Status:** Resolved by corrected evidence-view root-manifest generation; final verification pending.
