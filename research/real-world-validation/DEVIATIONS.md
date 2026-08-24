# Real-World Validation Deviations



This ledger contains the per-repository records ratified by SPEC-FINAL-R1. Historical entries not assigned to this repository remain in their source ledgers.



## DEVIATION-071 — CFHM real-network cardinality blocks the bound model

**Stage:** SPEC-RW1 C-section after the bound network construction and before any CFHM fit.

**Observed network:** 500 valid retracted papers were sampled with seed 7000, all 500 OpenCitations calls returned response files, and the resulting graph contained 8,507 nodes and 8,213 unique citation edges.

**Exact observed error:**

```text
CFHM_PREFLIGHT|ValueError|n_nodes must be 200
```

**Classification:** Binding implementation/interface compatibility failure. The execution layer did not truncate the network, pad it, change the certified MLP input contract, or create an unrequested model variant.

**Scientific impact:** Precision@50, the transmission coefficient, and the C4 thresholds are **not evaluated**. Network construction evidence remains preserved.

## DEVIATION-074 — Initial CFHM A2 parity reference was under-specified

**Stage:** Initial SPEC-RW2 Phase-1 CFHM parity.

The original SPEC-RW2 §G2.3 text supplied amplitude references for arm A1 but no separate references for arm A2. The executor reasonably applied the A1 values to A2, producing a false parity failure.

**Author ruling:** SPEC-RW2-R1 R1-001 overturned the halt. The certified A2 values are the SPEC-002 T1 table, world 1000, arm A2, V-REFIT: major `0.016286579456825427`, minor `0.01628656954388021`, advisory `0.016286499458644653`. The corrected rerun matched all three bit-for-bit. DEVIATION-074 is **CLOSED under R1-001**.

## DEVIATION-076 — Mandatory CFHM harness correction under SPEC-RW2-R1

SPEC-RW2-R1 required two harness corrections before the LHE gate: use the proper SPEC-002 T1 A2 references and report the actual computed spectral radius in a distinct field. The corrected harness cited the reference provenance explicitly and reported computed spectral radii `0.016286008171011557` (A1) and `0.016286579456825427` (A2). The corrected CFHM parity gate passed.

**Classification:** Harness/provenance correction authorized by the author ruling.

**Status:** CLOSED.

## DEVIATION-079 — CFHM real-data temporal-cardinality compatibility blocker

**Stage:** RW2 Phase-2 Section C.

The preserved real network contains 8,507 nodes and 8,213 unique edges. The generalized CFHM constructor accepts `n_nodes=8507` and nine-feature input, but the Section C temporal matrix has 52 weeks while the certified fit contract remains fixed at 130 total weeks.

**Exact result:**

```text
ValueError: events must have shape (8507, 130)
```

No weeks were padded, truncated, or invented; no precision@50 or transmission coefficient was claimed.

**Classification:** Binding interface compatibility finding, not a scientific threshold result.

**Status:** OPEN pending a separate author specification or ruling.

## DEVIATION-082 — CFHM Phase-2 procedure cross-reference

**Stage:** RW3 Phase-2 CFHM execution.

SPEC-RW3 §C3.4 conflicted with the earlier “unchanged” cross-reference in SPEC-RW1. SPEC-RW3-R2 R2-001 ruled that §C3.4 is the complete and exclusive procedure for this cycle. **Status: CLOSED by SPEC-RW3-R2 R2-001.**

## DEVIATION-083 — Shared World-2029 tolerance ruling

**Stage:** RW3 Phase-1 parity.

The MAF secondary World-2029 tolerance was widened to `1e-3` by SPEC-RW3-R1; CFHM parity itself passed. **Status: CLOSED by SPEC-RW3-R1.**
