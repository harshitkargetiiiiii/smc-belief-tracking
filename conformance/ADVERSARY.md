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

1. **Compiled delivery inspected by CONTENT, not tape NAME**
   (`delivery_inspect.py`): re-review-2 keyed the masked-subtape allowlist on the
   tape-name substring `(EQZ|LTZ)\(`, but an author controls tape names
   (`program.new_tape(fn, name='EQZ(spoof)')` writes the name verbatim), so a
   subtape delivering another party's verdict to the WRONG player and writing it
   to a file slipped through. The inspector now binds on CONTENT across the whole
   manifest: `privateoutput` only in main with players `[0,0,1,1,2,2]` (none in
   any subtape); NO public open-to-all (an open with the `True` flag) in ANY tape
   — the masked comparison opens carry the `False` flag; NO cleartext/file/socket
   sink (`print_*` / `intoutput` / `writesocket*` / …) anywhere except guarded
   `cond_print_*` in main; and every non-main tape must be a compiler-generated
   masked comparison tape matching `^(EQZ|LTZ)\(\d+\)_\d+$`. A digit-named spoof is
   still caught by the content rules even though its name matches.
   `manifest_signature` now hashes the FULL normalized assembly of every tape.
   THREE committed negative controls are REJECTED: `threshold_smc_leaky` (public
   `reveal()` in main), `threshold_smc_subleak` (separate `@function_tape` public
   reveal + `print_ln`), and `threshold_smc_namespoof` (name-spoofed subtape
   delivering party 1's verdict to player 0 via `privateoutput` + a file sink).
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
   passes. `--recompute` also binds each record to a CANONICAL case: it recomputes
   the `input_hash` and the plaintext-oracle `(ACCEPT, PAYLOAD)` for the pinned
   case set and requires a bijection — rejecting replayed duplicate records
   (distinct `case_id`s over one real record), an `input_hash` not tied to a
   canonical case, and any verdict value that disagrees with the oracle.

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
- `threshold_smc_namespoof.mpc` — INTENTIONALLY LEAKY negative control #3: a
  separate tape named `EQZ(spoof)` (via `program.new_tape(name=...)`) delivers
  party 1's verdict to player 0 through `privateoutput` and a `binary_output()`
  file sink — no stdout. Committed so the gate can prove CONTENT-based inspection
  rejects a leak the name-based allowlist accepted.

## Next gate (unauthorized until this clears)

Persistent `Sigma_T`: keep updated beliefs secret-shared across invocations
without plaintext reconstruction/re-input, with multi-invocation persistence
tests. Not started.
