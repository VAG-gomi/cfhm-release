# RW3 Report — Final Interface Generalization and Real-World Results

> **Scope.** This report records the SPEC-RW3 v1.0 campaign under SPEC-RW3-R1 and SPEC-RW3-R2. The v3/v2 code was executed only in isolated copies; original source repositories remained untouched until the SPEC-FINAL publication authorization.

## Executive verdict

| Design | Phase-1 parity | Phase-2 result | Final real-world label |
|---|---|---|---|
| MAF | PASS under the author-ratified World-2029 secondary tolerance | LaLonde `0/20` close-to-RCT; IHDP did not beat pooled regression | **FAIL** |
| CFHM | PASS on A1/A2 certified synthetic references | Precision@50 threshold passed; all amplitudes remained `≤0.05` | **CONFIRMED negative** |
| LHE | PASS on the preserved eight-row synthetic parity set | RW2 real-data result carried forward: Air Quality `FAIL 0/20`, Appliances `PASS 20/20` | **INCONCLUSIVE (split)** |

## Phase-1 parity

MAF World-2000 observed RMSE was `0.1118193525252465` with M-PSI `0.9082706766917292` and M-DAUROC `0.8`. World-2029 observed RMSE was `0.1323046844352985`; SPEC-RW3-R1 authoritatively re-scoped that secondary tolerance to `1e-3`. The MAF Phase-1 gate therefore passed.

CFHM World-1000 A1 amplitudes were `{'major': 0.016286008171011557, 'minor': 0.016285802691637867, 'advisory': 0.016285407525629885}` and A2 amplitudes were `{'major': 0.016286579456825427, 'minor': 0.01628656954388021, 'advisory': 0.016286499458644653}`. Gamma and spectral-radius checks passed on both arms. The CFHM Phase-1 gate passed.

LHE Phase-1 used the preserved SPEC-L1 synthetic rows for seeds 3000 and 3103, both methods, and all required budgets. The preserved parity table matched exactly and all five local LHE tests passed.

## MAF Phase-2 — LaLonde

The NSW RCT ATE computed from the preserved 185 treated and 260 control rows was `1794.342404270271`. For each author-enumerated pilot seed `1..20`, the runner used `default_rng(7000 + pilot_seed)` and selected 30 treated plus 30 control rows. The MAF fit used the PSID3 observational environment and the pilot NSW interventional environment, with feature width 8 accepted by the generalized encoder. The close-to-RCT criterion passed in `0/20` pilots and the MAF was closest to the ratified three-baseline set in `2/20`; the LaLonde result is **FAIL**.

| Pilot | MAF ATE | Absolute error | Closest to RCT |
|---:|---:|---:|:---:|
| 1 | 0.005827836692 | 1794.336576433579 | no |
| 2 | 0.003652835265 | 1794.338751435006 | no |
| 3 | 0.044632513076 | 1794.297771757195 | yes |
| 4 | 0.001953887986 | 1794.340450382285 | no |
| 5 | 0.017762994394 | 1794.324641275877 | no |
| 6 | 0.008190947585 | 1794.334213322686 | no |
| 7 | 0.024039255455 | 1794.318365014816 | no |
| 8 | 0.002016399521 | 1794.340387870750 | yes |
| 9 | 0.019472781569 | 1794.322931488702 | no |
| 10 | 0.005211441312 | 1794.337192828959 | no |
| 11 | 0.044211525470 | 1794.298192744801 | no |
| 12 | 0.022612543777 | 1794.319791726494 | no |
| 13 | 0.022767970338 | 1794.319636299932 | no |
| 14 | 0.002589842537 | 1794.339814427733 | no |
| 15 | 0.004898606334 | 1794.337505663937 | no |
| 16 | 0.052564505488 | 1794.289839764783 | no |
| 17 | 0.005870318506 | 1794.336533951765 | no |
| 18 | 0.013810254633 | 1794.328594015637 | no |
| 19 | 0.032575499266 | 1794.309828771005 | no |
| 20 | 0.060263697058 | 1794.282140573213 | no |

## MAF Phase-2 — IHDP

| Replication | MAF sqrt-PEHE | Pooled sqrt-PEHE | Per-environment sqrt-PEHE |
|---:|---:|---:|---:|
| 8 | 1.732174489502 | 1.541899103060 | 1.541802844168 |
| 9 | 28.157419548117 | 28.126208311794 | 27.948762944671 |
| 10 | 8.946672391909 | 8.906740273138 | 8.906568921558 |

Mean MAF sqrt-PEHE was `12.945422143176183` versus pooled `12.858282562664044` and per-environment `12.799044903465917`. The MAF-vs-pooled reduction was `-0.006776922196838342`; the IHDP criterion did not pass.

## CFHM Phase-2 — Retraction citation network

The preserved network contained `8507` nodes and `8213` edges. The actual data-derived temporal container used origin `1975-05-28`, cutoff `2020-01-01`, `2327` training weeks, and `342` test weeks. The model accepted the nine-feature node matrix and completed the fit without padding or truncating the data.

| Bootstrap | CFHM P@50 | B-FRAG P@50 | B-DEG P@50 |
|---:|---:|---:|---:|
| 1 | 0.500000 | 0.380000 | 0.320000 |
| 2 | 0.600000 | 0.400000 | 0.420000 |
| 3 | 0.540000 | 0.380000 | 0.380000 |
| 4 | 0.600000 | 0.400000 | 0.380000 |
| 5 | 0.500000 | 0.260000 | 0.300000 |

Mean CFHM P@50 was `0.548` versus B-FRAG `0.364`. The required threshold was `0.41859999999999997` and the threshold passed. Learned amplitudes were major `0.016272595146844458`, minor `0.0162725951993345`, and advisory `0.0162725951993345`. Every amplitude remained `≤0.05`, so the pre-registered collapse clause records a **CONFIRMED negative** real-data result rather than a bug.

## LHE real-world record

No separate RW3 LHE Phase-2 rerun was required by SPEC-FINAL-R1: the author ruled that LHE had no RW3-specific deviation. The completed RW2 real-world evidence remains the operative LHE record: Air Quality V-LHE won `0/20`, Appliances V-LHE won `20/20`, and the overall label is **INCONCLUSIVE (split)**.

## Interpretation boundary

The generalized interfaces removed the prior feature-width and temporal-cardinality blockers while retaining the original equations, losses, masks, recursion, and parity checks. The real-world evidence does not establish deployment effectiveness for any design: MAF is negative on both tested datasets, CFHM reproduces its channel-inert negative result on the real network, and LHE remains dataset-dependent.

## Provenance

Raw data were reused from the DS-1 preservation area. The complete source and evidence paths are listed in the SPEC-FINAL research folders. This report is a transmission artifact assembled from the isolated RW3 result JSON files, Phase-1 parity output, and the ratified SPEC-RW3-R1/R2 rulings.
