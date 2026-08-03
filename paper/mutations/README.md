# Mutation-reproduction evidence (paper artifact)

Reproducible evidence for the adversarial mutation study. **This directory is NOT
part of the frozen conformance artifact** (which stays at repo `305a3a8`); it
supports the manuscript only and changes no gate.

## Accounting

- **B0** — one motivating *stdout* failure (a public `reveal()` a transcript-only
  checker accepted).
- **B1–B6** — six *compiled-delivery mutation cases*. **They are not homogeneous:**
  - **B1, B2, B3, B5** — committed executable **source** controls.
  - **B4** — a **synthetic compiled-manifest counterexample**, *not* a source `.mpc`
    (see below).
  - **B6** — a **reconstructed source** mutation whose naive realization is itself
    caught (see below).
- **S1** — one *semantic* mutation (correct recipient, wrong delivered value),
  **executed end-to-end**.

## What is committed, and what is not (the five controls are not 1:1 with rows)

| row | kind | artifact |
|-----|------|----------|
| B0 | committed source control | `conformance/mpc/threshold_smc_leaky.mpc` |
| B1 | committed source control | `conformance/mpc/threshold_smc_subleak.mpc` |
| B2 | committed source control | `conformance/mpc/threshold_smc_namespoof.mpc` |
| B3 | committed source control | `conformance/mpc/threshold_smc_openfalse.mpc` (rr-4 **duplicate**-tape build) |
| B4 | **synthetic manifest** | *none* — reconstruct from the private manifest (below) |
| B5 | committed source control | `conformance/mpc/threshold_smc_openfalse_vec.mpc` |
| B6 | reconstructed source | `threshold_smc_callarg.mpc` (here) |
| S1 | reconstructed source | `threshold_smc_wrongsem.mpc` (here) |

**B4 is not B3's control.** `threshold_smc_openfalse.mpc` is the rr-4 build that
adds a **duplicate** `EQZ(3)_63` tape (rejected on the multiset). B4 is the *rr-5*
observation that the multiset rule is blind to tape **bodies**: a `reveal(False)` of
the verdict placed in an **existing** `EQZ(3)_63` body with the three pinned names
intact. R-45 demonstrated this with a **synthetic manifest**, not a source mutation.

## Outcomes vs the final linter (`delivery_inspect.py`@`305a3a8`, MP-SPDZ `9d809599`)

See `detection_matrix.json` for the machine-readable form.

- **B0–B3, B5** — **REJECTED**. They are **compiled and linted, never executed**:
  CI runs the delivery linter over the controls and runs *only the clean private
  build* at runtime. (No claim that CI runtime-tested the controls.)
- **B4** — **REJECTED by the memory rule (h)** with the **multiset intact** (a
  synthetic manifest; never compiled or executed). Reproduce:
  ```python
  # in conformance/, MPSPDZ set to a pinned MP-SPDZ checkout
  import delivery_inspect as di, copy
  man = di.compile_manifest('threshold_smc_private','p1_is_max','asm')
  syn = copy.deepcopy(man); k=[x for x in syn if di._base(x)=='EQZ(3)_63'][0]
  syn[k] += '\nldms s777, 4000\nasm_open 3, False, c0, s777\n'
  di.is_private_manifest(syn, di.EXPECTED_SUBTAPES)   # -> rejected: rule (h), multiset intact
  ```
- **B6** — the naive `call_arg` realization (`threshold_smc_callarg.mpc`) is itself
  **REJECTED** (adds a tape → multiset; MP-SPDZ's call frame also spills via memory).
  **B6 is not a bypass of the final linter.** Its point: the honest build passes
  secret comparison operands across the tape boundary via `call_tape`/`call_arg`, so
  a blocklist forbidding that channel would reject the honest build. The **studied
  opcode-identity / channel-blocklist linter cannot be promoted to a general
  non-leakage checker**; distinguishing legitimate from leaking flows needs analysis
  stronger than opcode/channel identity (operand/provenance-sensitive dataflow,
  typing, verified IR, …), **which we did not evaluate**.
- **S1** (`threshold_smc_wrongsem.mpc`) — **PASSES** the delivery linter and **FAILS
  the oracle, executed end-to-end** at the pin. On `secrets=(0,0,0)`, `p1_is_max`:
  all three parties complete (rc 0) and each delivers `ACCEPT 0 / PAYLOAD 1`, while
  the oracle masks the payload to `0` on reject — a real oracle mismatch at parties
  `[0,1,2]`. Raw per-party stdout, oracle-vs-delivered, source hash, and compile
  command are archived in `s1_runtime_evidence.json`.

## Reproduce (compiler + runtime at the pin)

```
git clone https://github.com/data61/MP-SPDZ && cd MP-SPDZ \
  && git fetch --depth 1 origin 9d809599ea6ce627216a389ca7d984fbb75d0cb9 \
  && git checkout 9d809599ea6ce627216a389ca7d984fbb75d0cb9
make -j replicated-ring-party.x && Scripts/setup-ssl.sh 3   # runtime (needed only for S1)

# honest build uses call_tape/call_arg to pass secret operands across tapes:
cp <repo>/conformance/mpc/threshold_smc_private.mpc Programs/Source/
./compile.py -R 64 -a asm_honest threshold_smc_private p1_is_max
grep -H "call_tape\|call_arg" asm_honest-threshold_smc_private-p1_is_max-*

# S1 end-to-end: compile threshold_smc_wrongsem, write inputs for (0,0,0), run 3 parties.
```

Assembly hashes in `detection_matrix.json` are `manifest_signature()` (sha256 over
the full normalized per-tape assembly).
