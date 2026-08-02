# STATUS (2026-08-02, round 3 correction)

Steps 1-3 REDONE after round-3 review refuted the first attempt; step 4 (MPC)
NOT started.

Round-3 finding (issue #2): `tcheck` must quantify over ALL POSSIBLE outputs
(Fig. 4 line 2), not the actual output. The first oracle checked only the actual
output — a different, leak-prone functionality. Fixed.

- Step 1: `conformance/CONTRACT.md` — corrected quantifier, Fig. 4 quoted,
  added clauses (deterministic scope, public queries, prior consistency,
  0<t<=1, §4.5 sharing). Citations still need a human PDF check.
- Step 2: fixture `sum_even` then `p1_is_max`, secrets (0,0,1), t=1/2 — shows
  divergence and reject-state-preservation. PLUS a discriminating single-shot
  example that distinguishes all-outputs from actual-only.
- Step 3: `conformance/oracle.py` + `test_conformance.py`, 9 hand-derived
  assertions. The centerpiece asserts the correct and buggy decisions DIFFER, so
  a revert to actual-only fails the suite.
- Step 4: NOT started.

Original target spec follows.

---

# Conformance target

The gate any future attempt must pass **before** any performance work.
Specified per the round-2 review; not implemented.

Rationale: CI automates a defined functionality, it cannot define one.
Comparing the MPC circuit against `reference/` would only confirm that two
non-conforming models agree — `reference/` implements our model (single
observer, no persistent state, no rejection semantics), not PLAS.

## Step 1 — transcribe the contract

From PLAS 2012 Figures 8-9 and SS4.4-4.5. The state transition and leakage
contract, written out explicitly:

- Beliefs for **every** observer/target pair `(j, i)` with `i != j`, not one pair
- Persistent secret-shared state `Sigma_T` returned as new shares each invocation
- Output or rejection released **privately to the intended recipient**; whether
  `P_j` received output or reject must not be observable by other participants
- State **unchanged** on rejection
- Per-invocation accept/reject decision computed inside the MPC

Each bullet needs a citation to the specific figure or section it comes from.
Anything not traceable to the paper does not belong in the contract.

## Step 2 — a tiny deterministic fixture

Three parties, domain size 2 or 3 — small enough to enumerate and verify by
hand. At least two invocations:

1. one accepted update
2. one **rejected** update

For each transition, specify:

- the recipient-visible outputs
- the reconstructed (test-only) state afterwards

The rejection case is the important one. It exercises state-preservation and
the privacy of the reject decision — the two properties the current circuits
violate.

## Step 3 — an independent plaintext oracle

Written **independently of the MPC code**, not derived from it, not sharing
helpers with `reference/`. If the oracle is written by transcribing the
circuit, it tests nothing.

## Step 4 — the smallest MPC circuit that realizes the fixture

Not a general implementation. The minimum that hits the fixture exactly.
Compare test-only reconstructed state and authorized outputs against the oracle.

## Only then

Local conformance test passes -> put it in CI -> then, and only then, consider
performance measurement.

## Explicitly out of scope until this passes

- Benchmarks of any kind
- Scaling studies
- Network emulation runs
- Anything in `mpc/` as it currently stands
