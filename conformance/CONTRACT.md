# PLAS 2012 SMC belief tracking — transcribed contract

Step 1 of `docs/conformance.md`. Every clause cites the paper. Source:
Mardziel, Hicks, Katz & Srivatsa, *Knowledge-Oriented Secure Multiparty
Computation*, PLAS 2012. https://www.cs.umd.edu/~mwh/papers/belief-smc.pdf

**Caveat on this transcription.** It was assembled via a single automated read
of the PDF, not a line-by-line human reading of Figures 8-9. The section/figure
citations below must be checked against the actual paper before this is trusted.
That check is a review task, not something this document establishes on its own.

## The policy

A knowledge-threshold policy for party `i` sets `t_i` bounding the maximum
posterior probability any *other* party may assign to any single value of `i`'s
secret. Reject condition (Fig. 4 line 4): `∃ n. δ̂({x_i = n}) > t_i` — reject if
some value's probability exceeds the threshold. (§3.2, Fig. 4)

## init_SMC (Fig. 9)

Each party `j`'s belief is the common prior `δ` conditioned on that party's own
secret: `δ_j := δ | (x_j = s_j)`. So even a public common prior yields
party-specific state depending on the secret `s_j`. (Fig. 9, `init_SMC`)

## threshold_SMC (Fig. 9), per query Q, real output o = Q(s_1..s_N)

For each recipient `P_j`:

1. Revised belief: `δ_j | (out = o)` — probabilistic execution of `Q` conditioned
   on the actual output `o`. (Fig. 9 line 6)
2. For every other party `i ≠ j`, check `tcheck(Q, δ_j, t_i, x_i)`: does the
   revised belief's marginal on `x_i` assign any value probability `> t_i`?
   (Fig. 9 lines 2-5)
3. Accept `P_j` iff all those checks pass (Fig. 9 line 5).
4. On accept: `P_j` sees `o`; `δ_j := δ_j | (out = o)`.
   On reject: `P_j` sees `⊥`; `δ_j` unchanged. (§4.4, Lemma 6)

## Privacy (§4.4) — NOT modelled by the oracle

Whether `P_j` received output or `⊥` must not be observable by any other party.
The paper's warning (§4.4, p.10): *"If P1 observes that P2 receives reject, it
knows that x2 must be either 0 or 9 ... if t2 < 1/2 we have violated the
threshold."* Achieved by XOR-sharing the persistent state `Σ_T` so no fragment
reveals anything (Fig. 8).

**This is an information-flow property of the protocol, not a function of the
state.** A functional conformance test cannot establish it. The oracle computes
*who sees what and the resulting beliefs*; it says nothing about observability.
Any claim that a circuit has this property needs a human MPC specialist, per the
round-2 review.

## Persistent state Σ_T (§4.5)

Carried between invocations: (1) the secrets, (2) the thresholds `t_i`, (3) the
current beliefs `δ_i`. XOR-shared across parties, reconstructed inside each
invocation.

---

# The fixture (step 2) and its hand derivation

3 parties, domain `{0,1,2}`, uniform prior, thresholds all `1/2`,
secrets `(0,0,1)`. Two invocations.

`δ_j` initial: prior conditioned on `x_j = s_j` → 9 states each (one coord
pinned, other two free over `{0,1,2}²`), uniform at `1/9`.

## Invocation 1 — `Q = p1_is_max` = `[x0 ≥ x1 ∧ x0 ≥ x2]`

Real output on `(0,0,1)`: `0 ≥ 0 ∧ 0 ≥ 1` → **o = 0**.

- **Party 0** (`x0=0`). Condition `δ_0` on `p1_is_max = 0`. With `x0=0`,
  `p1_is_max = 1` iff `x1=0 ∧ x2=0`; so `=0` removes exactly `(x1,x2)=(0,0)`:
  **9 → 8 states**, each `1/8`. Marginal on `x1`: value 0 → `2/8`, values 1,2 →
  `3/8` each. `max = 3/8 ≤ 1/2` ✓. Marginal on `x2` symmetric ✓. **Accept**;
  belief changes. Sees `0`.
- **Party 1** (`x1=0`). `p1_is_max = 0` iff `x0 < x2`. States: `(x0,x2) ∈
  {(0,1),(0,2),(1,2)}`, each `1/3`. Marginal on `x0`: `0 → 2/3`, `1 → 1/3`.
  `max = 2/3 > 1/2` → **reject**. Belief unchanged.
- **Party 2** symmetric to party 1 → **reject**.

Visible: `[0, ⊥, ⊥]`.

## Invocation 2 — `Q = any_is_2` = `[2 ∈ {x0,x1,x2}]`

Real output on `(0,0,1)`: no coordinate is 2 → **o = 0**.

- **Party 0**. `δ_0` is now the 8-state belief. Condition on `any_is_2 = 0`
  (`x1≠2 ∧ x2≠2`, `x0=0` already): keeps `(x1,x2) ∈ {(0,1),(1,0),(1,1)}` (the
  `(0,0)` state was already gone) → 3 states. Marginal on `x1`: `1 → 2/3`.
  `2/3 > 1/2` → **reject**. Belief unchanged — **stays the 8-state belief, does
  NOT collapse to these 3 states.** This is the property the current `mpc/`
  circuits violate.
- **Party 1**. Rejected in inv1, so `δ_1` is still its 9-state initial. Condition
  on `any_is_2 = 0`: `(x0,x2) ∈ {0,1}²` → 4 states. Marginal on `x0`: `0 → 1/2`,
  `1 → 1/2`. `max = 1/2 ≤ 1/2` ✓ (equality allowed). Marginal on `x2` ✓.
  **Accept**. Sees `0`.
- **Party 2** symmetric → **accept**.

Visible: `[⊥, 0, 0]` — divergence in one invocation: 0 rejects while 1,2 accept.

## What passing this establishes, and what it does not

Establishes: an MPC circuit reproducing these visible outputs and these
belief-state snapshots is functionally faithful to the PLAS transition on this
fixture — including per-recipient divergence and state-preservation on reject.

Does NOT establish: the reject-unobservability property (§4.4). That is not a
function of the state and no functional test can check it.
