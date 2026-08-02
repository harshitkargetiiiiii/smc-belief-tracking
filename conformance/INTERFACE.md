# Step-4 interface (defined BEFORE coding the circuit)

Per round-4 review (issue #3): fix the MPC interface before writing any circuit,
so "conformance" cannot be met by a circuit with the fixture baked in.

## Compile-time public

- Number of parties `N`, domain `D`.
- The query `Q` (public, and chosen independently of secrets). A circuit
  specialized to one public `Q` is acceptable — that is Futamura specialization
  of a *public* program, not the refuted claim-3 argument.
- Thresholds `t_i` MAY be public (the paper allows public thresholds). If taken
  public they are compile-time; if taken secret they move into `Sigma_T`.

## Runtime secret-shared (Sigma_T, §4.5)

Never compiled in:

- the secrets `s_1..s_N`,
- the current beliefs `delta_1..delta_N`,
- (if secret) the thresholds.

`Sigma_T` enters as secret shares and the circuit returns fresh secret shares of
the updated `Sigma_T`.

## Outputs

- Each recipient `P_j` privately receives its authorized output `o` or `reject`.
- No party learns any other party's accept/reject decision (§4.4). A functional
  test cannot prove this; a public `reveal()` of the verdict is a gross violation
  a test/inspection CAN catch, and must be treated as a hard failure.

## Anti-cheating requirement for the conformance test

- The secrets, current beliefs, and expected output vector MUST enter as runtime
  inputs, never as compiled-in constants. A circuit that hard-codes `(0,0,1)` or
  the expected `[0,0,reject]` is not an implementation.
- The conformance harness MUST run at least one ADDITIONAL secret/state input
  beyond the fixture (e.g. a second secret vector with an independently computed
  oracle result) so that a constant-output circuit cannot pass by accident.
- The circuit's returned updated shares, when reconstructed (test-only), must
  equal the oracle's post-invocation state — including the unchanged state on
  reject.

## What passing still does NOT establish

Reject-unobservability (§4.4). That is an information-flow property; it needs a
protocol-level argument and a human MPC specialist, not a functional match.
