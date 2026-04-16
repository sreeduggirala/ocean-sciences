# Stommel 1961 Two-Box Thermohaline Circulation Simulator

An interactive educational tool demonstrating the Stommel (1961) two-box model of thermohaline circulation, with real-time visualization of AMOC dynamics, tipping points, and hysteresis.

## Overview

This project implements a complete full-stack application for exploring the physics of Atlantic Meridional Overturning Circulation (AMOC) through Stommel's elegant two-box model. Users can adjust parameters in real-time to explore:

- **Circulation regimes**: Thermally-driven, haline-driven, and collapsed states
- **Tipping points**: The critical freshwater flux values where AMOC collapses
- **Hysteresis**: The difference between collapse and recovery thresholds
- **Stochastic forcing**: Impact of noise on system stability

## Model Physics

### Two-Box System
- **Equatorial box**: Warm, salty
- **Polar box**: Cold, fresh
- **Density-driven circulation**: `q = k[α(T_e − T_p) − β(S_e − S_p)]`

### Governing Equations
Salt conservation ODE system (temperatures held fixed):
```
dS_e/dt = −q(S_e − S_p) + F
dS_p/dt = +q(S_e − S_p) − F
```

Where:
- `S_e, S_p`: Equatorial and polar salinity (psu)
- `q`: Circulation strength (1/s)
- `F`: Freshwater forcing (psu/s)
- `α`: Thermal expansion coefficient
- `β`: Haline contraction coefficient
- `k`: Circulation parameter

## Project Structure

```
ocean-sciences/
├── backend/
│   ├── pyproject.toml      # uv package management
│   ├── model.py            # Stommel physics model
│   ├── solver.py           # ODE integration and bifurcation
│   ├── schemas.py          # Pydantic v2 validation
│   └── api.py              # FastAPI endpoints
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── types.ts
        ├── api.ts
        ├── hooks/useSimulation.ts
        └── components/
            ├── ParameterControls.tsx
            ├── OceanBoxDiagram.tsx
            ├── TimeSeriesPlot.tsx
            ├── PhaseSpacePlot.tsx
            ├── BifurcationPlot.tsx
            └── AMOCComparison.tsx
```

## Setup & Installation

### Backend (Python)

```bash
cd backend
uv sync                        # Install dependencies
uv run uvicorn api:app --reload
```

The API will be available at `http://localhost:8000`.

**Requirements** (via pyproject.toml):
- Python ≥ 3.11
- FastAPI, Uvicorn, Pydantic, SciPy, NumPy

### Frontend (Node.js)

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173` and will proxy API requests to the backend.

## API Endpoints

### POST /simulate
Run a time integration with given parameters.

**Request** (SimulationRequest):
```json
{
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
  "noise_amplitude": 0.0
}
```

**Response** (SimulationResponse):
```json
{
  "time": [...],
  "S_e": [...],
  "S_p": [...],
  "q": [...],
  "q_sv": [...],
  "steady_state_reached": true,
  "final_state": [36.02, 33.98],
  "metadata": {...}
}
```

### POST /bifurcation
Compute bifurcation diagram by sweeping freshwater flux F.

Returns forward and backward branches showing hysteresis and tipping points.

### GET /presets
Retrieve named experiment configurations (normal_amoc, weakened_amoc, collapsed_amoc, stommel_original).

### GET /health
Health check endpoint.

## Features

### Frontend Components
- **ParameterControls**: Collapsible sections for temperature, physics, forcing, and integration parameters
- **OceanBoxDiagram**: SVG animation of two boxes with circulation arrows
- **TimeSeriesPlot**: Plotly subplots showing q(t), S_e(t), S_p(t) evolution
- **PhaseSpacePlot**: (ΔS, q) phase portrait with trajectory and nullcline
- **BifurcationPlot**: F-sweep diagram with forward/backward branches and tipping points
- **AMOCComparison**: Bar chart comparing model q to observed RAPID array mean (~16.9 Sv)

### Key Features
- **Dark theme**: GitHub-inspired dark mode (#0d1117 background)
- **Real-time parameter adjustment**: Debounced auto-run on slider changes
- **Bifurcation analysis**: Automatic hysteresis detection and tipping point identification
- **Preset configurations**: One-click loading of archetypal scenarios
- **Export functionality**: Download results as JSON
- **Stochastic forcing**: Euler-Maruyama integration for noisy simulations

## Default Parameters

| Parameter | Default | Units | Range |
|-----------|---------|-------|-------|
| T_e | 25.0 | °C | [15, 35] |
| T_p | 5.0 | °C | [-2, 15] |
| S_e0 | 36.0 | psu | [30, 40] |
| S_p0 | 34.0 | psu | [28, 40] |
| alpha | 1.5e-4 | 1/°C | [0.5e-4, 3e-4] |
| beta | 8.0e-4 | 1/psu | [2e-4, 1.5e-3] |
| k | 1.5e-6 | 1/s | [5e-8, 1e-5] (log) |
| F | 1.0e-4 | psu/s | [0, 5e-4] |
| t_max | 3000 | years | [100, 10000] |
| noise | 0 | psu/s | [0, 5e-5] |

## Verification

1. **Backend unit test**: Default parameters should yield q ≈ 15 Sv
2. **Salt conservation**: S_e + S_p = constant throughout integration
3. **Bifurcation shape**: Forward/backward branches diverge in middle F range
4. **Presets**: Each preset produces distinct q_sv values
5. **Stochastic extension**: Noise produces different trajectories with similar statistics

## Scientific References

- Stommel, H. (1961). "A mathematical model of the Atlantic meridional overturning circulation." *Journal of Physical Oceanography*, 18, 1944-1955.

## License

Educational tool. Use freely for teaching and research.

## Author Notes

This simulator demonstrates how simple dynamical systems can capture essential climate physics. The two-box model's elegance lies in its ability to reveal universal mechanisms (hysteresis, tipping points, bistability) common to many complex systems. Perfect for classroom demonstrations of nonlinear dynamics and climate change mechanisms.
