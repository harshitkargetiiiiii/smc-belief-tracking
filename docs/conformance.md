# STATUS (2026-08-02, staged gate 2 started: private delivery)

Issue #4 (functional conformance + evidence gate) PASSED review. Now in staged
gate 2: adversary/leakage contract + PRIVATE per-recipient delivery. Sigma_T
persistence is the NEXT gate and is FROZEN until private delivery clears review.

- `conformance/ADVERSARY.md` — threat model, authorized recipients, what is
  demonstrated (functional) vs NOT claimed (simulation security).
- `conformance/mpc/threshold_smc_private.mpc` — private build: each
  (accept_j, payload_j) delivered only to P_j via reveal_to(j)+print_ln_to(j);
  nothing broadcast; weights not output.
- `conformance/private_run.py` — launches 3 parties with per-player output,
  captures each stdout, asserts party j learns only its own verdict and nothing
  about others. `results-private.txt`: PRIVATE DELIVERY OK.
- `conformance/test_private.py` — 5 unit tests incl. a negative control proving
  the checker DETECTS a broadcast leak (passing check is not vacuous).
- The DEBUG build `threshold_smc.mpc` and the functional conformance suite
  (`harness.py`, `coverage.py`, evidence gate) are UNCHANGED as the regression gate.

Still no security or performance claim; functional demonstration only.

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
