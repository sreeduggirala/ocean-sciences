# Quick Start Guide

## Prerequisites

- Python 3.11+ (with `uv` installed: `brew install uv` or `pip install uv`)
- Node.js 18+ (with npm)

## Terminal 1: Start Backend (FastAPI)

```bash
cd /Users/sree/Python/ocean-sciences/backend
uv sync                    # Install dependencies (one-time)
uv run uvicorn api:app --reload
```

Output should show:
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The API is now running at `http://localhost:8000`

## Terminal 2: Start Frontend (React + Vite)

```bash
cd /Users/sree/Python/ocean-sciences/frontend
npm install                # Install dependencies (one-time)
npm run dev
```

Output should show:
```
  VITE v5.4.21  ready in 205 ms
  ➜  Local:   http://localhost:5173/
```

## Open in Browser

Navigate to **http://localhost:5173** and you should see:
- **Left panel**: Parameter controls with sliders
- **Right panel**: 6 visualization panels showing:
  1. Two-box ocean diagram (animated)
  2. AMOC vs observations comparison
  3. Time series (q, S_e, S_p)
  4. Phase space (ΔS, q)
  5. Bifurcation diagram (hysteresis)
  6. (Plus any other visualizations)

## Quick Test

1. **Default simulation**: Should show ~14-15 Sv (Sverdrups) circulation
2. **Adjust F slider**: Freshwater forcing from 0 to 5e-4 psu/s
3. **Watch the tipping point**: AMOC collapses when F reaches critical value
4. **Compute bifurcation**: Click "Compute Bifurcation" to see forward/backward sweeps and hysteresis window
5. **Use presets**: Click preset buttons to jump to named scenarios

## Troubleshooting

### Backend won't start
```bash
# Make sure Python 3.11+ is available
python3 --version

# If scipy/numpy fails, try:
cd backend
rm -rf .venv
uv sync --force
```

### Frontend won't start
```bash
# Clear npm cache
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Port already in use
- Backend (8000): `lsof -i :8000` and `kill -9 <PID>`
- Frontend (5173): `lsof -i :5173` and `kill -9 <PID>`

## What You're Seeing

The Stommel model simulates the Atlantic Meridional Overturning Circulation (AMOC):

- **Thermally driven state** (high F): Warm equatorial water is transported north
- **Haline driven state** (low F): Salty equatorial water sinks in polar region
- **Tipping point**: Beyond critical freshwater forcing, AMOC collapses
- **Hysteresis**: Different thresholds for collapse vs recovery

This simple 2-box model captures the essential physics of climate tipping points!

## Key Keyboard Controls

- **Sliders**: Click and drag to adjust parameters
- **Auto-run**: Changes auto-run 500ms after you stop adjusting
- **Buttons**: "Run Simulation" for manual run, "Compute Bifurcation" for sweep analysis

## Files to Check

- Backend health: `curl http://localhost:8000/health`
- API presets: `curl http://localhost:8000/presets | jq`
- Frontend logs: Check browser console (F12)
- Backend logs: Check terminal where uvicorn is running

---

**Happy exploring!** 🌊 Try adjusting parameters and watch the AMOC respond in real-time.
