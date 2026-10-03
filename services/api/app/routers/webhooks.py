"""
CodeFort Webhook Router — Receives and processes GitHub App webhooks.

Verifies HMAC-SHA256 signature (SECURITY.md §4).
Handles idempotency (TRD §6).
"""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.security import verify_github_webhook
from codefort_schemas.models import AnalysisProfile, ScanRequest
from app.services.orchestrator import run_scan

logger = logging.getLogger("codefort.webhooks")

router = APIRouter()


@router.post("/github", status_code=202)
async def github_webhook(
    request: Request,
    verified: bool = Depends(verify_github_webhook),
) -> dict[str, str]:
    """
    GitHub webhook endpoint.

    Receives pull_request events and triggers analysis scans.
    Returns 202 Accepted immediately; analysis runs asynchronously.
    """
    event_type = request.headers.get("x-github-event", "")
    delivery_id = request.headers.get("x-github-delivery", "unknown")

    logger.info("Webhook received: event=%s delivery=%s", event_type, delivery_id)

    if event_type != "pull_request":
        return {"message": f"Ignored non-PR event: {event_type}"}

    payload = await request.json()
    action = payload.get("action", "")

    if action not in ("opened", "synchronize", "reopened"):
        return {"message": f"Ignored PR action: {action}"}

    try:
        scan_request = ScanRequest(
            installation_id=payload["installation"]["id"],
            repository_full_name=payload["repository"]["full_name"],
            pr_number=payload["pull_request"]["number"],
            head_sha=payload["pull_request"]["head"]["sha"],
            base_sha=payload["pull_request"]["base"]["sha"],
            profile=AnalysisProfile.BASIC,
            sender=payload.get("sender", {}).get("login"),
        )
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required field in webhook payload: {e}",
        )

    # Fire-and-forget: enqueue scan as background task
    # In production, this would go to a Redis/Celery worker queue
    asyncio.create_task(run_scan(scan_request))

    logger.info(
        "Scan enqueued for %s PR #%d (sha: %s)",
        scan_request.repository_full_name,
        scan_request.pr_number,
        scan_request.head_sha[:7],
    )

    return {
        "message": "Scan accepted",
        "repository": scan_request.repository_full_name,
        "pr_number": scan_request.pr_number,
    }


@router.post("/demo-scan", status_code=200)
async def demo_scan() -> dict:
    """
    Demo endpoint: triggers a scan with mock malicious PR data.

    This is for hackathon demonstrations only.
    """
    scan_request = ScanRequest(
        installation_id=0,
        repository_full_name="demo-org/vulnerable-app",
        pr_number=42,
        head_sha="abc1234567890deadbeef",
        base_sha="000000000000000000000",
        profile=AnalysisProfile.BASIC,
        sender="demo-attacker",
    )

    result = await run_scan(scan_request)

    return {
        "message": "Demo scan completed",
        "scan_id": result.scan_id,
        "findings_count": result.findings_count,
        "policy_decision": result.policy_result.decision.value if result.policy_result else None,
        "result": result.model_dump(),
    }
