from __future__ import annotations
import csv
import io
from typing import Iterable, Dict, Any


def rows_to_csv(rows: Iterable[Dict[str, Any]], field_order: list[str] | None = None) -> bytes:
    """Render an iterable of dict rows to CSV bytes using UTF‑8.
    If field_order is None, infer from first row.
    """
    buf = io.StringIO()
    it = iter(rows)
    try:
        first = next(it)
    except StopIteration:
        # empty CSV
        buf.write("\n")
        return buf.getvalue().encode("utf-8")

    if field_order is None:
        field_order = list(first.keys())

    writer = csv.DictWriter(buf, fieldnames=field_order, extrasaction="ignore")
    writer.writeheader()
    writer.writerow(first)
    for r in it:
        writer.writerow(r)

    return buf.getvalue().encode("utf-8")
