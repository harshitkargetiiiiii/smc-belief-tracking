# STATUS (2026-08-02, gate 2 re-review-2 fixes: private delivery)

Gate 2's first fix was REFUTED AGAIN (issue #5) with two bypasses; both closed in
one commit. Sigma_T persistence remains UNAUTHORIZED. Conformance suite + evidence
gate UNCHANGED.

Bypasses closed:

- **Separate-tape leak** (blocker 1): the old inspector read only the MAIN tape,
  so a build with a clean private main tape plus a separate `@function_tape` doing
  a public `reveal()` + `print_ln('LEAK ...')` passed. Now `delivery_inspect.py`
  inspects the COMPLETE tape manifest (main `privateoutput` to [0,0,1,1,2,2] + no
  public open; every non-main tape an allowlisted masked EQZ/LTZ subtape; no
  unconditional cleartext print in ANY tape) and hashes the whole manifest into
  the delivery signature. `threshold_smc_subleak.mpc` reproduces the leak and is
  REJECTED, alongside `threshold_smc_leaky.mpc`.
- **Exact two-line stdout** (blocker 2): `strict_parse_party` no longer skips
  non-verdict lines. A correct party's stdout is exactly two non-empty own PRIV
  lines (framework noise is on stderr), so any extra/leak line fails closed.
- **Forged bound record** (blocker 3): `validate_private` is now a typed
  exact-schema validator — exact field set + types (unknown field / bool-as-int rc
  rejected), re-parses each retained party stdout with the strict parser, checks
  the ring command + channel string semantically, and under `--recompute` (CI)
  requires each record's `source_sha256` and `delivery_sig` to equal values
  recomputed independently from the checked-out source + a fresh compile.
- `ADVERSARY.md` updated: complete-manifest binding, exact two-line, recomputed
  bindings, and a `tls_certs_present` caveat (cert presence != encrypted wire).
- Tests: 77 in `conformance/` (46 functional conformance + 31 private-gate), all
  green; `reference/` suite unchanged. Functional + compiled-delivery only; NOT a
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
