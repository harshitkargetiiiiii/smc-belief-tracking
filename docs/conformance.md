# STATUS (2026-08-02, step 4 hardened after round 5)

Step 4 circuit PASSES functional conformance; round-5 review confirmed the
functional core (reviewer ran 218 cases independently) and flagged harness/
provenance/wording defects, now fixed.

- `conformance/mpc/threshold_smc.mpc` — smallest circuit (two specialized query
  tables; NOT a general Q compiler). Header no longer claims private delivery.
- `conformance/mpc_run.py` — STRICT core: fail-closed on non-zero exit (keeps
  stderr); parser requires exactly one ACCEPT/PAYLOAD per party and one W per
  (party,idx), rejects duplicates/missing/out-of-range/malformed.
- `conformance/harness.py` — 4 named cases (fixture carried inv1->inv2 + 2 extra).
- `conformance/coverage.py` — 228 cases: all 27 secrets x both queries x
  {uniform, non-uniform, per-party-scaled}, near-tight bit-bound encodings, and
  carried query-pair transitions. All compared to the independent oracle.
- `conformance/results-step4.txt`, `results-coverage.txt` — raw: 4/4 and 228/228,
  each stamped with MP-SPDZ commit 9d809599...
- CI `conformance-mpc` job pins MP-SPDZ to 9d809599..., verifies HEAD==pin,
  runs harness + coverage, retains logs.
- `NOTES.md` — reject preserves VALUE not share identity (if_else = self*(a-b)+b);
  private delivery NOT implemented (build broadcasts, a test-only Sec 4.4 leak).

Functional conformance only. No security or performance claim. Next targets
(NOT started): private per-recipient delivery; Sigma_T share persistence.

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
