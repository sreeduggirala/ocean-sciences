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
    S_1: float,
    S_2: float,
    t_max: float,
    dt: float = 1.0,
    noise_amplitude: float = 0.0,
) -> dict:
    """
    Run time integration of Stommel model.

    Args:
        model: StommelModel instance
        S_1: Initial box 1 (equatorial) salinity (psu)
        S_2: Initial box 2 (polar) salinity (psu)
        t_max: Maximum integration time (years)
        dt: Output time step (years)
        noise_amplitude: Gaussian noise std (psu/s)

    Returns:
        dict with keys:
            time: array (years)
            S_1: array (psu)
            S_2: array (psu)
            q: array (1/s)
            q_sv: array (Sv)
            steady_state_reached: bool
            final_state: [S_1_final, S_2_final]
    """
    if noise_amplitude > 0:
        return _run_simulation_stochastic(model, S_1, S_2, t_max, dt, noise_amplitude)
    else:
        return _run_simulation_deterministic(model, S_1, S_2, t_max, dt)


def _run_simulation_deterministic(
    model: StommelModel,
    S_1: float,
    S_2: float,
    t_max: float,
    dt: float,
) -> dict:
    """Deterministic integration using solve_ivp with time in years."""

    def steady_state_event(t, state):
        """Terminal event: stop when steady state reached (max|dS/dt| < 1e-10 psu/year)."""
        rhs = model.rhs_years(t, state)
        return np.max(np.abs(rhs)) - 1e-10

    steady_state_event.terminal = True
    steady_state_event.direction = -1

    t_span = (0, t_max)  # time in years
    t_eval = np.arange(0, t_max + dt/2, dt)  # output points in years
    initial_state = np.array([S_1, S_2])

    sol = solve_ivp(
        model.rhs_years,
        t_span,
        initial_state,
        method="RK45",
        t_eval=t_eval,
        events=steady_state_event,
        dense_output=True,
        rtol=1e-8,
        atol=1e-11,
    )

    # Time is already in years
    time = sol.t
    S_1_vals = sol.y[0]
    S_2_vals = sol.y[1]

    # Compute circulation and convert to Sv
    q = np.array([model.q(s1, s2) for s1, s2 in zip(S_1_vals, S_2_vals)])
    q_sv = q * V_BOX / 1e6

    steady_state_reached = sol.status == 1  # Terminal event triggered

    return {
        "time": time.tolist(),
        "S_1": S_1_vals.tolist(),
        "S_2": S_2_vals.tolist(),
        "q": q.tolist(),
        "q_sv": q_sv.tolist(),
        "steady_state_reached": bool(steady_state_reached),
        "final_state": [float(S_1_vals[-1]), float(S_2_vals[-1])],
    }


def _run_simulation_stochastic(
    model: StommelModel,
    S_1: float,
    S_2: float,
    t_max: float,
    dt: float,
    noise_amplitude: float,
) -> dict:
    """Euler-Maruyama integration with Gaussian noise (time in years)."""
    n_steps = int(t_max / dt)
    dt_years = dt

    time = np.linspace(0, t_max, n_steps + 1)
    S_1_vals = np.zeros(n_steps + 1)
    S_2_vals = np.zeros(n_steps + 1)
    S_1_vals[0] = S_1
    S_2_vals[0] = S_2

    # noise_amplitude is already in psu/year units

    for i in range(n_steps):
        state = np.array([S_1_vals[i], S_2_vals[i]])
        rhs_per_year = model.rhs_years(0, state)
        noise = np.random.normal(0, noise_amplitude * np.sqrt(dt_years), 2)
        state_new = state + rhs_per_year * dt_years + noise
        S_1_vals[i + 1] = state_new[0]
        S_2_vals[i + 1] = state_new[1]

    # Compute circulation and convert to Sv
    q = np.array([model.q(s1, s2) for s1, s2 in zip(S_1_vals, S_2_vals)])
    q_sv = q * V_BOX / 1e6

    return {
        "time": time.tolist(),
        "S_1": S_1_vals.tolist(),
        "S_2": S_2_vals.tolist(),
        "q": q.tolist(),
        "q_sv": q_sv.tolist(),
        "steady_state_reached": False,
        "final_state": [float(S_1_vals[-1]), float(S_2_vals[-1])],
    }


def compute_bifurcation(
    base_model: StommelModel,
    T_2_min: float = 0.0,
    T_2_max: float = 20.0,
    n_points: int = 200,
) -> dict:
    """
    Compute bifurcation diagram by sweeping temperature difference (varying T_2).

    In the original Stommel (1961) model, the bifurcation is controlled by
    the temperature difference ΔT = T_1 - T_2. We sweep T_2 while holding
    T_1 fixed to explore the equilibrium structure.

    Forward sweep: T_2 from T_2_min → T_2_max (ΔT decreasing)
                  Starting from thermally-driven state
    Backward sweep: T_2 from T_2_max → T_2_min (ΔT increasing)
                   Starting from haline-driven state

    Returns:
        dict with keys:
            T_2_values: array of T_2 values (degrees C)
            delta_T_values: array of ΔT values (T_1 - T_2)
            q_forward: array of steady-state q for forward sweep
            q_backward: array of steady-state q for backward sweep
            tipping_points: list of dicts with delta_T and q values
    """
    T_2_values = np.linspace(T_2_min, T_2_max, n_points)
    delta_T_values = base_model.T_1 - T_2_values

    # Forward sweep: T_2 increasing (ΔT decreasing)
    q_forward = np.zeros(n_points)
    state = np.array([base_model.S_1_eq, base_model.S_2_eq])  # Start near equilibrium

    for i, T_2 in enumerate(T_2_values):
        model_T = StommelModel(
            T_1=base_model.T_1,
            T_2=T_2,
            S_1_eq=base_model.S_1_eq,
            S_2_eq=base_model.S_2_eq,
            alpha=base_model.alpha,
            beta=base_model.beta,
            k=base_model.k,
            lam=base_model.lam,
            t_max=100.0,  # Shorter integration for bifurcation (100 years)
            noise_amplitude=0.0,
        )
        result = _run_simulation_deterministic(
            model_T, state[0], state[1], t_max=100.0, dt=1.0
        )
        state = np.array(result["final_state"])
        q_forward[i] = float(result["q"][-1])

    # Backward sweep: start from fresh polar box condition (S_2 = 38)
    q_backward = np.zeros(n_points)
    state = np.array([base_model.S_1_eq, 38.0])

    for i, T_2 in enumerate(T_2_values[::-1]):
        idx = n_points - 1 - i
        model_T = StommelModel(
            T_1=base_model.T_1,
            T_2=T_2,
            S_1_eq=base_model.S_1_eq,
            S_2_eq=base_model.S_2_eq,
            alpha=base_model.alpha,
            beta=base_model.beta,
            k=base_model.k,
            lam=base_model.lam,
            t_max=100.0,
            noise_amplitude=0.0,
        )
        result = _run_simulation_deterministic(
            model_T, state[0], state[1], t_max=100.0, dt=1.0
        )
        state = np.array(result["final_state"])
        q_backward[idx] = float(result["q"][-1])

    # Detect tipping points: large jumps in q between adjacent T_2 values
    tipping_points = []
    threshold = 2e-7  # Threshold for detecting large jumps (1/s)

    # Forward tipping (circulation weakens as T_2 increases, ΔT decreases)
    for i in range(n_points - 1):
        if abs(q_forward[i + 1] - q_forward[i]) > threshold:
            tipping_points.append(
                {
                    "T_2": float(T_2_values[i + 1]),
                    "delta_T": float(delta_T_values[i + 1]),
                    "q": float(q_forward[i + 1]),
                    "direction": "forward",
                }
            )

    # Backward tipping (circulation strengthens as T_2 decreases, ΔT increases)
    for i in range(n_points - 1):
        if abs(q_backward[i + 1] - q_backward[i]) > threshold:
            tipping_points.append(
                {
                    "T_2": float(T_2_values[i + 1]),
                    "delta_T": float(delta_T_values[i + 1]),
                    "q": float(q_backward[i + 1]),
                    "direction": "backward",
                }
            )

    return {
        "T_2_values": T_2_values.tolist(),
        "delta_T_values": delta_T_values.tolist(),
        "q_forward": q_forward.tolist(),
        "q_backward": q_backward.tolist(),
        "tipping_points": tipping_points,
    }
