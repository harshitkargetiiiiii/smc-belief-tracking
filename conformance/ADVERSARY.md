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

1. **Compiled delivery inspected by CONTENT + a pinned tape multiset**
   (`delivery_inspect.py`): re-review-2 keyed the masked-subtape allowlist on the
   tape-name substring; re-review-4 noted that `asm_open(..., False, ...)` is ALSO
   a public reveal (the `False` flag only skips the post-open correctness check,
   not privacy), so a `reveal(False)` of a verdict inside a masked-named subtape
   leaked. A masked open cannot be told from a raw reveal at the opcode level, so
   the inspector binds on CONTENT across the whole manifest AND pins the non-main
   tape multiset: `privateoutput` only in main with players `[0,0,1,1,2,2]` (none
   in any subtape); NO cleartext/file/socket sink (`print_*` / `intoutput` /
   `writesocket*` / …) anywhere except guarded `cond_print_*` in main; every
   non-main tape must match `^(EQZ|LTZ)\(\d+\)_\d+$`; and — the load-bearing rule —
   the non-main tape base multiset must be EXACTLY the pinned comparison subtapes
   `{EQZ(3)_63, EQZ(81)_63, LTZ(36)_64}`. Since an author can only ADD an open
   (removing a real comparison breaks functional conformance), any injected open —
   `True` or `False` — lands in a NEW or DUPLICATE subtape and breaks the multiset.
   `manifest_signature` hashes the FULL normalized assembly of every tape. FOUR
   committed negative controls are REJECTED: `threshold_smc_leaky` (public
   `reveal()` in main), `threshold_smc_subleak` (separate `@function_tape` public
   reveal + `print_ln`), `threshold_smc_namespoof` (name-spoofed subtape delivering
   to the wrong player + a file sink), and `threshold_smc_openfalse` (a
   `reveal(False)` of party 1's verdict in a spoofed `EQZ(3)_63` subtape).
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
- `threshold_smc_openfalse.mpc` — INTENTIONALLY LEAKY negative control #4: a tape
  named `EQZ(3)_63` (a name the real comparison library also emits) publicly
  reconstructs party 1's verdict with `reveal(False)` — no stdout, no sink, no
  `privateoutput`. Committed so the gate can prove the pinned-multiset rule rejects
  a `False` public open that the flag-based check treated as safe.

## Next gate (unauthorized until this clears)

Persistent `Sigma_T`: keep updated beliefs secret-shared across invocations
without plaintext reconstruction/re-input, with multi-invocation persistence
tests. Not started.
