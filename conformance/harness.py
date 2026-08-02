"""
Named-case conformance harness for the threshold_SMC circuit. Uses run_and_check
in mpc_run.py (strict, fail-closed, finalized raw evidence per run).

Pinned fixture (two invocations, carrying circuit state) plus two extra valid
states. Expected values come from the independent oracle and never enter the
circuit.
"""
import sys

from mpc_run import N, S, run_and_check, mpspdz_sha, state


def uniform_support_weights(secrets):
    out = []
    for j in range(N):
        w = [0] * S
        for idx in range(S):
            if state(idx)[j] == secrets[j]:
                w[idx] = 1
        out.append(w)
    return out


def run_case(secrets, weight_vectors, query, label):
    ok, msgs, acc, pay, Wl = run_and_check(secrets, weight_vectors, query, case_id=label)
    print(f"[{label}] q={query} secrets={secrets} "
          f"accept={[acc[j] for j in range(N)]} payload={[pay[j] for j in range(N)]} "
          f"-> {'PASS' if ok else 'FAIL'}")
    for m in msgs:
        print("    ", m)
    return ok, Wl


def main():
    print(f"MP-SPDZ commit under test: {mpspdz_sha()}")
    results = []

    s1 = (0, 0, 1)
    w = uniform_support_weights(s1)
    ok, w = run_case(s1, w, "sum_even", "fixture-inv1")
    results.append(ok)
    ok, w = run_case(s1, w, "p1_is_max", "fixture-inv2")     # carry updated weights
    results.append(ok)

    ok, _ = run_case((1, 0, 2), uniform_support_weights((1, 0, 2)),
                     "p1_is_max", "extra-state")
    results.append(ok)
    ok, _ = run_case((2, 0, 0), uniform_support_weights((2, 0, 0)),
                     "p1_is_max", "extra-mask")
    results.append(ok)

    print("=" * 60)
    print("ALL PASS" if all(results) else "SOME FAILED")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
