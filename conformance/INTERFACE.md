# Step-4 interface (defined BEFORE coding the circuit)

Per round-4 review (issue #3): fix the MPC interface before writing any circuit,
so "conformance" cannot be met by an echo circuit or by a functionality PLAS
does not define. Revised after round-4b review.

## Scope of the circuit

Step 4 implements **`threshold_SMC` only**. It takes an already-valid `Sigma_T`
(a valid output of `init_SMC` or of a prior conforming invocation) and one
public query, and returns per-recipient private outputs plus fresh shares of the
updated `Sigma_T`. `init_SMC` is a separate concern, performed by the test
harness (test-only) to construct the input state; it is NOT part of the Step-4
circuit.

The circuit's input-state boundary assumes a valid `Sigma_T`. It does not defend
against attacker-chosen weights; validity is a precondition, stated here so the
precondition is explicit rather than implied.

## Compile-time public

- Number of parties `N`, domain `D`.
- The query `Q` — public AND chosen independently of the secrets. Specializing
  the circuit to one public `Q` is fine (Futamura specialization of a *public*
  program).
- **Thresholds `t_i` are PUBLIC** (Lemma 6: for `i != j`, `t_i` is publicly
  known so `P_j` can simulate whether it will be rejected). Including thresholds
  in `Sigma_T` (§4.5) keeps them fixed across invocations but does NOT make them
  secret. A secret-threshold variant is a *different* functionality with a
  different leakage profile (receiving `reject` could reveal others' thresholds)
  and the Lemma-6 argument no longer applies; it is OUT OF SCOPE here.

## Runtime secret-shared (Sigma_T, §4.5)

Enter as secret shares; fresh shares of the updated state are returned:

- the secrets `s_1..s_N`,
- the current beliefs `delta_1..delta_N`.

(Thresholds are public, so they are not secret-shared; per §4.5 they may still be
carried in `Sigma_T` as public fixed values.)

## Belief representation on the wire

- A dense `D^N` weight vector per party, in a FIXED lexicographic ordering of
  assignments. The plaintext oracle uses a sparse positive-support dict; the
  circuit carries explicit zero weights for absent states. The harness
  translates sparse-dict <-> dense-vector in that fixed order.
- **Unnormalized non-negative integer weights.** Normalization is deferred: two
  states are semantically equal iff their weight vectors are proportional
  (`w == c * w'` for some positive rational `c`), compared per party.
- Threshold check without division: for public `t_i = a/b` and marginal sum `M`
  over total `Z`, compare `b * M <= a * Z`.
- **Signed no-wraparound bound.** MP-SPDZ integer comparison is SIGNED: in a
  `2^k` ring, values `>= 2^(k-1)` are read as negative. So the requirement is

      B < 2^(k-1)   where  B = max(a,b) * S * W   (S = D^N, per-state weight <= W)

  NOT the earlier `2^k > B`, which is wrong (counterexample: `k=7`, `B=120`
  passes `128 > 120` but `b*M = 70` reads as `-58`, flipping a reject into an
  accept — see `test_circuit_spec.py::test_naive_bound_is_wrong_for_signed_comparison`).
  `B` must bound EVERY compared operand AND every intermediate in the secret
  evaluation of `Q`, with a compatible comparison `bit_length` and any
  protocol-specific margin. For the fixture (`N=3, |D|=3, S=27, W=1, t=1/2`):
  `B = 54`, so a 64-bit signed ring is vastly sufficient.

## Output alphabet — public, secret-support-safe (§4.4 leakage)

The circuit MUST iterate the PUBLIC compile-time alphabet `O_Q = {Q(s) : s in
D^N}`, never the secret support. A branch impossible under the actual belief has
`Z = 0`; with non-negative weights every `M = 0`, so `b*M <= a*Z` is `0 <= 0` =
pass. Iterating `O_Q` therefore yields the SAME decision as iterating the secret
support (proved in `test_circuit_spec.py::test_public_alphabet_matches_support_decision`)
with no secret-dependent branching. Never reveal `Z`, and never branch publicly
on whether `Z > 0`.

## Outputs

- Each recipient `P_j` privately receives a `(accept_j, payload_j)` pair, with
  an ENFORCED fixed mask on reject:

      payload_j = o_actual if accept_j else MASK      (MASK a fixed constant, e.g. 0)

  "Ignored by construction" is insufficient — the payload the recipient receives
  must be independent of `o_actual` on reject (pinned in
  `test_circuit_spec.py::test_reject_payload_is_fixed_and_output_independent`).
  Only `(accept_j, payload_j)` is revealed to `P_j`.
- No party learns any other party's `accept_j`. A functional test cannot prove
  this; a public `reveal()` of any verdict is a gross violation that inspection
  MUST reject as a hard failure.

## The conformance harness (anti-cheating)

- The **expected outputs and expected post-state NEVER enter the circuit** —
  not compiled in, not as runtime inputs. They exist only in the external test
  harness, which obtains them independently from the oracle and compares them
  against the circuit's test-only reconstructed results. (Round-4b: runtime
  injection of the expected vector is as invalid as compiling it in.)
- Inputs to the circuit are exactly: public `(N, D, Q, t_i)` and secret-shared
  `(secrets, beliefs)`.
- The harness MUST run at least one ADDITIONAL secret/state input beyond the
  fixture, with an independently computed oracle result, so a constant-output
  circuit cannot pass by accident.
- Reconstructed updated shares (test-only) must equal the oracle's
  post-invocation state under the proportional-weight equality above — including
  unchanged state on reject.

## What passing still does NOT establish

Reject-unobservability (§4.4): an information-flow property needing a
protocol-level argument and a human MPC specialist, not a functional match.
