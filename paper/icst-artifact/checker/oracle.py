"""
Independent plaintext oracle for PLAS 2012 "SMC belief tracking".

Scope: DETERMINISTIC, total, public queries adding only `out`. Faithful to the
PLAS ideal functionality restricted to that query class. Probabilistic queries
need likelihood weighting, not a Boolean support-filter, and are out of scope.

Written from the paper, independent of reference/ and of any circuit.
Source: Mardziel, Hicks, Katz & Srivatsa, PLAS 2012.
https://www.cs.umd.edu/~mwh/papers/belief-smc.pdf

Key semantics (Figure 4): tcheck runs [[q]]delta_i, then checks EVERY possible
output o, rejecting if some protected value's posterior probability > t. The
actual output is used only for the accepted state update (Fig. 9 line 6):
    delta_j := [[Q]]delta_j | (out = o_actual).

Support invariant (round 4, tightened round 4b): every belief primitive iterates
via `_positive_items`, which RAISES on negative mass and skips zero mass. So
`condition`, `possible_outputs`, `marginal_max`, and `tcheck_passes` all reject
a negative-mass belief at their boundary, not only the constructor. Zero-mass
keys are pruned and never treated as possible outputs.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Callable, Sequence

Assignment = tuple[int, ...]
Belief = dict[Assignment, Fraction]
Query = Callable[[Assignment], int]        # deterministic, total

REJECT = "reject"


def _positive_items(belief: Belief):
    """Yield (state, p) for p > 0. RAISE on p < 0. This is the single boundary
    that enforces the support invariant for every belief primitive below."""
    for s, p in belief.items():
        if p < 0:
            raise ValueError(f"negative probability at {s}: {p}")
        if p > 0:
            yield s, p


def _pruned(belief: Belief) -> Belief:
    """Reject negative mass, drop zero mass."""
    return dict(_positive_items(belief))


def uniform_prior(domain: Sequence[int], n: int) -> Belief:
    states = list(product(domain, repeat=n))
    p = Fraction(1, len(states))
    return {s: p for s in states}


def condition(belief: Belief, keep: Callable[[Assignment], bool]) -> Belief:
    """Bayesian conditioning. Raises on negative mass, drops zero, renormalizes.
    Raises if the conditioning event has probability zero."""
    kept = {s: p for s, p in _positive_items(belief) if keep(s)}
    z = sum(kept.values())
    if z == 0:
        raise ValueError("conditioning on a probability-zero event")
    return {s: p / z for s, p in kept.items()}


def possible_outputs(belief: Belief, query: Query) -> set[int]:
    """Outputs with positive probability under the belief (support only)."""
    return {query(s) for s, _ in _positive_items(belief)}


def marginal_max(belief: Belief, party: int) -> Fraction:
    acc: dict[int, Fraction] = {}
    for s, p in _positive_items(belief):
        acc[s[party]] = acc.get(s[party], Fraction(0)) + p
    return max(acc.values())


def tcheck_passes(dj: Belief, query: Query, i: int, t_i: Fraction) -> bool:
    """Figure 4, protected party i, from recipient belief dj.
    Accept iff EVERY possible output leaves i's marginal <= t_i."""
    for o in possible_outputs(dj, query):
        revised = condition(dj, lambda s, oo=o: query(s) == oo)
        if marginal_max(revised, i) > t_i:          # strict '>' rejects; '==' ok
            return False
    return True


class SmcBeliefTracking:
    def __init__(self, domain, secrets, thresholds, prior: Belief | None = None):
        self.n = len(secrets)
        self.domain = list(domain)
        self.secrets: Assignment = tuple(secrets)
        self.thresholds = list(thresholds)
        for t in self.thresholds:
            if not (Fraction(0) < t <= Fraction(1)):     # 0 < t_i <= 1
                raise ValueError(f"threshold out of (0,1]: {t}")
        prior = _pruned(prior if prior is not None
                        else uniform_prior(self.domain, self.n))
        if sum(prior.values()) != 1:
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
                # Fig. 9 line 6: delta_j := [[Q]]delta_j | (out = o_actual)
                new_beliefs[j] = condition(dj, lambda s: query(s) == o_actual)
            else:
                visible.append(REJECT)              # belief unchanged (Sec 4.4)
        self.beliefs = new_beliefs
        return visible

    def state_signature(self) -> tuple:
        return tuple(
            tuple((s, p.numerator, p.denominator) for s, p in sorted(b.items()))
            for b in self.beliefs
        )
