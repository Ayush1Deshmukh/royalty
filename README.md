# Royalty Split Calculator

Upload a royalty statement CSV and get back a CSV showing how much each writer
is owed.

- `backend/` : Python, FastAPI. Data is kept in memory.
- `frontend/` : React, Vite.

## How to run

Needs Python 3.10+ and Node 20+. Use two terminals.

**1. Backend** (runs on http://localhost:8000)

```bash
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/uvicorn app.main:app --port 8000
```

**2. Frontend** (runs on http://localhost:5173)

```bash
cd frontend && npm install && npm run dev
```

Open http://localhost:5173 and upload a CSV. A sample file can be downloaded
from the page.

**Tests**

```bash
cd backend && .venv/bin/pytest
```

## Rounding rule

Money is handled as whole cents, never floating point.

1. Each writer gets their share, rounded down to the cent.
2. Leftover cents go one by one to the writers with the largest remainder.
3. On a tie, the writer listed first in `splits.json` gets the cent.

The lines of a work always add up exactly to its statement amount.
Example: 10.00 split 33.33 / 33.33 / 33.34 gives 3.33 / 3.33 / 3.34.

## Duplicate rule

If the same work id appears more than once in a statement, the amounts are
added together and split once.

## Other decisions

- Bad rows are listed in `errors` with their row number. The header is row 1.
  Bad rows add no money, and the rest of the file still processes.
- `fileTotal` is the sum of the valid rows, and always equals
  `allocatedTotal + unmatchedTotal`. The API returns a `reconciled` flag so
  the UI does no money calculation.
- A work id that is not in the seed stays in the output as `UNMATCHED`.
- A seed work whose shares do not total 100 is reported in the server log at
  startup and is never paid.
- The currency picker only changes the symbol shown. Nothing is converted.

## What I would add next

- Tests for the CSV parser and the API routes.
- Show seed problems in the UI, not only in the server log.
- Save statements so they survive a restart.
- A currency column in the statement file.
