# fp-correctness-kit

Small toolkit for auditing floating-point rounding behaviour: given a computation implemented in `float` and a reference implementation done in exact or high-precision arithmetic (`Decimal` / `Fraction`), it reports the absolute error, relative error, and the drift expressed in ULPs (units in the last place).

This is a portfolio/demonstration project - a compact version of the kind of instrumentation used to sanity-check numerically sensitive code before trusting it in production.

## Why

Floating-point numbers are a finite, binary approximation of the reals. Two implementations of "the same" formula can silently diverge once you introduce reordered sums, mixed magnitudes, or repeated rounding. This toolkit makes that divergence visible and measurable instead of anecdotal.

## Example

```python
from decimal import Decimal
from fp_audit.core import audit, worst_offenders, to_decimal

def price_float(qty, price, fee_bps):
    return qty * price * (1 + fee_bps / 10_000)

def price_reference(qty, price, fee_bps):
    q, p, f = to_decimal(qty), to_decimal(price), to_decimal(fee_bps)
    return q * p * (1 + f / Decimal(10_000))

inputs = [(100, 19.99, 12.5), (1, 0.1, 5)]
reports = audit(price_float, price_reference, inputs)
for r in worst_offenders(reports):
    print(r)
```

## Layout

- `fp_audit/core.py` - the audit primitives (`audit`, `ulp_distance`, `to_decimal`, `worst_offenders`).
- `tests/test_core.py` - regression tests, several of which double as documentation of classic floating-point pitfalls.

## Status

Demo/portfolio project, not a published package.
