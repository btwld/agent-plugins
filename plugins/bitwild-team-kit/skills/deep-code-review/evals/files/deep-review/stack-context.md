# Stacked PR snapshot

This is a complete text snapshot for review, not a live checkout. Review only the
increment from immediate parent `edbb87f17aa967a24813b8086c5c4734b04a2499` to head `72353c1c4f72e86966bc8b6d62ec7d6d4b40246a`. Merge order is main,
stack-parent, review-target. `change.patch` contains the whole increment.

PR description: Add retry configuration parsing and clarify currency naming while
preserving the public formatting API. Python 3.11+; standard library only.

## Repository instructions (already present on the parent)

This is a Python 3.11+ standard-library-only package.
Preserve documented keyword arguments. Use unittest discovery for tests.
Regression fixtures under tests/fixtures are loaded by glob.
Keep one-off scratch notes and agent transcripts outside the repository.
Review only; do not modify this repository.

## README (unchanged)

# Pricing
Use format_price(1.25, currency="EUR") to get "EUR 1.25".

## pricing.py on the immediate parent

```python
def format_price(amount, currency="USD"):
    return f"{currency} {amount:.2f}"


def clamp_discount(value):
    """Return a percentage bounded to the inclusive interval [0, 100]."""
    return min(value, 100)
```

The fixtures are read through the glob in the added test. There are no additional
build, packaging, or documentation consumers. The scratch directory is new.
