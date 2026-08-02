"""
Independent plaintext oracle for PLAS 2012 "SMC belief tracking".

Written from the paper's ideal functionality (Figures 8-9, Sections 4.4-4.5),
NOT from any MPC circuit and NOT sharing code with reference/belief_exact.py.
This file is the specification a conformant MPC circuit must match on the
fixture; if the circuit is transcribed into this oracle, the test is worthless,
so this is deliberately a fresh implementation.

Source: Mardziel, Hicks, Katz & Srivatsa, "Knowledge-Oriented Secure Multiparty
Computation", PLAS 2012. https://www.cs.umd.edu/~mwh/papers/belief-smc.pdf

Contract transcribed (see docs/conformance.md for the cited version):

  init_SMC (Fig. 9): each party j's belief is the common prior delta conditioned
    on that party's OWN secret: delta_j := delta | (x_j = s_j).

  threshold_SMC (Fig. 9), per query Q with real output o = Q(s_1..s_N):
    for each recipient P_j:
      revised = delta_j | (out = o)                      # Fig. 9 line 6
      accept  = for every other party i != j, the marginal of `revised` on x_i
                assigns no value probability > t_i       # Fig. 9 lines 2-5, Fig. 4 line 4
      if accept: P_j sees o ;   delta_j := revised
      else:      P_j sees reject ; delta_j unchanged      # Sec 4.4, Lemma 6

  Privacy (Sec 4.4): whether P_j received output or reject is NOT observable by
    any other party. THIS ORACLE DOES NOT MODEL THAT. It computes the functional
    result (who sees what, resulting beliefs). The non-observability is an
    information-flow property of the *protocol*, not a function of the state, and
    a functional conformance test cannot establish it. Flagged, not tested.

  Persistent state Sigma_T (Sec 4.5): secrets, thresholds, and current beliefs
    delta_i, carried between invocations.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Callable, Sequence

Assignment = tuple[int, ...]
Belief = dict[Assignment, Fraction]          # full joint over (x_1..x_N)
Query = Callable[[Assignment], int]

REJECT = "reject"


def uniform_prior(domain: Sequence[int], n: int) -> Belief:
    states = list(product(domain, repeat=n))
    p = Fraction(1, len(states))
    return {s: p for s in states}


def condition(belief: Belief, keep: Callable[[Assignment], bool]) -> Belief:
    """Bayesian conditioning: restrict support to `keep`, renormalize.

    Raises if the conditioning event has probability zero.
    """
    kept = {s: p for s, p in belief.items() if keep(s)}
    z = sum(kept.values())
    if z == 0:
        raise ValueError("conditioning on a probability-zero event")
    return {s: p / z for s, p in kept.items()}


def marginal_max(belief: Belief, party: int) -> Fraction:
    """Largest probability the belief assigns to any single value of x_party."""
    acc: dict[int, Fraction] = {}
    for s, p in belief.items():
        acc[s[party]] = acc.get(s[party], Fraction(0)) + p
    return max(acc.values())


class SmcBeliefTracking:
    """Faithful plaintext model of the PLAS ideal functionality."""

    def __init__(
        self,
        domain: Sequence[int],
        secrets: Sequence[int],
        thresholds: Sequence[Fraction],
        prior: Belief | None = None,
    ):
        self.n = len(secrets)
        self.domain = list(domain)
        self.secrets: Assignment = tuple(secrets)
        self.thresholds = list(thresholds)
        prior = prior or uniform_prior(self.domain, self.n)
        # init_SMC: delta_j = delta | (x_j = s_j)
        self.beliefs: list[Belief] = [
            condition(prior, lambda s, j=j: s[j] == self.secrets[j])
            for j in range(self.n)
        ]

    def invoke(self, query: Query) -> list[object]:
        """Run one query. Returns the recipient-visible output per party:
        the integer output o if accepted, or REJECT if not.
        Mutates persistent belief state exactly as the contract requires.
        """
        o = query(self.secrets)                       # real output, actual secrets
        visible: list[object] = []
        new_beliefs = list(self.beliefs)              # copy; reject leaves entry as-is
        for j in range(self.n):
            revised = condition(self.beliefs[j], lambda s: query(s) == o)
            accept = all(
                marginal_max(revised, i) <= self.thresholds[i]
                for i in range(self.n)
                if i != j
            )
            if accept:
                visible.append(o)
                new_beliefs[j] = revised
            else:
                visible.append(REJECT)
                # belief unchanged (Sec 4.4, Lemma 6)
        self.beliefs = new_beliefs
        return visible

    def state_signature(self) -> tuple:
        """Canonical, comparable snapshot of the persistent beliefs.

        This is the 'test-only reconstructed state' a conformant circuit must
        match. Beliefs serialized as sorted (assignment, num, den) tuples.
        """
        return tuple(
            tuple((s, p.numerator, p.denominator) for s, p in sorted(b.items()))
            for b in self.beliefs
        )
