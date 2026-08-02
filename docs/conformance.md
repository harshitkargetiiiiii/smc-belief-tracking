# STATUS (2026-08-02, gate 2 re-review-3 fixes: private delivery)

Gate 2's re-review flagged more evidence-binding gaps, and an independent
adversarial pass found a CRITICAL name-spoof leak; all closed in one commit.
Sigma_T persistence remains UNAUTHORIZED. Conformance suite + evidence gate
UNCHANGED.

Bypasses closed:

- **Name-spoof subtape leak (CRITICAL)**: `program.new_tape(fn, name='EQZ(spoof)')`
  writes the tape name verbatim, so a subtape delivering party 1's verdict to
  player 0 via `privateoutput` + a `binary_output()` file sink passed the old
  name-based allowlist (verified end-to-end — it was ACCEPTED). `delivery_inspect.py`
  now binds on CONTENT across the whole manifest: `privateoutput` only in main with
  players [0,0,1,1,2,2] (none in any subtape); NO public open-to-all (the `True`
  open flag) anywhere — masked comparison opens carry `False`; NO file/socket/print
  sink outside guarded `cond_print` in main; every non-main tape must match the
  strict compiler pattern `^(EQZ|LTZ)\(\d+\)_\d+$`. A digit-named spoof is still
  caught by the content rules. `threshold_smc_namespoof.mpc` is a committed
  executable negative control.
- **Signature collision**: `manifest_signature` now hashes the FULL normalized
  assembly of every tape (was a 4-pattern subset that collided on injected sinks).
- **Replay / unbound input_hash / unchecked verdict values**: under `--recompute`
  the validator binds each record to a canonical case — recomputing `input_hash`
  and the plaintext-oracle `(ACCEPT, PAYLOAD)` from the pinned CASES and requiring
  a bijection. Four clones with distinct `case_id`s, a forged verdict value, and an
  `input_hash` not tied to a canonical case are all rejected.
- **Stale-assembly false rejection**: `compile_manifest` clears stale
  `{prefix}-{stem}-{query}-*` files before compiling, so a cached MP-SPDZ dir can't
  pollute the manifest.
- Tests: 86 in `conformance/` (46 functional conformance + 40 private-gate), all
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
