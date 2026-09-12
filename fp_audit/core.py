"""
fp_audit.core
=============

Small toolkit for auditing floating-point rounding behaviour.

The idea: take a computation that will run in `float` (binary64) and
compare it against a "reference" computation done in exact or
higher-precision arithmetic (`Decimal` or `Fraction`). The difference
between the two tells you whether an implementation is accurate enough,
and by how much it drifts, expressed both in absolute/relative error and
in ULPs (units in the last place).

This is a demonstration/portfolio project, not a production dependency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
from typing import Callable, Iterable, Sequence

getcontext().prec = 50


@dataclass(frozen=True)
class RoundingReport:
    """Result of comparing a float value against a high-precision reference."""

    input: tuple
    float_result: float
    reference: Decimal
    abs_error: Decimal
    rel_error: Decimal
    ulp_error: float

    def __str__(self) -> str:
        return (
            f"input={self.input!r} float={self.float_result!r} "
            f"ref={self.reference} abs_err={self.abs_error:.3E} "
            f"rel_err={self.rel_error:.3E} ulp_err={self.ulp_error:.3f}"
        )


def ulp(x: float) -> float:
    """Return the size of one unit in the last place at `x`."""
    if x == 0.0:
        return math.ulp(0.0)
    return math.ulp(x)


def ulp_distance(a: float, b: float) -> float:
    """Approximate distance between two floats measured in ULPs of `a`."""
    if a == b:
        return 0.0
    step = ulp(a) or ulp(b)
    if step == 0:
        return float("inf")
    return abs(a - b) / step


def to_decimal(value) -> Decimal:
    """Convert an int, float, Fraction or Decimal into an exact Decimal.

    Floats are converted through their exact binary value (`Decimal(float)`
    already does this correctly in Python), not through their repr string.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, Fraction):
        return Decimal(value.numerator) / Decimal(value.denominator)
    return Decimal(value)


def audit(
    float_fn: Callable[..., float],
    reference_fn: Callable[..., Decimal],
    inputs: Iterable[Sequence],
) -> list[RoundingReport]:
    """Run `float_fn` and `reference_fn` over `inputs` and report drift.

    `float_fn` is the implementation under test, evaluated in `float`.
    `reference_fn` must return an exact (or high-precision) `Decimal`
    for the same arguments.
    """
    reports = []
    for args in inputs:
        fval = float_fn(*args)
        ref = reference_fn(*args)
        fdec = to_decimal(fval)
        abs_err = abs(fdec - ref)
        rel_err = abs_err / ref if ref != 0 else abs_err
        reports.append(
            RoundingReport(
                input=tuple(args),
                float_result=fval,
                reference=ref,
                abs_error=abs_err,
                rel_error=rel_err,
                ulp_error=ulp_distance(fval, float(ref)),
            )
        )
    return reports


def worst_offenders(reports: list[RoundingReport], n: int = 5) -> list[RoundingReport]:
    """Return the `n` reports with the largest ULP error."""
    return sorted(reports, key=lambda r: r.ulp_error, reverse=True)[:n]
