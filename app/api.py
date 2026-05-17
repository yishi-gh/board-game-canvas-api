from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, HTTPException

from app.report_service import generate_report
from app.schemas import GenerateReportRequest, GenerateReportResponse
from app.template_loader import validate_required_templates


@asynccontextmanager
async def lifespan(_: FastAPI):
    validate_required_templates()
    yield


app = FastAPI(
    title="board-game-canvas-api",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "board-game-canvas-api", "status": "ok"}


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/generate_report", response_model=GenerateReportResponse)
def generate_report_endpoint(payload: GenerateReportRequest) -> GenerateReportResponse:
    try:
        return generate_report(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream request failed: {exc}",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
