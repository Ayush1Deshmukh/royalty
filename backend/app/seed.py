"""Load splits.json. Works whose shares don't total 100 are reported, not paid."""

import json
from decimal import Decimal

from .calculator import BP_TOTAL


def load_splits(path):
    """Returns (splits, problems).

    splits: {work_id: [(writer, share_bp), ...]}, only valid works.
    problems: list of messages for works that were left out.
    """
    with open(path, encoding="utf-8") as f:
        works = json.load(f, parse_float=Decimal)  # keep 33.33 exact, no float

    splits = {}
    problems = []
    for work in works:
        work_id = work["workId"]
        writers = []
        for w in work["writers"]:
            bp = Decimal(w["share"]) * 100  # percent -> basis points
            if bp != bp.to_integral_value() or bp < 0:
                problems.append(f"{work_id}: share {w['share']} for {w['name']} is not valid")
                break
            writers.append((w["name"], int(bp)))
        else:
            total = sum(bp for _, bp in writers)
            if total != BP_TOTAL:
                problems.append(
                    f"{work_id}: shares total {Decimal(total) / 100}, expected 100"
                )
            else:
                splits[work_id] = writers
    return splits, problems
