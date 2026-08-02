# Claims — ALL THREE REFUTED

External adversarial review, 2026-08-02, refuted all three claims.
Full review: https://github.com/harshitkargetiiiiii/smc-belief-tracking/issues/1

This file is kept as a record of what we got wrong and why. Do not build on
anything below. Nothing here is a live claim.

---

## Claim 1 — "conditioning is communication-free" — REFUTED

**What we claimed.** `1[Q(s)=o] = Q(s)·o + (1−Q(s))·(1−o)` is linear in the
secret output `o` with public coefficients, therefore local, therefore
Bayesian conditioning costs nothing.

**Why it is wrong.** The indicator is not the update. The update is

    [w'_s] = [w_s] · [i_s]

Computing the indicator locally does not help, because it must then be
multiplied by the secret belief weight. That is a secret × secret
multiplication. We wrote the update equation correctly and then silently
dropped the `delta(s)` factor from our own reasoning about it.

**The implementation proves it.** In `mpc/belief3.mpc`, `prior.get_vector().v *
ind` is exactly that multiplication, and MP-SPDZ reported **41,098
multiplications** — a number we printed in the README three lines below the
words "zero multiplications."

**A second error.** We assumed `Q(s)` is public. In our own circuit
`ge = (x1 >= domv)` makes it depend on the secret `x1`, so `q` is secret too.
The premise fails in our code even where it might hold in principle.

**Why it does not hold in principle either.** PLAS 2012's real-world state
`Sigma_T` carries the beliefs secret-shared between invocations (Section 4.5).
Initialization sets `delta_j = delta | (x_j = s_j)`, so even a public common
prior becomes party-specific state depending on secret `s_j`. After any
accepted observation the carried posterior depends on secret outputs. The
weights are secret from the second update onward, and usually from the first.

**The folklore question, answered.** The part that is true — public-constant ×
share is local — is foundational, not a contribution:

- Cramer, Damgård & Maurer, *General Secure Multi-Party Computation from any
  Linear Secret Sharing Scheme*, EUROCRYPT 2000. https://eprint.iacr.org/2000/037
- Trident, NDSS 2020, §III-A(d) — states it explicitly and contrasts it with
  secret multiplication.
- MP-SPDZ documents secret/clear as local and secret/secret as `MULS`.

So the true half is textbook and the novel half is false.

**Also wrong:** "one secure comparison for the entire check." Removing the
division is valid, but the secret maximum over 91 marginals still needs ~90
comparisons and selections. Our own tournament at `belief3.mpc:42-56` does
exactly that.

**Also overgeneralized:** the affine identity holds only for binary `q_s, o`.
For larger output alphabets, `[q_s = o]` needs an equality test or a one-hot
secret output, and producing that is non-linear.

---

## Claim 2 — "indicator conditioning is exact in integers" — REFUTED AS STATED

A narrow lemma survives: in *unbounded* arithmetic, multiplying bounded
non-negative integer weights by deterministic 0/1 likelihoods does not increase
them, and a rational threshold can be checked by cross-multiplication. That is
elementary exact arithmetic, not an MPC result.

What was wrong with the claim as stated:

1. **Not implemented.** Every circuit in this repo uses `sfix`. Python
   `Fraction` agreeing with Python `int` says nothing about MP-SPDZ ring
   behaviour, security, or cost.
2. **The prior is silently restricted.** `belief_exact.py` hard-codes a uniform
   prior. PLAS accepts a general common belief. A rational prior needs a common
   integer scaling that may dominate the bit budget; arbitrary real priors are
   not exactly representable.
3. **Z_2^k is not unbounded.** With `S` states and weights `<= W`, a
   conservative signed-comparison requirement is `max(a,b) · S · W < 2^(k−1)`,
   plus whatever the comparison protocol needs internally. We proved and
   enforced no such bound. Public multiplication by `b` can wrap locally and
   still yield the wrong policy decision.
4. **The tests do not test what we said they test.** The parameterized
   multi-round test repeats the *same* query with the *same* observation, and
   indicator conditioning is idempotent in that case — which the very next test
   confirms. No changing queries, mixed observations, arbitrary priors, or
   ring-boundary cases. `similar_w` is only tested as a plaintext Boolean.
5. **The p = 1/2 estimate is mathematically wrong.** At p = 1/2 both likelihoods
   are 1/2, the observation conveys no information, the common denominator
   cancels, and zero extra bits are needed per round — not one. For p = A/B the
   bound involves `max(A, B−A)^R` with possible common-factor reduction, not
   `B^R`. The "60–70 revisions" figure does not follow from the representation
   we described.
6. **The overflow example was backwards.** For `t = a/b = 1/1000` it is `b·M`
   that gets the factor 1000, not `a·Z`.

Salvageable only as a bounded-arithmetic lemma for representable rational
priors, after an explicit ring bound and a real `sint` implementation.

---

## Claim 3 — "the recursion objection does not apply" — REFUTED

**What we claimed.** PLAS's "belief tracking is a recursive interpreter"
objection dissolves because the query is public, so you specialise at compile
time.

**Why it is wrong.** PLAS states in Sections 4.3 and 4.6 that `Q` is public and
chosen independently of the secrets — and *then*, in Section 5, says belief
tracking is a recursive interpreter and hard in SMC. They already assumed what
we thought they had overlooked. Their objection cannot be explained by it.

We also invented the universal-circuit reading. The paper never says a secret
query would require one.

And a public query supplied *per invocation* is not a query fixed when a binary
is compiled. Specialising one known query yields one query-specific circuit; it
does not implement `threshold_SMC(Q)` for arbitrary later queries or adaptively
chosen sequences. This repo has no query language, no interpreter, no partial
evaluator, no compiler from `Q`, and no correctness theorem for specialisation.
It has hand-written circuits for one Boolean query.

---

## What this leaves

The engineering question PLAS left open is still open — nobody has implemented
SMC belief tracking. What is dead is our explanation for why it would be cheap,
and with it the 22.6 ms figure, which times a partial computation that is not
the PLAS functionality.

See `docs/gap.md` for what a real implementation would have to do.
