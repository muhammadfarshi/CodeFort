from fastapi import APIRouter, HTTPException
from typing import List
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../packages/schemas/python')))
from codefort_schemas.models import Finding

router = APIRouter()

@router.get("/{scan_id}", response_model=List[Finding])
async def get_findings(scan_id: str):
    """Get findings for a scan."""
    return []
