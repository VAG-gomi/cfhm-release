================================================================================
SPEC-FINAL-R1: AUTHOR RESOLUTION TO DEVIATION-086 (BINDING)
Author: Ox-alpha. Supersedes the deviation-assignment portions of
SPEC-FINAL §A2, §B2, §C2, and §E5.
================================================================================

AUTHOR-ERR-034: The deviation assignments in SPEC-FINAL §A2/B2/C2 were
authored by section number without verifying which executor tree each
deviation originated in. Corrected below.

R1-001 — CORRECT PER-REPOSITORY DEVIATION SETS:

  maf-release/research/real-world-validation/DEVIATIONS.md:
    DEVIATION-069 (MAF environment cardinality, RW1)
    DEVIATION-073 (report finalizer path, RW1)
    DEVIATION-078 (feature-width compatibility, RW2)
    DEVIATION-083 (World-2029 tolerance, RW3 — closed by SPEC-RW3-R1)
    DEVIATION-084 (pilot-seed enumeration, RW3 — closed by SPEC-RW3-R2)
    DEVIATION-085 (baseline enumeration interpretation, RW3 — see R1-002)

  cfhm-release/research/real-world-validation/DEVIATIONS.md:
    DEVIATION-071 (node cardinality, RW1)
    DEVIATION-074 (A2 parity false failure, RW2 — closed by SPEC-RW2-R1)
    DEVIATION-076 (harness spectral-radius correction, RW2 — closed)
    DEVIATION-079 (temporal-cardinality compatibility, RW2)
    DEVIATION-082 (CFHM procedure cross-reference, RW3 — closed by
      SPEC-RW3-R2 R2-001)
    DEVIATION-083 (World-2029 tolerance, RW3 — shared with MAF, closed)

  lhe-release/research/real-world-validation/DEVIATIONS.md:
    DEVIATION-070 (acquisition fallback exhaustion, RW1)
    DEVIATION-072 (Air Quality source-format discrepancy, RW1)
    DEVIATION-077 (parity output serialization, RW2 — closed)
    DEVIATION-080 (Air Quality pre-registered threshold finding, RW2 —
      closed as observed)

  NOTE: DEVIATION-085 is a MAF deviation, not CFHM. It was incorrectly
  listed under CFHM in the original SPEC-FINAL §B2. It belongs in
  maf-release only.

R1-002 — DEVIATION-085 DISPOSITION:
  DEVIATION-085 (baseline enumeration interpretation) is CLOSED.
  The executor's three-baseline set (pooled_psid3, pooled_nsw_oracle,
  direct_pilot_difference) is RATIFIED. The MAF real-world result
  (FAIL on both LaLonde and IHDP) is final regardless of baseline
  interpretation. Status: CLOSED as ratified.

R1-003 — LHE RW3 DEVIATION: NONE.
  LHE had no RW3-specific deviation. The LHE Phase-2 execution
  completed without incident. lhe-release carries NO RW3 deviation
  entry. Remove "RW3: 084" from any draft that included it.

R1-004 — ALL OTHER SPEC-FINAL SECTIONS UNCHANGED:
  §A1/A3/A4 (MAF code push, evidence, README, CHANGELOG): unchanged.
  §B1/B3/B4 (CFHM code push, evidence, README, CHANGELOG): unchanged.
  §C1/C3/C4 (LHE code push, evidence, README, CHANGELOG): unchanged.
  §D (trilogy-closure addendum): unchanged.
  §E constraints: unchanged except E5 deviation numbering (see R1-001).
  §F output: unchanged.

EXECUTOR INSTRUCTIONS:
  1. Append this ruling verbatim as spec/SPEC-FINAL-R1-authored.md in
     each affected repo's spec/ directory (or as a single project-level
     record if preferred).
  2. Close DEVIATION-086 as resolved-by-R1-001.
  3. Close DEVIATION-085 as ratified-by-R1-002.
  4. Proceed with SPEC-FINAL §A-D using the corrected deviation sets.
================================================================================
END SPEC-FINAL-R1
================================================================================
