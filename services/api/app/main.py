"""
CodeFort API — Main application entry point.

Build with confidence.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add shared schemas to path
_SCHEMAS_PATH = str(Path(__file__).resolve().parent.parent.parent.parent / "packages" / "schemas" / "python")
if _SCHEMAS_PATH not in sys.path:
    sys.path.insert(0, _SCHEMAS_PATH)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from codefort_schemas.models import HealthResponse
from app.routers import webhooks, scans, findings

app = FastAPI(
    title="CodeFort API",
    description="🏰 Build with confidence. Software supply-chain security for GitHub.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse()


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def api_health() -> HealthResponse:
    """API health check."""
    return HealthResponse()


app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(scans.router, prefix="/api/scans", tags=["Scans"])
app.include_router(findings.router, prefix="/api/findings", tags=["Findings"])
