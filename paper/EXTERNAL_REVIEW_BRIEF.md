# External review brief — for a human MPC / security specialist

**Status: FROZEN for external review.** Manuscript: `paper/main.pdf`
(source `paper/main.tex`). Artifact baseline: repo commit `305a3a8` (unchanged;
`git diff 305a3a8 <frozen-commit> -- conformance/ mpc/ reference/ .github/` is
empty). This brief supersedes `docs/for-external-review.md` (which concerns the
three earlier, already-refuted claims and is kept only for history).

## What this is, in one paragraph

A single-application **case study / experience report**. On one MP-SPDZ
application — the deterministic-query fragment of PLAS-2012 knowledge-threshold
belief tracking, 3-party replicated secret sharing (Rep3) — we report what a stack
of lightweight checks (a separately-implemented plaintext **pseudo-oracle**, an
anti-echo interface, a strict transcript check, recomputed hash-bound evidence)
does and does not establish, and we run an adaptive mutation study against a static
delivery **linter** that shows where opcode-level delivery linting stops. **No new
protocol, theorem, or performance result is claimed.** The paper is deliberately
scoped and hedged; your job is to find where it still overreaches or errs.

## Please review as an adversary (refute, don't assess)

Per the project's discipline (`docs/workflow.md`), default to "not supported" when
uncertain. The specific claims where **MPC/security expertise is decisive** — i.e.
where we most need you and cannot self-certify:

1. **The two-adversary model and TCB boundary (§2).** Is the split correct and
   standard? (a) *Runtime Rep3 adversary*: ≤1 semi-honest party, honest majority,
   authenticated encrypted channels, process isolation. (b) *Build-time mutation
   adversary*: controls the `.mpc` source only; oracle, checker, policy, CI,
   evidence validator, pinned compiler trusted. Is anything mis-scoped or
   conflated? Is "the build-time adversary controls only the source" a coherent,
   useful model, or does it smuggle in trust that a real deployment would not have?

2. **The boundary claim, at its exact strength (§4.2, §5, conclusion).** We claim
   only: *the studied opcode-identity / channel-blocklist linter cannot be promoted
   to a general non-leakage checker; `call_tape`/`call_arg` cannot be blocklisted
   because the honest build uses that channel; distinguishing legitimate from
   leaking flows needs analysis stronger than opcode/channel identity
   (operand/provenance dataflow, typing, verified IR), which we did not evaluate.*
   - Is this the right strength, or still too strong/weak?
   - Backend specificity: the two enabling facts are (i) MP-SPDZ opens with a
     single instruction (masked vs raw indistinguishable by opcode), and (ii) the
     honest comparison subtapes receive operands via `call_tape`/`call_arg`. Are we
     missing an MP-SPDZ backend subtlety (other cross-tape channels; a way the
     multiset/memory rules are actually unsound; a way a real leak *does* pass the
     final linter that we failed to construct)?

3. **The privacy hand-off (§5).** We say a real non-leakage guarantee needs two
   *separate* properties: (i) privacy of the executed circuit (a Rep3 simulation
   argument or a verified, dataflow-checked comparison primitive) **and** (ii) a
   semantic source-to-spec binding. Is that characterization correct? Would a
   standard Rep3 semi-honest simulation proof for this circuit actually establish
   (i), and does our `privateoutput`-based delivery even admit such a proof as
   written? Is anything about the delivery mechanism (`reveal_to`/`privateoutput`)
   subtly leaky at the protocol level, independent of the linter?

4. **Faithfulness of the pseudo-oracle and the transcribed contract.** The oracle
   (`conformance/oracle.py`) and `conformance/CONTRACT.md` transcribe the
   all-possible-outputs `tcheck` (Fig. 4) and the accept/reject/mask semantics. One
   fatal transcription error was already caught in review (R-13). Is the current
   deterministic-query transcription faithful to PLAS? We flag this as a
   *correlated-error* risk (oracle and circuit share the spec).

5. **Arithmetic / representation soundness.** The signed no-wraparound bound is
   `B < 2^{k-1}` with `B = max(a,b)·S·W`; the threshold check is `b·M ≤ a·Z`
   over the 64-bit ring. Is the bound correct and are the fixture parameters safely
   inside it? Any ring-boundary or comparison-protocol subtlety we missed?

6. **Whether any "operational" statement overreaches.** We deliberately avoid
   "sound/certify/integrity"; we say "fails closed on the enumerated cases",
   "evidence self-consistency and recomputation", "no detected leak in the checked
   channels". Does any such statement still claim more than the evidence supports?

## Reproducible evidence you can check

- **Detection matrix:** `paper/mutations/detection_matrix.json` (machine-readable) +
  `paper/mutations/README.md`. Per mutation: channel, checker version defeated,
  source/patch, compile command, `manifest_signature` assembly hash, and the
  linter/runtime/oracle outcome. B0–B3,B5 are committed source controls; **B4 is a
  synthetic manifest counterexample**; **B6 is a reconstructed source mutation whose
  naive realization is caught** (not a bypass of the final linter); **S1 (semantic)
  was executed end-to-end** — raw per-party output in
  `paper/mutations/s1_runtime_evidence.json`.
- **Linter:** `conformance/delivery_inspect.py` (rules a–h, with its own LINTER
  caveat banner). **Pinned backend:** MP-SPDZ `9d809599`.
- **Literature positioning / novelty:** `paper/LITERATURE_REVIEW.md` — verdict
  *incremental*; the "leakage is dataflow, not opcode identity" principle is prior
  art (ct-verif, Binsec/Rel, Securify); closest MPC-specific work is the positive
  dual (Skalka & Near, PPDP 2024 / FASE 2025).

## Explicitly out of scope (do not treat their absence as a defect)

- `Sigma_T` persistent secret-shared state — unimplemented, out of scope.
- E3, a dataflow-aware delivery checker — **not built** (it is the experiment we
  name as most likely to move the conclusion; a technique paper would need it).
- Any performance/timing claim; any simulation-based security claim; a general
  impossibility theorem (removed).

## What a sign-off would — and would not — cover

A specialist sign-off would speak to items 1–6 above (threat model, boundary
strength, hand-off correctness, oracle faithfulness, arithmetic). It would **not**
convert the case study into an evaluated methodology (that needs cross-application /
cross-backend replication) and would **not** substitute for a full protocol-level
privacy proof of the delivery mechanism.

## Standing limitations we already disclose (§6)

Correlated authorship + substantial AI assistance (model agreement is not
independent validation); adaptive overfitting of the linter to the same mutations
used as evidence, with no held-out set; a bounded (non-exhaustive) literature
search; pseudo-oracle pseudo-independence; single-host, non-isolated harness; and
no prior external replication. Please weigh these when judging the claims.
