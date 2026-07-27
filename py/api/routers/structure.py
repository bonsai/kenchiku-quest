"""Structure router: beam and CPM calculations under /api/v1/structure"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/structure", tags=["structure"])

# ===== 構造計算関数 =====

def section_modulus(b_mm: float, h_mm: float) -> float:
    return b_mm * h_mm ** 2 / 6

def moment_of_inertia(b_mm: float, h_mm: float) -> float:
    return b_mm * h_mm ** 3 / 12

def bending_stress(P_N: float, L_mm: float, Z_mm3: float) -> float:
    M = P_N * L_mm / 4
    return M / Z_mm3

def deflection_cantilever(P_N: float, L_mm: float, E_MPa: float, I_mm4: float) -> float:
    return P_N * L_mm ** 3 / (3 * E_MPa * I_mm4)

def cpm_critical_path(tasks: list[dict]) -> list[str]:
    """CPM: tasks = [{id, duration, predecessors[]}] -> critical_path_ids"""
    es = {}
    ef = {}
    for t in tasks:
        tid = t["id"]
        pred = t.get("predecessors", [])
        es[tid] = max([ef[p] for p in pred] + [0])
        ef[tid] = es[tid] + t["duration"]
    total = max(ef.values())
    ls = {}
    lf = {}
    for t in reversed(tasks):
        tid = t["id"]
        succs = [x["id"] for x in tasks if tid in x.get("predecessors", [])]
        lf[tid] = min([ls[s] for s in succs] + [total])
        ls[tid] = lf[tid] - t["duration"]
    critical = []
    for t in tasks:
        tid = t["id"]
        f = ls[tid] - es[tid]
        if abs(f) < 0.001:
            critical.append(tid)
    return critical

# ===== エンドポイント =====

@router.post("/beam")
async def v1_beam(data: dict):
    """梁計算API (v1): {b, h, P, L, E, fb} -> {Z, I, sigma, delta, ratio, result}"""
    b = float(data.get("b", 180))
    h = float(data.get("h", 200))
    P = float(data.get("P", 20000))
    L = float(data.get("L", 4000))
    E = float(data.get("E", 10000))
    fb = float(data.get("fb", 12))

    Z = section_modulus(b, h)
    I = moment_of_inertia(b, h)
    sigma = bending_stress(P, L, Z)
    delta = deflection_cantilever(P, L, E, I)
    ratio = sigma / fb

    result = "ok"
    if ratio > 1.0:
        result = "broken"
    elif ratio > 0.85:
        result = "danger"
    elif ratio > 0.6:
        result = "warn"

    return {
        "Z": round(Z, 2),
        "I": round(I, 2),
        "sigma_MPa": round(sigma, 3),
        "delta_mm": round(delta, 3),
        "ratio": round(ratio, 3),
        "result": result,
        "formula": "σ = P·L/(4·Z), δ = P·L³/(3·E·I)"
    }

@router.post("/cpm")
async def v1_cpm(data: dict):
    """CPM批判パス計算API (v1): {tasks} -> {critical_path, total_duration}"""
    tasks = data.get("tasks", [])
    if not tasks:
        return {"error": "no tasks"}
    critical = cpm_critical_path(tasks)
    total = max(
        t["duration"] + max([0] + [t2["duration"] for t2 in tasks if t2["id"] in t.get("predecessors", [])])
        for t in tasks
    )
    return {
        "critical_path": critical,
        "total_duration": total,
        "tasks": tasks
    }
