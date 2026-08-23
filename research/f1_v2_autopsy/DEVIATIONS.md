# SPEC-002 Deviation Ledger

## DEVIATION-015 — T2 requests four o_b3 values while D5 defines two

**Stage:** SPEC-002 pre-implementation audit.

D5 defines `o_b3_arm = median over seeds of [P25(V-ORAC) - P25(V-B3R)]`, separately per arm. This yields two values: `o_b3_A1` and `o_b3_A2`. T2, however, requests “the four o_b3 values” after requesting `o_A1` and `o_A2`; no additional indexing or formula defines four distinct o_b3 quantities.

This is material because the executor must not invent additional aggregations or duplicate the two defined values under different names. Implementation is paused before any fit. The executor requests an author binding for whether T2 should contain the two D5-defined values (`o_b3_A1`, `o_b3_A2`) or a newly specified four-value breakdown.

**Classification:** Specification ambiguity; no scientific or implementation choice has been made.

## DEVIATION-015 closure — resolved by SPEC-002-R1-001

The author bound T2 to the two D5-defined values `o_b3_A1` and `o_b3_A2`; the four oracle-gap values total are `{o_A1, o_A2, o_b3_A1, o_b3_A2}`. No additional aggregation or duplicate values will be emitted. Implementation is unblocked under SPEC-002 and SPEC-002-R1.

## DEVIATION-016 — SPEC-002-R1 T2 summary-count language is internally inconsistent

**Stage:** SPEC-002-R1 pre-implementation audit.

R1-001 says T2 transmits “exactly SIX summary statistics,” but its binding list names `g_A1`, `g_A2`, `collapse_fraction`, `amp_fraction`, `rho_median (A2)`, `o_A1`, `o_A2`, `o_b3_A1`, and `o_b3_A2`—nine named quantities. The original T2 additionally requires D1 pass rate and worst delta, bringing the complete set of explicitly named T2 entries to eleven. R1-001 also says “i.e., TEN entries where D2-D5 define ten,” which does not reconcile with either count: D2–D5 as explicitly defined yield nine quantities after resolving `o_b3` to two values, and adding the two D1 quantities yields eleven.

This is material because the executor cannot decide whether to omit named evidence or invent an unstated summary statistic. Implementation is paused pending an author binding for the exact T2 row set. No fit or autopsy output has been generated.

**Classification:** Specification counting contradiction; no scientific or transmission choice has been made.

## DEVIATION-016 closure — resolved by SPEC-002-R2-001

R2-001 binds the complete closed-world T2 table to exactly eleven rows: `d1_gate_pass_fraction`, `d1_worst_delta`, `g_A1`, `g_A2`, `collapse_fraction`, `amp_fraction`, `rho_median_A2`, `o_A1`, `o_A2`, `o_b3_A1`, and `o_b3_A2`. Prior prose cardinality claims are retired; no named quantity is omitted or added.

## DEVIATION-017 — Initial full-run shell redirection targeted a deleted log directory

**Stage:** SPEC-002 execution launch, before any fit.

The executor command redirected stdout/stderr to `f1_v2_autopsy/logs/full_autopsy.log`, but the output root’s `logs/` directory had not yet been created. The shell therefore failed before Python started:

```text
bash: f1_v2_autopsy/logs/full_autopsy.log: No such file or directory
```

The SPEC-002 runner itself deletes and recreates generated output directories at invocation start, so the corrected launch creates the log directory before shell redirection. No fit ran and no prior tree was modified.

## DEVIATION-017a — Runner reset removed the shell-owned full-run log

**Stage:** SPEC-002 full-run launch.

The corrected shell launch created `f1_v2_autopsy/logs/` before redirecting output, but the runner’s required idempotent reset then removed that directory at invocation start. The Python run itself completed successfully, producing T1/T2 and the completion status; the shell wrapper subsequently failed only when attempting to `tail` the deleted log file. No fit failed, no input read failed, and no prior tree was modified. The generated evidence is preserved in the new autopsy root; no executor log is required by T1–T4.


## DEVIATION-074 — Autopsy manifest contained a stale temporary-file entry

**Stage:** Read-only deep code and provenance review of the live CFHM canonical repository.

**Observed issue:** `AUTOPSY_MANIFEST.sha256` listed `AUTOPSY_MANIFEST.sha256.tmp` with the SHA-256 of an empty file, but no such temporary file existed. The remaining 16 listed autopsy payload files verified successfully from the autopsy root.

**Resolution:** The exact pre-correction manifest bytes are preserved in the canonical repository’s `research/provenance/f1_v2_autopsy-AUTOPSY_MANIFEST.invalid-original.sha256`. The active manifest is regenerated from the actual autopsy tree, excluding only the manifest being written and transient `.tmp` files. No autopsy source, raw table, summary, configuration, or recorded result is changed.

**Classification:** Provenance/manifest bookkeeping correction under G1; not a scientific redesign.

**Scientific impact:** None.

**Status:** Resolved by the production-readiness correction pass; active manifest verification passed on the correction branch.
