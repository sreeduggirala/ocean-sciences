"""
FastAPI application for Stommel model.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# CORS middleware for development (allows requests from frontend on localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for long-running computations
executor = ThreadPoolExecutor(max_workers=2)


def _create_model_from_request(req: SimulationRequest | BifurcationRequest) -> StommelModel:
    """Create StommelModel instance from request."""
    return StommelModel(
        T_e=req.T_e,
        T_p=req.T_p,
        S_e0=req.S_e0,
        S_p0=req.S_p0,
        alpha=req.alpha,
        beta=req.beta,
        k=req.k,
        F=req.F if isinstance(req, SimulationRequest) else 1.0e-4,  # Default for bifurcation
        t_max=req.t_max if isinstance(req, SimulationRequest) else 3000,
        noise_amplitude=req.noise_amplitude if isinstance(req, SimulationRequest) else 0,
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    """
    Run a time integration of the Stommel model.

    Returns time series of salinity and circulation.
    """
    model = StommelModel(
        T_e=request.T_e,
        T_p=request.T_p,
        S_e0=request.S_e0,
        S_p0=request.S_p0,
        alpha=request.alpha,
        beta=request.beta,
        k=request.k,
        F=request.F,
        t_max=request.t_max,
        noise_amplitude=request.noise_amplitude,
    )

    # Run simulation in thread pool to avoid blocking event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        run_simulation,
        model,
        request.S_e0,
        request.S_p0,
        request.t_max,
        request.dt,
        request.noise_amplitude,
    )

    # Build response
    return SimulationResponse(
        time=result["time"],
        S_e=result["S_e"],
        S_p=result["S_p"],
        q=result["q"],
        q_sv=result["q_sv"],
        steady_state_reached=result["steady_state_reached"],
        final_state=result["final_state"],
        metadata={
            "t_max_years": request.t_max,
            "noise_amplitude": request.noise_amplitude,
        },
    )


@app.post("/bifurcation", response_model=BifurcationResponse)
async def bifurcation(request: BifurcationRequest):
    """
    Compute bifurcation diagram by sweeping freshwater flux F.

    Returns forward and backward branches showing hysteresis.
    """
    model = StommelModel(
        T_e=request.T_e,
        T_p=request.T_p,
        S_e0=request.S_e0,
        S_p0=request.S_p0,
        alpha=request.alpha,
        beta=request.beta,
        k=request.k,
        F=1.0e-4,  # Not used in bifurcation computation
        t_max=3000,
        noise_amplitude=0.0,
    )

    # Run bifurcation computation in thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        compute_bifurcation,
        model,
        request.F_min,
        request.F_max,
        request.n_points,
    )

    return BifurcationResponse(**result)


@app.get("/presets", response_model=PresetsResponse)
async def get_presets():
    """
    Get named experiment configurations.

    Presets demonstrate different AMOC regimes.
    """
    presets = [
        PresetConfig(
            name="normal_amoc",
            description="Stable thermally-driven AMOC (~15 Sv)",
            params={
                "T_e": 25.0,
                "T_p": 5.0,
                "S_e0": 36.0,
                "S_p0": 34.0,
                "alpha": 1.5e-4,
                "beta": 8.0e-4,
                "k": 1.5e-6,
                "F": 8.0e-5,
                "t_max": 3000,
                "dt": 1.0,
                "noise_amplitude": 0.0,
            },
        ),
        PresetConfig(
            name="weakened_amoc",
            description="Weakened AMOC near tipping point (~8 Sv)",
            params={
                "T_e": 25.0,
                "T_p": 5.0,
                "S_e0": 36.0,
                "S_p0": 34.0,
                "alpha": 1.5e-4,
                "beta": 8.0e-4,
                "k": 1.5e-6,
                "F": 1.8e-4,
                "t_max": 3000,
                "dt": 1.0,
                "noise_amplitude": 0.0,
            },
        ),
        PresetConfig(
            name="collapsed_amoc",
            description="Collapsed AMOC post-tipping (reversed/near-zero)",
            params={
                "T_e": 25.0,
                "T_p": 5.0,
                "S_e0": 36.0,
                "S_p0": 34.0,
                "alpha": 1.5e-4,
                "beta": 8.0e-4,
                "k": 1.5e-6,
                "F": 3.0e-4,
                "t_max": 3000,
                "dt": 1.0,
                "noise_amplitude": 0.0,
            },
        ),
        PresetConfig(
            name="stommel_original",
            description="Parameters from Stommel 1961 original paper",
            params={
                "T_e": 25.0,
                "T_p": 5.0,
                "S_e0": 36.0,
                "S_p0": 34.0,
                "alpha": 1.5e-4,
                "beta": 8.0e-4,
                "k": 1.5e-6,
                "F": 1.0e-4,
                "t_max": 3000,
                "dt": 1.0,
                "noise_amplitude": 0.0,
            },
        ),
    ]

    return PresetsResponse(presets=presets)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
