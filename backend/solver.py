"""
Simulation and bifurcation analysis for Stommel model.
"""
import numpy as np
from scipy.integrate import solve_ivp, OdeSolution
from model import StommelModel


YEARS_TO_SECONDS = 365.25 * 24 * 3600
V_BOX = 7e15  # m³, used for Sv conversion (calibrated for ~15 Sv with defaults)


def run_simulation(
    model: StommelModel,
    S_e0: float,
    S_p0: float,
    t_max: float,
    dt: float = 1.0,
    noise_amplitude: float = 0.0,
) -> dict:
    """
    Run time integration of Stommel model.

    Args:
        model: StommelModel instance
        S_e0: Initial equatorial salinity (psu)
        S_p0: Initial polar salinity (psu)
        t_max: Maximum integration time (years)
        dt: Output time step (years)
        noise_amplitude: Gaussian noise std (psu/s)

    Returns:
        dict with keys:
            time: array (years)
            S_e: array (psu)
            S_p: array (psu)
            q: array (1/s)
            q_sv: array (Sv)
            steady_state_reached: bool
            final_state: [S_e_final, S_p_final]
    """
    if noise_amplitude > 0:
        return _run_simulation_stochastic(model, S_e0, S_p0, t_max, dt, noise_amplitude)
    else:
        return _run_simulation_deterministic(model, S_e0, S_p0, t_max, dt)


def _run_simulation_deterministic(
    model: StommelModel,
    S_e0: float,
    S_p0: float,
    t_max: float,
    dt: float,
) -> dict:
    """Deterministic integration using solve_ivp."""

    def steady_state_event(t, state):
        """Terminal event: stop when steady state reached (max|dS/dt| < 1e-10)."""
        rhs = model.rhs(t, state)
        return np.max(np.abs(rhs)) - 1e-10

    steady_state_event.terminal = True
    steady_state_event.direction = -1

    t_span = (0, t_max * YEARS_TO_SECONDS)
    t_eval = np.arange(0, t_max * YEARS_TO_SECONDS + 1, dt * YEARS_TO_SECONDS)
    initial_state = np.array([S_e0, S_p0])

    sol = solve_ivp(
        model.rhs,
        t_span,
        initial_state,
        method="Radau",
        t_eval=t_eval,
        events=steady_state_event,
        dense_output=True,
        rtol=1e-9,
        atol=1e-12,
    )

    # Convert time back to years
    time = sol.t / YEARS_TO_SECONDS
    S_e = sol.y[0]
    S_p = sol.y[1]

    # Compute circulation and convert to Sv
    q = np.array([model.q(se, sp) for se, sp in zip(S_e, S_p)])
    q_sv = q * V_BOX / 1e6

    steady_state_reached = sol.status == 1  # Terminal event triggered

    return {
        "time": time,
        "S_e": S_e,
        "S_p": S_p,
        "q": q,
        "q_sv": q_sv,
        "steady_state_reached": bool(steady_state_reached),
        "final_state": [float(S_e[-1]), float(S_p[-1])],
    }


def _run_simulation_stochastic(
    model: StommelModel,
    S_e0: float,
    S_p0: float,
    t_max: float,
    dt: float,
    noise_amplitude: float,
) -> dict:
    """Euler-Maruyama integration with Gaussian noise."""
    n_steps = int(t_max / dt)
    dt_seconds = dt * YEARS_TO_SECONDS

    time = np.linspace(0, t_max, n_steps + 1)
    S_e = np.zeros(n_steps + 1)
    S_p = np.zeros(n_steps + 1)
    S_e[0] = S_e0
    S_p[0] = S_p0

    for i in range(n_steps):
        state = np.array([S_e[i], S_p[i]])
        rhs = model.rhs(0, state)
        noise = np.random.normal(0, noise_amplitude * np.sqrt(dt_seconds), 2)
        state_new = state + rhs * dt_seconds + noise
        S_e[i + 1] = state_new[0]
        S_p[i + 1] = state_new[1]

    # Compute circulation and convert to Sv
    q = np.array([model.q(se, sp) for se, sp in zip(S_e, S_p)])
    q_sv = q * V_BOX / 1e6

    return {
        "time": time,
        "S_e": S_e,
        "S_p": S_p,
        "q": q,
        "q_sv": q_sv,
        "steady_state_reached": False,
        "final_state": [float(S_e[-1]), float(S_p[-1])],
    }


def compute_bifurcation(
    base_model: StommelModel,
    F_min: float = 0.0,
    F_max: float = 5e-4,
    n_points: int = 200,
) -> dict:
    """
    Compute bifurcation diagram by sweeping freshwater flux F.

    Forward sweep: F 0 → F_max, starting from previous steady state
    Backward sweep: F F_max → 0, starting from fresh polar box

    Returns:
        dict with keys:
            F_values: array of F values
            q_forward: array of steady-state q for forward sweep
            q_backward: array of steady-state q for backward sweep
            tipping_points: list of dicts with F and q values
    """
    F_values = np.linspace(F_min, F_max, n_points)

    # Forward sweep
    q_forward = np.zeros(n_points)
    state = np.array([base_model.S_e0, base_model.S_p0])  # Start from initial condition

    for i, F in enumerate(F_values):
        model_F = StommelModel(
            T_e=base_model.T_e,
            T_p=base_model.T_p,
            S_e0=base_model.S_e0,
            S_p0=base_model.S_p0,
            alpha=base_model.alpha,
            beta=base_model.beta,
            k=base_model.k,
            F=F,
            t_max=100.0,  # Shorter integration for bifurcation
            noise_amplitude=0.0,
        )
        result = _run_simulation_deterministic(
            model_F, state[0], state[1], t_max=100.0, dt=1.0
        )
        state = np.array(result["final_state"])
        q_forward[i] = result["q"][-1]

    # Backward sweep: start from fresh polar box condition (S_p = 40)
    q_backward = np.zeros(n_points)
    state = np.array([base_model.S_e0, 40.0])

    for i, F in enumerate(F_values[::-1]):
        idx = n_points - 1 - i
        model_F = StommelModel(
            T_e=base_model.T_e,
            T_p=base_model.T_p,
            S_e0=base_model.S_e0,
            S_p0=base_model.S_p0,
            alpha=base_model.alpha,
            beta=base_model.beta,
            k=base_model.k,
            F=F,
            t_max=100.0,
            noise_amplitude=0.0,
        )
        result = _run_simulation_deterministic(
            model_F, state[0], state[1], t_max=100.0, dt=1.0
        )
        state = np.array(result["final_state"])
        q_backward[idx] = result["q"][-1]

    # Detect tipping points: large jumps in q between adjacent F values
    tipping_points = []
    threshold = 2e-7  # Threshold for detecting large jumps

    # Forward tipping (AMOC weakens)
    for i in range(n_points - 1):
        if abs(q_forward[i + 1] - q_forward[i]) > threshold:
            tipping_points.append(
                {
                    "F": float(F_values[i + 1]),
                    "q": float(q_forward[i + 1]),
                    "direction": "forward",
                }
            )

    # Backward tipping (AMOC strengthens)
    for i in range(n_points - 1):
        if abs(q_backward[i + 1] - q_backward[i]) > threshold:
            tipping_points.append(
                {
                    "F": float(F_values[i + 1]),
                    "q": float(q_backward[i + 1]),
                    "direction": "backward",
                }
            )

    return {
        "F_values": F_values.tolist(),
        "q_forward": q_forward.tolist(),
        "q_backward": q_backward.tolist(),
        "tipping_points": tipping_points,
    }
