"""
Independent plaintext oracle for PLAS 2012 "SMC belief tracking".

Scope: DETERMINISTIC, total, public queries that add only `out`. This is a
faithful model of the PLAS ideal functionality *restricted to that query class*.
PLAS also permits probabilistic queries, which require likelihood weighting
under the paper's probabilistic semantics, NOT the Boolean support-filter used
here. Those are out of scope and this oracle must not be called faithful for
them. (Round-3 review, issue #2.)

Written from the paper, independent of reference/ and of any circuit.
Source: Mardziel, Hicks, Katz & Srivatsa, PLAS 2012.
https://www.cs.umd.edu/~mwh/papers/belief-smc.pdf

CORRECTED after round 3. The decisive fix: `tcheck` (Figure 4) quantifies over
ALL POSSIBLE outputs, not the actual one. Figure 4 verbatim:

    tcheck(q, delta_i, t_j, x_j):
      1  delta_i := [[q]] delta_i
      2  forall possible outputs o
      3    d_hat := (delta_i | (out = o)) restricted to {x_j}
      4    if exists n. d_hat({x_j = n}) > t_j then
      5      return reject
      6  return accept

Checking only the actual output makes the reject decision depend on secret data,
which lets the rejection itself leak (Section 3.2, "Avoiding leakage due to query
rejection"; the decision must be simulatable). The actual output is used ONLY for
the state update, and ONLY after all checks pass (Fig. 9 line 6).
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Callable, Sequence

Assignment = tuple[int, ...]
Belief = dict[Assignment, Fraction]
Query = Callable[[Assignment], int]        # deterministic, total

REJECT = "reject"


def uniform_prior(domain: Sequence[int], n: int) -> Belief:
    states = list(product(domain, repeat=n))
    p = Fraction(1, len(states))
    return {s: p for s in states}


def condition(belief: Belief, keep: Callable[[Assignment], bool]) -> Belief:
    kept = {s: p for s, p in belief.items() if keep(s)}
    z = sum(kept.values())
    if z == 0:
        raise ValueError("conditioning on a probability-zero event")
    return {s: p / z for s, p in kept.items()}


def marginal_max(belief: Belief, party: int) -> Fraction:
    acc: dict[int, Fraction] = {}
    for s, p in belief.items():
        acc[s[party]] = acc.get(s[party], Fraction(0)) + p
    return max(acc.values())


def tcheck_passes(dj: Belief, query: Query, i: int, t_i: Fraction) -> bool:
    """Figure 4, for protected party i, from recipient belief dj.
    Accept iff EVERY possible output leaves i's marginal <= t_i.
    """
    possible_outputs = {query(s) for s in dj}          # support of [[q]]dj
    for o in possible_outputs:
        revised = condition(dj, lambda s, oo=o: query(s) == oo)
        if marginal_max(revised, i) > t_i:             # strict '>' rejects; '<=' ok
            return False
    return True


class SmcBeliefTracking:
    def __init__(self, domain, secrets, thresholds, prior: Belief | None = None):
        self.n = len(secrets)
        self.domain = list(domain)
        self.secrets: Assignment = tuple(secrets)
        self.thresholds = list(thresholds)
        for t in self.thresholds:
            if not (Fraction(0) < t <= Fraction(1)):   # 0 < t_i <= 1
                raise ValueError(f"threshold out of (0,1]: {t}")
        prior = prior or uniform_prior(self.domain, self.n)
        if abs(sum(prior.values()) - 1) != 0:
            raise ValueError("prior must sum to 1")
        if prior.get(self.secrets, Fraction(0)) == 0:
            raise ValueError("prior must be consistent with the actual secrets")
        # init_SMC: delta_j = delta | (x_j = s_j)
        self.beliefs: list[Belief] = [
            condition(prior, lambda s, j=j: s[j] == self.secrets[j])
            for j in range(self.n)
        ]

    def invoke(self, query: Query) -> list[object]:
        o_actual = query(self.secrets)
        new_beliefs = list(self.beliefs)
        visible: list[object] = []
        for j in range(self.n):
            dj = self.beliefs[j]
            accept = all(
                tcheck_passes(dj, query, i, self.thresholds[i])
                for i in range(self.n)
                if i != j
            )
            if accept:
                visible.append(o_actual)
                new_beliefs[j] = condition(dj, lambda s: query(s) == o_actual)
            else:
                visible.append(REJECT)          # belief unchanged (Sec 4.4)
        self.beliefs = new_beliefs
        return visible

    def state_signature(self) -> tuple:
        return tuple(
            tuple((s, p.numerator, p.denominator) for s, p in sorted(b.items()))
            for b in self.beliefs
        )
