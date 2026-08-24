SPEC-RW2-R1: AUTHOR RULING ON DEVIATION-074 (BINDING)
Author: Ox-alpha. Relay: user. Executor: Manus. Deviations continue from
DEVIATION-076 (this ruling's own registration and any harness corrections
are logged here; DEVIATION-074 closes under R1-001).
================================================================================

AUTHOR-ERR-030: SPEC-RW2 §G2.3 bound amplitude references for arm A1
only and provided no references for arm A2. The executor reasonably
applied the A1 references to A2, producing a false parity failure.
Root cause: author under-specified the gate. Ruling below.

R1-001 — CFHM PHASE-1 GATE: OVERTURNED TO PASS.
  Ground truth: the certified A2 amplitudes are recorded in the
  SPEC-002 T1 table (world 1000, arm A2, V-REFIT), which exists in
  the executor workspace at cfhm_v2/research/f1_v2_autopsy/AUTOPSY_ROWS.csv:
    major    = 0.016286579456825427
    minor    = 0.01628656954388021
    advisory = 0.016286499458644653
  The v2 observed A2 values match these BIT-FOR-BIT (delta = 0 on all
  three). Combined with A1's bit-exact match, CFHM v2 achieves PERFECT
  parity on both arms. Gamma (both arms, delta = 0) and spectral radius
  checks also pass. The D4 collapse signature (all amplitudes <= 0.05)
  is unaffected on both arms — the negative result stands.

R1-002 — HARNESS CORRECTIONS (mandatory before LHE gate):
  a. A2 amplitude references in the parity harness are corrected to the
     SPEC-002 certified values above.
  b. Harness bug: the reported spectral_radius field echoed the major
     amplitude value instead of the computed spectral radius. Report
     the actual computed value; the <= 0.95 + 1e-9 check itself passed
     and is unaffected.

R1-003 — PROVENANCE RULE (standing, project-wide):
  Every future parity gate must cite the PROVENANCE of each expected
  reference value (which certified artifact/table/row it derives from).
  Uncited references are prohibited. This rule exists because of this
  incident.

R1-004 — SEQUENCE RESUMES:
  1. Apply R1-002 harness corrections; log as DEVIATION-076 (closed).
  2. Re-run the CFHM A2 parity check against the corrected references
     (expected result: PASS with delta = 0 on all three amplitudes).
  3. Proceed to LHE Phase-1 gate (G3.3), then Phase 2 per SPEC-RW2,
     all thresholds and orderings unchanged.
================================================================================
END SPEC-RW2-R1
================================================================================
