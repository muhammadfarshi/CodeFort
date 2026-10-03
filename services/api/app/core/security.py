import hmac
import hashlib
from fastapi import Request, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature using HMAC-SHA256."""
    if not signature:
        return False
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected_signature, signature)

async def verify_github_webhook(request: Request) -> bool:
    """Dependency to verify GitHub webhook."""
    signature = request.headers.get("x-hub-signature-256")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    payload = await request.body()
    if not verify_webhook_signature(payload, signature, settings.GITHUB_WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    return True
