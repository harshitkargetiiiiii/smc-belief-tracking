# PLAS 2012 SMC belief tracking — transcribed contract (corrected, round 3)

Step 1 of `docs/conformance.md`. Source: Mardziel, Hicks, Katz & Srivatsa, PLAS
2012. https://www.cs.umd.edu/~mwh/papers/belief-smc.pdf

**Round-3 review found a fatal error in the previous version** (issue #2): the
safety check was conditioned on the *actual* output only. It must quantify over
*all possible outputs*. Corrected below. The section/figure citations should
still get a line-by-line human check against the PDF.

## Scope

DETERMINISTIC, total, public queries adding only `out`. PLAS also permits
probabilistic queries, which need likelihood weighting under the paper's
probabilistic semantics — a Boolean support-filter is not faithful for those.
Out of scope here; the oracle and any circuit must say "deterministic queries".

## The policy (§3.2, Fig. 4)

Threshold `t_i` bounds the maximum posterior probability any other party may
assign to any single value of `i`'s secret, with `0 < t_i <= 1`. Reject when a
value's probability is *strictly greater* than the threshold — so acceptance
uses `<= t_i` (equality allowed).

**Query assumption.** Queries are public AND their choice is independent of the
secrets (a query chosen as a function of a secret could leak through the choice
itself, separate from the output). "Public" alone does not imply this;
secret-independent choice is required.

**Thresholds are PUBLIC.** Lemma 6: for `i != j`, `t_i` is publicly known so
`P_j` can simulate whether it will be rejected. §4.5 carries thresholds in
`Sigma_T` to keep them fixed across invocations; that does not make them secret.
A secret-threshold variant is a *different* functionality (receiving `reject`
could reveal others' thresholds; the Lemma-6 simulation argument fails) and is
out of scope.

Support invariant: a belief's states are its positive-probability support;
zero-mass states are not "possible outputs" and negative mass is illegal.

## tcheck — ALL possible outputs (Fig. 4, verbatim)

    tcheck(q, delta_i, t_j, x_j):
      1  delta_i := [[q]] delta_i
      2  forall possible outputs o
      3    d_hat := (delta_i | (out = o)) restricted to {x_j}
      4    if exists n. d_hat({x_j = n}) > t_j then return reject
      5  return accept

§3.2 ("Avoiding leakage due to query rejection") explains why: rejecting based
on the actual output makes the reject decision depend on secret data, so the
rejection itself leaks. The decision must be *simulatable* — independent of the
true secret — which requires quantifying over every possible output.

**Oracle vs circuit iteration.** The plaintext oracle iterates the secret
support (`possible_outputs`). A circuit cannot reveal the support, so it iterates
the PUBLIC alphabet `O_Q = {Q(s) : s in D^N}`. These agree: an impossible branch
has `Z = 0` hence every `M = 0` and `b*M <= a*Z` passes vacuously, so the two
iterations give the same accept/reject (see `INTERFACE.md` and
`test_circuit_spec.py`).

## init_SMC (Fig. 9)

`delta_j := delta | (x_j = s_j)` — each party's belief is the common prior
conditioned on that party's own secret. So even a public prior yields
secret-dependent per-party state.

## threshold_SMC (Fig. 9), per query Q

For each recipient `P_j`:

1. Predicted output distribution `[[Q]]delta_j`; possible outputs = its support.
2. For every other party `i != j`, run tcheck over ALL those outputs (above).
3. Accept `P_j` iff every tcheck passes.
4. On accept: `P_j` sees the ACTUAL output `o`;
   `delta_j := [[Q]]delta_j | (out = o)` (Fig. 9 line 6 — the query is evaluated
   into the belief, then conditioned on the actual output; used ONLY here, ONLY
   after checks pass). For deterministic total queries this equals filtering
   `delta_j`'s support by `Q(s) = o` and renormalizing, which is what the oracle
   does. On reject: `P_j` sees reject; `delta_j` unchanged (§4.4, Lemma 6).

## Privacy (§4.4) — a requirement, NOT established by functional tests

Whether `P_j` got output or reject must not be observable by any other party.
Warning (§4.4): *"If P1 observes that P2 receives reject, it knows that x2 must
be either 0 or 9 ... if t2 < 1/2 we have violated the threshold."*

This is an information-flow property of the protocol, not a function of the
state. Functional conformance cannot prove it. Interface tests / circuit
inspection CAN catch gross violations (e.g. a public `reveal()` of the verdict),
but proving simulation-based non-observability needs a protocol-level security
argument and a human MPC specialist. Keep it as a mandatory requirement.

## Persistent state Sigma_T (§4.5)

Carried between invocations: secrets, thresholds, current beliefs. §4.5 returns
fresh shares of the new Sigma_T with each recipient's authorized output. The
sharing (XOR in the paper) is one instantiation; any equivalent secure sharing
satisfies the abstract functionality. (Corrected: the sharing construction is
§4.5, not Figure 8.)

---

# Worked example — the discriminating case (why all-outputs matters)

Fresh model, 3 parties, domain `{0,1,2}`, uniform prior, thresholds `1/2`,
secrets `(0,0,1)`. Query `p1_is_max = [x0 >= x1 ∧ x0 >= x2]`. Recipient 0.

`delta_0` = uniform over the 9 states with `x0 = 0`. Actual output on `(0,0,1)`
is `0` (since `0 >= 1` fails).

- **Actual branch** (`p1_is_max = 0`): removes only `(x1,x2)=(0,0)` → 8 states;
  `x1` marginal max `3/8 <= 1/2`. **An actual-output-only check would ACCEPT.**
- **Alternate branch** (`p1_is_max = 1`, i.e. `x1=0 ∧ x2=0`): the single state
  `(0,0,0)`; `x1` marginal `= 1 > 1/2`.

Correct all-outputs tcheck sees the alternate branch and **REJECTS**. The two
semantics give different visible results here — this is the regression pinned in
`test_conformance.py::test_discriminating_case`. Intuition: if `P1` *had* been
the max, recipient 0 would learn `x1 = x2 = 0` with certainty; rejecting only in
that world would let the reject itself reveal it, so the query is refused in
*all* worlds.

# Fixture — divergence + reject-state-preservation

secrets `(0,0,1)`, `t=1/2`, two invocations:

- **inv1 `sum_even`** (actual sum 1, odd → output 0): all three accept, each
  belief updates (party 2: 9 → 5 states). Visible `[0, 0, 0]`.
- **inv2 `p1_is_max`** (actual output 0): parties 0,1 accept, party 2 rejects →
  `[0, 0, reject]`. Party 2's belief is unchanged (stays 5 states, does not
  collapse). Per-recipient divergence in one invocation.

This fixture does NOT distinguish the two semantics (party 2's actual branch is
already unsafe); it exists for divergence and state-preservation. The
discriminating example above is what guards the all-outputs rule.

## What a passing conformance test establishes — and does not

Establishes: a circuit reproducing these visible outputs and belief snapshots is
functionally faithful to the deterministic-query PLAS transition ON THESE CASES.
A single fixture is a regression vector, not a proof of general conformance —
hence the added targeted tests (equality boundary, unrealized output, impossible
event, non-uniform prior, threshold range).

Does NOT establish: reject-unobservability (§4.4). No functional test can.
