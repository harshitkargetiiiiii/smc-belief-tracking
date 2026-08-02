# Step-4 notes for adversarial review (no security/performance claims)

The circuit in `mpc/threshold_smc.mpc` passes functional conformance against the
oracle on the pinned fixture (two invocations) and two additional valid states
(`results-step4.txt`). That is ALL that is claimed. This file lists, for the
next reviewer, exactly what is test-only and what is NOT established — so none of
it is mistaken for a security or performance result.

## Private reveals — TEST-ONLY, currently a gross leak

The circuit ends with `print_ln(... .reveal())` for every verdict, payload, and
all 81 updated weights. That reveals the entire state to all parties. It exists
ONLY so the external harness can reconstruct and compare against the oracle.

A deployment MUST NOT do this. Required, and NOT implemented here:

- `accept_j` and `payload_j` are private OUTPUTS to `P_j` alone. In particular
  no other party may learn `accept_j` — §4.4 (a rejection observed by others
  leaks). The current `print_ln` broadcast is the exact violation the mechanism
  forbids; it is present only because this is a conformance build.
- Updated weights must be returned as fresh secret shares of `Sigma_T`, never
  revealed.

So this build establishes functional correctness of the transition, NOT the
privacy property. The privacy property is out of scope for a functional test and
needs a protocol-level argument plus MPC-specialist review.

## Share persistence — NOT implemented; harness carries state in plaintext

The multi-invocation fixture is run as INDEPENDENT circuit executions. Between
inv1 and inv2 the harness takes the circuit's OWN reconstructed updated weights
from inv1 and re-inputs them as fresh secret inputs to inv2 (carried in plaintext
by the harness). The circuit does NOT round-trip `Sigma_T` as persistent secret
shares across invocations.

Consequently the two-invocation result demonstrates per-invocation conformance,
not genuine secret-state persistence. Implementing real `Sigma_T` share
refresh/carry-over across invocations (without reconstruction) is unbuilt and is
part of the attack surface.

## Reject "unchanged weights" — value only, NOT share identity

On reject, `upd[j][idx] = accept_j.if_else(filtered, delta[j][idx])`. MP-SPDZ
compiles arithmetic `if_else(a,b)` as `self*(a-b) + b`, a secret multiplication.
So this establishes equality of the reconstructed **value**, not byte-for-byte
identity of the shares — the multiplication may change the sharing even when the
value is unchanged. **The rejected secret value is unchanged; share
identity/freshness has not been established.** Whether a deployment needs a fresh
re-sharing (share refresh) is a protocol detail for the specialist.

## Encoding assumptions

- The named harness encodes beliefs as dense 0/1 weight vectors (uniform-over-
  support). Non-uniform and per-party-scaled positive integer weights ARE tested,
  by `coverage.py` (228 cases), and pass — so the general integer-weight path is
  covered, not just 0/1.
- `o_actual = Q(secrets)` is computed via a secret one-hot over the 27 states,
  then only released (masked) as `payload`. It is also revealed via the test-only
  weight/payload dump.

## Bit bound

For these inputs, weights are 0/1, `S = 27`, so `Z, M <= 27` and `2*M <= 54 < 2^63`
in the 64-bit signed ring — within the `B < 2^(k-1)` requirement (INTERFACE.md).
No wraparound for this fixture. A general bound for larger `N, D, W` still must be
enforced per INTERFACE.md and is not auto-checked by the circuit.

## Explicitly NOT claimed

- No simulation-based security / privacy claim.
- No claim that the accept/reject decision is unobservable to other parties (the
  test build broadcasts it).
- No performance claim of any kind. No timings taken; none should be read from
  this build.
- No claim of share-persistence correctness across invocations.

## Suggested attack surface for the MPC specialist

1. Replace the broadcast reveals with per-recipient private output; confirm no
   cross-party leakage of verdicts.
2. Implement and verify `Sigma_T` secret-share persistence across invocations.
3. Check comparison bit-length / rounding parameters and any protocol margin
   beyond the `B < 2^(k-1)` value bound.
4. Provide the protocol/security argument for reject-unobservability (§4.4).
