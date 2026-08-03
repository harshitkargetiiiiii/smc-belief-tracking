# STATUS (2026-08-02, gate 2 re-review-5 fixes: private delivery)

Re-review-5: pinning the tape multiset caught an added/duplicate open tape, but a
`reveal(False)` injected INTO an existing expected `EQZ(3)_63` slot (multiset
untouched) still leaked. Closed by binding the MEMORY channel. Sigma_T persistence
remains UNAUTHORIZED. Conformance suite + evidence gate UNCHANGED.

Delivery inspection (`delivery_inspect.py`) binds on CONTENT, a pinned tape
multiset, AND the memory channel, with NO reliance on the open flag:

- `privateoutput` only in main with players [0,0,1,1,2,2] (none in any subtape);
  NO file/socket/print sink outside guarded `cond_print` in main; every non-main
  tape must match `^(EQZ|LTZ)\(\d+\)_\d+$`; the non-main tape base multiset must be
  EXACTLY {EQZ(3)_63, EQZ(81)_63, LTZ(36)_64}; and — the load-bearing rule (rr-5) —
  the MAIN tape performs NO memory STORE and every subtape touches memory NOT AT
  ALL. The verdict is a MAIN register and a cross-tape register reference is a
  compiler error, so the only channel by which it can reach a subtape's open is
  MAIN store → subtape load; the clean build uses neither. `manifest_signature`
  hashes the full assembly.
- FOUR committed negative controls are rejected: `threshold_smc_leaky` (public
  reveal in main), `threshold_smc_subleak` (separate-tape reveal + print),
  `threshold_smc_namespoof` (name-spoofed wrong-player delivery + file sink), and
  `threshold_smc_openfalse` (a `reveal(False)` in a spoofed `EQZ(3)_63` subtape).

Evidence binding (re-review-3, still in force): `validate_evidence.py --recompute`
binds each record to a canonical case (recomputed `input_hash` + oracle
`(ACCEPT, PAYLOAD)`, bijection required) and to a recomputed source/delivery
signature — rejecting replay, unbound `input_hash`, forged verdict values, and
forged bound records. `compile_manifest` clears stale assembly before compiling.

Tests: 90 in `conformance/` (46 functional conformance + 44 private-gate), all
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
