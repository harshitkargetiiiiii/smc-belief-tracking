"""
Tests for the reference implementation.

Run:  python3 -m pytest reference/ -v

The important test is `test_known_case_63_40_55`, which pins the one worked
example we can compute by hand. If that ever breaks, stop and find out why
before trusting any other number in this repo.
"""

from fractions import Fraction

import pytest

from belief_exact import (
    ExactBelief,
    IntegerBelief,
    q_richest,
    q_similar,
    richest_indicator,
)


DOMAIN = list(range(10, 101))          # the paper's domain: 91 values, 10..100
SMALL = list(range(1, 11))             # small domain for fast exhaustive tests


# --------------------------------------------------------------------------
# The pinned worked example
# --------------------------------------------------------------------------

def test_known_case_63_40_55():
    """Observer holds 63; both others are <= 63, so output is 1.

    Posterior support is every (s2, s3) with s2 <= 63 and s3 <= 63, i.e.
    54 x 54 states, uniform. The marginal on s2 is uniform over 54 values,
    so the max marginal is exactly 1/54.
    """
    belief = IntegerBelief(DOMAIN, unknown=2)
    belief = belief.revise_indicator(richest_indicator(63, 1))

    assert belief.max_marginal(0) == 54          # 54 states share each s2 value
    assert belief.total() == 54 * 54

    frac = Fraction(belief.max_marginal(0), belief.total())
    assert frac == Fraction(1, 54)
    assert abs(float(frac) - 0.018518518518) < 1e-12


def test_uniform_prior_max_marginal():
    """Before any revision the max marginal is 1/|D|."""
    belief = IntegerBelief(DOMAIN, unknown=2)
    assert Fraction(belief.max_marginal(0), belief.total()) == Fraction(1, len(DOMAIN))


# --------------------------------------------------------------------------
# The claim that matters: integer and rational paths agree exactly
# --------------------------------------------------------------------------

@pytest.mark.parametrize("observer", [15, 40, 63, 88, 100])
@pytest.mark.parametrize("rounds", [1, 2, 5])
def test_integer_matches_exact_rational(observer, rounds):
    """Exact integer conditioning == exact rational conditioning, always.

    This is the empirical backing for claim 2 in docs/claims.md. If this ever
    fails, the "no fixed-point error" argument collapses.
    """
    exact = ExactBelief(SMALL, unknown=2)
    integer = IntegerBelief(SMALL, unknown=2)

    obs = min(observer, max(SMALL))
    ind = richest_indicator(obs, 1)

    for _ in range(rounds):
        exact = exact.revise(lambda s: Fraction(ind(s)))
        integer = integer.revise_indicator(ind)

    assert exact.marginal(0) == integer.as_fractions(0)
    assert exact.max_belief(0) == max(integer.as_fractions(0).values())


def test_repeated_revision_is_idempotent_for_deterministic_query():
    """Conditioning twice on the same deterministic observation changes nothing.

    Worth pinning: it is a sanity check that the indicator is being applied as
    a filter rather than accumulating weight.
    """
    b1 = IntegerBelief(SMALL, unknown=2).revise_indicator(richest_indicator(5, 1))
    b2 = b1.revise_indicator(richest_indicator(5, 1))
    assert b1.as_fractions(0) == b2.as_fractions(0)


# --------------------------------------------------------------------------
# Threshold check
# --------------------------------------------------------------------------

@pytest.mark.parametrize("threshold", [Fraction(1, 5), Fraction(1, 50), Fraction(1, 100)])
def test_exact_threshold_matches_float_comparison(threshold):
    """b*max <= a*Z agrees with the rational comparison it stands in for."""
    belief = IntegerBelief(DOMAIN, unknown=2).revise_indicator(richest_indicator(63, 1))
    exact_ratio = Fraction(belief.max_marginal(0), belief.total())
    assert belief.exceeds(0, threshold) == (exact_ratio > threshold)


def test_threshold_at_exact_boundary():
    """Boundary case: max marginal exactly equals the threshold.

    The policy is `<= t`, so exactly-at-threshold must NOT be a violation.
    This is the case fixed-point arithmetic gets wrong and integers get right.
    """
    belief = IntegerBelief(DOMAIN, unknown=2).revise_indicator(richest_indicator(63, 1))
    exact = Fraction(belief.max_marginal(0), belief.total())   # 1/54
    assert exact == Fraction(1, 54)
    assert not belief.exceeds(0, Fraction(1, 54))              # equal -> allowed
    assert belief.exceeds(0, Fraction(1, 55))                  # tighter -> violated


# --------------------------------------------------------------------------
# Query definitions
# --------------------------------------------------------------------------

def test_q_richest():
    assert q_richest([10, 5, 3]) == 1
    assert q_richest([5, 10, 3]) == 0
    assert q_richest([5, 5, 5]) == 1        # ties count as richest


def test_q_similar_window():
    assert q_similar(0)([5, 5, 5]) == 1
    assert q_similar(0)([4, 5, 6]) == 0
    assert q_similar(1)([4, 5, 6]) == 1
    assert q_similar(16)([1, 5, 9]) == 1


# --------------------------------------------------------------------------
# Guard against silent domain errors
# --------------------------------------------------------------------------

def test_impossible_observation_raises():
    """Observer holds the minimum and claims to be strictly richest than all.

    Conditioning on a zero-probability observation must raise, not silently
    produce a degenerate belief.
    """
    belief = IntegerBelief([5], unknown=2)
    with pytest.raises(ValueError):
        belief.revise_indicator(lambda s: 0)
