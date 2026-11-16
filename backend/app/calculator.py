"""Split calc. Pure func: rows + splits in, result dict out. No I/O here.

Money is int cents, shares are int basis points (33.33% -> 3333). No floats.
"""

import re

UNMATCHED = "UNMATCHED"
BP_TOTAL = 10000  # 100.00% in basis points

_NUMBER_RE = re.compile(r"^-?\d+(\.\d+)?$")


def fmt(value):
    """int cents (or basis points) -> '12.34'."""
    return f"{value // 100}.{value % 100:02d}"


def parse_amount(text):
    """'12.5' -> (1250, None). On bad input -> (None, reason)."""
    if text == "":
        return None, "amount is missing. Add a number like 12.50"
    if not _NUMBER_RE.match(text):
        return None, "amount is not a number. Use plain digits like 12.50, no symbols or commas"
    if text.startswith("-"):
        return None, "amount is negative. Amounts must be 0 or more"
    whole, _, frac = text.partition(".")
    if len(frac) > 2:
        return None, "amount has more than 2 decimal places. Round it to cents, like 12.50"
    return int(whole) * 100 + int(frac.ljust(2, "0")), None


def split_cents(total, shares_bp):
    """Split total cents by shares. Parts always sum to total.

    Rule: floor every part, then hand leftover cents one by one to the
    largest remainder. Tie -> writer listed first in the seed wins.
    """
    raw = [total * bp for bp in shares_bp]
    parts = [r // BP_TOTAL for r in raw]
    leftover = total - sum(parts)
    # biggest remainder first, index breaks ties
    order = sorted(range(len(raw)), key=lambda i: (-(raw[i] % BP_TOTAL), i))
    for i in order[:leftover]:
        parts[i] += 1
    return parts


def calculate(rows, splits):
    """rows: [(row_no, [cells])] from the parser.
    splits: {work_id: [(writer, share_bp), ...]} from the seed.
    """
    errors = []
    works = {}  # work_id -> [title, cents]. dict keeps first-seen order
    file_total = 0
    matched_lines = 0

    for row_no, cells in rows:
        if len(cells) != 3:
            errors.append({
                "row": row_no,
                "reason": f"expected 3 columns but found {len(cells)}. "
                          "Each row needs work_id,title,amount. Quote values that contain commas",
            })
            continue
        work_id, title, amount = (c.strip() for c in cells)
        if not work_id:
            errors.append({"row": row_no, "reason": "work_id is missing. Add the work id"})
            continue
        cents, reason = parse_amount(amount)
        if reason:
            errors.append({"row": row_no, "reason": reason})
            continue

        file_total += cents
        if work_id in splits:
            matched_lines += 1
        # dup work id in same file -> add amounts, split once
        if work_id in works:
            works[work_id][1] += cents
        else:
            works[work_id] = [title, cents]

    line_results = []
    writer_cents = {}
    allocated = 0
    unmatched = 0

    for work_id, (title, cents) in works.items():
        writers = splits.get(work_id)
        if writers is None:
            # not in seed -> keep the money visible, never drop it
            unmatched += cents
            line_results.append({
                "workId": work_id, "title": title, "writer": UNMATCHED,
                "sharePercent": "", "amount": fmt(cents),
            })
            continue

        parts = split_cents(cents, [bp for _, bp in writers])
        for (writer, bp), part in zip(writers, parts):
            allocated += part
            writer_cents[writer] = writer_cents.get(writer, 0) + part
            line_results.append({
                "workId": work_id, "title": title, "writer": writer,
                "sharePercent": fmt(bp), "amount": fmt(part),
            })

    # highest amount first, name breaks ties
    writer_totals = [
        {"writer": w, "amount": fmt(c)}
        for w, c in sorted(writer_cents.items(), key=lambda x: (-x[1], x[0]))
    ]

    return {
        "fileTotal": fmt(file_total),
        "allocatedTotal": fmt(allocated),
        "unmatchedTotal": fmt(unmatched),
        # checked here so the UI never does money math
        "reconciled": file_total == allocated + unmatched,
        "lines": len(rows),
        "matchedLines": matched_lines,
        "errors": errors,
        "writerTotals": writer_totals,
        "lineResults": line_results,
    }
