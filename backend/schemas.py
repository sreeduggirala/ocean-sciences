"""
Pydantic v2 schemas for request/response validation.
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional


class SimulationRequest(BaseModel):
    """Request body for /simulate endpoint (Stommel 1961 original model)."""

    # Temperature (fixed during integration)
    T_1: float = Field(default=25.0, ge=15, le=35, description="Box 1 (equatorial) temperature (°C)")
    T_2: float = Field(default=5.0, ge=-2, le=25, description="Box 2 (polar) temperature (°C)")

    # Equilibrium salinity (restoring targets)
    S_1_eq: float = Field(default=36.0, ge=30, le=40, description="Box 1 equilibrium salinity (psu)")
    S_2_eq: float = Field(default=34.0, ge=28, le=40, description="Box 2 equilibrium salinity (psu)")

    # Initial conditions for integration
    S_1_init: float = Field(default=36.0, ge=30, le=40, description="Box 1 initial salinity (psu)")
    S_2_init: float = Field(default=34.0, ge=28, le=40, description="Box 2 initial salinity (psu)")

    # Physical parameters (Stommel 1961 values)
    alpha: float = Field(default=2.0e-4, ge=0.5e-4, le=3e-4, description="Thermal expansion (1/°C)")
    beta: float = Field(default=1.0e-3, ge=2e-4, le=2e-3, description="Haline contraction (1/psu)")
    k: float = Field(default=3.0e-9, ge=1e-10, le=1e-6, description="Circulation coefficient (1/s)")
    lam: float = Field(default=3.0e-11, ge=1e-12, le=1e-9, description="Relaxation rate (1/s)")

    # Integration
    t_max: float = Field(default=3000, ge=100, le=10000, description="Maximum time (years)")
    dt: float = Field(default=1.0, ge=0.1, le=100, description="Output time step (years)")

    # Stochastic
    noise_amplitude: float = Field(default=0.0, ge=0, le=5e-5, description="Noise std (psu/s)")

    @model_validator(mode="after")
    def check_temperature_order(self):
        """Ensure T_1 > T_2."""
        if self.T_1 <= self.T_2:
            raise ValueError("T_1 must be greater than T_2")
        return self


class SimulationResponse(BaseModel):
    """Response from /simulate endpoint."""

    time: list[float]  # years
    S_1: list[float]  # psu (Box 1 salinity)
    S_2: list[float]  # psu (Box 2 salinity)
    q: list[float]  # 1/s (circulation strength)
    q_sv: list[float]  # Sv (circulation in Sverdrups)
    steady_state_reached: bool
    final_state: list[float]  # [S_1_final, S_2_final]
    metadata: dict = Field(default_factory=dict)


class BifurcationRequest(BaseModel):
    """Request body for /bifurcation endpoint (Stommel 1961 original model)."""

    # Temperature (T_1 is fixed, T_2 is swept)
    T_1: float = Field(default=25.0, ge=15, le=35, description="Box 1 (equatorial) temperature (°C)")
    T_2: float = Field(default=5.0, ge=-2, le=25, description="Box 2 initial temperature (°C)")

    # Equilibrium salinity
    S_1_eq: float = Field(default=36.0, ge=30, le=40, description="Box 1 equilibrium salinity (psu)")
    S_2_eq: float = Field(default=34.0, ge=28, le=40, description="Box 2 equilibrium salinity (psu)")

    # Physical parameters (Stommel 1961 values)
    alpha: float = Field(default=2.0e-4, ge=0.5e-4, le=3e-4, description="Thermal expansion (1/°C)")
    beta: float = Field(default=1.0e-3, ge=2e-4, le=2e-3, description="Haline contraction (1/psu)")
    k: float = Field(default=3.0e-9, ge=1e-10, le=1e-6, description="Circulation coefficient (1/s)")
    lam: float = Field(default=3.0e-11, ge=1e-12, le=1e-9, description="Relaxation rate (1/s)")

    # Bifurcation sweep (varying T_2 to change ΔT)
    T_2_min: float = Field(default=0.0, ge=-5, le=25, description="Minimum T_2 (°C)")
    T_2_max: float = Field(default=20.0, ge=0, le=30, description="Maximum T_2 (°C)")
    n_points: int = Field(default=200, ge=10, le=500, description="Number of points in sweep")

    @model_validator(mode="after")
    def check_T2_range(self):
        """Ensure T_2_min < T_2_max."""
        if self.T_2_min >= self.T_2_max:
            raise ValueError("T_2_min must be less than T_2_max")
        return self

    @model_validator(mode="after")
    def check_temperature_order(self):
        """Ensure T_1 > T_2 (at minimum T_2 value)."""
        if self.T_1 <= self.T_2_min:
            raise ValueError("T_1 must be greater than T_2_min")
        return self


class BifurcationResponse(BaseModel):
    """Response from /bifurcation endpoint."""

    T_2_values: list[float]  # T_2 values swept (°C)
    delta_T_values: list[float]  # ΔT = T_1 - T_2 values (°C)
    q_forward: list[float]  # Forward sweep steady-state circulation (1/s)
    q_backward: list[float]  # Backward sweep steady-state circulation (1/s)
    tipping_points: list[dict]  # Detected bifurcation points


class PresetConfig(BaseModel):
    """A preset configuration."""

    name: str
    description: str
    params: dict


class PresetsResponse(BaseModel):
    """Response from /presets endpoint."""

    presets: list[PresetConfig]
