# Review log

Every external critique gets an entry, whether it survived or not. Entries are
append-only — do not delete a refuted objection, mark it resolved and say why.

Two reasons this file exists. First, so we do not relitigate the same objection
three times. Second, because a paper that can show what was challenged and how
it was answered is a stronger paper, and reviewers notice.

Status values: `open` · `resolved` · `fatal` · `deferred`

---

## Template

```
### R-NN — <one-line summary>

- **Date:**
- **Source:** (name / model / venue — be specific, "an LLM" is not a source)
- **Targets:** claim 1 / claim 2 / claim 3 / measurement / other
- **Objection:** what they actually said, in their words where possible
- **Assessment:** our evaluation — does it land?
- **Resolution:** what changed as a result. "Nothing" is a valid answer if justified.
- **Status:**
```

---

## Open questions nobody has answered yet

These are seeded from our own uncertainty, not from external review. They stay
open until someone with actual MPC expertise addresses them.

### R-01 — Is claim 1 already folklore?

- **Date:** seeded at repo creation
- **Source:** self (Claude, during initial scoping)
- **Targets:** claim 1
- **Objection:** The observation that public-constant × secret-share is local,
  and therefore that indicator conditioning on an enumerated public hypothesis
  space is free, may be common knowledge among MPC practitioners. If so the
  claim is true but contributes nothing.
- **Assessment:** Unresolved and important. An initial literature search did not
  find it stated, but that search could not reach Google Scholar or Semantic
  Scholar, so absence of evidence is weak here.
- **Resolution:** pending. Ask on the MP-SPDZ issue tracker or at TPMPC before
  writing anything up.
- **Status:** `open`

### R-02 — Loopback timings are not network timings

- **Date:** seeded at repo creation
- **Source:** self
- **Targets:** measurement
- **Objection:** All reported timings ran with three parties on one 2-core host
  over loopback. Round count × RTT is entirely hidden. At 50 ms WAN RTT, 88
  rounds adds ~4.4 s — two orders of magnitude above the reported 22.6 ms.
- **Assessment:** Lands completely. The numbers are honest about what they
  measure and useless as performance claims.
- **Resolution:** CI matrix with `tc netem` added (localhost / LAN / WAN). Still
  emulation on one host; a paper must say so explicitly.
- **Status:** `open` until real multi-machine numbers exist

### R-03 — The security argument has never been checked

- **Date:** seeded at repo creation
- **Source:** self
- **Targets:** other
- **Objection:** The claim "the rejection decision leaks nothing" is a security
  claim written by people with no MPC background. Its failure modes are silent:
  a leaky truncation, a loop bound that depends on a revealed value, a circuit
  whose shape depends on a secret.
- **Assessment:** Lands. No part of this has been reviewed.
- **Resolution:** pending. Needs an ideal-functionality statement, an explicit
  list of what is revealed, and a data-independence checklist — then a human
  who knows MPC.
- **Status:** `open`

### R-04 — Probabilistic truncation leaks and gives no worst-case bound

- **Date:** seeded at repo creation
- **Source:** MP-SPDZ compiler warning, citing eprint 2024/1127
- **Targets:** measurement
- **Objection:** MP-SPDZ's default probabilistic truncation is unbiased but not
  bounded, so no certified error bound `eps` can be derived — and the compiler
  itself warns that it leaks.
- **Assessment:** Lands. Any soundness argument needs deterministic
  round-to-nearest, measured at 17.7× more multiplications.
- **Resolution:** Claim 2 (exact integer conditioning) sidesteps this entirely
  for deterministic queries. Not yet implemented in the circuits.
- **Status:** `open`

---

### R-05 — Claim 1 omits the secret x secret multiplication

- **Date:** 2026-08-02
- **Source:** ChatGPT, adversarial review, issue #1
- **Targets:** claim 1
- **Objection:** The affine indicator is not the Bayesian update. `[w'_s] =
  [w_s] * [i_s]` is a secret-by-secret multiplication whenever the belief is
  secret. The claim dropped `delta(s)` from its own update equation.
- **Assessment:** **Correct, and decisive.** Verified in `belief3.mpc:33`
  (`prior.get_vector().v * ind`). MP-SPDZ counted 41,098 multiplications — a
  figure printed in our own README three lines below "zero multiplications."
  Also correct that `ge = (x1 >= domv)` makes `q` secret, so the premise fails
  in our own circuit; and that PLAS §4.5 keeps beliefs secret-shared across
  invocations, so weights are secret from the second update onward.
- **Resolution:** Claim 1 marked refuted in `docs/claims.md`; README rewritten.
- **Status:** `fatal`

### R-06 — The true part of claim 1 is textbook (answers R-01)

- **Date:** 2026-08-02
- **Source:** ChatGPT, issue #1
- **Targets:** claim 1
- **Objection:** Public-constant x share being local is foundational MPC.
  Cited Cramer, Damgard & Maurer (EUROCRYPT 2000, eprint 2000/037), Trident
  (NDSS 2020 §III-A(d)), and MP-SPDZ's secret/clear vs `MULS` distinction.
- **Assessment:** Correct. This is the direct answer to R-01, and it is the
  answer we said we least wanted: the true half is folklore, the novel half is
  false.
- **Resolution:** R-01 closed by this entry.
- **Status:** `resolved`

### R-07 — Claim 2 is an unbounded-arithmetic lemma, not an MPC result

- **Date:** 2026-08-02
- **Source:** ChatGPT, issue #1
- **Targets:** claim 2
- **Objection:** Six sub-points: not implemented in MPC; uniform prior hard-coded
  while PLAS allows a general belief; no ring-overflow bound for Z_2^k; the
  multi-round test repeats an idempotent operation so tests nothing; the p=1/2
  bit-growth estimate is wrong (zero extra bits, not one); the 1/1000 overflow
  example was backwards (`b*M` gets the factor, not `a*Z`).
- **Assessment:** All six correct. The test point is the sharpest — our own
  `test_repeated_revision_is_idempotent` proves the parameterized multi-round
  test is vacuous for rounds > 1.
- **Resolution:** Claim 2 marked refuted. R-04 superseded — exact integers were
  our escape from probabilistic truncation and no longer available unbounded.
- **Status:** `fatal`

### R-08 — Claim 3 misreads PLAS 2012

- **Date:** 2026-08-02
- **Source:** ChatGPT, issue #1
- **Targets:** claim 3
- **Objection:** PLAS states Q is public in §4.3 and §4.6, then raises the
  interpreter objection in §5. They already assumed what we thought they missed.
  The universal-circuit reading is ours, not theirs. And specialising one query
  does not implement `threshold_SMC(Q)` for arbitrary later queries — this repo
  has no query language, interpreter, partial evaluator, or correctness theorem.
- **Assessment:** Correct on all counts.
- **Resolution:** Claim 3 marked refuted.
- **Status:** `fatal`

### R-09 — The circuits are not the PLAS functionality

- **Date:** 2026-08-02
- **Source:** ChatGPT, issue #1 §4-5
- **Targets:** other
- **Objection:** Publicly reveals the accept/reject verdict, which PLAS §4.4
  explicitly forbids; no private per-recipient output; one observer/target pair
  instead of all; no persistent `Sigma_T`; prior not preserved on rejection;
  `belief4.mpc` builds `q` once for `Q_0` while varying the query per round;
  unpinned MP-SPDZ; no committed raw outputs; no MPC-vs-reference comparison.
- **Assessment:** Correct. The `belief4.mpc` bug is verified — `q` is built
  before the loop, `o` uses `x2 + r` inside it. The 20-round timing is
  incoherent. R-02 and R-03 are subsumed: there is no point measuring or
  security-arguing a program that is not the functionality.
- **Resolution:** Recorded in `docs/gap.md`. Highest-value fix identified: make
  CI compare MPC output against the reference oracle.
- **Status:** `open`

### R-10 — No paper contribution remains; stop the project

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 2, issue #1
- **Targets:** other
- **Objection:** "Nobody appears to have implemented it" is an engineering gap,
  not a research contribution. Implementing and timing a 2012 construction is
  not a paper absent a new protocol, theorem, compiler, security result, or
  empirically supported systems insight. Explicitly *not* a finding that cost is
  prohibitive — there is no faithful implementation to draw that from.
- **Assessment:** Accepted without challenge. No concrete counter-evidence
  exists. The gate proposed — reopen only on an independent literature review
  producing a specific, new, falsifiable contribution stated *before* further
  implementation — is the correct discipline, and is the reverse of how this
  project started (implementation first, story after).
- **Resolution:** Paper work stopped. README leads with the stop. Performance CI
  disabled (`if: false`). Circuits marked non-conforming.
- **Status:** `resolved`

### R-11 — Conformance target, not oracle-comparison CI, is the first move

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 2, issue #1
- **Targets:** other
- **Objection:** CI automates a defined functionality; it cannot define one.
  Comparing MPC against `reference/` would confirm only that two non-conforming
  models agree — `reference/` implements our model, not PLAS. The first move is
  an executable conformance target: transcribe the Figures 8-9 contract, build a
  tiny fixture with an accepted *and* a rejected invocation, write an
  independent plaintext oracle, then the smallest MPC circuit that matches.
- **Assessment:** Correct, and it invalidates the move I proposed. My oracle is
  single-observer, stateless, with no rejection semantics. Comparing against it
  would have produced a green check for the wrong thing.
- **Resolution:** Steps 1-3 done — contract transcribed (`conformance/CONTRACT.md`),
  fixture with accept-then-reject and divergence, independent oracle with 7
  hand-derived passing assertions. Step 4 (MPC circuit) not started. Up for
  review before any circuit is written.
- **Status:** `in_progress`

### R-12 — README internally inconsistent after partial edit

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 2, issue #1
- **Targets:** other
- **Objection:** README still opened "An implementation of", closed with
  "implements and benchmarks", said "Claim 2 is the way out", and kept checklist
  items to migrate to and verify the refuted claims.
- **Assessment:** Correct. Leftovers from patching rather than rewriting.
- **Resolution:** README rewritten from scratch.
- **Status:** `resolved`

### R-13 — tcheck must quantify over ALL possible outputs, not the actual one

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 3, issue #2
- **Targets:** contract, oracle, fixture
- **Objection:** The transcription conditioned the safety check on the actual
  output only. Figure 4 line 2 is `forall possible outputs o`; the reject
  condition is `exists o, exists n: (delta|out=o)(x_i=n) > t_i`. Checking only
  the realized output makes the decision secret-dependent and lets the rejection
  leak (Sec 3.2, simulatability). The fixture's accepts were an artifact of the
  bug; corrected, invocation-1 of the old fixture is all-reject.
- **Assessment:** Correct and fatal. Verified from Figure 4 directly via a
  targeted read: line 2 reads "forall possible outputs o". Not taken on the
  reviewer's word. The whole simulatable-rejection property depends on it.
- **Resolution:** oracle rewritten to all-outputs semantics; old fixture and its
  7 tests invalidated; new fixture + 9 tests including a discriminating case that
  asserts all-outputs and actual-only give different results. CONTRACT.md
  corrected. Added clauses: deterministic-query scope, public queries, prior
  consistency, 0<t<=1, §4.5 (not Fig 8) for sharing.
- **Status:** `resolved`

### R-14 — Boundary is `<=` (equality allowed); other clarifications

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 3, issue #2
- **Targets:** contract
- **Objection:** Confirmed `<=` (reject only on strict `>`). Also: the oracle is
  a deterministic-query model and must not call itself the full PLAS
  functionality; a single fixture is a regression vector not a proof;
  reject-unobservability is not "untestable" absolutely — interface tests catch
  gross violations (public reveal), they just can't prove simulation-based
  non-observability.
- **Assessment:** All correct.
- **Resolution:** Scope stated in oracle docstring and CONTRACT.md; targeted
  tests added; unobservability reframed as a mandatory requirement with
  functional negative tests plus required expert review.
- **Status:** `resolved`

### R-11 (update)

- Steps 1-3 redone under the corrected semantics and re-submitted for review
  (issue #3). Step 4 still not started. Still `in_progress`.

### R-15 — Support invariant: zero-mass keys and negative mass

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 4, issue #3
- **Objection:** `possible_outputs = {query(s) for s in dj}` treated every dict
  key as support. A zero-mass key invents a non-possible output and then raises
  on conditioning. Constructor also accepted negative mass. Counterexample:
  `b={(0,0):1,(1,0):0}`, `q=s[0]` — support is {0}, should accept at t=1, but
  code invented output 1 and crashed.
- **Assessment:** Correct. Verified the counterexample.
- **Resolution:** `_pruned` enforces the invariant (reject negative, drop zero);
  `condition`, `possible_outputs`, `marginal_max` all filter `p>0` defensively.
  Regressions added: zero-mass-not-a-possible-output, negative-mass-raises,
  zero-mass-prior-entry-pruned.
- **Status:** `resolved`

### R-16 — Accepted-update formula omitted query evaluation

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 4, issue #3
- **Objection:** CONTRACT said `delta_j := delta_j | (out=o)`, which is
  ill-typed (pre-query belief has no `out`). Figure 9 line 6 is
  `delta_j := [[Q]]delta_j | (out=o)`. Python is equivalent only because queries
  are deterministic and total.
- **Assessment:** Correct.
- **Resolution:** CONTRACT.md fixed with the paper's formula and the
  deterministic-equivalence note.
- **Status:** `resolved`

### R-17 — Missing clauses: query-choice independence, step-4 interface

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 4, issue #3
- **Objection:** "Public query" does not imply the query CHOICE is
  secret-independent — add that assumption. And define the step-4 interface
  before coding: compile-time public (domain, query) vs runtime secret-shared
  (Sigma_T), private per-recipient outputs, returned shares; forbid compiling in
  secrets/expected vector; require a varying-secret test so constants can't pass.
- **Assessment:** Correct.
- **Resolution:** Query-independence clause added to CONTRACT.md; `INTERFACE.md`
  written defining the step-4 boundary and the anti-cheating requirement.
- **Status:** `resolved`

### R-18 — Expected output vector must NEVER enter the circuit

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 4b, issue #3
- **Objection:** INTERFACE.md said the expected output vector must enter as a
  runtime input. That lets the circuit echo it; runtime injection is as invalid
  as compiling it in. The expected vector is not part of Sigma_T or Figure 9.
- **Assessment:** Correct. My anti-cheating wording defeated itself.
- **Resolution:** INTERFACE.md rewritten — expected outputs/post-state exist
  only in the external harness, obtained independently from the oracle, compared
  against reconstructed results; circuit inputs are exactly public (N,D,Q,t_i)
  and secret-shared (secrets, beliefs).
- **Status:** `resolved`

### R-19 — Thresholds are public, not optionally secret

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 4b, issue #3
- **Objection:** INTERFACE.md allowed secret thresholds in Sigma_T. Lemma 6 has
  each party's threshold public (so P_j can simulate its own rejection); §4.5
  carrying them in Sigma_T keeps them fixed, not secret. Secret thresholds are a
  different functionality with different leakage.
- **Assessment:** Correct.
- **Resolution:** Thresholds declared PUBLIC in INTERFACE.md and CONTRACT.md;
  secret-threshold variant explicitly out of scope.
- **Status:** `resolved`

### R-20 — Support invariant not enforced at every boundary

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 4b, issue #3
- **Objection:** Only the constructor rejected negative mass; `condition` and
  `tcheck_passes` silently discarded it (reproduced: condition on
  {(0,0):5/4,(0,1):-1/4} returned {(0,0):1}). Docstring falsely claimed "_pruned
  enforces at every boundary." Wanted a direct negative-belief regression.
- **Assessment:** Correct.
- **Resolution:** Added `_positive_items` (raises on negative, skips zero); all
  primitives (condition, possible_outputs, marginal_max, hence tcheck_passes)
  iterate through it. Docstring corrected. Added
  test_negative_mass_belief_raises_in_helpers.
- **Status:** `resolved`

### R-21 — Step-4 wire/state representation must be pinned before coding

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 4b, issue #3
- **Objection:** Specify: threshold_SMC-only vs also init_SMC; fixed D^N belief
  ordering with sparse<->dense translation; weight/threshold encoding,
  normalization equivalence, integer bit bounds, no-wraparound; private
  (accept,payload) output with payload masked on reject.
- **Assessment:** Correct; these are prerequisites for a meaningful circuit.
- **Resolution:** INTERFACE.md now specifies threshold_SMC-only on a valid
  Sigma_T, fixed lexicographic dense ordering, unnormalized integer weights with
  proportional-weight equality, b*M<=a*Z check, the max(a,b)*S*W bit bound, and
  masked-payload private outputs.
- **Status:** `open` (spec written; not yet exercised by a circuit)

### R-22 — Signed no-wraparound bound (2^k > B is wrong; need B < 2^(k-1))

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-4b re-review, issue #3
- **Objection:** INTERFACE said `ring modulus > B`. MP-SPDZ comparison is signed:
  values >= 2^(k-1) read as negative. Counterexample: k=7, B=120 passes 128>120,
  but b*M=70 reads as -58, flipping reject into accept. Correct rule: B < 2^(k-1),
  bounding every operand and every intermediate in the secret eval of Q.
- **Assessment:** Correct — a real bug in the advertised bound. Verified 400
  random b*M<=a*Z cases already agreed; the failure is purely the ring size rule.
- **Resolution:** INTERFACE.md corrected to `B < 2^(k-1)` with bit_length/margin
  note; fixture B=54 shown sufficient for 64-bit. circuit_spec.signed_ring_ok +
  test_naive_bound_is_wrong_for_signed_comparison reproduce the misread.
- **Status:** `resolved`

### R-23 — Secret-support-safe zero branches (public alphabet)

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-4b, issue #3
- **Objection:** Enumerate the public compile-time alphabet O_Q, not the secret
  support. Z=0 branches: non-negative weights => M=0 => b*M<=a*Z true, safe.
  Never reveal Z>0 or branch on it publicly.
- **Assessment:** Correct, and it is the circuit-vs-oracle iteration distinction.
- **Resolution:** circuit_spec.tcheck_public iterates O_Q;
  test_public_alphabet_matches_support_decision proves it equals the oracle's
  support-based decision across the fixture and randomized cases; documented in
  INTERFACE.md and CONTRACT.md.
- **Status:** `resolved`

### R-24 — Mandatory fixed masking on reject

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-4b, issue #3
- **Objection:** "masked (or ignored by construction)" is unenforceable. Require
  payload_j = accept_j ? o_actual : MASK, reveal only (accept_j, payload_j).
- **Assessment:** Correct.
- **Resolution:** INTERFACE.md states the enforceable rule;
  circuit_spec.masked_payload + test_reject_payload_is_fixed_and_output_independent
  pin that the reject payload is independent of o_actual.
- **Status:** `resolved`

### R-25 — Step 4 built: smallest threshold_SMC circuit + conformance harness

- **Date:** 2026-08-02
- **Source:** self (authorized by Codex round-4c gate, issue #3)
- **Targets:** implementation
- **Note:** Wrote `mpc/threshold_smc.mpc` within the exact authorized scope (N=3,
  D={0,1,2}, t=1/2, 64-bit ring, one public query, secret secrets+beliefs,
  all-outputs b*M<=a*Z, private (accept,payload), unchanged-on-reject weights).
  External `harness.py` runs the fixture (2 invocations) + 2 extra valid states
  and matches the oracle on verdicts, payloads, and reconstructed weights (4/4
  PASS). CORRECTION (round-5 re-review): the circuit computes recipient-indexed
  (accept,payload) but BROADCASTS them (test-only leak) — private DELIVERY is NOT
  implemented. `NOTES.md` flags this and the missing Sigma_T persistence. No
  security/performance claims.
- **Status:** `open` (functional conformance only; awaiting adversarial review
  of private reveals, share persistence, comparison params, security argument)

### R-26 — Harness unsound as a gate (execution + parsing)

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 5, issue #4
- **Objection:** ring.sh ran without checking exit status (forced rc=73 passed);
  parser pre-filled 81 zeros and enforced no completeness/uniqueness (deleting
  all zero W rows still passed; duplicates last-write-wins).
- **Assessment:** Correct; both reproduced by the reviewer.
- **Resolution:** `mpc_run.py` fails closed on non-zero exit (retains stderr) and
  strictly validates records (exactly one ACCEPT/PAYLOAD per party, one W per
  (party,idx); rejects duplicate/missing/out-of-range/malformed). Framework
  noise ignored but tampering caught by completeness+uniqueness.
- **Status:** `resolved`

### R-27 — Add non-uniform / all-secret / property-generated coverage

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 5, issue #4 (reviewer ran 218/218)
- **Resolution:** `coverage.py` reproduces the structure as project evidence:
  228/228 across all 27 secrets, both queries, uniform/non-uniform/scaled
  weights, near-tight bit-bound (W=floor((2^63-1)/54)), and carried pairs. Run in
  CI; SUMMARY only in `results-coverage.txt`; SHA-bound raw evidence is the CI artifact.
- **Status:** `resolved`

### R-28 — MP-SPDZ provenance unpinned

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 5, issue #4
- **Objection:** Cache key said v0.4.3 but a miss cloned unpinned HEAD; no SHA
  recorded. "Reproduced in CI" had unknown backend.
- **Resolution:** Pinned to 9d809599...; cache key includes it; CI clones+checks
  out the pin and asserts HEAD==pin; the SHA is printed and stamped into both
  results files. Local evidence rebuilt at the same commit.
- **Status:** `resolved`

### R-29 — False share-identity statement in NOTES

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 5, issue #4
- **Objection:** NOTES said reject returns the ORIGINAL sharing. if_else compiles
  to self*(a-b)+b, a secret mult that may change the sharing; only the VALUE is
  unchanged.
- **Resolution:** NOTES corrected: "rejected secret value is unchanged; share
  identity/freshness has not been established."
- **Status:** `resolved`

### R-30 — Circuit must not claim private output

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round 5, issue #4
- **Objection:** Circuit computes recipient-indexed values then broadcasts them;
  header should not say "private".
- **Resolution:** Circuit header reworded — computes recipient-indexed
  (accept,payload) but BROADCASTS (test-only leak); private delivery not
  implemented.
- **Status:** `resolved`

### R-31 — CI false-green: pipe to tee masked non-zero suite status

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-5 re-review, issue #4
- **Objection:** Steps ran `python ... | tee log` under `bash -e` without
  pipefail, so the step status was tee's (0). A parser exception, mismatch, or
  ring.sh failure could leave the job green. Reproduced: `python exit 73 | tee`
  -> rc 0.
- **Assessment:** Correct — the Python core was fail-closed but CI integration
  was not.
- **Resolution:** `set -o pipefail` on both suite steps; a dedicated pipefail
  canary step that fails the job if non-zero does not propagate;
  `test_mpc_run.py::test_pipefail_propagates_nonzero` pins the mechanism.
- **Status:** `resolved`

### R-32 — "Retains logs" was false; only summaries kept

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-5 re-review, issue #4
- **Objection:** mpc_run discarded compile stdout/stderr, ring stderr, and raw
  ring stdout after parsing; the uploaded artifact (615 B) and results-*.txt were
  summaries. docs/R-27 wrongly called summaries "raw".
- **Resolution:** mpc_run writes a JSONL record per run (repo+MP-SPDZ SHA, query,
  case id, input hash, return codes, compile+ring stdout/stderr, all retained).
  `_evidence/*.jsonl.gz` committed; CI regenerates and uploads them. Summaries
  relabeled as summaries in docs, R-27, NOTES.
- **Status:** `resolved`

### R-33 — Wording, missing runner tests, carried-fail counting

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-5 re-review, issue #4
- **Objection:** (a) .mpc still said "byte-for-byte unchanged on reject";
  (b) NOTES said harness advances the oracle between invocations (it carries
  circuit output); (c) NOTES said non-uniform untested (coverage tests it);
  (d) R-25 said private output implemented; (e) mpc_run said "unexpected records
  rejected" but ignores unknown tags; (f) no committed runner/parser tests;
  (g) carried-pair counted two failures as one.
- **Resolution:** (a)-(d) corrected; (e) docstring states the exact ignore
  policy; (f) `test_mpc_run.py` (13 tests incl. the 6 reviewer attacks + fail-
  closed + pipefail); (g) coverage counts each carried transition separately.
- **Status:** `resolved`

### R-34 — Committed evidence had no repository provenance (repo_sha UNKNOWN)

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-5c, issue #4
- **Objection:** Every committed record said `repo_sha: "UNKNOWN"` (generated
  outside a git repo). Claiming SHA-bound provenance for the committed files was
  false; UNKNOWN must not satisfy the schema.
- **Assessment:** Correct.
- **Resolution:** `repo_provenance()` classifies source; only CI (GITHUB_SHA
  present) is `bound: true`. Committed files relabeled `local-unbound-*.jsonl.gz`
  (`repo_sha: null`, `bound: false`); README/docs state the authoritative
  SHA-bound evidence is the CI artifact. CI validation requires `--require-bound`
  and exact `repo_sha == $GITHUB_SHA`.
- **Status:** `resolved`

### R-35 — Records omitted the final parsed/comparison result

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-5c, issue #4
- **Objection:** `_evidence()` ran inside `run_circuit()` before parse/compare,
  so records had no parse status, comparison status, or pass/fail; a
  parser/oracle mismatch could not appear in the record.
- **Resolution:** `run_and_check()` finalizes each record AFTER strict parse +
  oracle compare with `parse_ok`, `comparison_ok`, `mismatches`, `error`,
  `final`. Failure records retained. Tests
  `test_run_and_check_writes_finalized_record` / `_records_failure` pin it.
- **Status:** `resolved`

### R-36 — Evidence retention could vanish without failing the job

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-5c, issue #4
- **Objection:** `gzip ... || true` returned 0 on a missing glob, and
  upload-artifact lacked `if-no-files-found: error`; a future run could lose the
  JSONL and stay green with only summaries.
- **Resolution:** Removed `|| true`; added a fail-closed `validate_evidence.py`
  step (exact counts 4/228, required fields, bound, exact repo+MP-SPDZ SHA) BEFORE
  compression; upload sets `if-no-files-found: error`. Validator unit-tested (6).
- **Status:** `resolved`

### R-27 (residual) — fixed

- The "SUMMARY only in results-coverage.txt; SHA-bound raw evidence is the CI artifact" line now points to the CI
  `conformance-evidence` artifact; results-*.txt labeled summaries throughout.

### R-37 — Validator certified contradictory/incomplete evidence

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-5d, issue #4
- **Objection:** validate_evidence accepted four bypasses: final=PASS with
  parse_ok/comparison_ok=false; duplicate case_id; missing fields (REQUIRED was a
  subset of EVIDENCE_FIELDS); bound=true with repo_sha_source="unbound". The
  "good" unit test itself used two identical records + incomplete transcript,
  pinning the bypass.
- **Assessment:** Correct — a gate certifying bad evidence is worse than none.
- **Resolution:** Validator now requires the FULL field set with types, enforces
  the PASS invariant (parse_ok/comparison_ok True, mismatches==[], error null,
  final PASS, ring_rc 0, compile_rc in {0,null}), unique non-empty case IDs,
  64-hex input_hash, and under --require-bound both bound True AND
  repo_sha_source=="github_actions". Regressions added for all four bypasses
  plus bad input_hash; the "good" test now uses complete, unique records.
- **Status:** `resolved`

### R-38 — Comparison exception not retained; CI dropped failure JSONL

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-5d, issue #4
- **Objection:** run_and_check retained process/parse failures but a compare()
  exception propagated with zero evidence written. The CI failure path also
  skipped compression and uploaded only ci-*.jsonl.gz, so failure JSONL was lost.
- **Resolution:** run_and_check resets LAST_TRANSCRIPT (no stale leak), defaults
  all transcript fields, and writes a complete FAIL record on the comparison
  exception path too. Test `test_run_and_check_retains_comparison_exception`
  pins it. CI always-upload now includes uncompressed `ci-*.jsonl` as well as the
  `.gz`, so failure records survive.
- **Status:** `resolved`

### R-27 (residual, actually fixed now)

- The real line ("raw retained in results-coverage.txt") was NOT changed last
  round despite the note; corrected now. results-*.txt are SUMMARIES throughout;
  SHA-bound raw evidence is the CI artifact. Verified no "raw retained" strings
  remain in docs/.

### R-39 — Issue #4 evidence/conformance gate PASSED

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, round-5e, issue #4
- **Note:** Scoped PASS at fa403c9 — functional conformance + evidence machinery
  certified (71/71, 4/4, 228/228, hardened validator, bound CI artifact SHA-256
  matched). Authorized next phase: private per-recipient delivery, then Sigma_T
  persistence, staged. Round-5 harness/provenance considered settled.
- **Status:** `resolved`

### R-40 — Staged gate 2: private per-recipient delivery (started)

- **Date:** 2026-08-02
- **Source:** self (authorized by round-5e)
- **Note:** Added ADVERSARY.md (threat model, authorized recipients, demonstrated
  vs not-claimed). New private build delivers (accept_j,payload_j) only to P_j via
  reveal_to+print_ln_to; nothing broadcast; weights not output. private_run.py
  launches 3 parties with per-player output and asserts no cross-party verdict
  leakage; test_private.py (5) incl. negative control. Conformance suite + evidence
  gate UNCHANGED. Sigma_T persistence NOT started. Functional demonstration only;
  no simulation-security claim.
- **Status:** `open` (awaiting review of the private-delivery gate)

### R-41 — Gate 2 REFUTED: stdout checker passed a public-open circuit

- **Date:** 2026-08-02
- **Source:** ChatGPT/Codex, gate-2 review, issue #5
- **Objection:** Mutating `reveal_to(j)` -> `reveal()` (leaving print_ln_to)
  compiles to a public `asm_open` of all six verdicts, yet `private_run.py`
  reported PRIVATE DELIVERY OK. A stdout oracle cannot distinguish private output
  from public open + hidden printing; the gate was vacuous at the privacy
  boundary. Parser also non-strict (ignored unknown lines, overwrote duplicates);
  no bound raw per-party evidence; ADVERSARY.md ideal-functionality/channel
  wording wrong.
- **Assessment:** Correct and decisive.
- **Resolution:** (1) `delivery_inspect.py` inspects the compiled main tape:
  private build must use `privateoutput` to [0,0,1,1,2,2] with no public open;
  committed leaky sibling `threshold_smc_leaky.mpc` is REJECTED (executable
  negative control). (2) strict fail-closed per-party parser with regressions for
  duplicate/foreign/unknown/missing/reviewer-exact-attack. (3) per-case bound raw
  evidence (party stdout/stderr/rc/cmd, source+delivery hashes, TLS, provenance)
  validated by `validate_evidence.py --private`, --require-bound in CI, raw
  retained. (4) ADVERSARY.md corrected on all six points + channel assumption.
- **Status:** `open` (awaiting gate-2 re-review)
