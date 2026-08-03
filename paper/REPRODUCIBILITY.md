# REPRODUCIBILITY — clean-room run

A from-scratch reproduction of the frozen artifact and the paper's mutation
evidence, in a fresh environment with a fresh MP-SPDZ build at the pin. **Nothing
in the frozen artifact (`conformance/`, `mpc/`, `reference/`, `.github/`) was
modified**; the B6/S1 mutation sources were taken from the committed
`paper/mutations/`. Result: **everything reproduces**, and the compiled assembly is
byte-for-byte deterministic against the committed `paper/mutations/detection_matrix.json`.

## Environment (recorded)

| item | value |
|---|---|
| Repo | fresh clone of `github.com/harshitkargetiiiiii/smc-belief-tracking`, checkout tag `paper-external-review-v1` = commit `67da5eb` |
| MP-SPDZ | fresh `--depth 1` clone + `git fetch --depth 1 origin <pin>` + checkout **`9d809599`** |
| Python | 3.11.15 |
| pytest | 9.1.1 |
| C++ | Ubuntu clang 18.1.3 (MP-SPDZ default `CONFIG`, `-O3 -std=c++20`) |
| git | 2.43.0 |
| CPU | 2 cores |

## Exact commands (in order)

```
# 1. fresh MP-SPDZ at the pin
git clone --depth 1 https://github.com/data61/MP-SPDZ.git MP-SPDZ
cd MP-SPDZ && git fetch --depth 1 origin 9d809599ea6ce627216a389ca7d984fbb75d0cb9 \
           && git checkout 9d809599ea6ce627216a389ca7d984fbb75d0cb9
make -j2 replicated-ring-party.x           # build
Scripts/setup-ssl.sh 3                      # TLS certs (runtime)
cd ..

# 2. fresh repo at the frozen tag
git clone https://github.com/harshitkargetiiiiii/smc-belief-tracking.git repo
cd repo && git checkout paper-external-review-v1
export MPSPDZ=$PWD/../MP-SPDZ

# 3. pure-Python suites (no MP-SPDZ needed)
python3 -m pytest reference/ conformance/ -q

# 4. MP-SPDZ artifact runs
EVIDENCE=$PWD/conformance/_evidence/cr-harness.jsonl  MPSPDZ=$MPSPDZ python3 conformance/harness.py
EVIDENCE=$PWD/conformance/_evidence/cr-private.jsonl  MPSPDZ=$MPSPDZ python3 conformance/private_run.py
EVIDENCE=$PWD/conformance/_evidence/cr-coverage.jsonl MPSPDZ=$MPSPDZ python3 conformance/coverage.py
MPSPDZ=$MPSPDZ python3 conformance/validate_evidence.py conformance/_evidence/cr-private.jsonl \
    --count 4 --private --repo $(git rev-parse HEAD) --mpspdz 9d809599ea6ce627216a389ca7d984fbb75d0cb9 --recompute
MPSPDZ=$MPSPDZ python3 conformance/validate_evidence.py conformance/_evidence/cr-coverage.jsonl \
    --count 228 --repo $(git rev-parse HEAD) --mpspdz 9d809599ea6ce627216a389ca7d984fbb75d0cb9

# 5. mutation reproductions (B4 synthetic manifest; B6/S1 from paper/mutations/) — see paper/reproduce.sh
```

A convenience wrapper, `paper/reproduce.sh`, runs the whole sequence (it only
orchestrates the existing, unmodified scripts; it adds no artifact logic).

## Results

| step | command | result | wall-clock |
|---|---|---|---|
| Build MP-SPDZ @ pin | `make -j2 replicated-ring-party.x` | binary built, no errors | **151 s** |
| Unit tests | `pytest reference/ conformance/` | **117 passed** (conformance 92 collected = 46 functional + 46 delivery-gate; reference 25) | 0.4 s |
| Named-case harness | `harness.py` | **4/4 PASS** (fixture inv1/inv2 + 2 extra states) | 1 s |
| Delivery gate + private cases | `private_run.py` | delivery **PASS** both queries; **all 5 negative controls rejected** (leaky, subleak, namespoof, openfalse, openfalse\_vec); 4 private cases PASS | 5 s |
| Validate private evidence | `validate_evidence.py --private --recompute` | **EVIDENCE OK (4 records)** — source hash, delivery sig, and oracle case-table binding recomputed | <1 s |
| 228-case matrix | `coverage.py` | **228/228** (single=216, carried=12, fail=0) | 22 s |
| Validate coverage evidence | `validate_evidence.py --count 228` | **EVIDENCE OK (228 records)** | <1 s |
| B4 (synthetic manifest) | `is_private_manifest(synthetic)` | **REJECTED by rule (h)**, multiset **intact** (as documented; not a source `.mpc`) | <1 s |
| B6 (`threshold_smc_callarg.mpc`) | compile + linter | **REJECTED** (adds `_leak` tape → multiset; call frame also spills to memory) — not a bypass | <1 s |
| S1 lint (`threshold_smc_wrongsem.mpc`) | compile + linter | **PASSES** delivery linter (three pinned subtapes; structure intact) | <1 s |
| S1 runtime | 3 parties, `secrets=(0,0,0)`, `p1_is_max` | rc `{0:0,1:0,2:0}`; delivered `ACCEPT 0 / PAYLOAD 1` to all; oracle payload `0`; **mismatch at `[0,1,2]`** | 2 s |
| Honest-build channel | grep compiled private build | main **3× `call_tape`**; each of `{EQZ(3)_63, EQZ(81)_63, LTZ(36)_64}` **1× `call_arg`**; no memory | <1 s |

**Total reproduction wall-clock ≈ 3.5 min** (dominated by the 151 s build; the fresh
clones added a few seconds each).

## Determinism / hash check

A fresh build at the pin produced **byte-identical** compiled assembly. The
`manifest_signature` (sha256 over the full normalized per-tape assembly) recomputed
here equals the values committed in `paper/mutations/detection_matrix.json`:

| manifest | clean-room sha256 (16) | detection\_matrix | match |
|---|---|---|---|
| private build | `715b006b11c3067c` | (= prior run's delivery sig) | ✓ |
| B6 `callarg` | `506710b60ab7a9d9` | `506710b60ab7a9d9` | ✓ |
| S1 `wrongsem` | `18b24ff7e008ac2c` | `18b24ff7e008ac2c` | ✓ |

## Failures / retries (recorded honestly)

- **One retry, operator error (not an artifact failure):** the first
  `validate_evidence.py --private` invocation passed a placeholder `--repo LOCAL`.
  The validator correctly rejected it because the evidence records carry the real
  repo SHA (`67da5eb`, read from git provenance). Re-running with
  `--repo $(git rev-parse HEAD)` gave `EVIDENCE OK`. This actually confirms the
  SHA-binding works.
- **No artifact-level failures.** Every documented result reproduced on the first
  correct invocation.
- Note on provenance flag: a local git clone yields `bound: false` (only CI, with
  `GITHUB_SHA`, is `bound: true`); we therefore validated **without**
  `--require-bound`. The `--recompute` binding (source hash + delivery sig + oracle
  case table) was exercised and passed.

## What this establishes — and does not

**Establishes:** the frozen artifact and the paper's mutation evidence reproduce
from a clean checkout with a fresh pinned-MP-SPDZ build, quickly, and the compiled
assembly is deterministic (the archived hashes are reproducible). **Does not:** say
anything new about privacy, performance, or any other backend version (see
`paper/CROSS_VERSION.md`). No claim is strengthened or weakened by this run on its
own; it is a reproducibility check.
