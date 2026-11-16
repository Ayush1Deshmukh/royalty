"""In-memory statement store. Gone on restart, fine for this app."""

_statements = {}


def save(result):
    """Stores a result, returns its id: st_01, st_02, ..."""
    statement_id = f"st_{len(_statements) + 1:02d}"
    _statements[statement_id] = result
    return statement_id


def get(statement_id):
    return _statements.get(statement_id)
