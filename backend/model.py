"""
Stommel (1961) Two-Box Thermohaline Circulation Model

Original formulation with relaxation-toward-equilibrium salinity forcing:
    H_i = -λ_i(S_i - S_i^0)

Density: ρ = ρ₀(1 − αT + βS)
Circulation: q = k[α(T_1 − T_2) − β(S_1 − S_2)]

ODE system:
    dS_1/dt = H_1 + q(S_2 - S_1) = -λ_1(S_1 - S_1^0) + q(S_2 - S_1)
    dS_2/dt = H_2 + q(S_1 - S_2) = -λ_2(S_2 - S_2^0) + q(S_1 - S_2)
"""
from dataclasses import dataclass
import numpy as np


@dataclass
class StommelModel:
    """
    Two-box thermohaline circulation model (Stommel 1961).

    Boxes: 1 = Equatorial (warm, salty), 2 = Polar (cold, fresh)
    Density: ρ = ρ₀(1 − αT + βS)
    Circulation: q = k[α(T_1 − T_2) − β(S_1 − S_2)]

    Relaxation forcing: H_i = -λ_i(S_i - S_i^0)
    Relaxation timescale: τ = 1/λ ≈ 1000 years
    """

    # Temperature (fixed)
    T_1: float = 25.0  # Box 1 (equatorial) temperature (°C)
    T_2: float = 5.0   # Box 2 (polar) temperature (°C)

    # Equilibrium salinity (restoring targets)
    S_1_eq: float = 36.0  # Box 1 equilibrium salinity (psu)
    S_2_eq: float = 34.0  # Box 2 equilibrium salinity (psu)

    # Thermal expansion and haline contraction (Stommel 1961 values)
    alpha: float = 2.0e-4  # Thermal expansion coefficient (1/°C)
    beta: float = 1.0e-3   # Haline contraction coefficient (1/psu)

    # Circulation strength parameter (Stommel 1961 value)
    k: float = 3.0e-9  # Circulation coefficient (1/s)

    # Relaxation coefficient (Stommel 1961 value)
    # λ ≈ 3×10^-11 s^-1 ≈ 1/(1000 years) ≈ 1/(30 million seconds)
    lam: float = 3.0e-11  # Relaxation rate (1/s), "lam" to avoid Python 'lambda' keyword

    # Maximum time
    t_max: float = 3000.0  # Maximum integration time (years)

    # Stochastic forcing
    noise_amplitude: float = 0.0  # Gaussian noise std (psu/s)

    def q(self, S_1: float, S_2: float) -> float:
        """
        Circulation strength (positive = thermally driven, AMOC-like).

        q = k[α(T_1 − T_2) − β(S_1 − S_2)]

        Args:
            S_1: Box 1 (equatorial) salinity (psu)
            S_2: Box 2 (polar) salinity (psu)

        Returns:
            Circulation strength (1/s)
        """
        dT = self.T_1 - self.T_2
        dS = S_1 - S_2
        return self.k * (self.alpha * dT - self.beta * dS)

    def rhs(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Right-hand side of ODE system for solve_ivp (time in seconds).

        dS_1/dt = H_1 + q(S_2 - S_1) = -λ(S_1 - S_1^0) + q(S_2 - S_1)
        dS_2/dt = H_2 + q(S_1 - S_2) = -λ(S_2 - S_2^0) + q(S_1 - S_2)

        Args:
            t: Time in seconds (not used, system is autonomous)
            state: [S_1, S_2]

        Returns:
            [dS_1/dt, dS_2/dt] in units of psu/s
        """
        S_1, S_2 = state
        q_val = self.q(S_1, S_2)
        # Relaxation forcing
        H_1 = -self.lam * (S_1 - self.S_1_eq)
        H_2 = -self.lam * (S_2 - self.S_2_eq)
        # Transport + relaxation
        dS_1_dt = H_1 - q_val * (S_1 - S_2)
        dS_2_dt = H_2 + q_val * (S_1 - S_2)
        return np.array([dS_1_dt, dS_2_dt])

    def rhs_years(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Right-hand side of ODE system with time in years.

        Converts circulation strength and relaxation rate from 1/s to 1/year.

        dS_1/dt = H_1 + q(S_2 - S_1) = -λ(S_1 - S_1^0) + q(S_2 - S_1)
        dS_2/dt = H_2 + q(S_1 - S_2) = -λ(S_2 - S_2^0) + q(S_1 - S_2)

        Args:
            t: Time in years (not used, system is autonomous)
            state: [S_1, S_2]

        Returns:
            [dS_1/dt, dS_2/dt] in units of psu/year
        """
        YEARS_TO_SECONDS = 365.25 * 24 * 3600
        S_1, S_2 = state
        # Convert q and λ from 1/s to 1/year
        q_val = self.q(S_1, S_2) * YEARS_TO_SECONDS
        lam_per_year = self.lam * YEARS_TO_SECONDS
        # Relaxation forcing (per year)
        H_1 = -lam_per_year * (S_1 - self.S_1_eq)
        H_2 = -lam_per_year * (S_2 - self.S_2_eq)
        # Transport + relaxation
        dS_1_dt = H_1 - q_val * (S_1 - S_2)
        dS_2_dt = H_2 + q_val * (S_1 - S_2)
        return np.array([dS_1_dt, dS_2_dt])

    def equilibrium_delta_S(self) -> list[float]:
        """
        Find equilibrium salt differences ΔS* = S_1 - S_2 from relaxation equilibrium.

        At equilibrium (dS_1/dt = 0, dS_2/dt = 0), rearranging gives:
            λ(ΔS* - ΔS₀) + 2q·ΔS* = 0

        Substituting q = k[α(T_1 - T_2) - β·ΔS*]:
            2kβ(ΔS*)² - (2kαΔT + λ)(ΔS*) + λΔS₀ = 0

        This is a quadratic in ΔS* with solutions representing stable/unstable equilibria.

        Returns:
            list of equilibrium ΔS* values (real roots only)
        """
        dT = self.T_1 - self.T_2
        dS_0 = self.S_1_eq - self.S_2_eq

        # Quadratic: a(ΔS)² + b(ΔS) + c = 0
        a = 2 * self.k * self.beta
        b = -(2 * self.k * self.alpha * dT + self.lam)
        c = self.lam * dS_0

        if abs(a) < 1e-15:
            # Degenerate case: linear equation
            if abs(b) < 1e-15:
                return []
            return [-c / b]

        # Solve quadratic
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            return []

        sqrt_disc = np.sqrt(discriminant)
        root1 = (-b + sqrt_disc) / (2*a)
        root2 = (-b - sqrt_disc) / (2*a)

        return [root1, root2]
