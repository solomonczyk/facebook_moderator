"""FastAPI application entry point for the aggregator API."""

from fastapi import FastAPI
from .api import router
from .database import init_db

app = FastAPI(
    title="Sezonski rad Srbija — Lead Intake API",
    description="Source-agnostic seasonal work lead aggregator for Serbia.",
    version="0.1.0",
)

app.include_router(router)


@app.on_event("startup")
def on_startup():
    init_db()


if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
