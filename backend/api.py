"""
FastAPI application for Stommel model.
"""
import os
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from concurrent.futures import ThreadPoolExecutor
import asyncio

from model import StommelModel
from solver import run_simulation, compute_bifurcation
from schemas import (
    SimulationRequest,
    SimulationResponse,
    BifurcationRequest,
    BifurcationResponse,
    PresetConfig,
    PresetsResponse,
)

app = FastAPI(title="Stommel Circulation Model", version="0.1.0")

# CORS: only needed when frontend is hosted on a different origin (dev or split deploy).
# In single-service production deploys, the frontend is served from the same origin.
_cors_origins = os.environ.get(
    "CORS_ALLOW_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for long-running computations
executor = ThreadPoolExecutor(max_workers=2)

# API routes are mounted under /api so the frontend (which calls /api/*) works
# whether served by the dev Vite proxy or by this app in production.
api_router = APIRouter(prefix="/api")


def _create_model_from_request(req: SimulationRequest | BifurcationRequest) -> StommelModel:
    """Create StommelModel instance from request."""
    return StommelModel(
        T_1=req.T_1,
        T_2=req.T_2,
        S_1_eq=req.S_1_eq,
        S_2_eq=req.S_2_eq,
        alpha=req.alpha,
        beta=req.beta,
        k=req.k,
        lam=req.lam,
        t_max=req.t_max if isinstance(req, SimulationRequest) else 3000,
        noise_amplitude=req.noise_amplitude if isinstance(req, SimulationRequest) else 0,
    )


@api_router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@api_router.post("/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    """
    Run a time integration of the Stommel model.

    Returns time series of salinity and circulation.
    """
    model = StommelModel(
        T_1=request.T_1,
        T_2=request.T_2,
        S_1_eq=request.S_1_eq,
        S_2_eq=request.S_2_eq,
        alpha=request.alpha,
        beta=request.beta,
        k=request.k,
        lam=request.lam,
        t_max=request.t_max,
        noise_amplitude=request.noise_amplitude,
    )

    # Run simulation in thread pool to avoid blocking event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        run_simulation,
        model,
        request.S_1_init,
        request.S_2_init,
        request.t_max,
        request.dt,
        request.noise_amplitude,
    )

    # Build response
    return SimulationResponse(
        time=result["time"],
        S_1=result["S_1"],
        S_2=result["S_2"],
        q=result["q"],
        q_sv=result["q_sv"],
        steady_state_reached=result["steady_state_reached"],
        final_state=result["final_state"],
        metadata={
            "t_max_years": request.t_max,
            "noise_amplitude": request.noise_amplitude,
        },
    )


@api_router.post("/bifurcation", response_model=BifurcationResponse)
async def bifurcation(request: BifurcationRequest):
    """
    Compute bifurcation diagram by sweeping temperature difference ΔT = T_1 - T_2.

    In the original Stommel (1961) model, bifurcation is controlled by the
    temperature difference. Returns forward and backward branches showing hysteresis.
    """
    model = StommelModel(
        T_1=request.T_1,
        T_2=request.T_2,  # Will be varied in the bifurcation computation
        S_1_eq=request.S_1_eq,
        S_2_eq=request.S_2_eq,
        alpha=request.alpha,
        beta=request.beta,
        k=request.k,
        lam=request.lam,
        t_max=3000,
        noise_amplitude=0.0,
    )

    # Run bifurcation computation in thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        compute_bifurcation,
        model,
        request.T_2_min,
        request.T_2_max,
        request.n_points,
    )

    return BifurcationResponse(**result)


@api_router.get("/presets", response_model=PresetsResponse)
async def get_presets():
    """
    Get named experiment configurations.

    Presets demonstrate different AMOC regimes.
    """
    presets = [
        PresetConfig(
            name="normal_amoc",
            description="Stable thermally-driven AMOC (Stommel 1961 original)",
            params={
                "T_1": 25.0,
                "T_2": 5.0,
                "S_1_eq": 36.0,
                "S_2_eq": 34.0,
                "S_1_init": 36.0,
                "S_2_init": 34.0,
                "alpha": 2.0e-4,
                "beta": 1.0e-3,
                "k": 3.0e-9,
                "lam": 3.0e-11,
                "t_max": 3000,
                "dt": 1.0,
                "noise_amplitude": 0.0,
            },
        ),
        PresetConfig(
            name="weakened_amoc",
            description="Weakened AMOC with reduced thermal forcing",
            params={
                "T_1": 25.0,
                "T_2": 12.0,  # Smaller ΔT weakens thermally-driven circulation
                "S_1_eq": 36.0,
                "S_2_eq": 34.0,
                "S_1_init": 36.0,
                "S_2_init": 34.0,
                "alpha": 2.0e-4,
                "beta": 1.0e-3,
                "k": 3.0e-9,
                "lam": 3.0e-11,
                "t_max": 3000,
                "dt": 1.0,
                "noise_amplitude": 0.0,
            },
        ),
        PresetConfig(
            name="collapsed_amoc",
            description="Near-collapsed AMOC with very small thermal forcing",
            params={
                "T_1": 25.0,
                "T_2": 20.0,  # Very small ΔT allows haline mode
                "S_1_eq": 36.0,
                "S_2_eq": 34.0,
                "S_1_init": 36.0,
                "S_2_init": 36.5,  # Start from fresh polar condition
                "alpha": 2.0e-4,
                "beta": 1.0e-3,
                "k": 3.0e-9,
                "lam": 3.0e-11,
                "t_max": 3000,
                "dt": 1.0,
                "noise_amplitude": 0.0,
            },
        ),
        PresetConfig(
            name="stommel_original",
            description="Stommel (1961) parameters with moderate thermal forcing",
            params={
                "T_1": 25.0,
                "T_2": 7.5,  # ΔT = 17.5°C
                "S_1_eq": 36.0,
                "S_2_eq": 34.0,
                "S_1_init": 36.0,
                "S_2_init": 34.0,
                "alpha": 2.0e-4,
                "beta": 1.0e-3,
                "k": 3.0e-9,
                "lam": 3.0e-11,
                "t_max": 3000,
                "dt": 1.0,
                "noise_amplitude": 0.0,
            },
        ),
    ]

    return PresetsResponse(presets=presets)


app.include_router(api_router)


# Serve the built React frontend (single-service deployment).
# FRONTEND_DIST may be set explicitly; otherwise we look for ../frontend/dist
# relative to this file (works in the Docker image where the dist is copied in).
_default_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
_frontend_dist = Path(os.environ.get("FRONTEND_DIST", _default_dist))

if _frontend_dist.is_dir():
    assets_dir = _frontend_dist / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def index():
        return FileResponse(_frontend_dist / "index.html")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # Serve a real file if it exists (favicon, etc.), otherwise fall back to index.html
        candidate = _frontend_dist / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_frontend_dist / "index.html")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
