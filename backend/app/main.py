"""App entry. Loads the seed once at startup."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from .routes import router
from .seed import load_splits

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "splits.json"
log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app):
    splits, problems = load_splits(SEED_PATH)
    # bad seed works are reported here and left out, so they are never paid
    for problem in problems:
        log.warning("Seed problem, work will not be paid: %s", problem)
    log.info("Loaded %d works from seed", len(splits))
    app.state.splits = splits
    yield


app = FastAPI(title="Royalty Split Calculator", lifespan=lifespan)
app.include_router(router)
