# PAPER_PLAN.md

> ## ⚠️ SUPERSEDED — read `paper/main.tex` instead
>
> This planning document predates the consolidated manuscript and its Codex
> re-reviews. It is retained for provenance only; the **authoritative artifact is
> `paper/main.tex`** (branch `paper/first-draft`), with `paper/LITERATURE_REVIEW.md`
> and `paper/mutations/`. The following parts of this plan are **superseded** and must
> not be cited as current:
> - **RQ4** (review-outperforms-single-pass) — **removed**; the review loop is now an
>   *experience lesson*, not a contribution (no comparator).
> - **Conjecture 1** (dataflow-free impossibility) — **removed** from the paper (a
>   one-line future-work note only).
> - **"Independent oracle"** — replaced by *separately-implemented pseudo-oracle* with
>   a stated correlated-error limitation.
> - **Broad static-analysis claims** ("cannot be made sound"; "a sound checker needs
>   operand-sensitive dataflow") — **narrowed** to: *the studied opcode-identity /
>   channel-blocklist linter cannot be promoted to a general non-leakage checker;
>   `call_tape`/`call_arg` cannot be blocklisted because the honest build uses that
>   channel; distinguishing legitimate from leaking flows requires analysis stronger
>   than opcode/channel identity (operand/provenance dataflow, typing, verified IR),
>   which we did not evaluate.*
> - **Novelty** is **incremental** (case study / experience report), per
>   `LITERATURE_REVIEW.md`; not a new technique.
>
> **Current thesis (authoritative).** On one MP-SPDZ application, separately
> implemented functional pseudo-oracles, anti-echo interfaces, transcript checks, and
> recomputed evidence provide useful coverage-bounded assurance; an adaptive mutation
> sequence exposes the limit of the studied opcode-identity delivery linter, including
> the MP-SPDZ `call_tape`/`call_arg` path, under a precisely bounded build-time
> adversary (controls the `.mpc` source only; oracle/checker/policy/CI/validator/
> pinned compiler trusted).
>
> **Current contributions.** (1) application of established conformance / pseudo-oracle
> practice to an MPC application (anti-echo + recomputed evidence as the delta); (2) a
> reproducible case-study artifact (fixture + bounded 228-case matrix + five committed
> controls, pinned backend); (3) a reproducible adversarial mutation study (B0; B1–B6
> compiled-delivery cases — B1/B2/B3/B5 committed source, **B4 synthetic manifest**,
> B6 reconstructed & caught; **S1 semantic, executed end-to-end**) with a
> machine-readable detection matrix; (4) the assurance-boundary / hand-off statement.
>
> **Current RQs.** RQ1 — what the checks establish on the tested matrix vs what
> remains unestablished. RQ2 — through which specific compiled channels the studied
> opcode-identity linter fails for this MPC application, and at what exact strength.
> RQ3 — the boundary between implementation-level evidence and a protocol-level proof
> (grounded in the two-adversary / TCB split). *(RQ4 removed.)*
>
> The 11 sections below are the original plan, kept for history.

**Working title:** *Executable Conformance for a Secure-Multiparty Application:
What Implementation-Level Evidence Can Certify, and Where It Stops Short of a
Privacy Proof*

**Frozen artifact baseline:** commit `305a3a8` (`305a3a8d1810c427edcc32520352e74610c7866c`),
repo `smc-belief-tracking`, `main`, CI green. Every claim in this plan is
traceable to a file at that commit. Case study: the PLAS-2012 knowledge-threshold
belief computation (Mardziel, Hicks, Katz & Srivatsa).

**Reading discipline for this plan.** `[OPEN]` marks anything not currently
supported by the repository — a claim we would need to *earn* (a new experiment,
a literature review, a theorem, or an expert sign-off) before it can appear
un-hedged in the paper. `[REPO]` tags a fact with the file that grounds it. This
plan does **not** silently fill research gaps; it names them.

> **Scope guardrails carried from the directive.**
> 1. We do **not** claim "static analysis is impossible in general." The
>    demonstrated result is narrower and precise: *the studied syntactic /
>    opcode-level delivery-certification approach is unsound against an adversary
>    who controls the `.mpc` source.* A stronger impossibility claim is stated
>    only as an `[OPEN]` conjecture with the missing proof obligations named
>    (§5.3, §8).
> 2. We do **not** implement new functionality to enlarge the paper. §8 lists
>    additional experiments; each names the exact RQ or reviewer objection it
>    resolves, and every item requiring new code (especially `Sigma_T`) is marked
>    **STOP-FOR-AUTHORIZATION**.
> 3. `Sigma_T` persistence is **not** started and remains unauthorized.

---

## 1. Thesis (one sentence)

Executable conformance testing against an independently written oracle can
rigorously establish that a secure-multiparty *application* computes an intended
functionality on the inputs it is tested on and that it contains no *gross*
information leak, but it cannot certify per-recipient non-leakage against an
adversary who controls the source — because at the compiled-opcode level a masked
comparison-open is indistinguishable from a raw secret-reveal and a secret can be
routed into that open through the very register-argument channel the honest code
uses — so implementation-level evidence has a definite boundary at which it must
hand off to a protocol-level (simulation-based) privacy proof.

---

## 2. Research questions

- **RQ1 (what conformance establishes).** For an MPC application, what functional
  and integrity properties can an executable conformance harness built around an
  *independent* plaintext oracle establish, and at what strength — per-tested-input
  agreement versus general correctness? Where is the line between the two?

- **RQ2 (soundness of syntactic delivery certification).** Can a static,
  opcode-level inspection of compiled MPC assembly *soundly* certify
  per-recipient non-leakage against an adversary who controls the source? If not,
  what specifically defeats it, and is the defeat incidental (patchable) or
  structural?

- **RQ3 (the hand-off boundary).** What is the precise boundary between properties
  that implementation-level evidence can support and properties that require a
  protocol-level security argument, and how should a research artifact *represent*
  that boundary so that a green CI check is not mistaken for a privacy proof?

- **RQ4 (adversarial review as method).** Does an adversarial, reproduce-before-fix
  review loop surface implementation-level leaks and specification errors that a
  single authoring pass misses, and does the *sequence* of surviving/failing
  bypasses reveal structure about the underlying problem (RQ2) that any one bypass
  does not?

---

## 3. Contributions (defensible, repo-grounded)

1. **An executable-conformance methodology for an MPC application.** Independent
   plaintext oracle (not co-derived with the circuit) + a tiny hand-verifiable
   fixture containing both an *accepted* and a *rejected* invocation + an
   explicit anti-echo interface contract (expected outputs never enter the
   circuit) + SHA-bound, recomputed raw evidence. The point is that this makes CI
   *mean something*: it checks a defined functionality against an independent
   reference, rather than confirming that two co-derived models agree. `[REPO:
   conformance/oracle.py, conformance/CONTRACT.md, conformance/INTERFACE.md,
   conformance/harness.py, conformance/validate_evidence.py, docs/conformance.md]`

2. **A concrete, reproducible conformance artifact** for the deterministic-query
   fragment of PLAS-2012 `threshold_SMC` (N=3, D={0,1,2}, thresholds 1/2, two
   queries): an MP-SPDZ circuit checked against the oracle on a named fixture and
   a 228-case adversarial coverage sweep, 92 conformance tests + 9 reference
   tests, 5 committed executable negative controls, all green in CI against a
   pinned backend with bound evidence. `[REPO: conformance/, .github/workflows/benchmark.yml,
   MP-SPDZ pin 9d809599ea6ce627216a389ca7d984fbb75d0cb9]`

3. **An empirical boundary result with a taxonomy.** Six escalating
   static-delivery bypasses (each a concrete build that leaked a verdict yet
   passed the then-current gate) plus one independent *semantic* bypass, each
   reproduced end-to-end — establishing that the studied syntactic/opcode-level
   certification approach is unsound against a source-controlling author, and
   isolating the two structural reasons: (i) masked vs. raw opens are the same
   opcode (a dataflow property, not an opcode-identity property), and (ii) a
   secret reaches a subtape's open through the `call_tape`/`call_arg` register
   channel the honest comparison subtapes themselves use (so it cannot be
   forbidden). `[REPO: docs/limits.md, docs/review-log.md R-41..R-47,
   conformance/mpc/threshold_smc_*.mpc]`

4. **A precise articulation of the hand-off.** A real non-leakage guarantee needs
   *two separate* properties — privacy of the executed circuit (a protocol-level
   Rep3 argument or a formally-verified, dataflow-checked comparison primitive)
   **and** a semantic source-to-spec binding (that the circuit computes the
   *intended* function, not merely one that agrees with the oracle on tested
   cases) — and functional conformance supplies neither in general. `[REPO:
   docs/limits.md "What a real non-leakage guarantee requires"]`

5. **The adversarial three-party review process as a reusable discipline**, with
   an append-only, auditable review log (47 entries, R-01..R-47) as a
   first-class artifact — including a self-refutation (our own "memory is the only
   cross-tape channel" soundness premise was itself later refuted). `[REPO:
   docs/workflow.md, docs/review-log.md]`

> **Novelty honesty (addresses review-log R-10).** The contribution is
> *methodological and boundary-finding*, **not** "first implementation of PLAS."
> R-10 correctly established that implementing and timing a 2012 construction is
> not, by itself, a paper. The artifact is a *vehicle* for contributions 1, 3,
> and 4; the paper must foreground the method and the boundary, not an
> implementation claim. Whether contributions 1/3/4 are *new relative to prior
> art* is `[OPEN]` until the literature review of §6/§8 is done.

---

## 4. Claim → evidence → limitation table (grounded ONLY in the repository)

Every claim below is one the paper may make *as stated*. The limitation column is
load-bearing; it is what keeps the claim honest.

| # | Claim the paper can make | Evidence in the repo | Limitation (stated next to the claim) |
|---|---|---|---|
| C1 | A deterministic-query `threshold_SMC` circuit reproduces the independent oracle's visible outputs, payloads, and reconstructed belief weights on a fixture with one accepted and one rejected invocation. | `conformance/harness.py`, `conformance/oracle.py`, `conformance/CONTRACT.md` fixture; 4/4 named cases. | Per-tested-input agreement, not general correctness; a single fixture is a regression vector, not a proof (R-14). |
| C2 | Agreement holds across a 228-case adversarial sweep: all 27 secrets × 2 queries × uniform/non-uniform/scaled integer weights, near-tight bit bound, and carried pairs. | `conformance/coverage.py`; `results-coverage.txt`: `single=216 carried=12 total=228 pass=228`. | Still a fixed, enumerable case set at N=3, D={0,1,2}; not a general-domain or probabilistic-query result. |
| C3 | The oracle is written independently of the circuit and of `reference/`, and faithfully transcribes the *all-possible-outputs* `tcheck` semantics (Fig. 4), including the accept-boundary `<=`. | `conformance/oracle.py`, `conformance/CONTRACT.md`; R-13 fixed a fatal actual-output-only bug; `test_conformance.py::test_discriminating_case`. | Faithfulness is a human transcription of one paper's deterministic-query fragment; no MPC expert has signed off (workflow.md rule); the oracle could be wrong in unreviewed ways. |
| C4 | The circuit interface forbids echo-cheating: expected outputs/post-state never enter the circuit; inputs are exactly public (N,D,Q,t) and secret-shared (secrets, beliefs). | `conformance/INTERFACE.md` (R-17, R-18); harness runs ≥1 extra secret state so a constant circuit cannot pass. | An interface discipline, enforced by construction and review, not by a machine-checked proof of the harness. |
| C5 | The signed no-wraparound requirement is `B < 2^{k-1}` (not `2^k > B`), and the fixture (B=54) is safely inside a 64-bit ring. | `conformance/INTERFACE.md`, `conformance/circuit_spec.py`, `test_...::test_naive_bound_is_wrong_for_signed_comparison` (R-22). | Bound is enforced/derived for the fixture parameters; a general bound for larger N,D,W is stated, not auto-checked by the circuit (NOTES.md). |
| C6 | A static compiled-delivery *linter* rejects five committed executable negative controls (public reveal in main; separate-tape reveal+print; name-spoofed wrong-player delivery + file sink; `reveal(False)` via scalar memory ops; the same via vectorized `vstms`/`vldms`). | `conformance/delivery_inspect.py`; `threshold_smc_{leaky,subleak,namespoof,openfalse,openfalse_vec}.mpc`; 46 private-gate tests. | A linter, **not** a non-leakage proof: a PASS means "no known gross-leak pattern," explicitly not "provably private" (R-47; runtime banners say so). |
| C7 | The runtime transcript layer fails closed: a correct party's stdout is exactly two own records (ACCEPT+PAYLOAD); any foreign/duplicate/unknown/missing/extra line raises. | `conformance/private_run.py::strict_parse_party`; `test_private.py`. | Sound for what it checks (gross stdout leakage), but a transcript check cannot see shares, timing, or network — it is not a view-simulatability check. |
| C8 | Raw evidence is typed, SHA-bound, and recomputed: under `--recompute` in CI each record's `source_sha256` and `delivery_sig` must equal values recomputed from the checked-out source and a fresh compile, and each record is bound to a canonical case via a recomputed `input_hash` + oracle verdict (bijection required). | `conformance/validate_evidence.py`; CI step with `--require-bound --recompute`; `repo_provenance()` (R-34, R-37, R-43). | Binds evidence to source+backend+oracle; it does **not** bind the *source* to the *intended* PLAS functionality beyond the tested cases (see C11). |
| C9 | Provenance is real: committed local evidence is labeled `local-unbound-*` (`bound:false`), and only CI runs with `GITHUB_SHA` are `bound:true`, with `HEAD==pin` asserted for MP-SPDZ. | `conformance/_evidence/`, `benchmark.yml`, `repo_provenance()` (R-28, R-34). | Provenance discipline, not a reproducibility guarantee on arbitrary machines. |
| C10 | **Negative boundary result:** the studied syntactic/opcode-level delivery gate cannot be made sound against a source-controlling author; six reproduced bypasses show why, and the last (register-channel) cannot be forbidden without breaking the honest build. | `docs/limits.md`, `docs/review-log.md` R-41..R-47; the `call_tape`/`call_arg` verification. | This is an *empirical* demonstration + a structural argument, **not** a formal theorem (see §5.3 `[OPEN]`). It concerns *dataflow-free syntactic* checkers on *this backend*, not static analysis in general. |
| C11 | **Semantic gap:** functional conformance binds source to spec only up to test coverage; a build can deliver to the correct recipient yet compute the wrong secret function and still pass. | `docs/limits.md` "correct recipient, wrong function"; `docs/gap.md`. | This is why privacy-of-delivery is insufficient even if achieved; it motivates the second hand-off property (§3 C4/contribution 4). |
| C12 | The three-party adversarial loop is auditable and self-correcting: 47 append-only review entries, including a case where our own soundness premise was refuted. | `docs/review-log.md` (R-45 premise → R-47 refutation), `docs/workflow.md`. | Process evidence; it argues the method is rigorous, not that the conclusions are complete. |

**Explicitly NOT claimed anywhere in the paper** (carried from ADVERSARY.md /
NOTES.md / README.md): simulation-based security; non-leakage under a
source-controlling author; any guarantee under collusion, a malicious party,
unencrypted channels, or a shared-host adversary; `Sigma_T` share-persistence
correctness; and **any performance result** — the `results/` timings are for
`belief3`, a computation that is not the mechanism (README "Do not cite the
timings"; `docs/gap.md`).

---

## 5. Adversarial mutation taxonomy

The engine of the paper's boundary result. Each mutation is a concrete `.mpc`
build that leaked (or mis-computed) yet passed the gate that existed when it was
found. The gate was strengthened after each of B1–B5; B6 could not be, which
forced the linter-scoping decision.

### 5.1 The six static-delivery bypasses (leak-channel sequence)

Baseline gross case **B0 (R-41):** `reveal_to(j)` → `reveal()` while keeping
`print_ln_to(j,...)` compiles to a public `asm_open` of all six verdicts, yet a
stdout oracle reports "PRIVATE DELIVERY OK" — a stdout check cannot distinguish
private output from public open + private printing. Motivated moving from a
stdout oracle to *compiled-delivery* inspection. Committed control:
`threshold_smc_leaky.mpc`.

| ID | Round | Mutation | Channel it used | Why it passed the then-current gate | Closed? | Committed control |
|----|-------|----------|-----------------|--------------------------------------|---------|-------------------|
| B1 | rr-2 / R-42 | separate `@function_tape` public `reveal()` + `print_ln('LEAK…')` | a second tape | inspector read only the MAIN tape | yes — whole-manifest inspection | `threshold_smc_subleak.mpc` |
| B2 | rr-3 / R-43 | name-spoofed `EQZ(spoof)` subtape: wrong-player `privateoutput` + `binary_output()` file sink (no stdout) | a name-trusted subtape | masked allowlist keyed on tape *names* | yes — bind on CONTENT not name | `threshold_smc_namespoof.mpc` |
| B3 | rr-4 / R-44 | `final_verdict.reveal(False)` in an `EQZ/LTZ`-named subtape | a public open with the `False` flag | gate treated `False` opens as safe (wrong: `False` only skips the post-open correctness check) | yes — stop relying on the open flag; pin non-main tape *multiset* | `threshold_smc_openfalse.mpc` |
| B4 | rr-5 / R-45 | `reveal(False)` injected into an *existing* `EQZ(3)_63` body via scalar `stms`/`ldms`, multiset intact | MAIN store → subtape load (memory) | multiset pins names/counts, not bodies | yes — forbid MAIN store + any subtape memory access (rules g,h) | `threshold_smc_openfalse.mpc` (trips g,h) |
| B5 | rr-6 / R-46 | same leak crossing the tape boundary with vectorized `vstms`/`vldms` | vectorized memory | memory regex matched only scalar/gf2n forms | yes — broaden regex to `v?g?stm*`/`v?g?ldm*` | `threshold_smc_openfalse_vec.mpc` |
| B6 | rr-7 / R-47 | verdict routed into a subtape's open via `call_tape`/`call_arg` register arguments (no memory) | direct register-argument channel | rules g,h cover only the memory channel | **NO** — this is the channel the honest comparison subtapes use; forbidding it breaks the honest build | none (unforbiddable) |

**The two structural reasons (why B1–B5 were whack-a-mole).** `[REPO: docs/limits.md]`

- *Open-type ambiguity.* A public reveal and a legitimate masked comparison-open
  are the **same opcode** (`asm_open`/`vasm_open`); the `True`/`False` flag is not
  a privacy flag. "Safe" depends on whether the operand is masked — a **dataflow**
  property present in the assembly but **not determined by opcode identity alone**.
- *Unforbiddable channel.* The verdict is a MAIN-tape register; a cross-tape
  register reference is a compiler error, so the only ways into a subtape's open
  are (a) memory — an attacker-only channel, soundly forbidden — or (b)
  `call_tape`/`call_arg` register arguments, which the honest subtapes use and
  which therefore cannot be forbidden.

### 5.2 The independent semantic bypass (a different axis)

**S1 — correct recipient, wrong secret function.** A build can deliver
`(accept_j, payload_j)` privately to exactly the right party and still compute the
*wrong* secret function inside. Privacy-of-delivery says nothing about *which*
value is delivered. The functional-conformance layer binds source→spec, but only
up to **test coverage**, not in general. This is orthogonal to the six leak
channels and is why "privacy" alone is not enough — it motivates the second
hand-off property (semantic source-to-spec binding). `[REPO: docs/limits.md]`

### 5.3 Can the boundary be made a theorem? `[OPEN]`

The directive is explicit: do not overstate. What we have is an empirical
demonstration + a structural argument. A *stronger* claim would be an impossibility
theorem. We state it as a conjecture and name the missing proof obligations.

> **Conjecture (dataflow-free syntactic certification is unsound), `[OPEN]`.**
> Fix the pinned MP-SPDZ Rep3 backend and the `threshold_SMC` functionality F.
> Call a checker *syntactic/dataflow-free* if it is a computable predicate on the
> compiled tape-manifest that is invariant under a transformation class T which
> preserves opcode identity and tape structure but may relabel an open's operand
> (e.g., substitute a verdict-derived register for a masked one) and may move a
> register between tapes via the `call_arg` channel. Then there exist source
> programs P_safe (delivers F privately) and P_leak (leaks a verdict) whose
> compiled manifests are T-related; hence any such checker C satisfies
> C(P_safe)=C(P_leak) and cannot both accept P_safe and reject P_leak. So no
> dataflow-free syntactic checker is sound-and-complete for non-leakage here.

**What proof is missing** (why we do *not* assert this as a theorem):

1. **A formal model** of the compiled manifest and a *rigorous* definition of the
   transformation class T — i.e., a precise formalization of "does not do
   dataflow" (invariance under operand relabeling / cross-tape `call_arg` moves).
2. **An explicit T-related pair** P_safe / P_leak with a proof that they are
   T-equivalent and that the honest build is a fixed point of the gate. We have
   empirical instances (the B3/B4 `reveal(False)` pairs), not a proof of
   T-equivalence.
3. **A protocol-level definition of "leak"** to prove P_leak actually leaks and
   P_safe does not. This is the crux: proving the impossibility *rigorously*
   requires the very simulation-based privacy definition whose absence is the
   boundary. Without it, "leak" is informal.

Because (3) makes the impossibility depend on the protocol-level machinery we
lack, the honest paper presents §5.3 as a **conjecture with a proof sketch and an
explicit list of obligations**, and keeps the asserted result at the empirical
level (C10). This is exactly the line the directive draws: the *studied syntactic
approach* is shown unsound; a general impossibility is future theory. Note that a
**dataflow-aware** analysis (taint/masking verification) is explicitly *not*
conjectured impossible — `docs/limits.md` lists it as one route to a real
guarantee.

---

## 6. Related work & the exact novelty claim we must substantiate

The repository has **not** done a literature search that can reach Google Scholar
/ Semantic Scholar (R-01 states this explicitly). So every novelty statement here
is `[OPEN]` pending §8's literature review. Below are the categories to survey and
the precise claim each must clear.

1. **MPC frameworks / compilers** (MP-SPDZ [Keller, CCS 2020] and peers). These
   provide the substrate. *Novelty to clear `[OPEN]`:* they do not offer
   application-level conformance-against-an-independent-oracle nor certify
   per-recipient delivery; confirm none ships such a check.

2. **Knowledge-based security / belief tracking / quantitative information flow**
   (Mardziel–Hicks–Katz–Srivatsa PLAS 2012, and the QIF line). This is the
   functionality. *Novelty to clear `[OPEN]`:* PLAS *simulated* SMC belief
   tracking without implementing it; confirm no later work implements the
   deterministic-query fragment with an executable conformance target.

3. **Formal verification of MPC / secure compilation** (verified MPC compilers,
   computational-soundness results, type systems for information flow, e.g.
   Wysteria/λ-calculi for MPC, symbolic-to-computational soundness). *Novelty to
   clear `[OPEN]`:* these are the *alternative* to testing; our negative result
   must be positioned as "why an opcode-level *syntactic* shortcut fails," not as
   competing with dataflow-aware verification. Cite them as the correct heavy
   machinery the boundary hands off to.

4. **Conformance / differential / metamorphic testing of crypto implementations**
   (test-vector conformance, differential testing of TLS/crypto, Wycheproof-style
   suites). This is the closest methodological neighbor. *Novelty to clear
   `[OPEN]`:* the transfer of independent-oracle conformance discipline to an MPC
   *application* with an anti-echo interface and recomputed evidence binding.

5. **Static analysis / linting for information-flow leaks.** Where the negative
   result lands. *Novelty to clear `[OPEN]`:* articulate the specific unsoundness
   (opcode-identity vs. dataflow; honest-used register channel) as a named failure
   mode for opcode-level linters of MPC bytecode.

> **Exact novelty claim the paper would need to substantiate (all `[OPEN]`):**
> *(a)* No prior work provides an executable conformance methodology for an MPC
> **application** validated against an independently written oracle with anti-echo
> interface discipline and SHA-bound recomputed evidence; **and** *(b)* the
> specific unsoundness of opcode-level per-recipient-delivery certification against
> a source-controlling author has not been previously articulated as a failure
> mode; **and** *(c)* the two-property hand-off (executed-circuit privacy +
> semantic source-to-spec binding) is a useful framing not already standard in the
> MPC-verification literature. If the survey finds any of (a)–(c) is prior art,
> the paper reframes toward whichever of the contributions in §3 survive — the
> methodology-as-experience-report and the reproduced boundary taxonomy are robust
> to (c) failing.

---

## 7. Experiments & results we already have `[REPO]`

1. **Functional conformance on the fixture.** 2 invocations (accept-then-reject,
   per-recipient divergence, reject-state preservation) + 2 extra valid states;
   4/4 match the oracle on verdicts, payloads, reconstructed weights.
   `[harness.py, results-step4.txt]`
2. **Adversarial coverage sweep.** 228/228 (216 single + 12 carried) across all 27
   secrets, both queries, uniform/non-uniform/scaled integer weights, near-tight
   bit bound `W=floor((2^63-1)/54)`. `[coverage.py, results-coverage.txt]`
3. **Test suites.** 92 conformance tests (46 functional = 6 circuit-spec + 13
   conformance + 27 mpc-run; 46 private-gate) + 9 reference tests, all green.
   `[conformance/test_*.py, reference/test_reference.py]`
4. **Five executable negative controls** rejected by the linter (B0–B5 above).
   `[delivery_inspect.py, threshold_smc_{leaky,subleak,namespoof,openfalse,openfalse_vec}.mpc]`
5. **Evidence discipline, exercised in CI.** SHA-bound provenance (`GITHUB_SHA`,
   `HEAD==pin`), `--require-bound --recompute` binding to canonical cases via the
   oracle, `pipefail` + a dedicated canary, JSONL raw evidence uploaded with
   `if-no-files-found: error`. `[benchmark.yml, validate_evidence.py]`
6. **The reproduced bypass sequence** B0–B6 + S1, each demonstrated end-to-end;
   B6 is the one that forced the linter-scoping decision. `[docs/limits.md,
   docs/review-log.md]`
7. **Backend pin.** MP-SPDZ `9d809599…`, `replicated-ring-party.x`, Rep3 over
   Z_2^64, 3-party semi-honest honest-majority. `[benchmark.yml, ADVERSARY.md]`

**Not among our results, and the paper says so:** any timing/throughput number;
any multi-invocation `Sigma_T` result; any privacy/security proof.

---

## 8. Additional experiments for a strong full paper

Each item names the RQ or reviewer objection it resolves. **New-code items are
STOP-FOR-AUTHORIZATION** per the directive; scholarship items are not blocked.

- **E1 — Literature review (REQUIRED, no new code).** Resolves R-01/R-10 and the
  §6 novelty `[OPEN]`s; needed for RQ2/RQ3 positioning. Substantiate or refute
  novelty (a)–(c). *Not blocked* — this is the single highest-value next step and
  gates whether the paper's framing holds. **Recommend doing this first.**

- **E2 — Attempt the §5.3 impossibility theorem (no code; theory).** Resolves the
  reviewer objection "you only show *your* gate fails; maybe a cleverer syntactic
  gate works." Deliver either a proof of the conjecture under a formalized T, or a
  crisp statement of why (3) blocks it. *Not blocked;* bounded effort.
  **Recommend attempting**, boxed as `[OPEN]` if it does not close.

- **E3 — A dataflow-aware delivery checker (NEW CODE — STOP-FOR-AUTHORIZATION).**
  Resolves RQ2 directly and the strongest reviewer objection to the negative
  result: *does the unsoundness survive a checker that traces operands rather than
  reading opcodes?* This is the most scientifically valuable new experiment,
  because a genuine attempt to build the stronger checker either (i) closes the
  gap the linter cannot — changing the paper's conclusion — or (ii) fails in an
  instructive, documentable way that upgrades C10 from "syntactic gates fail" to
  "here is exactly where dataflow is needed." **Stop for authorization before
  implementing.**

- **E4 — Generalize conformance beyond the fixture (NEW CODE —
  STOP-FOR-AUTHORIZATION).** Larger domains, probabilistic queries (likelihood
  weighting, out of current scope), more parties. Resolves R-14 ("a single fixture
  is a regression vector, not a proof") and strengthens RQ1's generality. **Stop
  for authorization.**

- **E5 — `Sigma_T` persistence (NEW CODE — EXPLICITLY UNAUTHORIZED / STOP).**
  Resolves the gap.md "no persistent secret state" objection and a reviewer's
  "single-invocation only" complaint. The directive forbids starting it. **Do not
  implement; flag as future work.** Only worth doing if a reviewer objection
  specifically requires multi-invocation secret-state persistence, and only after
  authorization.

- **E6 — Protocol-level Rep3 privacy argument / simulator (EXPERT, not us).**
  Resolves RQ3's hand-off by *taking* the hand-off: a human MPC specialist
  supplies the simulation argument. Out of scope for us to author; the paper names
  it as the required next actor (workflow.md rule: "a human MPC expert still has
  to sign off").

> **Recommended pre-authorization path:** E1 → E2 → (write draft) → then bring E3
> to the user for an authorization decision, since E3 is the experiment most
> likely to change a conclusion. Nothing in E3–E5 should be started without an
> explicit go-ahead.

---

## 9. Proposed figures & tables

**Figures**
- **F1 — The three-party review loop.** Claude (implement) ↔ repo-as-mailbox ↔
  Codex (adversarial review) ↔ Harshit (direction); append-only review log.
  `[workflow.md]`
- **F2 — The conformance pipeline.** Independent oracle ↔ harness ↔ circuit, with
  the anti-echo boundary (expected values live only in the harness). `[INTERFACE.md]`
- **F3 — The three-layer private-delivery gate.** Compiled-delivery lint → strict
  runtime transcript → recomputed SHA-bound evidence; annotate each layer "sound
  for X / not a proof of Y." `[private_run.py, validate_evidence.py]`
- **F4 — Bypass escalation diagram.** B0→B6 as a ladder of channels closed vs.
  opened, terminating at the unforbiddable `call_arg` channel; S1 drawn on an
  orthogonal axis. `[docs/limits.md]`
- **F5 (optional) — The hand-off.** A boundary line: left = implementation-level
  evidence (conformance, gross-leak linting, transcript, provenance); right =
  protocol-level obligations (executed-circuit privacy, semantic binding).

**Tables**
- **T1 — Claim→evidence→limitation** (§4).
- **T2 — Adversarial mutation taxonomy** (§5.1: mutation, channel, why it passed,
  closed?, committed control).
- **T3 — What conformance establishes vs. what needs a protocol-level proof**
  (the two hand-off properties).
- **T4 — Artifact/evidence facts** (backend pin, test counts 92+9, coverage 228,
  5 negative controls, provenance/recompute bindings).

**Listings**
- **L1 — The `reveal(False)` bypass** (minimal `openfalse` excerpt) — shows a
  public open with a `False` flag. `[threshold_smc_openfalse.mpc]`
- **L2 — The honest `call_tape`/`call_arg` channel** — shows why B6 is
  unforbiddable. `[docs/limits.md verification excerpt]`

---

## 10. Threats to validity

- **Construct validity.** "Conformance" = agreement with an *independent* oracle on
  *tested* inputs. The oracle is a human transcription of one paper's
  deterministic-query fragment; it carried a fatal actual-vs-all-outputs bug until
  review caught it (R-13), so unreviewed transcription errors may remain. No human
  MPC expert has signed off (workflow.md).
- **Internal validity.** The linter's *soundness for the memory channel* rests on
  empirical facts about the pinned backend (the clean build uses no memory; a
  cross-tape register reference is a compile error). These are backend-version
  specific; a different MP-SPDZ version could change opcode semantics or channels.
  The `tls_certs_present` flag is a weak proxy (files exist ≠ wire encrypted) — a
  stated caveat.
- **External validity.** Results are for one functionality (deterministic-query
  `threshold_SMC`), N=3, D={0,1,2}, one backend, semi-honest honest-majority, and a
  **single-host** test harness that runs all three parties as one OS user (not an
  adversarially isolated deployment — the isolation assumption is stated, not
  enforced). Generalization is `[OPEN]` (E4).
- **The boundary result is empirical, not a theorem** (§5.3 `[OPEN]`). The paper
  must not phrase C10 as a proof.
- **Semantic gap (S1/C11).** Even perfect delivery privacy would not establish the
  circuit computes the intended function beyond tested cases.
- **No performance claims** — deliberately excluded; the `results/` timings measure
  `belief3`, which is not the mechanism.
- **Reviewer independence.** Two models agreeing is weak evidence (workflow.md);
  the adversarial framing mitigates but does not remove correlated blind spots —
  hence the standing requirement for human-expert sign-off.

---

## 11. Full paper outline (9–12 pages, two-column)

Target framing: a **methodology + negative/boundary-finding paper** (experience
report backed by a reproducible artifact). Venue is `[OPEN]` — natural fits are a
PL/security workshop (e.g., PLAS-style), an artifact/experience track, or a
systematization/short-paper venue; final choice depends on E1. Page budget is
indicative.

1. **Introduction (1–1.25 pp).** The gap: MPC *applications* get green CI checks
   that are easy to mistake for privacy guarantees. Thesis (§1). The pivot away
   from "first implementation" (address R-10 up front). Contributions list (§3).
   State the boundary result and its honest scope (empirical, not a theorem) in
   the intro so no reader over-reads it.

2. **Background (1 p).** PLAS-2012 knowledge-threshold belief tracking (the
   deterministic-query fragment), threshold policies, private per-recipient
   delivery; MP-SPDZ Rep3 over Z_2^k, semi-honest honest-majority; compiled tapes
   and opcodes just enough to make §5 legible. Explicit scope box: what we do and
   do not model.

3. **Method: executable conformance for an MPC application (2–2.5 pp).** Independent
   oracle; anti-echo interface (INTERFACE.md); the accept-*and*-reject fixture and
   the discriminating case (why all-outputs `tcheck` matters, R-13); the signed
   ring bound `B<2^{k-1}` (R-22); the 228-case sweep; the evidence discipline
   (SHA-bound, `--recompute`, pipefail, provenance). F2, T4. *This is contribution
   1/2.*

4. **The private-delivery gate and its adversarial refutation (2.5–3 pp).** The
   three layers (F3). The mutation taxonomy (§5.1, T2) told as an escalation (F4):
   B0 gross reveal → B1–B5 closed → B6 unforbiddable. The two structural reasons.
   The independent semantic bypass S1 (§5.2). *This is contribution 3.* Box §5.3 as
   an `[OPEN]` conjecture with proof obligations — do **not** claim a theorem.

5. **The hand-off: what would make it a real guarantee (1–1.5 pp).** The two
   separate properties (executed-circuit privacy + semantic source-to-spec
   binding); why conformance supplies neither in general (T3, F5); what actor
   supplies each (protocol-level Rep3 argument / verified dataflow-checked
   primitive; a semantic binding argument). *This is contribution 4.*

6. **The adversarial review process (0.5–0.75 p).** The three-party loop (F1), the
   append-only log, the self-refutation (R-45→R-47) as evidence the method has
   teeth. *This is contribution 5.* Keep short; it is supporting, not central.

7. **Related work (1 p).** The five categories of §6; position the negative result
   against dataflow-aware verification (not against it — it hands off to it). All
   novelty statements gated on E1; write this section *after* E1.

8. **Threats to validity (0.5 p).** §10, condensed.

9. **Limitations & future work (0.5 p).** `Sigma_T` persistence (unauthorized
   here); generalization (E4); the dataflow checker (E3) as the experiment most
   likely to move the conclusion; the impossibility theorem (E2); required human
   expert sign-off.

10. **Conclusion (0.25 p).** Conformance + adversarial review is a rigorous,
    reusable discipline for MPC applications that establishes real functional and
    anti-gross-leak properties — and has a sharp, nameable boundary at
    per-recipient non-leakage, which is where protocol-level proof must begin.

**Appendices (not counted).** A: full `tcheck` transcription and the
discriminating worked example (CONTRACT.md). B: the five negative controls with
excerpts. C: evidence schema and a sample recomputed record. D: the review log
index (R-01..R-47).

---

## Build / delivery notes (process, not paper content)

- Manuscript authored in LaTeX under `paper/` in the repo; drafted and compiled in
  the sandbox (pdflatex), then mirrored to the Mac repo for commit (workflow.md:
  repo is the source of truth).
- First draft uses only C1–C12 claims; every gap is written `[OPEN]` inline, never
  silently filled.
- No new functionality is implemented for the paper. E3/E4/E5 are held for
  explicit authorization; E5 (`Sigma_T`) stays unstarted.
