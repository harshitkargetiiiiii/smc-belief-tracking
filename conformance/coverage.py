"""
Adversarial coverage suite for the threshold_SMC circuit (round-5, issue #4).

Reproduces the structure of the reviewer's 218-case mutation run and retains it
as project evidence: every valid secret tuple, both queries, uniform /
non-uniform / per-party-scaled positive integer weights, near-tight bit-bound
encodings, and carried query-pair transitions. Every case is compared to the
independent Fraction oracle via the strict core in mpc_run.py.

Run:  MPSPDZ=/path/to/MP-SPDZ python3 coverage.py
Exits non-zero on any mismatch; prints the MP-SPDZ commit it tested against.
"""
import sys
from itertools import product

from mpc_run import D, N, S, state, run_and_check, mpspdz_sha

WT = (2 ** 63 - 1) // 54          # per-weight bound so 54*W < 2^63 (near-tight)


def support(j, sj):
    return [idx for idx in range(S) if state(idx)[j] == sj]


def wvec(j, sj, scheme, scale=1):
    w = [0] * S
    for k, idx in enumerate(support(j, sj)):
        if scheme == "uniform":
            w[idx] = 1 * scale
        elif scheme == "nonuniform":
            w[idx] = (1 + k) * scale          # 1..9
        elif scheme == "tight":
            w[idx] = WT
    return w


def single_cases():
    for secrets in product(D, repeat=N):
        for q in ("sum_even", "p1_is_max"):
            yield (secrets,
                   [wvec(j, secrets[j], "uniform") for j in range(N)], q, "uniform")
            yield (secrets,
                   [wvec(j, secrets[j], "nonuniform") for j in range(N)], q, "nonuniform")
            yield (secrets,
                   [wvec(j, secrets[j], "nonuniform", scale=j + 1) for j in range(N)],
                   q, "scaled")
        for q in ("sum_even", "p1_is_max"):
            yield (secrets,
                   [wvec(j, secrets[j], "tight") for j in range(N)], q, "tight")


def main():
    sha = mpspdz_sha()
    print(f"MP-SPDZ commit under test: {sha}")
    total = 0
    fails = 0

    # single-invocation cases
    for i, (secrets, wvecs, query, label) in enumerate(single_cases()):
        total += 1
        ok, msgs, _, _, _ = run_and_check(secrets, wvecs, query,
                                          case_id=f"single-{i}-{label}")
        if not ok:
            fails += 1
            print(f"FAIL [{label}] secrets={secrets} q={query}")
            for m in msgs:
                print("   ", m)

    # carried query-pair transitions: run qA, feed the circuit's updated weights
    # as the next state, run qB; compare to the oracle carried the same way.
    # Each transition is counted separately (two failed transitions != one).
    carried = 0
    for secrets in [(0, 0, 1), (2, 0, 0), (1, 0, 2)]:
        for qA, qB in [("sum_even", "p1_is_max"), ("p1_is_max", "sum_even")]:
            wvecs = [wvec(j, secrets[j], "uniform") for j in range(N)]
            okA, mA, _, _, WlA = run_and_check(secrets, wvecs, qA,
                                               case_id=f"carriedA-{secrets}-{qA}")
            total += 1
            carried += 1
            if not okA:
                fails += 1
                print(f"FAIL [carriedA] secrets={secrets} {qA} (stage 1 of {qA}->{qB})")
                for m in mA:
                    print("   ", m)
            ok2, m2, _, _, _ = run_and_check(secrets, WlA, qB,
                                             case_id=f"carriedB-{secrets}-{qB}")
            total += 1
            carried += 1
            if not ok2:
                fails += 1
                print(f"FAIL [carriedB] secrets={secrets} {qB} (stage 2 of {qA}->{qB})")
                for m in m2:
                    print("   ", m)

    print("=" * 60)
    print(f"single={total - carried}  carried={carried}  total={total}  "
          f"pass={total - fails}  fail={fails}")
    print(f"COVERAGE {'PASS' if fails == 0 else 'FAIL'}  ({total - fails}/{total})  "
          f"MP-SPDZ={sha}")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    main()
