from app.calculator import calculate, split_cents

SPLITS = {
    "MNT000001": [("Alice Brown", 5000), ("Ben Cole", 5000)],
    "MNT000002": [("Alice Brown", 7000), ("Dana Fox", 3000)],
    "MNT000003": [("Ben Cole", 3333), ("Dana Fox", 3333), ("Eli Grant", 3334)],
}

# same data as the sample statement.csv (row 1 is the header)
SAMPLE_ROWS = [
    (2, ["MNT000001", "Midnight Drive", "100.00"]),
    (3, ["MNT000002", "Paper Moon", "10.00"]),
    (4, ["MNT000003", "Cold Harbour", "10.00"]),
    (5, ["MNT999999", "Unknown Song", "5.00"]),
]


def cents(text):
    whole, frac = text.split(".")
    return int(whole) * 100 + int(frac)


def amounts(result, work_id):
    return [l["amount"] for l in result["lineResults"] if l["workId"] == work_id]


def test_rounding_last_cent_goes_to_largest_remainder():
    result = calculate([(2, ["MNT000003", "Cold Harbour", "10.00"])], SPLITS)
    assert amounts(result, "MNT000003") == ["3.33", "3.33", "3.34"]


def test_rounding_tie_goes_to_first_writer():
    # 0.01 split 50/50 -> equal remainders, first writer gets the cent
    assert split_cents(1, [5000, 5000]) == [1, 0]


def test_split_always_adds_up():
    shares = [3333, 3333, 3334]
    for total in range(0, 2000):
        assert sum(split_cents(total, shares)) == total


def test_sample_statement_matches_expected_output():
    result = calculate(SAMPLE_ROWS, SPLITS)
    got = [
        (l["workId"], l["writer"], l["sharePercent"], l["amount"])
        for l in result["lineResults"]
    ]
    assert got == [
        ("MNT000001", "Alice Brown", "50.00", "50.00"),
        ("MNT000001", "Ben Cole", "50.00", "50.00"),
        ("MNT000002", "Alice Brown", "70.00", "7.00"),
        ("MNT000002", "Dana Fox", "30.00", "3.00"),
        ("MNT000003", "Ben Cole", "33.33", "3.33"),
        ("MNT000003", "Dana Fox", "33.33", "3.33"),
        ("MNT000003", "Eli Grant", "33.34", "3.34"),
        ("MNT999999", "UNMATCHED", "", "5.00"),
    ]
    assert result["writerTotals"] == [
        {"writer": "Alice Brown", "amount": "57.00"},
        {"writer": "Ben Cole", "amount": "53.33"},
        {"writer": "Dana Fox", "amount": "6.33"},
        {"writer": "Eli Grant", "amount": "3.34"},
    ]
    assert result["lines"] == 4
    assert result["matchedLines"] == 3
    assert result["errors"] == []


def test_unmatched_work_is_kept_not_dropped():
    result = calculate([(2, ["MNT999999", "Unknown Song", "5.00"])], SPLITS)
    assert result["lineResults"] == [{
        "workId": "MNT999999", "title": "Unknown Song", "writer": "UNMATCHED",
        "sharePercent": "", "amount": "5.00",
    }]
    assert result["unmatchedTotal"] == "5.00"
    assert result["allocatedTotal"] == "0.00"
    assert result["writerTotals"] == []


def test_bad_rows_are_reported_and_rest_still_processes():
    rows = [
        (2, ["MNT000001", "Midnight Drive", "100.00"]),
        (3, ["MNT000002", "Paper Moon", ""]),        # missing amount
        (4, ["MNT000002", "Paper Moon", "abc"]),     # not a number
        (5, ["MNT000002", "Paper Moon", "-4.00"]),   # negative
        (6, ["", "No Id", "4.00"]),                  # missing work id
        (7, ["MNT000002", "Paper Moon", "1.005"]),   # too many decimals
        (8, ["MNT000002", "Paper", "Moon", "1.00"]), # extra column
    ]
    result = calculate(rows, SPLITS)

    assert [e["row"] for e in result["errors"]] == [3, 4, 5, 6, 7, 8]
    reasons = [e["reason"] for e in result["errors"]]
    assert reasons[0].startswith("amount is missing")
    assert reasons[1].startswith("amount is not a number")
    assert reasons[2].startswith("amount is negative")
    assert reasons[3].startswith("work_id is missing")
    assert reasons[4].startswith("amount has more than 2 decimal places")
    assert reasons[5].startswith("expected 3 columns but found 4")

    # good row still paid, bad rows add no money
    assert result["fileTotal"] == "100.00"
    assert amounts(result, "MNT000001") == ["50.00", "50.00"]
    assert result["lines"] == 7
    assert result["matchedLines"] == 1


def test_reconciliation_is_exact():
    result = calculate(SAMPLE_ROWS, SPLITS)
    assert result["fileTotal"] == "125.00"
    assert result["allocatedTotal"] == "120.00"
    assert result["unmatchedTotal"] == "5.00"
    assert result["reconciled"] is True

    # check it from the lines too, in int cents
    lines = result["lineResults"]
    paid = sum(cents(l["amount"]) for l in lines if l["writer"] != "UNMATCHED")
    unpaid = sum(cents(l["amount"]) for l in lines if l["writer"] == "UNMATCHED")
    assert paid == cents(result["allocatedTotal"])
    assert unpaid == cents(result["unmatchedTotal"])
    assert paid + unpaid == cents(result["fileTotal"])
    assert sum(cents(w["amount"]) for w in result["writerTotals"]) == paid


def test_each_work_adds_up_to_its_statement_amount():
    rows = [(2, ["MNT000003", "Cold Harbour", "0.01"]),
            (3, ["MNT000002", "Paper Moon", "99.99"])]
    result = calculate(rows, SPLITS)
    assert sum(cents(a) for a in amounts(result, "MNT000003")) == 1
    assert sum(cents(a) for a in amounts(result, "MNT000002")) == 9999


def test_duplicate_work_ids_are_added_together():
    rows = [
        (2, ["MNT000003", "Cold Harbour", "5.00"]),
        (3, ["MNT000003", "Cold Harbour", "5.00"]),
    ]
    result = calculate(rows, SPLITS)
    # split once on 10.00, not twice on 5.00
    assert amounts(result, "MNT000003") == ["3.33", "3.33", "3.34"]
    assert result["lines"] == 2
    assert result["matchedLines"] == 2
    assert result["fileTotal"] == "10.00"
