# Claims to verify

Two observations make this project cheap. Neither appears in the PLAS 2012
paper. Neither has been checked by anyone who knows MPC.

**Treat both as hypotheses.** If either is wrong, most of the cost analysis in
the README goes with it, and the project needs rethinking rather than
continuing. Verifying these is the first real work, and it is what makes the
resulting paper yours rather than a summary of someone else's.

---

## Claim 1: the conditioning step is communication-free

### Statement

In any linear secret-sharing scheme, Bayesian conditioning on a public
hypothesis space with a secret observation requires no multiplications, no
communication, and no rounds.

### Argument

The Bayesian update is

    delta'(s) proportional to delta(s) * 1[Q(s) = o]

For each enumerated state `s`:

- `Q` is public. All parties agree the query before running it; that is what
  makes a knowledge-threshold policy meaningful in the first place.
- `s` is an enumerated hypothesis, not a secret. The observer is reasoning over
  all possible values.
- Therefore `Q(s)` is a **public constant**.
- Only the observed output `o` is secret.

So the indicator can be written

    1[Q(s) = o] = Q(s)*o + (1 - Q(s))*(1 - o)

which is **linear in `o` with public coefficients**. Public-constant times
secret-share is a local operation in any linear scheme. No interaction.

A corollary: the threshold check needs no division. With public `t`,

    max_v m_v / Z <= t     becomes     max_v m_v <= t * Z

again public-times-secret. One secure comparison for the entire check.

### What to check

- [ ] Is the linearity argument actually right for replicated secret sharing
      over Z_2^k specifically, not just "linear schemes" in the abstract?
- [ ] Does MP-SPDZ actually compile this to a local operation? Read the emitted
      bytecode, do not trust the multiplication counter alone.
- [ ] Does anything downstream branch on a revealed value? A `@for_range` whose
      bound depends on a secret would break obliviousness silently.
- [ ] Is the circuit structure itself independent of all secrets? The circuit is
      public; if its shape depends on a secret, that leaks regardless of what
      the wires carry.

### Why it might be wrong

The most likely failure is that this is already folklore in the MPC community
and simply too obvious to write down — in which case the observation is correct
but not a contribution. Ask someone before building a paper on it.

---

## Claim 2: indicator conditioning is exact in integers

### Statement

For deterministic queries there is no fixed-point error, because there is no
fixed point. Bayesian conditioning under a 0/1 likelihood is exact integer
arithmetic.

### Argument

Represent the belief as unnormalised non-negative integer weights rather than
normalised fixed-point probabilities.

- Conditioning multiplies each weight by 0 or 1. Weights never grow, never
  round, never lose precision.
- Renormalisation is only needed to keep magnitudes in range. Under indicator
  conditioning magnitudes are non-increasing, so **it can be dropped entirely**.
- The threshold check against a public rational `t = a/b` becomes
  `b * max_v m_v <= a * Z`. Exact. No division.

Error: zero. Not "small". Zero.

This covers two of the paper's three benchmark queries completely
(`richest`, `similar_w`).

`reference/test_reference.py::test_integer_matches_exact_rational` is the
empirical backing.

### Where it breaks

`richest_p`, the noisy maximum. Likelihoods are `p` and `1-p`, so weights get
multiplied by rationals and denominators compound as `b^R` over `R` rounds.

Back-of-envelope: with `p = 1/2` you need roughly one extra bit per round.
Starting from `ceil(log2 8281) = 13` bits of prior in a 128-bit ring, leaving
~40 bits of slack for comparisons, that is **roughly 60-70 exact revisions**
before overflow.

That number is a bit-budget estimate, not a proof and not a measurement.

### What to check

- [ ] Prove the overflow bound properly rather than estimating it.
- [ ] Confirm weights genuinely stay bounded across long revision sequences for
      `similar_w`, not just `richest`.
- [ ] Check the comparison `b*M <= a*Z` does not overflow for realistic `a`, `b`.
      Thresholds like 1/1000 make `a*Z` large.
- [ ] Migrate `mpc/belief3.mpc` from `sfix` to `sint` integer weights and
      confirm the measured cost drops as predicted. **Not yet done** - the
      current circuits still use fixed point.

### Why this matters

Renormalisation is ~80% of the measured runtime *and* 100% of the precision
problem. If claim 2 holds, dropping it removes both at once. The 2012 paper
could not have seen this because it worked in the reals, where the distinction
between "normalised probability" and "unnormalised weight" is invisible.

---

## The thing neither claim covers

Multi-round tracking with a **non-factorable posterior**. After conditioning,
the joint is not a product of marginals, so round 2 needs the full explicit
table carried as secret state. Fine at 8281 states; hopeless at 6 parties.

The idea worth exploring: compile the *conjunction of all past observations*
into one weighted Boolean formula over `(s, o_1, ..., o_R)`, leaving the `o_r`
free. Structure depends only on the public queries; the secret outputs enter as
weights at evaluation time. One weighted-model-counting pass gives the current
posterior marginal with no explicit table and no accumulated error.

That is: compile the observation history, do not materialise the posterior.

This was not found in the literature during the initial survey, but the survey
was not exhaustive — Google Scholar and Semantic Scholar were both unreachable.
Search properly before claiming novelty. Relevant prior art to read first:
Dice (OOPSLA 2020), Bit Blasting Probabilistic Programs (PLDI 2024), and the
`rsdd` BDD library that Dice is built on.

Catch: Dice's optimisations (flip-lifting, determinism elimination) inspect
probability values, so compiling with secret priors would make the BDD
structure secret-dependent — which leaks, since structure is public. Symbolic
weights only.
