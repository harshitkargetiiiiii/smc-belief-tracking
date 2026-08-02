# Adversary / leakage contract (staged gate 2, corrected after re-review)

Scope: adversary model, authorized recipients, and PRIVATE per-recipient
delivery of `(accept_j, payload_j)`. Persistent `Sigma_T` secret-sharing across
invocations is the NEXT gate and is out of scope / unauthorized.

## Parties, corruption, channels

- `N = 3` parties, semi-honest (honest-but-curious). PLAS 2012's model. A party's
  VIEW is its local state plus the messages it sends and receives.
- Replicated secret sharing over `Z_2^64` (MP-SPDZ Rep3), honest majority.
- **At most one corrupted party; no collusion.** Two colluding parties pooling
  views is out of scope.
- **Authenticated, encrypted point-to-point channels (TLS).** Honest-majority
  Rep3 REQUIRES this: MP-SPDZ's own docs warn a network eavesdropper can
  otherwise reconstruct secrets. CI runs `setup-ssl.sh 3`; evidence records
  `tls_certs_present` and the channel assumption per case.
- **Process / host isolation.** NOTE: the test harness runs all three parties as
  one OS user on one host sharing the input directory. That is NOT an
  adversarially isolated deployment; the isolation assumption is stated, not
  enforced by the test.

## Ideal functionality (authorized information)

A corrupted party `P_k` learns **no additional information beyond**: the public
parameters (`Q`, domain, public thresholds), its own input, and its own
authorized output `(accept_k, payload_k)`. Anything `P_k` can logically infer
from those is not — and cannot be — prohibited. `payload_k = o_actual` if
`accept_k` else a fixed `MASK = 0`. This replaces the earlier, wrong phrasing
"no party may learn another party's output."

## Mechanisms (kept separate)

- `reveal_to(j)` is the PRIVATE-OUTPUT protocol: at pinned MP-SPDZ it compiles to
  `privateoutput`, delivering the missing replicated share only to `P_j`.
- `print_ln_to(j, ...)` only gates LOCAL PRINTING; it is not a privacy mechanism.
  A build could `reveal()` publicly and still `print_ln_to(j, ...)` — that is the
  leaky sibling, and it must be REJECTED (see below).

## What is opened vs delivered

- No **unmasked** final verdict, payload, or belief weight is publicly opened.
  (The comparison machinery does have protocol `open`s of MASKED intermediates in
  the EQZ/LTZ subroutines; those are not the final verdicts.)
- The six final verdict wires are delivered via `privateoutput`, one authorized
  pair per party.

## What is DEMONSTRATED (this gate) vs NOT claimed

Demonstrated, executably:

1. **Compiled delivery** (`delivery_inspect.py`): the private build's MAIN tape
   delivers the six verdicts via `privateoutput` to players `[0,0,1,1,2,2]` and
   has NO public open; the intentionally leaky sibling (`reveal()` +
   `print_ln_to`) is REJECTED because its main tape `asm_open`s the verdicts. A
   stdout oracle cannot make this distinction; this compiler-level check can.
2. **Strict runtime** (`private_run.py`): each party's captured stdout contains
   exactly one own `ACCEPT` and one own `PAYLOAD` under a fail-closed parser that
   rejects duplicate / foreign-index / unknown / missing records.
3. **Bound raw evidence**: per case, each party's raw stdout/stderr, return code,
   command, source hash, delivery signature, provenance, and TLS status are
   retained and validated (`validate_evidence.py --private`).

NOT claimed:

- **Simulation-based security.** A functional + compiled-delivery check catches
  gross public opening and cleartext cross-party printing. It does NOT prove that
  a corrupted party's FULL view (shares, timing, network) is simulatable from its
  authorized output alone. That needs a protocol-level Rep3 argument and a human
  MPC specialist. No security claim is made from these tests.
- Any guarantee under collusion, a malicious party, unencrypted channels, or a
  shared-host adversary.

## Builds

- `threshold_smc.mpc` — DEBUG/CONFORMANCE build: broadcasts verdicts + weights
  via `reveal()` for test-only reconstruction. The UNCHANGED functional
  conformance suite uses it as the regression gate.
- `threshold_smc_private.mpc` — PRIVATE-DELIVERY build (this gate).
- `threshold_smc_leaky.mpc` — INTENTIONALLY LEAKY negative control: `reveal()` +
  `print_ln_to`. Committed so the gate can prove it rejects public opening.

## Next gate (unauthorized until this clears)

Persistent `Sigma_T`: keep updated beliefs secret-shared across invocations
without plaintext reconstruction/re-input, with multi-invocation persistence
tests. Not started.
