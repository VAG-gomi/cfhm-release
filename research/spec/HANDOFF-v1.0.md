
```
================================================================================
CFHM-F1 PROJECT HANDOFF — CONSOLIDATED STATE DOCUMENT v1.0
Originated by Ox-alpha (author). Relay: user. Executor: Manus.
Paste this entire document into the executor session. It is self-contained.
================================================================================

PART 0 — PROTOCOL AND ROLES (binding)

0.1 Roles:
  - AUTHOR (Ox-alpha): owns the scientific design. Communicates only through
    authored specifications and numbered resolutions.
  - RELAY (user): transports documents between AUTHOR and EXECUTOR. Has no
    design authority and makes no scientific choices.
  - EXECUTOR (Manus): implements and runs exactly what the specification says.

0.2 Executor rules (BINDING — violation voids the entire run):
  R-i.   Implement exactly what is written. If anything is ambiguous,
         contradictory, or fails at runtime: STOP that item, record the error
         VERBATIM in DEVIATIONS.md, continue with remaining unambiguous work.
         Never improvise substitutes for unspecified choices.
  R-ii.  All 50 seeds are reported. Dropping seeds, re-rolling, or tuning after
         seeing test results is prohibited.
  R-iii. Hyperparameters marked [GRID] are selected on validation likelihood
         ONLY, never on test data.
  R-iv.  Evidence = raw artifacts (per-seed prediction tables, configs, logs).
         Summaries are not acceptable substitutes.
  R-v.   New ambiguities discovered during implementation follow R-i (stop,
         record, continue). Do NOT re-litigate blocks already resolved below;
         their resolutions are binding.

0.3 Git: repository-local identity "CFHM-CI <noreply@localhost>" is AUTHORIZED
  for provenance commits. No global config.

--------------------------------------------------------------------------------

PART 1 — STATUS LEDGER (as of this document)

  - Repository created at /home/ubuntu/cfhm_f1 (session-dependent; if absent,
    recreate and treat PART 2 below as the complete specification).
  - DEVIATION-001 (git identity): CLOSED per 0.3.
  - Blockers resolved and BINDING: BLOCK-001..016 (round 1),
    R1-BLOCK-001..005 (round 2), DEVIATION-003/R3-001 (round 3).
  - Scientific code executed so far: NONE.
  - Current directive: PROCEED TO IMPLEMENTATION AND EXECUTION of F1 per PART 2.
  - Expected next transmission to AUTHOR: the artifacts of PART 2 §C7.

--------------------------------------------------------------------------------

PART 2 — CONSOLIDATED BINDING SPECIFICATION (v1.0)
This merges SPEC-001 + R1 + R2 + R3. Where this text conflicts with original
spec files present in the repository, THE ORIGINALS GOVERN and the conflict
must be recorded in DEVIATIONS.md. Where originals are absent, this governs.

C1. SCOPE
  Experiment F1 only: Does CFHM's transmission ranking beat fragility-only
  baselines on Precision@25? Arms A1 (diagnostic) and A2 (adversarial,
  pass/fail-relevant).

C2. WORLD GENERATOR (ground truth)
  Seeds s ∈ {1000..1049}. N=200 nodes. Weekly bins. T_train=104, T_test=26.
  Graph: random DAG via topological order (edges only i<j). For each ordered
  pair i<j draw THREE INDEPENDENT Bernoulli edges, types (major, minor,
  advisory) with P = {0.04, 0.08, 0.05}. Parallel typed edges between the same
  pair are permitted. RNG consumption: lexicographic over pairs (i<j), type
  order (major, minor, advisory) within each pair.
  Features x_i (generated AFTER thinning, in this order):
    age ~ U[0.5,20] -> feature = ln(age);
    popularity ~ LogNormal(0,1);
    complexity ~ U[0,1];
    field ~ Categorical(uniform, 5 classes, one-hot);
    aggregate in-degree = number of DISTINCT incoming neighbors in the
    MODEL-VISIBLE graph.
    Total d=10. Standardized across nodes using TRAIN-WINDOW statistics only.
  Ground-truth parameters (per seed):
    b*_{tau,m} ~ LogNormal(ln mu_tau, 0.2), mu = {major:0.30, minor:0.15,
      advisory:0.08}; within-type tap shares {0.5, 0.35, 0.15}.
    c*_i ~ Uniform[0.2, 1.0].
    w* ~ N(0,1)/sqrt(10) per dimension. NO intercept term.
    a*_i = w*'T x'_i + N(0, 0.3).
  Event rate gate: scale w*-contribution by kappa from {0.25, 0.5, 1, 2, 4};
    select SMALLEST kappa giving train-window event rate in [3%, 5%]. If none,
    extend to {0.125, 8}. If still none: mark seed RATE-EXCLUDED, exclude from
    the 50, record realized rates. Never re-roll a seed.
  ARM A1 (matched): excitation via 3-tap geometric kernel.
    Tap states: E_{j,m}(t) = rho_m * E_{j,m}(t-1) + n_j(t-1),
      rho = {0.5, 0.8, 0.95}, E(0)=0 (cold start).
    Refractory: R_i(t) = 0.7*R_i(t-1) + n_i(t-1), R(0)=0.
    Hazard: lambda_i(t+1) = sigmoid( a*_i + SUM over typed edges e=(j->i,tau)
      of SUM_m b*_{tau,m} * E_{j,m}(t)  -  c*_i * R_i(t) ).
    Events: n_i(t+1) ~ Bernoulli(lambda_i(t+1)), capped 1/node-week.
    Model receives FULL graph.
  ARM A2 (adversarial): ground truth uses SINGLE-channel truncated power-law:
    E^PL_j(t) = SUM_{s=1..52} (1+s)^(-1.5) * n_j(t-s), cold start zeros.
    Per-typed-edge scalar amplitude b*_tau^{A2} = b*_{tau,1}+b*_{tau,2}+b*_{tau,3}
    (deterministic from the A1-distribution draws above).
    Hazard sums over TRUE-graph typed edges (thinning affects visibility,
    NOT physics). Model architecture UNCHANGED (still 3-tap geometric) and
    model receives THINNED graph: uniform random subset of typed edges,
    size floor(0.85 * |E_true|), drawn once per seed.
  Hidden maintainers (A2 only):
    Candidates: 30 highest DISTINCT-CHILDREN out-degree nodes in the TRUE
    graph; ties broken by ascending node index; sample 5 uniformly among them.
    Maintainers are scored nodes; their own events follow ordinary hazard.
    Per week each maintainer fires independently with p = 1/26.
    Conditional on firing, forces an event on EACH child with independent
    coin p=0.5. Forcing success -> child event = 1 that week, overriding the
    child's own draw; failure -> child's ordinary Bernoulli(hazard) proceeds.
    Forced events count as events and enter ALL accumulators (E and R).
  RNG streams: keys = np.random.SeedSequence(s).spawn(6) ->
    [world, thinning, maintainer, dynamics, model-init, bootstrap].
    Integer conversion (only sanctioned path):
      key_k = int(child_k.generate_state(1, dtype=np.uint32)[0]).
    NumPy streams: np.random.default_rng(spawned_child_k).
    PyTorch: torch.manual_seed(int(key_world) + 4000).

C3. LEARNED MODEL (CFHM)
  States: E_{j,m}(t) = rho_m * E_{j,m}(t-1) + n_j(t-1), rho={0.5,0.8,0.95}
    FIXED, E(0)=0.  R_i(t) = 0.7*R_i(t-1) + n_i(t-1), R(0)=0, decay fixed.
    Accumulators are NEVER standardized.
  Parameters:
    Fragility: a_i = MLP(x'_i), layers 10 -> 16 (tanh) -> 1 LINEAR output,
      biases everywhere, PyTorch default init. 193 parameters total.
    Transmission: b_{tau,m} = (0.95/3) * sigmoid(r_{tau,m}), r init -4.0
      (=> b ~ 0.006 at init; SUM_m b_{tau,m} <= 0.95 holds structurally,
      no projection step).
    Recovery: c_i = 2 * sigmoid(r^c_i), r^c_i init -4.0 (=> c ~ 0.036).
  Hazard (teacher-forced on realized n, typed-edge-indexed):
    lambda_i(t+1) = sigmoid( a_i + SUM_{typed edges e=(j->i,tau)} SUM_m
      b_{tau,m} * E_{j,m}(t)  -  c_i * R_i(t) ).
  Loss: Bernoulli NLL (weeks 2..104)
    + lambda1 * L1 on b only (all types, all taps; NOT c)
    + 1e-4 * ||W||^2 (ALL MLP weights and biases).
    lambda1 GRID = {1e-4, 1e-3, 1e-2}, selected on VALIDATION NLL:
    fit on weeks 1-78, validate on 79-104; grid ties -> smaller lambda1;
    then REFIT on full weeks 1-104 with chosen lambda1 before test scoring.
  Optimizer: Adam lr 1e-3, 50 epochs, full-batch.
  Hazards clipped to [1e-6, 1 - 1e-6].
  Forecast (ex-ante): freeze E,R at t=104; propagate with n == 0 through
    t=130 (E scales by rho_m^s, R by 0.7^s); H_i = SUM_{s=1..26} lambda_i(104+s),
    computed numerically. Realized test events NEVER enter any predictor.

C4. BASELINES (same train window, same task, refit per seed)
  B1: descending distinct in-degree (model-visible graph).
  B2: descending z(log-age) + z(popularity).
  B3: sklearn LogisticRegression(C=1.0, solver=lbfgs, max_iter=1000) on
      node-week rows (weeks 1-104); per-node score = predicted probability at
      that node's covariate vector.
  B4: CFHM.

C5. EVALUATION
  Rank all 200 nodes by H_i (or baseline score). Label: >=1 event in test
  quarter. Metrics: Precision@25 PRIMARY; Precision@10 and AUROC secondary.
  Ranking ties: ascending node index. One shared scoring script for all methods.
  Stability gate: 10 bootstrap replicates per seed. Replicate = resample 200
  nodes WITH replacement -> integer multiplicities m_i (sum 200); refit with
  LOSS WEIGHTS m_i on node-week NLL terms (no duplicated nodes anywhere;
  graph/features/series unchanged); zero-copy nodes receive normal predictions;
  lambda1 NOT reselected (known conservatism, accepted). Ranking per replicate
  = full 200-node ranking. Kendall tau of each replicate vs the FULL-DATA-FIT
  ranking; mean over 10 replicates. Gate: mean tau >= 0.5 per seed for CFHM
  and B3, else that method's results are NOT DECISION-GRADE. B1/B2 deterministic.
  B3 uses identical multiplicity weighting on its rows.

C6. VERDICT ARITHMETIC (pre-registered, computed on A2 only)
  Best baseline per seed = max P@25 over B1, B2, B3.
  Relative improvement = (P25_CFHM - P25_base) / max(P25_base, 0.01).
  PASS: relative improvement >= 0.20 in >= 80% of non-excluded A2 seeds.
  KILL-B3: relative improvement vs B3 specifically < 0.05 in >= 50% of seeds.
  Any Part 0 rule violation: KILL regardless of numbers.
  A1 is diagnostic only; reported, never verdict-relevant.

C7. REQUIRED RETURN ARTIFACTS
  1. Repo + commit hash; config JSON per run; environment file.
  2. Full loss curves.
  3. PER-SEED CSV: predictions and labels for EVERY method (B1-B4), both arms.
  4. Verdict computation script + its raw output.
  5. Stability table (mean Kendall tau per seed per gated method).
  6. Complete DEVIATIONS.md including resolution statuses of DEVIATION-001/-002/-003
     and all 16 + 5 + 1 blockers, plus any NEW items with verbatim errors.
  Summaries are returned unread. Raw tables are the evidence.

PART 3 — IMMEDIATE NEXT ACTIONS FOR EXECUTOR
  1. Save this document as spec/HANDOFF-v1.0.md; provenance commit (identity 0.3).
  2. Implement per PART 2. Run all seeds. Produce PART 2 C7 artifacts.
  3. Transmit artifacts via RELAY to AUTHOR. Author audits against C6.
     On PASS -> SPEC-002 (F2 counterfactual removal) follows.
     On KILL -> post-mortem names the failed component before any redesign.

================================================================================
END HANDOFF
================================================================================
```
