================================================================================
SPEC-C1 v1.1: CFHM RESEARCH ARTIFACT — PACKAGING AND VERIFICATION (BINDING)
Author: Ox-alpha. Relay: user. Executor: Manus.
§0 rules UNCHANGED. R2-002 enumeration rule and R2-003 stream-table rule
STANDING. Deviation numbering continues from DEVIATION-062.
================================================================================

SECTION 0 — WHAT THIS ARTIFACT IS (bound narrative; reproduce verbatim
where §E instructs):
  CFHM = Contagion-Fragility Hazard Model (acronym defined HERE for the
  first time in project records). Purpose: predict which node in a
  dependency network suffers the next adverse event, and rank single-node
  removals by predicted total-hazard reduction, using observational event
  logs plus a declared dependency graph.

  EMPIRICAL OUTCOME (all three stages):
    Stage 1 — F1-v1: VOID-BY-DESIGN / INCONCLUSIVE_RATE_EXCLUSIONS. The
      rate gate was unsatisfiable by construction (AUTHOR-ERR-005): no
      intercept term meant median hazard ~0.5 at any kappa. Zero eligible
      seeds; clean void.
    Stage 2 — F1-v2: INCONCLUSIVE_STABILITY_GATE after R6 repair added
      intercept gamma=-3.2 with deterministic bisection fallback. All 100
      seed-arm cases eligible; KILL-B3 fraction 0.98 BUT the pre-
      registered all-seed bootstrap stability gate failed (CFHM gate
      0/50, B3 gate 1/50), so neither PASS nor KILL was licensed.
    Stage 3 — SPEC-002 component autopsy: MIXED classification.
      collapse_fraction=1.0 (all S_tau <= 0.0163 vs init ~0.0171);
      amp_fraction=0.0; channel-gap g_A1=g_A2=0.0 (ablation is a no-op);
      oracle-lift o_A1=+0.20, o_A2=+0.24 (signal exists and is rankable);
      o_b3 ~ 0.0/0.04 (oracle CFHM merely ties plain logistic regression).
      Classification: CHANNEL-INERT + ARCHITECTURE-OVERHEAD +
      REGIME-STARVED.

  ROOT CAUSE (bound statement): the transmission signal enters the
  training objective as b*.E ~ hundredths of a logit against an intercept
  of gamma ~ -4, invisible in loss units; even with perfect fragility
  (V-ORAC) the channel could not learn. The failure is REGIME-SPECIFIC,
  not proof the architecture class is useless.

  CROSS-PROJECT CONTRAST (bound statement; supplied by author because
  executor session lacks global records): sibling design MAF
  (Mechanism-Artifact Factorization) used the same quarantine-channel +
  zero-init-skepticism philosophy WITH a do-masked interventional branch;
  its identifiability gate passed at r=0.9999 BEFORE training; it
  achieved a pre-registered PASS (57% RMSE reduction over best baseline;
  ablation degraded results 161%/251%). Same philosophy, opposite fates;
  the difference is signal visibility in the objective. This artifact
  presents CFHM as the boundary case proving structural priors are
  conditional.

A. SCOPE AND SOURCE OF TRUTH
  A1. Package `cfhm` version 0.1.0, research artifact documenting a
      NEGATIVE result. Target user: researchers studying negative
      results or attempting favorable-regime replications.
  A2. Source of truth: f1_v2/run_experiment.py behavior + SPEC-001 chain
      semantics + SPEC-002 findings. Conflicts => BINDINGS GOVERN.
  A3. Work ONLY in new root cfhm_release/. All existing trees byte-
      immutable. Branch cfhm-artifact from current HEAD d88ec4a855118457
      2d7b1a0d8d521e70e5b23468.
  A4. Copy into cfhm_release/spec/ BEFORE execution:
      SPEC-001-authored.txt, SPEC-001-R1..R6-authored.md,
      SPEC-002_HANDOFF.md, SPEC-C1-authored.md.

B. PACKAGE LAYOUT (closed-world; nothing else ships):
   pyproject.toml (name=cfhm, version=0.1.0, deps pinned numpy/pandas/
     scipy/torch exact as maf_release pins; python>=3.12); LICENSE(MIT);
   README.md (E1 strings); docs/AUTOPSY.md (E2); docs/EMPIRICAL_RECORD.md
   (E3); docs/FAVORABLE_REGIME.md (E4); docs/API.md; src/cfhm/__init__.py;
   src/cfhm/model.py; src/cfhm/worlds.py (generate_world(seed, arm)
   including R6-002 gamma-bisection path); src/cfhm/metrics.py;
   data/autopsy_rows.csv (SPEC-002 T1 verbatim, 400 rows); tests/
   (D1-D4); examples/reproduce_collapse.py; verification/VERIFY.md; spec/.

C. PUBLIC API (bound; nothing else public):
   generate_world(seed:int, arm:str)->WorldDict
     # keys: gamma_calibrated, kappa, true_graph, visible_graph,
     # features_raw[200,9], features_std[200,9], events[N,130],
     # labels[200], b_truth[3,3], c_truth[200],
     # maintainers[5] (A2) or empty (A1); arm in {"A1","A2"}
   CFHMModel(n_nodes:int=200, seed:int|None=None)
     .fit(world:WorldDict, epochs:int=50, lambda1:float=0.01) -> FitReport
       # R3-001 loop semantics; typed-edge hazard recursion (R3-002)
     .forecast_hazard_mass() -> numpy.ndarray  # ex-ante n==0 propagation
     .transmission_amplitudes() -> dict[str,float]
       # {"major":S,"minor":S,"advisory":S} sums over taps
     .spectral_radius() -> float  # <= 0.95 + 1e-9 structurally

D. TESTS (four files, closed-world):
   D1 test_generator.py:
      generate_world(1000,"A1") twice => identical arrays;
      gamma == -4.02490234375 +/- 1e-9;
      train-window event rate == 0.04004807692 +/- 1e-9;
      generate_world(1000,"A2") gamma == -3.712158203125 +/- 1e-9.
      [Anchors from transmitted v2 ledger]
   D2 test_graph_constraint.py: no amplitude exists for non-declared
      edges (structural zero — excitation flows only on declared edges).
   D3 test_stability_cap.py: spectral_radius() <= 0.95 + 1e-9 on every fit.
   D4 test_collapse_signature.py: full bound fit (world 1000, arm A1,
      50 epochs, lambda1 0.01) => ALL THREE transmission_amplitudes()
      <= 0.05. THIS REPRODUCES THE DOCUMENTED COLLAPSE — the artifact's
      central feature. If ANY S_tau > 0.05 => SCIENTIFIC HALT per G2:
      a revived channel means the preserved pipeline differs from what
      was audited, and that discovery outranks shipping.

E. DOCUMENTATION BINDINGS:
   E1. README verbatim string: "RESEARCH ARTIFACT: documents a negative
       result. The contagion transmission channel does not train in the
       shipped regime — it remains at initialization. See
       docs/AUTOPSY.md. Not a working hazard predictor."
   E2. docs/AUTOPSY.md content = SECTION 0 of this document (verbatim
       reproduction required).
   E3. docs/EMPIRICAL_RECORD.md = three-stage table from SECTION 0.
   E4. docs/FAVORABLE_REGIME.md: hypothesis (b* scaled up several-fold,
       gamma nearer zero, lambda1 floored for b) labeled UNTESTED —
       never presented as a finding.

F. ACCEPTANCE CRITERIA:
   F1 fresh install/import (cfhm 0.1.0); F2 four tests pass zero skips;
   F3 D1 anchors within 1e-9; F4 D2/D3/D4 hold; F5 all files exist with
   E-section strings; F6 sha256 manifest over cfhm_release/ incl. spec/,
   self-entry excluded only (D-052 convention); F7 prior-tree spot
   checks: f1_v2_autopsy/SUMMARY.csv, lhe_v1/SUMMARY.csv,
   maf_v1/SUMMARY.csv.

G. FAILURE POLICY:
   G1 tooling failures => fix + deviation log (from DEVIATION-063).
   G2 SCIENTIFIC failures (D1 anchors move, D2/D3 violated, or D4
      channel trains) => NO fix authorized; record verbatim; HALT;
      await author. Exception context: D4 revival would be a DISCOVERY,
      not a bug.

H. TRANSMISSION: STATUS pings start/completion; VERIFY_REPORT.md
   (transmission copy of verification/VERIFY.md); DEVIATIONS.md verbatim
   (numbering from DEVIATION-063); sha256 manifest covering every
   subtree incl. spec/.

I. COMPLETION ACTION (after acceptance): merge cfhm-artifact to main;
   tag cfhm-v0.1.0; push; GitHub Release page remains a separate RELAY
   decision.
================================================================================
END SPEC-C1 v1.1