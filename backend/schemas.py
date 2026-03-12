"""
Pydantic v2 schemas for request/response validation.
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional


class SimulationRequest(BaseModel):
    """Request body for /simulate endpoint."""

    # Temperature
    T_e: float = Field(default=25.0, ge=15, le=35, description="Equatorial temperature (°C)")
    T_p: float = Field(default=5.0, ge=-2, le=15, description="Polar temperature (°C)")

    # Initial salinity
    S_e0: float = Field(default=36.0, ge=30, le=40, description="Initial equatorial salinity (psu)")
    S_p0: float = Field(default=34.0, ge=28, le=40, description="Initial polar salinity (psu)")

    # Parameters
    alpha: float = Field(default=1.5e-4, ge=0.5e-4, le=3e-4, description="Thermal expansion (1/°C)")
    beta: float = Field(default=8.0e-4, ge=2e-4, le=1.5e-3, description="Haline contraction (1/psu)")
    k: float = Field(default=1.5e-6, ge=5e-8, le=1e-5, description="Circulation coefficient (1/s)")
    F: float = Field(default=1.0e-4, ge=0, le=5e-4, description="Freshwater flux (psu/s)")

    # Integration
    t_max: float = Field(default=3000, ge=100, le=10000, description="Maximum time (years)")
    dt: float = Field(default=1.0, ge=0.1, le=100, description="Output time step (years)")

    # Stochastic
    noise_amplitude: float = Field(default=0.0, ge=0, le=5e-5, description="Noise std (psu/s)")

    @model_validator(mode="after")
    def check_temperature_order(self):
        """Ensure T_e > T_p."""
        if self.T_e <= self.T_p:
            raise ValueError("T_e must be greater than T_p")
        return self


class SimulationResponse(BaseModel):
    """Response from /simulate endpoint."""

    time: list[float]  # years
    S_e: list[float]  # psu
    S_p: list[float]  # psu
    q: list[float]  # 1/s
    q_sv: list[float]  # Sv
    steady_state_reached: bool
    final_state: list[float]  # [S_e_final, S_p_final]
    metadata: dict = Field(default_factory=dict)


class BifurcationRequest(BaseModel):
    """Request body for /bifurcation endpoint."""

    # Temperature
    T_e: float = Field(default=25.0, ge=15, le=35)
    T_p: float = Field(default=5.0, ge=-2, le=15)

    # Initial salinity
    S_e0: float = Field(default=36.0, ge=30, le=40)
    S_p0: float = Field(default=34.0, ge=28, le=40)

    # Parameters
    alpha: float = Field(default=1.5e-4, ge=0.5e-4, le=3e-4)
    beta: float = Field(default=8.0e-4, ge=2e-4, le=1.5e-3)
    k: float = Field(default=1.5e-6, ge=5e-8, le=1e-5)

    # Bifurcation sweep
    F_min: float = Field(default=0.0, ge=0)
    F_max: float = Field(default=5e-4, ge=0)
    n_points: int = Field(default=200, ge=10, le=500)

    @model_validator(mode="after")
    def check_F_range(self):
        """Ensure F_min < F_max."""
        if self.F_min >= self.F_max:
            raise ValueError("F_min must be less than F_max")
        return self

    @model_validator(mode="after")
    def check_temperature_order(self):
        """Ensure T_e > T_p."""
        if self.T_e <= self.T_p:
            raise ValueError("T_e must be greater than T_p")
        return self


class BifurcationResponse(BaseModel):
    """Response from /bifurcation endpoint."""

    F_values: list[float]
    q_forward: list[float]  # Sv
    q_backward: list[float]  # Sv
    tipping_points: list[dict]


class PresetConfig(BaseModel):
    """A preset configuration."""

    name: str
    description: str
    params: dict


class PresetsResponse(BaseModel):
    """Response from /presets endpoint."""

    presets: list[PresetConfig]
