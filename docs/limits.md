# Fundamental limit: automated non-leakage certification of private delivery

## What we set out to do

Gate 2 aims to show that the private-delivery build (`threshold_smc_private.mpc`)
delivers each recipient's `(accept_j, payload_j)` privately — no party learns
another party's verdict — and to check this AUTOMATICALLY in CI by inspecting the
compiled MP-SPDZ assembly (`conformance/delivery_inspect.py`).

## The finding

**A static, opcode-level inspection of the compiled circuit cannot SOUNDLY certify
non-leakage against an adversary who controls the `.mpc` source.** It can only act
as a LINTER that catches gross or accidental leaks. This was established
empirically by six consecutive adversarial re-reviews on issue #5, each producing a
concrete build that leaked a verdict yet passed the then-current gate.

## Why (the theory)

Two facts combine to defeat any purely syntactic gate:

1. **Masked and raw opens are the same opcode.** A public reveal compiles to
   `asm_open`/`vasm_open`; the `True`/`False` flag only controls a post-open
   correctness check, not privacy. The comparison library legitimately opens
   MASKED (blinded) intermediates with the same opcode. Whether an open is "safe"
   depends on whether its operand is masked — a DATAFLOW property invisible at the
   opcode level.

2. **A secret can reach a subtape's open through channels the honest code uses.**
   The verdict is computed in the MAIN tape and can be moved into a comparison
   subtape (where an open lives) via:
   - MEMORY — a MAIN `store` + a subtape `load` (scalar / gf2n / vectorized:
     `stm*` / `ldm*` / `vstms` / `vldms`); and
   - REGISTER ARGUMENTS — `call_tape` in MAIN passing registers to a subtape that
     receives them via `call_arg`. This is EXACTLY how the real EQZ/LTZ comparison
     subtapes receive their operands, so the channel cannot be forbidden.

   Forbidding the memory channel (re-review-5/6) still leaves the register-argument
   channel (re-review-7). Enumerating channels is a losing game; the root gap is
   the masked-vs-raw indistinguishability in (1).

## The bypass sequence (the empirical demonstration)

Each was reproduced end-to-end, then closed — except the last, which prompted this
scoping decision.

| # | round | bypass | why it passed the then-current gate |
|---|-------|--------|-------------------------------------|
| 1 | rr-2 | separate `@function_tape` public reveal + print | inspector read only the MAIN tape |
| 2 | rr-3 | name-spoofed subtape (`EQZ(spoof)`): wrong-player `privateoutput` + file sink | masked allowlist trusted tape NAMES |
| 3 | rr-4 | `reveal(False)` — a False open is still a public reveal | gate treated `False` opens as safe |
| 4 | rr-5 | `reveal(False)` in an EXISTING `EQZ(3)_63` body, multiset intact | multiset pins names/counts, not bodies |
| 5 | rr-6 | vectorized `vstms`/`vldms` memory transfer | memory regex was scalar-only |
| 6 | rr-7 | `call_tape`/`call_arg` register transfer (no memory) | a memory rule cannot see the register channel |

## What the linter DOES provide (kept)

- Rejects five committed executable negative controls:
  `threshold_smc_{leaky,subleak,namespoof,openfalse,openfalse_vec}.mpc`.
- Catches gross / accidental leaks and regressions: any MAIN-tape public open,
  wrong-player `privateoutput`, cleartext/file/socket sink, author-introduced
  tape, unexpected memory store, etc.
- Layers 2-3 — the strict runtime transcript check and the typed, recomputed,
  SHA-bound evidence validator — remain SOUND for what they check; they are
  independent of the compiled-assembly limitation above.

## What a real non-leakage guarantee requires (out of scope here)

- A protocol-level Rep3 simulation argument by a human MPC specialist; OR
- A formally-verified comparison primitive plus a dataflow analysis proving every
  `open`'s operand is masked and that no verdict-derived register flows into any
  open.

`ADVERSARY.md` states this in "NOT claimed"; `delivery_inspect.py` and
`private_run.py` print a LINTER caveat at runtime; and the `Sigma_T` persistence
gate remains unauthorized.
