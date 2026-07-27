import json, os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="kenchiku-quest", description="2級建築士試験4科目ゲーム化API")

# Paths relative to this file (py/api/main.py -> ../../src/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "..", "src", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "..", "src", "templates")
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "data")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ===== 構造計算モジュール（既存 /api/calc 用） =====

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
    es = {}; ef = {}
    for t in tasks:
        tid = t["id"]
        pred = t.get("predecessors", [])
        es[tid] = max([ef[p] for p in pred] + [0])
        ef[tid] = es[tid] + t["duration"]
    total = max(ef.values())
    ls = {}; lf = {}
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

# ===== オントロジー読み込み =====

ontology_cache = {}

def load_ontology(name: str) -> dict:
    path = os.path.join(DATA_DIR, f"{name}-ontology.json")
    if name not in ontology_cache:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                ontology_cache[name] = json.load(f)
        else:
            ontology_cache[name] = {}
    return ontology_cache[name]

# ===== ROUTES（既存仕様そのまま） =====

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health():
    return {"status": "ok", "game": "kenchiku-quest"}

@app.post("/api/calc/beam")
async def calc_beam(data: dict):
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
    if ratio > 1.0: result = "broken"
    elif ratio > 0.85: result = "danger"
    elif ratio > 0.6: result = "warn"
    return {
        "Z": round(Z, 2),
        "I": round(I, 2),
        "sigma_MPa": round(sigma, 3),
        "delta_mm": round(delta, 3),
        "ratio": round(ratio, 3),
        "result": result,
        "formula": "σ = P·L/(4·Z), δ = P·L³/(3·E·I)"
    }

@app.post("/api/calc/cpm")
async def calc_cpm(data: dict):
    tasks = data.get("tasks", [])
    if not tasks:
        return {"error": "no tasks"}
    critical = cpm_critical_path(tasks)
    total = max(t["duration"] + max([0] + [t2["duration"] for t2 in tasks if t2["id"] in t.get("predecessors", [])]) for t in tasks)
    return {
        "critical_path": critical,
        "total_duration": total,
        "tasks": tasks
    }

@app.get("/api/ontology/{name}")
async def get_ontology(name: str):
    data = load_ontology(name)
    return data if data else {"error": f"ontology '{name}' not found"}

@app.post("/api/game/save")
async def game_save(player: dict):
    return {"saved": True, "player": player.get("name")}

@app.post("/api/game/quiz")
async def game_quiz(data: dict):
    return {"correct": True, "score": 10, "explanation": "（実装中）"}

# ===== 新規 routers =====
from py.api.routers import structure, env, draw, regu

app.include_router(structure.router)
app.include_router(env.router)
app.include_router(draw.router)
app.include_router(regu.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("py.api.main:app", host="0.0.0.0", port=8000, reload=True)
