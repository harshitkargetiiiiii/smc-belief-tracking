# STATUS (2026-08-02, step 4 built)

Steps 1-3 cleared review (issue #2, #3). Step 4 (smallest threshold_SMC circuit)
BUILT and passing FUNCTIONAL conformance; security/persistence NOT done.

- `conformance/mpc/threshold_smc.mpc` — smallest circuit, N=3, D={0,1,2}, t=1/2,
  64-bit ring, one public query per specialization. All-outputs check b*M<=a*Z,
  per-recipient (accept,payload) with fixed reject mask, filtered-on-accept /
  unchanged-on-reject weights.
- `conformance/harness.py` — external harness; expected results live only here,
  never enter the circuit. Runs the pinned fixture (2 invocations) + 2 extra
  valid states; compares verdicts, payloads, reconstructed weights to the oracle.
- `conformance/results-step4.txt` — raw output: 4/4 PASS.
- `conformance/NOTES.md` — what is TEST-ONLY and NOT established: private reveals
  (the build broadcasts verdicts — a §4.4 violation, present only for the test),
  no Sigma_T share persistence (harness carries state in plaintext between
  invocations), no security or performance claim.

Open for adversarial review (issue #4). NO security or performance claims.

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
