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

from mpc_run import (
    D, N, S, state, run_circuit, parse_strict, compare, mpspdz_sha, write_inputs,
    oracle_expect,
)

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


def run_single(secrets, wvecs, query):
    write_inputs(secrets, wvecs)
    acc, pay, Wl = parse_strict(run_circuit(query))
    return acc, pay, Wl


def main():
    sha = mpspdz_sha()
    print(f"MP-SPDZ commit under test: {sha}")
    total = 0
    fails = 0

    # single-invocation cases
    for secrets, wvecs, query, label in single_cases():
        total += 1
        acc, pay, Wl = run_single(secrets, wvecs, query)
        msgs = compare(secrets, wvecs, query, acc, pay, Wl)
        if msgs:
            fails += 1
            print(f"FAIL [{label}] secrets={secrets} q={query}")
            for m in msgs:
                print("   ", m)

    # carried query-pair transitions: run qA, feed the circuit's updated weights
    # as the next state, run qB; compare to the oracle carried the same way.
    carried = 0
    for secrets in [(0, 0, 1), (2, 0, 0), (1, 0, 2)]:
        for qA, qB in [("sum_even", "p1_is_max"), ("p1_is_max", "sum_even")]:
            wvecs = [wvec(j, secrets[j], "uniform") for j in range(N)]
            accA, payA, WlA = run_single(secrets, wvecs, qA)
            mA = compare(secrets, wvecs, qA, accA, payA, WlA)
            # oracle carried state = circuit's updated weights (must be valid Sigma_T)
            acc2, pay2, Wl2 = run_single(secrets, WlA, qB)
            m2 = compare(secrets, WlA, qB, acc2, pay2, Wl2)
            total += 2
            carried += 2
            if mA or m2:
                fails += 1
                print(f"FAIL [carried] secrets={secrets} {qA}->{qB}")
                for m in mA + m2:
                    print("   ", m)

    print("=" * 60)
    print(f"single={total - carried}  carried={carried}  total={total}  "
          f"pass={total - fails}  fail={fails}")
    print(f"COVERAGE {'PASS' if fails == 0 else 'FAIL'}  ({total - fails}/{total})  "
          f"MP-SPDZ={sha}")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    main()
