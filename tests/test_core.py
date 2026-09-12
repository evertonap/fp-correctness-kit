"""Regression tests that double as documentation of classic float pitfalls."""

from decimal import Decimal
from fractions import Fraction

from fp_audit.core import audit, to_decimal, ulp_distance, worst_offenders


def test_ulp_distance_zero_for_equal_values():
    assert ulp_distance(1.0, 1.0) == 0.0


def test_to_decimal_matches_exact_binary_value():
    # 0.1 cannot be represented exactly in binary64; Decimal(0.1) exposes
    # the real stored value instead of the rounded "0.1" repr.
    d = to_decimal(0.1)
    assert d != Decimal("0.1")
    assert abs(d - Decimal("0.1")) < Decimal("1E-16")


def test_audit_flags_classic_summation_error():
    def float_sum(a, b, c):
        return a + b + c

    def reference_sum(a, b, c):
        # These three floats are meant to represent the exact decimals
        # 0.1, 0.2 and -0.3, not their binary64 approximations.
        exact = {0.1: Fraction(1, 10), 0.2: Fraction(2, 10), -0.3: Fraction(-3, 10)}
        return to_decimal(exact[a] + exact[b] + exact[c])

    inputs = [(0.1, 0.2, -0.3)]
    reports = audit(float_sum, reference_sum, inputs)
    assert reports[0].abs_error > 0


def test_worst_offenders_orders_by_ulp_error():
    def f(x):
        return x

    def ref(x):
        return to_decimal(x)

    reports = audit(f, ref, [(1.0,), (2.0,), (3.0,)])
    ranked = worst_offenders(reports, n=2)
    assert len(ranked) == 2
