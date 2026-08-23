# CFHM Provenance Correction Records

This directory preserves the exact bytes of two manifest files as they existed at the reviewed canonical head before the authorized production-readiness correction pass.

The files ending in `.invalid-original.sha256` are archival records of the prior manifest state. They are retained so that the correction is auditable and reversible as a provenance event; they are not active verification manifests.

The active corrected manifests remain at their original paths:

| Active manifest | Verification root | Corrected scope |
|---|---|---|
| `research/f1_v2/metrics/artifact_manifest.sha256` | `research/f1_v2/` | All dereferenced F1-v2 regular files except the historical `HANDOFF_REPORT.md`, the active manifest itself, and transient `.tmp` files |
| `research/f1_v2_autopsy/AUTOPSY_MANIFEST.sha256` | `research/f1_v2_autopsy/` | All autopsy regular files except the active manifest itself and transient `.tmp` files |

This correction pass does not modify the CFHM model implementation, historical runner source, configurations, seeds, logs, raw tables, predictions, summaries, or authored specifications. The manifest and documentation changes are recorded in the repository deviation ledger.
