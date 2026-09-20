"""Shared drawer-front divisions (bottom to top) for UI, geometry, Cut List.

Legacy custom data: n-1 numbers, with the TOP drawer calculated automatically.
New custom data: n values, exactly one `null` (Python None), marking whichever
front is calculated. All other values are explicit millimetre heights.
"""
import json

MIN_FRONT = 10.0


def decode(raw):
    """Return a validated list of explicit dimensions and optionally one None."""
    if isinstance(raw, (list, tuple)):
        seq = raw
    else:
        try:
            seq = json.loads(raw or "[]")
        except (TypeError, ValueError):
            return []
    if not isinstance(seq, (list, tuple)):
        return []
    try:
        result = [None if x is None else float(x) for x in seq]
    except (ValueError, TypeError, OverflowError):
        return []
    if sum(x is None for x in result) > 1:
        return []
    if any(x is not None and not (MIN_FRONT <= x <= 10000) for x in result):
        return []
    return result


def auto_index(custom, count):
    """Auto front index; for legacy data the last front remains automatic."""
    values = decode(custom)
    if len(values) == count and values.count(None) == 1:
        return values.index(None)
    return max(0, count - 1)


def heights(total, count, gap, custom=None):
    """Return complete heights bottom-to-top, or [] if the split is invalid.

    A single automatic front consumes the exact space after all explicit fronts
    and (count-1) Front Gaps. Invalid/stale count falls back to equal heights.
    """
    count = int(count)
    if count < 1:
        return []
    usable = float(total) - max(0.0, float(gap)) * (count - 1)
    if usable < count * MIN_FRONT - 0.001:
        return []
    values = decode(custom)
    if len(values) == count - 1 and None not in values:
        values = values + [None]  # compatibility with 0.5 documents
    if len(values) != count or values.count(None) != 1:
        return [usable / count] * count
    remaining = usable - sum(v for v in values if v is not None)
    if remaining < MIN_FRONT - 0.001 or remaining > 10000.001:
        return []
    return [remaining if value is None else value for value in values]
