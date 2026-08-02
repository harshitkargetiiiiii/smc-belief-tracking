"""
Search for a minimal fixture that exercises BOTH the accept and the reject path
for the same party, so a conformance test meaningfully checks state-preservation
on rejection (the property the current mpc/ circuits violate).

Domain {0,1,2}, N=3, uniform prior. Two invocations. We want some party p that
accepts on invocation 1 (changing its belief) and rejects on invocation 2
(leaving that changed belief intact).
"""
from fractions import Fraction
from itertools import product

from oracle import SmcBeliefTracking, REJECT

DOMAIN = [0, 1, 2]
N = 3

# small, named query library (all public, deterministic)
QUERIES = {
    "p1_is_max": lambda s: int(s[0] >= s[1] and s[0] >= s[2]),
    "p2_eq_p3": lambda s: int(s[1] == s[2]),
    "sum_ge_3": lambda s: int(sum(s) >= 3),
    "p1_gt_p2": lambda s: int(s[0] > s[1]),
    "all_equal": lambda s: int(s[0] == s[1] == s[2]),
}


def belief_changed(before, after) -> bool:
    return before != after


def search():
    qnames = list(QUERIES)
    for secrets in product(DOMAIN, repeat=N):
        # thresholds: sweep a few rational values
        for t in (Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)):
            thresholds = [t, t, t]
            for q1 in qnames:
                for q2 in qnames:
                    try:
                        m = SmcBeliefTracking(DOMAIN, secrets, thresholds)
                    except ValueError:
                        continue
                    pre = [dict(b) for b in m.beliefs]
                    try:
                        out1 = m.invoke(QUERIES[q1])
                    except ValueError:
                        continue
                    mid = [dict(b) for b in m.beliefs]
                    try:
                        out2 = m.invoke(QUERIES[q2])
                    except ValueError:
                        continue
                    post = [dict(b) for b in m.beliefs]
                    for p in range(N):
                        accepted_1 = out1[p] != REJECT
                        rejected_2 = out2[p] == REJECT
                        changed_1 = belief_changed(pre[p], mid[p])
                        unchanged_2 = mid[p] == post[p]
                        if accepted_1 and changed_1 and rejected_2 and unchanged_2:
                            return dict(
                                secrets=secrets, threshold=t, q1=q1, q2=q2,
                                party=p, out1=out1, out2=out2,
                            )
    return None


if __name__ == "__main__":
    r = search()
    if not r:
        print("no fixture found in this search space")
    else:
        print("FIXTURE FOUND")
        for k, v in r.items():
            print(f"  {k}: {v}")
