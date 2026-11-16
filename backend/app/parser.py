"""CSV bytes -> rows. Only file-level checks here, row checks live in calculator."""

import csv
import io

MAX_BYTES = 5 * 1024 * 1024  # 5 MB
HEADER = ["work_id", "title", "amount"]


class FileRejected(Exception):
    """Whole file is bad -> route turns this into a 400."""


def parse_statement(data):
    """Returns [(row_no, [cells])]. row_no is the line in the file, header = 1."""
    if len(data) > MAX_BYTES:
        raise FileRejected("File is over 5 MB. Split it into smaller files and upload each one.")
    try:
        text = data.decode("utf-8-sig")  # -sig drops the Excel BOM
    except UnicodeDecodeError:
        raise FileRejected("File is not readable text. Save it as a UTF-8 CSV and try again.")
    if not text.strip():
        raise FileRejected("File is empty. It needs a header row: work_id,title,amount")

    reader = csv.reader(io.StringIO(text, newline=""))
    rows = []
    header = None
    try:
        for cells in reader:
            if not any(c.strip() for c in cells) and len(cells) <= 1:
                continue  # blank line
            if header is None:
                header = [c.strip().lower() for c in cells]
                if header != HEADER:
                    raise FileRejected(
                        "Wrong or missing header. The first row must be exactly: "
                        f"work_id,title,amount (found: {','.join(cells)[:80]})"
                    )
                continue
            rows.append((reader.line_num, cells))
    except csv.Error:
        raise FileRejected("File is not a valid CSV. Export it again as CSV and try again.")
    return rows
