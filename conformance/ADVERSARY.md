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
  **Caveat (do not overread `tls_certs_present`):** that flag records only that
  N certificate files EXIST on disk. It is NOT proof that the runtime negotiated
  or used encryption. That the channels are in fact TLS is INFERRED from the
  pinned backend's default (`replicated-ring-party.x` at the pinned MP-SPDZ
  commit uses authenticated TLS sockets by default) plus the recorded launch
  command (no flag disables it). The evidence does not packet-capture the wire.
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

1. **Compiled delivery over the COMPLETE tape manifest** (`delivery_inspect.py`):
   the private build's MAIN tape delivers the six verdicts via `privateoutput` to
   players `[0,0,1,1,2,2]` with no public open, AND every other generated tape is
   an allowlisted masked-comparison subtape (EQZ/LTZ) — no public open and no
   UNCONDITIONAL cleartext print (`print_reg_plain`/`print_char*`) may appear in
   ANY tape. Two committed negative controls are REJECTED: `threshold_smc_leaky`
   (`reveal()` opens the verdicts in the main tape) and `threshold_smc_subleak`
   (main tape is byte-identical to the private build, but a separate
   `@function_tape` does a public `reveal()` + `print_ln('LEAK ...')`). The
   earlier main-tape-only inspector accepted the subleak; inspecting the whole
   manifest, and hashing it into the delivery signature, rejects it.
2. **Strict runtime, exact two lines** (`private_run.py`): a correct party's
   captured STDOUT is exactly two non-empty lines — one own `ACCEPT`, one own
   `PAYLOAD`. Framework diagnostics go to stderr, so the parser skips NOTHING:
   every non-empty stdout line must be a well-formed own `PRIV` record and there
   must be exactly two. A duplicate / foreign-index / unknown / missing record,
   or ANY extra line (an unconditional public `LEAK`), fails closed.
3. **Typed, bound, recomputed raw evidence**: per case, each party's raw
   stdout/stderr, return code, command, source hash, delivery signature,
   provenance, and TLS status are retained and validated
   (`validate_evidence.py --private --recompute`). The validator enforces an EXACT
   field set + types (an unknown field, or a bool where an int return code is
   required, is rejected), re-parses each retained party stdout with the strict
   two-line parser, checks the launch command and channel string semantically,
   and — under `--recompute` in CI — requires each record's `source_sha256` and
   `delivery_sig` to equal values recomputed independently from the checked-out
   source and a fresh compile. A hand-forged "all-flags-true" record no longer
   passes.

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
- `threshold_smc_leaky.mpc` — INTENTIONALLY LEAKY negative control #1: `reveal()`
  opens the verdicts publicly in the MAIN tape. Committed so the gate can prove it
  rejects public opening.
- `threshold_smc_subleak.mpc` — INTENTIONALLY LEAKY negative control #2: the MAIN
  tape is byte-identical to the private build, but a separate `@function_tape`
  publicly `reveal()`s and `print_ln('LEAK ...')`s each verdict. Committed so the
  gate can prove complete-manifest inspection rejects a leak the main-tape-only
  check missed.

## Next gate (unauthorized until this clears)

Persistent `Sigma_T`: keep updated beliefs secret-shared across invocations
without plaintext reconstruction/re-input, with multi-invocation persistence
tests. Not started.
