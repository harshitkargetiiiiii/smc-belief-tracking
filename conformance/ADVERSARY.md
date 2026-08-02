# Adversary / leakage contract (staged gate 2)

Scope of this phase: the adversary model, the authorized recipients, and PRIVATE
per-recipient delivery of `(accept_j, payload_j)`. Persistent `Sigma_T`
secret-sharing across invocations is the NEXT phase and is out of scope here.

## Parties and threat model

- `N = 3` parties `P_0, P_1, P_2`, semi-honest (honest-but-curious): each follows
  the protocol but tries to learn more from its view. Matches PLAS 2012's model.
- Honest majority, replicated secret sharing over `Z_2^64` (MP-SPDZ Rep3).
- **No collusion** is assumed for the leakage claim below (two colluding parties
  pooling views is out of scope and must be stated as a limitation).

## Authorized recipients

- The query `Q`, domain `D`, and public thresholds are public.
- For each `j`, party `P_j` is the SOLE authorized recipient of its own pair
  `(accept_j, payload_j)`. `payload_j = o_actual` if `accept_j` else a fixed
  `MASK = 0`.
- **No party may learn any other party's `accept_k` or `payload_k`** (PLAS Sec
  4.4: an observed rejection of another party leaks about secrets).
- Belief weights (`Sigma_T`) are secret and are NOT delivered to anyone in this
  phase; they are neither broadcast nor revealed.

## What the private build does

`mpc/threshold_smc_private.mpc` computes the same verdicts as the debug build,
then delivers each pair with `reveal_to(j)` + `print_ln_to(j, ...)`, so only
party `j`'s process prints its own `(accept_j, payload_j)`. Nothing is broadcast;
weights are not output.

## What is DEMONSTRATED vs what is NOT

- **Demonstrated (functional):** running all three parties with per-player output
  (`-OF .`) and capturing each stdout separately, party `j`'s cleartext stream
  contains exactly its own verdict and NO record of any other party
  (`private_run.py`, `test_private.py` incl. a negative control that the checker
  detects a broadcast leak).
- **NOT demonstrated / NOT claimed:** simulation-based security. A functional
  test can catch gross leakage (a broadcast) but cannot prove that a party's full
  protocol view (shares, timing, network) is simulatable from its authorized
  output alone. That requires a protocol-level argument and a human MPC
  specialist. No security claim is made from these tests.
- The `reveal_to`/`print_ln_to` mechanism relies on MP-SPDZ's per-player output
  gating; the guarantee is only as strong as that mechanism and the semi-honest,
  non-colluding assumption.

## Builds

- `threshold_smc.mpc` — DEBUG/CONFORMANCE build: broadcasts verdicts + weights
  via `reveal()` for test-only reconstruction. Used by the UNCHANGED functional
  conformance suite (`harness.py`, `coverage.py`) as the regression gate.
- `threshold_smc_private.mpc` — PRIVATE-DELIVERY build: this phase.

## Next phase (frozen until this clears review)

Persistent `Sigma_T`: keep updated beliefs secret-shared across invocations
without plaintext reconstruction/re-input, with multi-invocation persistence
tests. Not started.
