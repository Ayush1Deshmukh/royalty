"""Line results -> shares.csv text."""

import csv
import io


def shares_csv(line_results):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["work_id", "title", "writer", "share_percent", "amount"])
    for line in line_results:
        writer.writerow([
            line["workId"], line["title"], line["writer"],
            line["sharePercent"], line["amount"],
        ])
    return out.getvalue()
