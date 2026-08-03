# Mutation-reproduction evidence (paper artifact)

Reproducible evidence for the adversarial mutation study. **This directory is NOT
part of the frozen conformance artifact** (which stays at repo `305a3a8`); it
supports the manuscript only. It adds no functionality and changes no gate.

## Accounting

- **B0** — one motivating *stdout* failure (a public `reveal()` that a
  transcript-only checker accepted).
- **B1–B6** — six *compiled-delivery* mutations.
- **S1** — one *semantic* mutation (correct recipient, wrong delivered value).

## What maps to a committed control, and what does not

The five committed negative controls live in the frozen artifact under
`conformance/mpc/` and do **not** map one-to-one to the rows:

| row | committed control | note |
|-----|-------------------|------|
| B0 | `threshold_smc_leaky.mpc` | |
| B1 | `threshold_smc_subleak.mpc` | |
| B2 | `threshold_smc_namespoof.mpc` | |
| B3 | `threshold_smc_openfalse.mpc` | **shared with B4** |
| B4 | `threshold_smc_openfalse.mpc` | **same file as B3** |
| B5 | `threshold_smc_openfalse_vec.mpc` | |
| B6 | *(none)* — reconstructed here: `threshold_smc_callarg.mpc` | |
| S1 | *(none)* — reconstructed here: `threshold_smc_wrongsem.mpc` | |

## Precise outcomes (see `detection_matrix.json` for machine-readable data)

Against the **final** linter (`conformance/delivery_inspect.py` @ `305a3a8`,
rules a–h) with MP-SPDZ pinned at `9d809599…`:

- **B0–B5** are **REJECTED** by the final linter (they defeated *earlier* linter
  versions; each was then closed — see `docs/review-log.md` R-41…R-46).
- **B6** (`threshold_smc_callarg.mpc`) routes party 1's verdict through the
  `call_tape`/`call_arg` register channel. Its naive realization via
  `@function_tape` is itself **REJECTED** (it adds a tape → multiset rule; the
  MP-SPDZ call frame also spills via memory → rules g,h). **B6 is therefore NOT a
  demonstrated bypass of the final linter.** Its point is precise: the honest
  build passes *secret comparison operands* across the tape boundary via
  `call_tape`/`call_arg` (reproduce below), so a blocklist forbidding that channel
  would reject the honest build. The `call_arg` channel **cannot be closed by an
  opcode/channel blocklist** without rejecting the honest build; this is **not** a
  claim that no stronger analysis can distinguish the flows — an operand-sensitive
  type system, verified IR, or dataflow analysis could.
- **S1** (`threshold_smc_wrongsem.mpc`) drops the reject-mask (delivers
  `o_actual` even on reject). It **PASSES** the delivery linter (structure intact)
  but **FAILS** the oracle: on `secrets=(0,0,0)`, `p1_is_max`, the true output is
  `1`, all parties reject (oracle payload `0`), yet S1 delivers `1` to all three.
  The delivery linter is semantics-blind.

## Reproduce

```
# MP-SPDZ at the pin (compiler only; the C++ runtime is not needed for linting)
git clone https://github.com/data61/MP-SPDZ && cd MP-SPDZ \
  && git fetch --depth 1 origin 9d809599ea6ce627216a389ca7d984fbb75d0cb9 \
  && git checkout 9d809599ea6ce627216a389ca7d984fbb75d0cb9

# honest build uses call_tape/call_arg to pass secret operands across tapes:
cp <repo>/conformance/mpc/threshold_smc_private.mpc Programs/Source/
./compile.py -R 64 -a asm_honest threshold_smc_private p1_is_max
grep -H "call_tape\|call_arg" asm_honest-threshold_smc_private-p1_is_max-*

# run the final linter on any mutation (drive conformance/delivery_inspect.py):
#   compile_manifest(stem, 'p1_is_max', prefix) -> is_private_manifest(man, EXPECTED_SUBTAPES)
```

Assembly hashes in `detection_matrix.json` are `manifest_signature()` (sha256 over
the full normalized per-tape assembly). This reproduction is compiler + linter +
oracle only; B0–B5 runtime rejection is covered by prior CI evidence
(`conformance/_evidence/`).
