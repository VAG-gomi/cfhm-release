# CFHM Empirical Record

This table is a human-readable transcription of the three-stage bound narrative in `docs/AUTOPSY.md`. It records outcomes without upgrading any inconclusive or negative result into a favorable claim.

| Stage | Recorded outcome | Meaning |
|---|---|---|
| F1-v1 | `VOID-BY-DESIGN / INCONCLUSIVE_RATE_EXCLUSIONS` | The original rate gate was unsatisfiable by construction because the model had no intercept term; zero eligible seeds remained. |
| F1-v2 | `INCONCLUSIVE_STABILITY_GATE` | The R6 intercept repair and deterministic bisection made all 100 seed-arm cases eligible, but the all-seed bootstrap stability gate failed: CFHM `0/50`, B3 `1/50`. Neither PASS nor KILL was licensed. |
| SPEC-002 autopsy | `MIXED` | `collapse_fraction=1.0`, `amp_fraction=0.0`, `g_A1=g_A2=0.0`, oracle lifts `o_A1=+0.20`, `o_A2=+0.24`, and oracle-B3 lifts approximately `0.0/0.04`. |

## Interpretation boundary

The observed CFHM failure is classified as **CHANNEL-INERT + ARCHITECTURE-OVERHEAD + REGIME-STARVED**. The channel signal entered the training objective at hundredths of a logit against an intercept near `-4`, so the learned transmission amplitudes remained near initialization. This is a regime-specific negative result, not proof that the architecture class is universally useless.

The raw T1 table is [`../data/autopsy_rows.csv`](../data/autopsy_rows.csv). The authored narrative that governs this summary is [`AUTOPSY.md`](AUTOPSY.md).
