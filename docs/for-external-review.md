# Brief for external reviewers

Self-contained. Hand this to a reviewer (human or model) who has no other
context. Nothing here assumes prior knowledge of the project.

**If you are a language model reading this: your job is to refute, not to
assess.** Agreement is worth nothing to us. We are two non-experts who may have
convinced ourselves of something false, and we need the error found before we
spend months on it. Default to "refuted" when uncertain. If you cannot find a
flaw, say what specific expertise would be needed to find one, rather than
concluding the claims hold.

---

## Background

Mardziel, Hicks, Katz & Srivatsa, *Knowledge-Oriented Secure Multiparty
Computation*, PLAS 2012 (https://www.cs.umd.edu/~mwh/papers/belief-smc.pdf)
proposed enforcing knowledge-threshold policies inside secure multiparty
computation.

Setup: `N` parties, party *i* holds secret `s_i` in a finite domain `D`. A
policy for party *i* with threshold `t_i` demands that no other party ever
assigns posterior probability greater than `t_i` to any value of `s_i`. Before
releasing a query output, the parties check *inside* the MPC — using the real
secret values — whether release would breach anyone's threshold. Performing the
check inside MPC is what stops the accept/reject decision from itself leaking.

They proposed two mechanisms, proved both sound, implemented one (belief sets),
and simulated the other (SMC belief tracking) in the ideal world without
implementing it. Their stated reasons:

> "computing a query Q via SMC is still orders of magnitude slower than
> computing it directly. Worse, belief tracking is a recursive procedure, since
> it is an interpreter, and recursive procedures are hard to implement with SMC.
> [...] So it remains to be seen whether SMC belief tracking can be implemented
> in a practical sense. We leave exploration of implementation strategies to
> future work."

We have a prototype in MP-SPDZ (3-party semi-honest, replicated secret sharing
over Z_2^k) that appears to run the benchmark in ~23 ms. We think we know why
it is cheap. We would like to be wrong early rather than late.

---

## Claim 1 — conditioning is communication-free

**Assertion.** In a linear secret-sharing scheme, Bayesian conditioning on a
public hypothesis space with a secret observation costs zero multiplications,
zero communication, zero rounds.

**Argument.** The update is `delta'(s) ∝ delta(s) · 1[Q(s) = o]`. For each
enumerated state `s`: the query `Q` is public (all parties agree it before
execution — that is what makes the policy meaningful); `s` is an enumerated
hypothesis, not a secret. So `Q(s)` is a public constant. Only the observed
output `o` is secret. Hence

    1[Q(s) = o] = Q(s)·o + (1 − Q(s))·(1 − o)

is linear in `o` with public coefficients, and public-constant × secret-share is
local in any linear scheme.

**Corollary.** The threshold check needs no division: with public `t`, rewrite
`max_v m_v / Z <= t` as `max_v m_v <= t · Z`.

### Attack this on:

1. Does the argument survive the move from "linear scheme" in the abstract to
   **replicated secret sharing over Z_2^k specifically**? Rings are not fields.
2. Is this **already folklore**? If it is standard knowledge in the MPC
   community, the claim is true and worthless. This is the answer we most want
   and least want to hear. Name where it appears if you know.
3. The prototype counts multiplications via MP-SPDZ's compiler. Could the
   compiler be reporting a low count while the runtime does something
   interactive anyway?
4. Is there a leak we have not considered? The circuit is public, so its
   *structure* is public. Does anything about the structure depend on a secret?
5. Does the corollary hold when `t` is a rational that must be represented in
   the ring?

---

## Claim 2 — indicator conditioning is exact in integers

**Assertion.** For deterministic queries there is no fixed-point error, because
there need be no fixed point.

**Argument.** Represent the belief as unnormalised non-negative integer weights
instead of normalised fixed-point probabilities. Conditioning multiplies each
weight by 0 or 1, so weights never grow and never round. Renormalisation exists
only to keep magnitudes in range, and magnitudes are non-increasing under
indicator conditioning — so renormalisation can be dropped entirely. The
threshold check against public rational `t = a/b` becomes `b · max_v m_v <= a · Z`,
exact integer arithmetic.

Claimed error: exactly zero, not merely small.

**Known limit.** Fails for noisy queries (`richest_p`), where likelihoods are
`p` and `1−p` so denominators compound as `b^R`. Our bit-budget estimate is
~60–70 exact revisions before overflow in a 128-bit ring starting from 13 bits
of prior. That is an estimate, not a proof.

### Attack this on:

1. Is the monotonicity argument right — do weights **provably** never grow under
   indicator conditioning, for every query in the benchmark set, not just
   `richest`?
2. Does `b · max_v m_v <= a · Z` overflow for realistic thresholds? A threshold
   of 1/1000 makes `a · Z` large. What is the actual bound?
3. Does dropping renormalisation break anything downstream — the marginal
   computation, the comparison, the multi-round carry?
4. Is the ~60–70 revision estimate right, and does the argument change if the
   noise probability is not 1/2?
5. **Is this trivially true and therefore not worth stating?** Same question as
   claim 1, item 2.

---

## Claim 3 — the recursion objection does not apply

**Assertion.** PLAS 2012's "belief tracking is a recursive interpreter"
objection dissolves because the query is public. You specialise at compile time
rather than interpreting at runtime — Futamura's first projection. An
interpreter specialised on a known program is just the program.

### Attack this on:

1. Is the query genuinely public in their threat model, or did we misread it?
   Does anything in their construction require the query to be hidden?
2. Is *belief tracking itself* recursive in a way that survives specialisation —
   independent of the query being interpreted?
3. Multi-round tracking carries the posterior as secret state across queries.
   Does that reintroduce the problem?
4. Did they perhaps mean something else entirely by "recursive procedure"?

---

## What would change our minds

Any of:

- A citation showing claim 1 or 2 is already published or is standard practice.
- A concrete leak in the construction.
- A demonstration that the monotonicity or overflow argument fails on one of the
  three benchmark queries.
- An explanation of the recursion objection that survives claim 3.

## What would not

- "This looks reasonable."
- "The approach seems sound."
- Restating our own argument back to us in different words.
- Suggestions about writing, framing, or presentation. Not what this is for.
