"""
Exact-rational reference implementation of knowledge-threshold belief tracking.

This is ground truth. Every MPC result must be checked against this. When an MPC
run and this module disagree, this module is right until proven otherwise.

Model (Mardziel, Hicks, Katz & Srivatsa, PLAS 2012):
  N parties, party i holds secret s_i in a finite domain D.
  Observer j holds a belief: a distribution over the other parties' secrets.
  After observing query output o, the belief is revised by Bayes:
      delta'(s) proportional to delta(s) * Pr[Q(s) = o]
  A knowledge-threshold policy for party i with threshold t_i demands
      max_v delta_j(s_i = v) <= t_i
  for every other party j.

Two representations are provided:

  ExactBelief    - Fraction-based. Always correct, slow. The oracle.
  IntegerBelief  - unnormalised integer weights. Also always correct, for
                   deterministic (0/1-likelihood) queries, and it is what the
                   MPC circuit should mirror. See docs/claims.md, claim 2.

The IntegerBelief path is the interesting one: when the likelihood is an
indicator, conditioning never introduces rounding, so the whole fixed-point
soundness problem disappears. This module exists partly to demonstrate that
those two paths agree exactly.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from typing import Callable, Iterable, Sequence

# A query maps a full secret assignment to an output value.
Query = Callable[[Sequence[int]], int]


# --------------------------------------------------------------------------
# Queries from the PLAS 2012 evaluation
# --------------------------------------------------------------------------

def q_richest(secrets: Sequence[int]) -> int:
    """Q1, "am I the richest?" - is party 0's secret the maximum?"""
    return int(all(secrets[0] >= s for s in secrets[1:]))


def q_similar(window: int) -> Query:
    """similar_w - is every secret within `window` of the mean?

    The paper sweeps w over {0, 1, 2, 4, 8, 16}.
    """
    def f(secrets: Sequence[int]) -> int:
        mean = Fraction(sum(secrets), len(secrets))
        return int(all(abs(Fraction(s) - mean) <= window for s in secrets))
    return f


def q_richest_noisy(p: Fraction) -> Callable[[Sequence[int]], dict[int, Fraction]]:
    """richest_p - noisy maximum.

    Unlike the others this returns a *distribution* over outputs rather than a
    single value, because the likelihood is no longer an indicator. This is the
    case where exact integer conditioning breaks down (denominators compound);
    see docs/claims.md, claim 2, "where it breaks".
    """
    def f(secrets: Sequence[int]) -> dict[int, Fraction]:
        true = q_richest(secrets)
        return {true: 1 - p, 1 - true: p}
    return f


# --------------------------------------------------------------------------
# Exact rational belief
# --------------------------------------------------------------------------

class ExactBelief:
    """A belief over the unknown parties' secrets, as exact rationals.

    `unknown` is the number of secrets the observer does not know (for a
    3-party setting where party 0 observes, that is 2).
    """

    def __init__(self, domain: Sequence[int], unknown: int):
        self.domain = list(domain)
        self.unknown = unknown
        self.states = list(product(self.domain, repeat=unknown))
        n = len(self.states)
        self.probs = {s: Fraction(1, n) for s in self.states}

    def revise(self, likelihood: Callable[[tuple[int, ...]], Fraction]) -> "ExactBelief":
        """Bayesian revision. `likelihood` gives Pr[observation | state]."""
        weights = {s: self.probs[s] * likelihood(s) for s in self.states}
        z = sum(weights.values())
        if z == 0:
            raise ValueError("observation has probability zero under this belief")
        out = ExactBelief.__new__(ExactBelief)
        out.domain, out.unknown, out.states = self.domain, self.unknown, self.states
        out.probs = {s: w / z for s, w in weights.items()}
        return out

    def marginal(self, party: int) -> dict[int, Fraction]:
        """Marginal distribution over the secret of one unknown party."""
        m = {v: Fraction(0) for v in self.domain}
        for s, p in self.probs.items():
            m[s[party]] += p
        return m

    def max_belief(self, party: int) -> Fraction:
        return max(self.marginal(party).values())

    def violates(self, threshold: Fraction) -> bool:
        """True if any party's max marginal exceeds the threshold."""
        return any(self.max_belief(i) > threshold for i in range(self.unknown))


# --------------------------------------------------------------------------
# Unnormalised integer belief - what the MPC circuit should mirror
# --------------------------------------------------------------------------

class IntegerBelief:
    """Belief as unnormalised non-negative integer weights.

    For deterministic queries the likelihood is 0 or 1, so revision is
    elementwise multiplication by a bit. Weights never grow and never round.
    The threshold check max_v m_v / Z <= a/b becomes b * max_v m_v <= a * Z,
    which is exact integer arithmetic - no division, no truncation, no error.

    This is the representation the MPC implementation should use. `mpc/`
    currently uses sfix; migrating it to this is the main outstanding task.
    """

    def __init__(self, domain: Sequence[int], unknown: int):
        self.domain = list(domain)
        self.unknown = unknown
        self.states = list(product(self.domain, repeat=unknown))
        self.weights = {s: 1 for s in self.states}   # uniform prior

    def revise_indicator(self, indicator: Callable[[tuple[int, ...]], int]) -> "IntegerBelief":
        """Revision under a 0/1 likelihood. Exact; no rounding anywhere."""
        out = IntegerBelief.__new__(IntegerBelief)
        out.domain, out.unknown, out.states = self.domain, self.unknown, self.states
        out.weights = {s: self.weights[s] * indicator(s) for s in self.states}
        if sum(out.weights.values()) == 0:
            raise ValueError("observation has probability zero under this belief")
        return out

    def marginal(self, party: int) -> dict[int, int]:
        m = {v: 0 for v in self.domain}
        for s, w in self.weights.items():
            m[s[party]] += w
        return m

    def total(self) -> int:
        return sum(self.weights.values())

    def max_marginal(self, party: int) -> int:
        return max(self.marginal(party).values())

    def exceeds(self, party: int, threshold: Fraction) -> bool:
        """Exact threshold test: max_v m_v / Z > a/b  <=>  b*max > a*Z."""
        a, b = threshold.numerator, threshold.denominator
        return b * self.max_marginal(party) > a * self.total()

    def as_fractions(self, party: int) -> dict[int, Fraction]:
        z = self.total()
        return {v: Fraction(w, z) for v, w in self.marginal(party).items()}


# --------------------------------------------------------------------------
# Convenience: run the paper's Q1 benchmark
# --------------------------------------------------------------------------

def richest_indicator(observer_secret: int, observed_output: int) -> Callable[[tuple[int, ...]], int]:
    """Indicator 1[Q(s) = o] for "am I the richest?" from the observer's view.

    Note the structure that makes this cheap in MPC: for each enumerated state
    s, Q(s) is a *public* constant (the query is public and s is an enumerated
    hypothesis). Only `observed_output` is secret. So

        1[Q(s) = o] = Q(s)*o + (1 - Q(s))*(1 - o)

    is linear in o with public coefficients - a local operation in any linear
    secret-sharing scheme. See docs/claims.md, claim 1.
    """
    def f(state: tuple[int, ...]) -> int:
        qs = int(all(observer_secret >= v for v in state))
        return int(qs == observed_output)
    return f


def run_q1(domain: Sequence[int], observer_secret: int, rounds: int = 1) -> IntegerBelief:
    """Run `rounds` revisions of Q1 with the truthful output each time."""
    belief = IntegerBelief(domain, unknown=2)
    for _ in range(rounds):
        # The truthful output depends on the real secrets; for the reference we
        # take the observer's own view where the output is whatever the real
        # world produced. Here we assume the honest "yes" case.
        belief = belief.revise_indicator(richest_indicator(observer_secret, 1))
    return belief
