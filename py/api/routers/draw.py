"""Drawing router: matplotlib diagram generation under /api/v1/draw"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from py.draw.mpl_structure import draw_sm_diagram

router = APIRouter(prefix="/api/v1/draw", tags=["draw"])


@router.get("/structure")
async def draw_structure(L: float = 4000, P: float = 20000, mode: str = "sm"):
    """matplotlibで単純梁のS図・M図PNGを生成して返却"""
    buf = draw_sm_diagram(L, P, mode)
    return StreamingResponse(buf, media_type="image/png")
