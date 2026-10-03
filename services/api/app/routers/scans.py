"""
CodeFort Scans Router — Endpoints for listing and retrieving scan results.

Pagination per API rules (AGENTS.md §10).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from codefort_schemas.models import ScanResult, ScanSummary
from app.services.orchestrator import get_scan, list_scans

router = APIRouter()


@router.get("/", response_model=list[ScanSummary])
async def list_scans_endpoint(
    skip: int = 0,
    limit: int = 20,
) -> list[ScanSummary]:
    """List scans with pagination."""
    scans = list_scans(limit=limit, offset=skip)

    return [
        ScanSummary(
            scan_id=s.scan_id,
            scan_status=s.scan_status,
            repository_full_name=s.repository_full_name,
            pr_number=s.pr_number,
            head_sha=s.head_sha,
            profile=s.profile,
            findings_count=s.findings_count,
            severity_summary=s.severity_summary,
            policy_decision=s.policy_result.decision if s.policy_result else None,
            created_at=s.created_at,
            completed_at=s.completed_at,
        )
        for s in scans
    ]


@router.get("/{scan_id}", response_model=ScanResult)
async def get_scan_endpoint(scan_id: str) -> ScanResult:
    """Get full scan result by ID."""
    scan = get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
