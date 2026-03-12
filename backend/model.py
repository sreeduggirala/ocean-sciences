"""
Stommel 1961 Two-Box Thermohaline Circulation Model
"""
from dataclasses import dataclass
import numpy as np


@dataclass
class StommelModel:
    """
    Two-box thermohaline circulation model.

    Density: ρ = ρ₀(1 − αT + βS)
    Circulation: q = k[α(T_e − T_p) − β(S_e − S_p)]

    ODE system (salt conserved):
    dS_e/dt = −q(S_e − S_p) + F
    dS_p/dt = +q(S_e − S_p) − F
    """

    # Temperature (fixed)
    T_e: float = 25.0  # Equatorial temperature (°C)
    T_p: float = 5.0   # Polar temperature (°C)

    # Initial salinity
    S_e0: float = 36.0  # Equatorial salinity (psu)
    S_p0: float = 34.0  # Polar salinity (psu)

    # Thermal expansion and haline contraction
    alpha: float = 1.5e-4  # Thermal expansion coefficient (1/°C)
    beta: float = 8.0e-4   # Haline contraction coefficient (1/psu)

    # Circulation strength parameter
    k: float = 1.5e-6  # Circulation coefficient (1/s)

    # Freshwater forcing
    F: float = 1.0e-4  # Freshwater flux (psu/s)

    # Maximum time
    t_max: float = 3000.0  # Maximum integration time (years)

    # Stochastic forcing
    noise_amplitude: float = 0.0  # Gaussian noise std (psu/s)

    def q(self, S_e: float, S_p: float) -> float:
        """
        Circulation strength (positive = thermally driven, AMOC-like).

        q = k[α(T_e − T_p) − β(S_e − S_p)]

        Args:
            S_e: Equatorial salinity
            S_p: Polar salinity

        Returns:
            Circulation strength (1/s)
        """
        dT = self.T_e - self.T_p
        dS = S_e - S_p
        return self.k * (self.alpha * dT - self.beta * dS)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Right-hand side of ODE system for solve_ivp.

        Args:
            t: Time (not used, system is autonomous)
            state: [S_e, S_p]

        Returns:
            [dS_e/dt, dS_p/dt]
        """
        S_e, S_p = state
        q_val = self.q(S_e, S_p)
        dS_e_dt = -q_val * (S_e - S_p) + self.F
        dS_p_dt = +q_val * (S_e - S_p) - self.F
        return np.array([dS_e_dt, dS_p_dt])

    def q_cubic_roots(self, delta_S: float) -> list[float]:
        """
        Find steady-state circulation from q = k[α·ΔT − β·ΔS]
        at salt balance: F = q(S_e − S_p) = q·ΔS

        Combining: F = ΔS · k[α·ΔT − β·ΔS]
                   F = k·ΔS·α·ΔT − k·β·(ΔS)²

        Rearranging: k·β·(ΔS)² − k·α·ΔT·ΔS + F = 0

        Returns roots via numpy.roots (quadratic in this simplified form,
        but kept for generality if extending to 3-box models).
        """
        a = self.k * self.beta
        b = -self.k * self.alpha * (self.T_e - self.T_p)
        c = self.F

        if a == 0:
            if b == 0:
                return []
            return [-c / b]

        coeffs = [a, b, c]
        roots = np.roots(coeffs)
        # Return only real roots
        return [r.real for r in roots if abs(r.imag) < 1e-10]
