# CROSS-VERSION — MP-SPDZ replication of the paper-critical backend observations

We tested whether the backend facts the paper depends on hold on **one additional
MP-SPDZ version** beyond the pin. We made **no compatibility claim in advance** and
tested **only** the paper-critical observations (not the full artifact, not
performance). Frozen artifact code (`conformance/delivery_inspect.py`, the oracle)
was used unmodified; only the MP-SPDZ backend was swapped.

## Versions

| | commit | how obtained | build |
|---|---|---|---|
| **Pinned** | `9d809599` | `git fetch origin <pin>` on a fresh clone | `make -j2 replicated-ring-party.x`, **151 s**, clean |
| **Cross** | **v0.4.3** = `26a60536` | `git clone --depth 1 --branch v0.4.3` | same command, **142 s**, clean |

Both build with the same toolchain (clang 18.1.3, `-O3 -std=c++20`, MP-SPDZ default
`CONFIG`). We did **not** verify git ancestry (shallow clones); v0.4.3 is the latest
tagged stable release, distinct from the pin. Probes used query `p1_is_max` (the
discriminating S1 case); compilation used `./compile.py -R 64 -a <prefix> <stem> p1_is_max`.

## Compile / API changes (recorded separately from semantics)

**None observed.** `compile.py` accepted the identical invocation; the compiled
tape manifest had the **same structure and the same subtape names**
`{EQZ(3)_63, EQZ(81)_63, LTZ(36)_64}` on both versions — so even the frozen linter's
pinned-multiset rule still matches v0.4.3 (it did not have to). No flag, opcode-name,
or manifest-shape change surfaced in what we exercised.

## Paper-critical observations (pinned vs v0.4.3)

| # | Observation (paper) | Pinned `9d809599` | v0.4.3 `26a60536` | Replicates? |
|---|---|---|---|---|
| (a) | legitimate comparison opens and raw reveals compile through the **same open-instruction family** | masked opens: `vasm_open`; raw reveal (leaky control): `asm_open`/`vasm_open` | **identical** | **YES** |
| (b) | honest build uses **`call_tape`/`call_arg`** for secret comparison operands | main **3× `call_tape`**; subtapes **3× `call_arg`**; no memory | **identical** | **YES** |
| (c) | the **B6** reconstructed mutation exhibits the same mechanism | adds a `_leak` tape via the call mechanism → frozen linter **REJECTS** | **identical** (adds `_leak`; REJECTED) | **YES** |
| (d) | **S1** still passes the delivery linter structurally and, when executed, produces the same semantic/oracle mismatch | linter **PASS** (3 pinned subtapes); runtime: `ACCEPT 0 / PAYLOAD 1` to all; oracle payload `0`; **mismatch `[0,1,2]`** | **identical** (linter PASS; same runtime mismatch) | **YES** |
| — | (bonus) honest comparison-subtape **multiset** | `{EQZ(3)_63, EQZ(81)_63, LTZ(36)_64}` | **identical** | **YES** |

Semantic differences: **none** across (a)–(d).

## Interpretation (assessment only — the manuscript is NOT edited here)

- The paper-critical backend facts are **not idiosyncratic to the exact pinned
  commit**: they replicate on the latest stable MP-SPDZ release with no compile/API
  or semantic change. This is mild evidence **against** the strongest reading of the
  manuscript's "backend/version specific" caveat.
- **But this is still only two versions.** It does **not** establish general
  cross-version compatibility, and we did not sweep other queries, ring sizes, or
  protocols. The honest conclusion is *replicated on the pin and on v0.4.3*, not
  *version-independent*.
- **Would this justify changing the manuscript?** It would justify a *small, careful*
  softening of the "version-specific" wording for the pinned-backend finding — e.g.
  "observed on the pin **and v0.4.3**" — **not** a compatibility or generality claim.
  Per instructions, no such edit is made now; this is left for the manuscript-revision
  step and Codex review.

## Honest caveats

- One additional version only; `p1_is_max` query only for the probes (the artifact
  establishes both queries yield the same subtapes); single-host runtime; shallow
  clones (ancestry unverified). If any of these is material to a claim, it must be
  tested before that claim is strengthened.
