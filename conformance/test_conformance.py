"""
The conformance fixture, pinned with HAND-DERIVED expected values.

The expected outputs below were computed by hand from the PLAS contract (see the
derivation in docs/conformance.md), NOT read off the oracle. A test that only
checks the oracle against itself proves nothing; these literals are the
independent ground truth the oracle — and later the MPC circuit — must match.

Fixture: 3 parties, domain {0,1,2}, uniform prior, thresholds all 1/2,
secrets (0,0,1). Two invocations:
  inv1 = p1_is_max   real output 0
  inv2 = any_is_2    real output 0

Hand-derived facts:
  inv1: party 0 accepts (belief 9 -> 8 states), parties 1,2 reject.
  inv2: party 0 rejects (belief unchanged, stays 8 states),
        parties 1 and 2 accept.
"""

from fractions import Fraction

import pytest

from oracle import SmcBeliefTracking, REJECT

DOMAIN = [0, 1, 2]
SECRETS = (0, 0, 1)
THRESHOLDS = [Fraction(1, 2)] * 3

Q_P1_IS_MAX = lambda s: int(s[0] >= s[1] and s[0] >= s[2])
Q_ANY_IS_2 = lambda s: int(2 in s)

# Hand-derived expected recipient-visible outputs
EXPECTED_INV1 = [0, REJECT, REJECT]
EXPECTED_INV2 = [REJECT, 0, 0]


@pytest.fixture
def model():
    return SmcBeliefTracking(DOMAIN, SECRETS, THRESHOLDS)


def test_initial_belief_support_is_domain_squared(model):
    # delta_j = prior | (x_j = s_j): 3^3 states pinned on one coord -> 9 states.
    for j in range(3):
        assert len(model.beliefs[j]) == 9


def test_inv1_visible_outputs_match_hand_derivation(model):
    assert model.invoke(Q_P1_IS_MAX) == EXPECTED_INV1


def test_inv1_party0_belief_shrinks_to_8_states(model):
    model.invoke(Q_P1_IS_MAX)
    # accepted: delta_0 conditioned on p1_is_max == 0 removes exactly (x1,x2)=(0,0)
    assert len(model.beliefs[0]) == 8


def test_inv1_rejecting_parties_keep_initial_belief(model):
    before = [dict(b) for b in model.beliefs]
    model.invoke(Q_P1_IS_MAX)
    assert model.beliefs[1] == before[1]      # party 1 rejected -> unchanged
    assert model.beliefs[2] == before[2]      # party 2 rejected -> unchanged


def test_inv2_divergence_and_state_preservation(model):
    model.invoke(Q_P1_IS_MAX)
    after_inv1 = [dict(b) for b in model.beliefs]

    visible = model.invoke(Q_ANY_IS_2)
    assert visible == EXPECTED_INV2

    # per-recipient divergence: 0 rejects, 1 and 2 accept, same invocation
    assert visible[0] == REJECT
    assert visible[1] != REJECT and visible[2] != REJECT

    # THE property the mpc/ circuits violate: reject leaves belief untouched.
    assert model.beliefs[0] == after_inv1[0]

    # accepting parties did change
    assert model.beliefs[1] != after_inv1[1]
    assert model.beliefs[2] != after_inv1[2]


def test_reject_does_not_collapse_to_singleton(model):
    """The sharp version: on inv2 party 0's belief must NOT become the single
    posterior state it would if the reject had (wrongly) updated it."""
    model.invoke(Q_P1_IS_MAX)
    model.invoke(Q_ANY_IS_2)
    # had the reject wrongly updated, support would drop to 3 states.
    assert len(model.beliefs[0]) == 8


def test_state_signature_is_stable_across_reject(model):
    model.invoke(Q_P1_IS_MAX)
    sig_before = model.state_signature()[0]
    model.invoke(Q_ANY_IS_2)          # party 0 rejects
    sig_after = model.state_signature()[0]
    assert sig_before == sig_after
