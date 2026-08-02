"""
Conformance tests, ALL-OUTPUTS semantics (corrected after round 3).

Expected values are HAND-DERIVED from the PLAS contract, not read off the
oracle. The centerpiece, test_discriminating_case, computes BOTH the correct
all-outputs decision and the buggy actual-output-only decision and asserts they
DIFFER — so it pins the exact error round 3 found and cannot pass if the oracle
reverts to actual-only.
"""
from fractions import Fraction

import pytest

from oracle import (
    SmcBeliefTracking, REJECT, condition, tcheck_passes, marginal_max,
)

F = Fraction
DOMAIN = [0, 1, 2]
HALF = F(1, 2)

Q_P1_IS_MAX = lambda s: int(s[0] >= s[1] and s[0] >= s[2])
Q_SUM_EVEN = lambda s: int(sum(s) % 2 == 0)


# ============================================================
# Scenario 1 — the discriminating regression (the important one)
# Fresh model, secrets (0,0,1), t=1/2, query p1_is_max, recipient 0.
# Hand derivation (CONTRACT.md):
#   delta_0 = uniform over {(0,x1,x2)} = 9 states.
#   actual output 0 -> branch excludes (0,0,0): 8 states, x1 marginal max 3/8.
#     => actual-output-only check would ACCEPT (3/8 <= 1/2).
#   alternate output 1 -> only (0,0,0): x1 marginal = 1 > 1/2.
#     => correct all-outputs check REJECTS.
# ============================================================

def test_discriminating_case():
    m = SmcBeliefTracking(DOMAIN, (0, 0, 1), [HALF] * 3)
    d0 = m.beliefs[0]
    assert len(d0) == 9

    # actual output branch: safe on its own
    actual = condition(d0, lambda s: Q_P1_IS_MAX(s) == 0)
    assert len(actual) == 8
    assert marginal_max(actual, 1) == F(3, 8)
    assert marginal_max(actual, 1) <= HALF          # actual-only would accept

    assert marginal_max(actual, 2) == F(3, 8)       # symmetric in x2
    assert marginal_max(actual, 2) <= HALF

    # alternate output branch: unsafe, symmetrically in x1 and x2
    alt = condition(d0, lambda s: Q_P1_IS_MAX(s) == 1)
    assert alt == {(0, 0, 0): F(1)}
    assert marginal_max(alt, 1) == F(1)             # > 1/2
    assert marginal_max(alt, 2) == F(1)             # > 1/2

    # correct semantics rejects on either protected party; the two decisions differ
    assert tcheck_passes(d0, Q_P1_IS_MAX, 1, HALF) is False
    assert tcheck_passes(d0, Q_P1_IS_MAX, 2, HALF) is False

    visible = m.invoke(Q_P1_IS_MAX)
    assert visible[0] == REJECT                     # recipient 0 rejects
    assert m.beliefs[0] == d0                       # reject leaves belief intact


# ============================================================
# Scenario 2 — divergence + accept-then-reject state preservation
# secrets (0,0,1), t=1/2. inv1 sum_even -> all accept; inv2 p1_is_max.
# (This fixture does NOT distinguish the two semantics; Scenario 1 does.
#  It is here for divergence and reject-state-preservation only.)
# ============================================================

def test_inv1_all_accept_and_change():
    m = SmcBeliefTracking(DOMAIN, (0, 0, 1), [HALF] * 3)
    before = [dict(b) for b in m.beliefs]
    assert m.invoke(Q_SUM_EVEN) == [0, 0, 0]
    for j in range(3):
        assert m.beliefs[j] != before[j]            # every accept changed belief
    assert len(m.beliefs[2]) == 5                    # sum-odd branch


def test_inv2_divergence_and_reject_preserves_state():
    m = SmcBeliefTracking(DOMAIN, (0, 0, 1), [HALF] * 3)
    m.invoke(Q_SUM_EVEN)
    after1 = [dict(b) for b in m.beliefs]

    visible = m.invoke(Q_P1_IS_MAX)
    assert visible == [0, 0, REJECT]                 # divergence: 0,1 accept; 2 rejects
    assert visible[2] == REJECT
    assert visible[0] != REJECT and visible[1] != REJECT

    assert m.beliefs[2] == after1[2]                 # THE preserved-state property
    assert len(m.beliefs[2]) == 5                    # did not collapse
    assert m.beliefs[1] != after1[1]                 # an accepting party did change


# ============================================================
# Unit tests on the primitives, with explicit hand-built beliefs
# ============================================================

def _uniform_2x2():
    return {(a, b): F(1, 4) for a in (0, 1) for b in (0, 1)}


def test_equality_boundary_allowed():
    """Every branch's marginal is exactly 1/2; '<=' accepts, strict '<' would not."""
    b = _uniform_2x2()
    q = lambda s: s[0]                               # outputs {0,1}, each splits x1 evenly
    assert tcheck_passes(b, q, 1, HALF) is True      # 1/2 <= 1/2
    assert tcheck_passes(b, q, 1, F(2, 5)) is False  # 1/2 > 2/5


def test_unrealized_output_not_checked():
    b = _uniform_2x2()
    q = lambda s: int(s[0] == 7)                     # always 0 on this support
    assert {q(s) for s in b} == {0}
    assert tcheck_passes(b, q, 1, HALF) is True      # sole branch marginal 1/2


def test_condition_on_impossible_raises():
    with pytest.raises(ValueError):
        condition(_uniform_2x2(), lambda s: False)


def test_non_uniform_prior_rejects():
    # delta_0 = prior|(x0=0) = {(0,0):2/3,(0,1):1/3}; Q="x1==0".
    # alternate output 1 => x1=0 with certainty => reject.
    prior = {(0, 0): F(1, 2), (0, 1): F(1, 4), (1, 0): F(1, 8), (1, 1): F(1, 8)}
    m = SmcBeliefTracking([0, 1], (0, 0), [HALF, HALF], prior)
    assert m.invoke(lambda s: int(s[1] == 0)) == [REJECT, REJECT]


def test_inconsistent_prior_raises():
    with pytest.raises(ValueError):
        SmcBeliefTracking([0, 1], (1, 1), [HALF, HALF], {(0, 0): F(1)})


def test_threshold_out_of_range_raises():
    with pytest.raises(ValueError):
        SmcBeliefTracking([0, 1], (0, 0), [F(0), HALF])
    with pytest.raises(ValueError):
        SmcBeliefTracking([0, 1], (0, 0), [F(3, 2), HALF])


# ---- round-4 blockers: zero-mass and negative-mass support -------------

def test_zero_mass_key_is_not_a_possible_output():
    """Codex counterexample: a zero-mass key must not invent a possible output,
    and must not cause a conditioning error. support([[q]]b) = {0}, accept at
    equality t=1."""
    from oracle import possible_outputs
    b = {(0, 0): F(1), (1, 0): F(0)}
    q = lambda s: s[0]
    assert possible_outputs(b, q) == {0}
    assert tcheck_passes(b, q, 1, F(1)) is True


def test_negative_mass_prior_raises():
    with pytest.raises(ValueError):
        SmcBeliefTracking([0, 1], (0, 0), [HALF, HALF],
                          {(0, 0): F(5, 4), (0, 1): F(-1, 4)})


def test_zero_mass_prior_entry_is_pruned_not_counted():
    # a prior carrying an explicit zero entry is accepted (pruned), and the zero
    # state is not part of any belief's support.
    prior = {(0, 0): F(1, 2), (0, 1): F(1, 2), (1, 0): F(0), (1, 1): F(0)}
    m = SmcBeliefTracking([0, 1], (0, 0), [HALF, HALF], prior)
    for b in m.beliefs:
        assert all(p > 0 for p in b.values())
    assert (1, 0) not in m.beliefs[0] and (1, 1) not in m.beliefs[0]


def test_negative_mass_belief_raises_in_helpers():
    """Support invariant enforced at every boundary, not just the constructor.
    Codex round-4b counterexample: helpers must RAISE, not silently drop."""
    bad = {(0, 0): F(5, 4), (0, 1): F(-1, 4)}
    with pytest.raises(ValueError):
        condition(bad, lambda s: True)
    with pytest.raises(ValueError):
        tcheck_passes(bad, lambda s: s[0], 1, F(1))
    from oracle import marginal_max as mm, possible_outputs as po
    with pytest.raises(ValueError):
        mm(bad, 0)
    with pytest.raises(ValueError):
        po(bad, lambda s: s[0])
