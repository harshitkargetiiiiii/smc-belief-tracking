# STATUS (2026-08-02, gate 2 re-review fixes: private delivery)

Gate 2 was REFUTED (issue #5): the stdout checker passed a public-open circuit.
Fixed. Sigma_T persistence remains UNAUTHORIZED. Conformance suite + evidence
gate UNCHANGED.

- Compiled-delivery inspection (`delivery_inspect.py`): the private build's main
  tape delivers 6 verdicts via `privateoutput`; the committed leaky sibling
  (`threshold_smc_leaky.mpc`, reveal()) `asm_open`s them and is REJECTED. The
  executable public-open negative control a stdout oracle could not provide.
- Strict per-party parser (`private_run.py`): exactly one own ACCEPT+PAYLOAD;
  duplicate/foreign/unknown/missing -> fail closed. Reviewer's attacks pinned.
- Bound raw evidence: per case, each party's raw stdout/stderr/rc/cmd, source
  hash, delivery signature, provenance, TLS status; validated
  `validate_evidence.py --private` (fail-closed, --require-bound in CI).
- `ADVERSARY.md` corrected: standard ideal-functionality (no ADDITIONAL info),
  one corruption / no collusion / encrypted channels / host isolation,
  reveal_to vs print_ln_to separated, "no unmasked open" wording,
  demonstrated-vs-not-claimed downgraded.
- Tests: 64 conformance / 89 total. Functional + compiled-delivery only; NOT a
  simulation-security proof.

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
