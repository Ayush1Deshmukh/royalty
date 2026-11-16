"""HTTP layer only. No parsing or money logic in here."""

from fastapi import APIRouter, File, HTTPException, Request, Response, UploadFile

from . import store
from .calculator import calculate
from .csv_out import shares_csv
from .parser import MAX_BYTES, FileRejected, parse_statement

router = APIRouter(prefix="/api")


def _summary(statement_id, result):
    # everything except the line breakdown
    summary = {"id": statement_id}
    summary.update({k: v for k, v in result.items() if k != "lineResults"})
    return summary


def _find(statement_id):
    result = store.get(statement_id)
    if result is None:
        raise HTTPException(404, f"Statement {statement_id} not found. Upload the file again.")
    return result


@router.post("/statements", status_code=201)
async def upload_statement(request: Request, file: UploadFile | None = File(None)):
    if file is None:
        raise HTTPException(400, "No file was sent. Choose a .csv file and upload it.")
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Only .csv files are accepted. Export the statement as CSV.")

    data = await file.read(MAX_BYTES + 1)  # +1 so parser can tell it's too big
    try:
        rows = parse_statement(data)
    except FileRejected as e:
        raise HTTPException(400, str(e))

    result = calculate(rows, request.app.state.splits)
    statement_id = store.save(result)
    return _summary(statement_id, result)


@router.get("/statements/{statement_id}")
def get_statement(statement_id: str):
    result = _find(statement_id)
    return {**_summary(statement_id, result), "lineResults": result["lineResults"]}


@router.get("/statements/{statement_id}/shares.csv")
def download_shares(statement_id: str):
    result = _find(statement_id)
    return Response(
        shares_csv(result["lineResults"]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="shares.csv"'},
    )
