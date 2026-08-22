# SPEC-001-R4: Author Resolution to DEVIATION-004/-005

The executor is four-for-four: softplus-zero, the 0.5^k collision, typed-edge sampling, and now this — each time refusing to guess, each time correct to refuse. This one is pure author arithmetic: I wrote "d = 10 total" without counting my own feature list. Logged as **AUTHOR-ERR-004**.

## The decision: bind **d = 9**, do not invent a tenth feature

Rationale, on the record:

1. **The number 10 has no design content.** It entered the spec as an uncounted estimate. Amending reality to match a typo inverts the authority relation between intent and text.
2. **A tenth feature would be new science smuggled in as bookkeeping.** The obvious candidate (visible out-degree) interacts with maintainer selection, which keys off out-degree in the true graph — binding it now would change the experiment's semantics under the guise of fixing a count. Feature-set changes are design decisions, not patch material.
3. **F1's question is sharpest with a minimal fragility channel.** Fewer fragility features, cleaner attribution of any ranking advantage to transmission structure.

## Binding amendments (superseding all prior texts where they conflict)

**R4-001 — Feature dimension.** d = **9**: [log-age, distinct in-degree (model-visible graph), log popularity, complexity, field one-hot ×5]. No tenth feature exists.

**R4-002 — Ground-truth weights.** `w* ~ N(0, 1)/√9` per dimension (i.e., scale 1/3). All other ground-truth distributions unchanged per R-003/R2/R3.

**R4-003 — Model architecture.** Fragility MLP: **9 → 16 (tanh) → 1 linear**, biases everywhere, PyTorch default init. Corrected parameter count: (9·16 + 16) + (16·1 + 1) = **177 parameters** (supersedes "193," which superseded "≈350"). Transmission and recovery parameterizations (R-008) are untouched by this amendment.

**R4-004 — Everything else stands.** κ-gate unchanged (it self-calibrates the marginal effect of the rescaled w*); standardization, baselines, evaluation, verdict arithmetic, bootstrap procedure: unchanged.

## On DEVIATION-005's second finding (status-ledger discrepancy)

Correctly flagged, and here is the explanation for the record: HANDOFF-v1.0's Part 1 ledger reflected state **at authoring time** — it left this conversation before your implementation session had begun committing code, and reached Manus after. A snapshot document cannot track live state; only resolution documents like this one update the ledger. Classification: provenance-timing artifact, zero scientific impact. The running status is now: **implementation begun, smoke run halted at RUNTIME-001, zero scientific results produced, all prior bindings intact.**

## Executor instructions

1. Append verbatim as `spec/SPEC-001-R4-authored.md`; provenance commit.
2. Apply R4-001…003 as a minimal diff from commit `60dc0e3f` — nothing else may change in that diff.
3. Re-run the seed-1000 smoke command exactly as recorded in DEVIATION-004. If it passes, proceed to the full 50-seed run under PART 2 of HANDOFF-v1.0 as amended by R1–R4.
4. Artifacts per C7, now including: the smoke-log pair (failing + passing), both commits (`60dc0e3f`, the R4-applied hash), and resolution statuses for blocks 16+5+1+1 plus AUTHOR-ERR-004.

---

Error-trajectory note, since the pattern is now statistically meaningful: all four author faults were **prose–arithmetic collisions** — a word ("zero") contradicting a function (softplus), two probabilities colliding, three numbers lacking a combining rule, a list contradicting its own count. The natural-language layer is where my specifications fail; the mathematics underneath has survived every audit. Which is, incidentally, an empirical point in favor of the whole protocol: the expensive errors weren't caught by smarter prose, they were caught by an executor structurally forbidden from smoothing them over.