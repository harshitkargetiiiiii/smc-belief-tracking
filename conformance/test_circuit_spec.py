"""
Boundary regressions for the three Step-4 interface rules (round-4b re-review).
No MPC circuit; these pin the rules the circuit must obey and assert the
public-alphabet formulation agrees with the oracle.
"""
from fractions import Fraction
from itertools import product

from oracle import SmcBeliefTracking, tcheck_passes
from circuit_spec import (
    public_output_alphabet, tcheck_public, signed_ring_ok, weight_bound,
    signed_read, masked_payload, MASK,
)

F = Fraction
DOMAIN = [0, 1, 2]
HALF = F(1, 2)
Q_P1_IS_MAX = lambda s: int(s[0] >= s[1] and s[0] >= s[2])
Q_SUM_EVEN = lambda s: int(sum(s) % 2 == 0)


# ---- rule 1: public alphabet == secret support, for the decision ----------

def test_public_alphabet_matches_support_decision():
    """Iterating the full public O_Q (incl. impossible branches) gives the same
    accept/reject as the oracle's support-based tcheck, on every belief that
    arises in the fixture."""
    alpha_max = public_output_alphabet(DOMAIN, 3, Q_P1_IS_MAX)
    alpha_even = public_output_alphabet(DOMAIN, 3, Q_SUM_EVEN)
    assert alpha_max == [0, 1] and alpha_even == [0, 1]

    m = SmcBeliefTracking(DOMAIN, (0, 0, 1), [HALF] * 3)
    for j in range(3):
        dj = m.beliefs[j]
        for i in range(3):
            if i != j:
                assert (tcheck_public(dj, Q_P1_IS_MAX, i, HALF, alpha_max)
                        == tcheck_passes(dj, Q_P1_IS_MAX, i, HALF))
    m.invoke(Q_SUM_EVEN)                     # advance to post-inv1 beliefs
    for j in range(3):
        dj = m.beliefs[j]
        for i in range(3):
            if i != j:
                assert (tcheck_public(dj, Q_P1_IS_MAX, i, HALF, alpha_max)
                        == tcheck_passes(dj, Q_P1_IS_MAX, i, HALF))


def test_impossible_branch_passes_vacuously():
    """A public output with zero probability under the belief must pass (0<=0),
    never reveal Z, never flip the decision."""
    # belief where Q never outputs 1 on the support
    m = SmcBeliefTracking([0, 1], (0, 0), [HALF, HALF])
    d0 = m.beliefs[0]
    q = lambda s: int(s[1] == 2)              # always 0 on domain {0,1}
    alpha = public_output_alphabet([0, 1], 2, q)   # public alphabet = {0}
    assert alpha == [0]
    # even if we force-include the impossible output 1, it passes vacuously
    from circuit_spec import branch_check_int
    assert branch_check_int(d0, q, 1, 1, 1, 2) is True   # Z=0 branch


def test_public_alphabet_agrees_randomized():
    import itertools
    secrets_space = list(itertools.product(DOMAIN, repeat=3))
    for secrets in secrets_space[:12]:
        for t in (HALF, F(2, 3)):
            m = SmcBeliefTracking(DOMAIN, secrets, [t] * 3)
            for q in (Q_P1_IS_MAX, Q_SUM_EVEN):
                alpha = public_output_alphabet(DOMAIN, 3, q)
                for j in range(3):
                    for i in range(3):
                        if i != j:
                            assert (tcheck_public(m.beliefs[j], q, i, t, alpha)
                                    == tcheck_passes(m.beliefs[j], q, i, t))


# ---- rule 2: signed no-wraparound bound ----------------------------------

def test_fixture_bit_bound_is_satisfied_by_64bit_signed():
    # fixture: S = 3^3 = 27, filter-only W = 1, t = 1/2 -> a=1,b=2
    B = weight_bound(1, 2, 27, 1)
    assert B == 54
    assert signed_ring_ok(B, 64) is True


def test_naive_bound_is_wrong_for_signed_comparison():
    """Codex counterexample: modulus 2^7=128, B=120 passes the naive 2^k>B, but
    the signed range is only 2^(k-1)=64, and the check misreads."""
    B = weight_bound(1, 2, 60, 1)            # 2*60 = 120
    assert B == 120
    assert (1 << 7) > B                       # naive '2^k > B' would accept the ring
    assert signed_ring_ok(B, 7) is False      # correct signed rule rejects it
    assert signed_ring_ok(B, 8) is True       # k=8 is enough

    # the concrete misread: check 2*35 <= 1*60 (i.e. 70 <= 60) must be False
    M, Z, a, b = 35, 60, 1, 2
    assert (b * M <= a * Z) is False          # correct decision: reject
    assert signed_read(b * M, 7) == -58       # 70 reads as -58 in signed 7-bit
    assert (signed_read(b * M, 7) <= a * Z) is True   # WRONG accept under too-small ring


# ---- rule 3: fixed masking on reject -------------------------------------

def test_reject_payload_is_fixed_and_output_independent():
    for o in range(5):
        assert masked_payload(False, o) == MASK      # reject payload independent of o
    for o in range(5):
        assert masked_payload(True, o) == o          # accept carries the real output
