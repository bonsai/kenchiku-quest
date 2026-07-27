"""Environment router: parameters and thermal simulation under /api/v1/env"""
from fastapi import APIRouter
from pydantic import BaseModel
from py.sim import heat

router = APIRouter(prefix="/api/v1/env", tags=["environment"])


class HeatSimPayload(BaseModel):
    U_W_m2K: float
    area_m2: float
    dT_K: float


@router.get("/params")
async def env_params():
    """環境計算パラメータ（材料特性・単位変換係数）を返却"""
    return {
        "materials": {
            "concrete": {
                "conductivity_W_mK": 1.5,
                "density_kg_m3": 2300,
                "specific_heat_J_kgK": 880,
            },
            "wood": {
                "conductivity_W_mK": 0.14,
                "density_kg_m3": 600,
                "specific_heat_J_kgK": 1600,
            },
            "steel": {
                "conductivity_W_mK": 50.0,
                "density_kg_m3": 7850,
                "specific_heat_J_kgK": 460,
            },
        },
        "conversion": {
            "1_MPa_to_N_mm2": 1.0,
            "1_kN_to_N": 1000.0,
            "1_m_to_mm": 1000.0,
        },
    }


@router.post("/simulate")
async def env_simulate(payload: HeatSimPayload):
    """熱シミュレーション受付（雛形）"""
    heat_loss = heat.calc_heat_loss(payload.U_W_m2K, payload.area_m2, payload.dT_K)
    return {
        "heat_loss_W": round(heat_loss, 2),
        "note": "accepted",
    }
