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

