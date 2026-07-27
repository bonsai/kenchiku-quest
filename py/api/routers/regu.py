"""Regulation router: compliance check stub under /api/v1/regu"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/regu", tags=["regulation"])


@router.post("/check")
async def regu_check(data: dict):
    """法規判定雛形（現状はダミー200応答）"""
    return {
        "passed": True,
        "checklist": [],
        "message": "regulation check stub (ok)",
    }
