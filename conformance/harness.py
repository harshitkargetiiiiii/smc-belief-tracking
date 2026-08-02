"""
Named-case conformance harness for the threshold_SMC circuit. Uses the strict
run/parse/compare core in mpc_run.py (round-5: fail-closed execution, strict
parsing). The broad adversarial suite is in coverage.py.

The pinned fixture (two invocations) plus two additional valid states. Expected
values come from the independent oracle and never enter the circuit.
"""
import sys
from fractions import Fraction

from mpc_run import (
    D, N, S, run_circuit, parse_strict, compare, write_inputs, mpspdz_sha, state,
)


def uniform_support_weights(secrets):
    """Dense 0/1 weights: 1 on states with x_j = s_j (init_SMC uniform)."""
    out = []
    for j in range(N):
        w = [0] * S
        for idx in range(S):
            if state(idx)[j] == secrets[j]:
                w[idx] = 1
        out.append(w)
    return out


def run_case(secrets, weight_vectors, query, label):
    write_inputs(secrets, weight_vectors)
    acc, pay, Wl = parse_strict(run_circuit(query))
    msgs = compare(secrets, weight_vectors, query, acc, pay, Wl)
    ok = not msgs
    print(f"[{label}] q={query} secrets={secrets} "
          f"accept={[acc[j] for j in range(N)]} payload={[pay[j] for j in range(N)]} "
          f"-> {'PASS' if ok else 'FAIL'}")
    for m in msgs:
        print("    ", m)
    return ok, Wl


def main():
    print(f"MP-SPDZ commit under test: {mpspdz_sha()}")
    results = []

    # Pinned fixture, secrets (0,0,1). Two invocations, carrying circuit state.
    s1 = (0, 0, 1)
    w = uniform_support_weights(s1)
    ok, w = run_case(s1, w, "sum_even", "fixture-inv1")
    results.append(ok)
    ok, w = run_case(s1, w, "p1_is_max", "fixture-inv2")   # carry updated weights
    results.append(ok)

    # Additional valid states
    ok, _ = run_case((1, 0, 2), uniform_support_weights((1, 0, 2)),
                     "p1_is_max", "extra-state")
    results.append(ok)
    ok, _ = run_case((2, 0, 0), uniform_support_weights((2, 0, 0)),
                     "p1_is_max", "extra-mask")            # accept payload 1 vs masked 0
    results.append(ok)

    print("=" * 60)
    print("ALL PASS" if all(results) else "SOME FAILED")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
