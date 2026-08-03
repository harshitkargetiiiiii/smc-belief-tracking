# REPRODUCIBILITY — clean-room run

A from-scratch reproduction of the frozen artifact and the paper's mutation
evidence, in a fresh environment with a fresh MP-SPDZ build at the pin. **Nothing
in the frozen artifact (`conformance/`, `mpc/`, `reference/`, `.github/`) was
modified**; the mutation reproductions drive the frozen linter/oracle over the
mutation sources committed under `paper/mutations/`. Result: **everything
reproduces**, and each compiled tape's `manifest_signature` (sha256 over the
normalized per-tape assembly) recomputes to the committed values in
`paper/mutations/detection_matrix.json`.

## One-command reproduction

`paper/reproduce.sh` runs the **whole** sequence — the core artifact **and** the
B4/B6/S1 mutation reproductions — by orchestrating only the frozen artifact's own
scripts and functions (`delivery_inspect`, `mpc_run`, `coverage`, `private_run`)
plus the compiler/runtime. It adds no detection or oracle logic.

```
git clone https://github.com/harshitkargetiiiiii/smc-belief-tracking.git repo
cd repo && git checkout paper/strengthening        # the wrapper lives on this branch
[MPSPDZ=/path/to/pinned/MP-SPDZ] bash paper/reproduce.sh
```

The wrapper is invoked from `paper/strengthening` (which is where the script
exists), but the **artifact under test is the frozen tag**: the script checks out
`paper-external-review-v1` into a scratch git worktree, **verifies its commit is
`67da5eb`, and fails closed otherwise**, then runs every artifact step *from that
frozen checkout* — so nothing on the strengthening branch can influence the
result. It likewise **fails closed** if `MPSPDZ` is not the pinned commit
`9d809599` (an unset/other `MPSPDZ` triggers a fresh pinned clone+build). The
B4/B6/S1 mutation reproductions are then driven by
`paper/mutations/reproduce_mutations.py` (orchestration glue: it imports the frozen
`delivery_inspect`/`mpc_run`/`private_run` and makes no linter/oracle decision of
its own).

> Note: earlier revisions of this file implied `paper/reproduce.sh` could be run
> *from* the `paper-external-review-v1` checkout. That tag does not contain the
> script; the wrapper runs from the strengthening branch and clones/verifies the
> frozen tag internally, as described above.

## Environment (recorded)

| item | value |
|---|---|
| Repo | fresh clone of `github.com/harshitkargetiiiiii/smc-belief-tracking`; wrapper on `paper/strengthening`, artifact-under-test checked out at tag `paper-external-review-v1` = commit `67da5eb` |
| MP-SPDZ | fresh `--depth 1` clone + `git fetch --depth 1 origin <pin>` + checkout **`9d809599`** |
| Python | 3.11.15 |
| pytest | 9.1.1 |
| C++ | Ubuntu clang 18.1.3 (MP-SPDZ default `CONFIG`, `-O3 -std=c++20`) |
| git | 2.43.0 |
| CPU | 2 cores |

## What the wrapper runs (in order)

1. **Frozen checkout + verify** — `git worktree add --detach <tmp> paper-external-review-v1`; assert `HEAD == 67da5eb` (else abort).
2. **MP-SPDZ at the pin** — reuse `$MPSPDZ` iff its `HEAD == 9d809599`, else fresh clone + `make -j replicated-ring-party.x`; assert pin (else abort); `Scripts/setup-ssl.sh 3` for the runtime.
3. **Core artifact (from the frozen checkout):** `pytest reference/ conformance/`; `harness.py`; `private_run.py` (delivery gate + five negative controls + private cases); `coverage.py` (228-case matrix); `validate_evidence.py` on both evidence files with `--recompute`, bound to the frozen repo SHA and the pin.
4. **Mutation reproductions B4/B6/S1** via `paper/mutations/reproduce_mutations.py` (below).

## Results

| step | command | result | wall-clock |
|---|---|---|---|
| Build MP-SPDZ @ pin | `make -j2 replicated-ring-party.x` | binary built, no errors | **151 s** |
| Unit tests | `pytest reference/ conformance/` | **117 passed** (conformance 92 = 46 functional + 46 delivery-gate; reference 25) | 0.4 s |
| Named-case harness | `harness.py` | **4/4 PASS** (fixture inv1/inv2 + 2 extra states) | 1 s |
| Delivery gate + private cases | `private_run.py` | delivery **PASS** both queries; **all 5 negative controls rejected** (leaky, subleak, namespoof, openfalse, openfalse\_vec); 4 private cases PASS | 5 s |
| Validate private evidence | `validate_evidence.py --private --recompute` | **EVIDENCE OK (4 records)** — source hash, delivery sig, and oracle case-table binding recomputed | <1 s |
| 228-case matrix | `coverage.py` | **228/228** (single=216, carried=12, fail=0) | 22 s |
| Validate coverage evidence | `validate_evidence.py --count 228` | **EVIDENCE OK (228 records)** | <1 s |
| **B4** (synthetic manifest) | `reproduce_mutations.py` → `is_private_manifest(synthetic)` | **REJECTED by rule (h)** (`ldms` in `EQZ(3)_63`), multiset **intact** (a synthetic manifest; not a source `.mpc`) | <1 s |
| **honest channel** | grep of the frozen private manifest | main **3× `call_tape`**; subtapes **3× `call_arg`**; no subtape memory | <1 s |
| **B6** (`threshold_smc_callarg.mpc`) | compile + frozen linter | **REJECTED** (adds `_leak` tape → multiset; frame also spills to memory) — not a bypass; sig `506710b6…` **== detection_matrix** | 2 s |
| **S1 lint** (`threshold_smc_wrongsem.mpc`) | compile + frozen linter | **PASSES** (three pinned subtapes; structure intact); sig `18b24ff7…` **== detection_matrix** | 2 s |
| **S1 runtime** | 3 parties, `secrets=(0,0,0)`, uniform weights, `p1_is_max` | rc `{0:0,1:0,2:0}`; delivered `ACCEPT 0 / PAYLOAD 1` to all; frozen oracle payload `0`; **mismatch at `[0,1,2]`** | 2 s |

**Total reproduction wall-clock ≈ 3.5–4 min** (dominated by the 151 s build; with
`MPSPDZ` pre-supplied, everything after the build is well under a minute).

## Determinism / signature check

The claim is stated precisely: a fresh build at the pin recomputes **identical
`manifest_signature` values**, where `manifest_signature()` is the
**sha256 over the full per-tape assembly after stripping comments and blank lines**
(the frozen definition in `delivery_inspect.py`). Raw assembly / object files were
**not** independently byte-compared; the reproduced quantity is the normalized-assembly
signature.

| manifest | recomputed sha256 (16) | committed | wrapper-asserted? |
|---|---|---|---|
| B6 `callarg` | `506710b60ab7a9d9` | `detection_matrix.json` B6 | **yes** (`== detection_matrix`) |
| S1 `wrongsem` | `18b24ff7e008ac2c` | `detection_matrix.json` S1 | **yes** (`== detection_matrix`) |
| private build | `715b006b11c3067c` | (= the delivery gate's internal delivery signature) | recomputed each run; equals the prior run |

## Failures / retries (recorded honestly)

- **One retry in the original by-hand run, operator error (not an artifact
  failure):** the first `validate_evidence.py --private` invocation passed a
  placeholder `--repo LOCAL`. The validator correctly rejected it because the
  evidence records carry the real repo SHA (read from git provenance). Re-running
  with the resolved `--repo $(git rev-parse HEAD)` gave `EVIDENCE OK`. This
  confirms the SHA-binding works. **`paper/reproduce.sh` passes the resolved frozen
  SHA directly**, so this placeholder mistake cannot recur in the wrapper path.
- **No artifact-level failures.** Every documented result reproduced on the first
  correct invocation.
- Note on provenance flag: a local git clone/worktree yields `bound: false` (only
  CI, with `GITHUB_SHA`, is `bound: true`); we therefore validated **without**
  `--require-bound`. The `--recompute` binding (source hash + delivery sig + oracle
  case table) was exercised and passed.

## What this establishes — and does not

**Establishes:** the frozen artifact and the paper's mutation evidence reproduce
from a clean checkout with a fresh pinned-MP-SPDZ build, quickly, in a single
command; the B4/B6/S1 mutation outcomes reproduce against the **frozen** linter and
oracle; and each mutation's normalized-assembly `manifest_signature` recomputes to
the archived value. **Does not:** say anything new about privacy, performance, or
any other backend version (see `paper/CROSS_VERSION.md`), and does not claim
raw-byte determinism of the compiled object files. No claim is strengthened or
weakened by this run on its own; it is a reproducibility check.
