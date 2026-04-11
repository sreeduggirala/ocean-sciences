export interface SimulationParams {
  // Temperature (Stommel 1961 original model)
  T_1: number  // Box 1 (equatorial) temperature (°C)
  T_2: number  // Box 2 (polar) temperature (°C)

  // Equilibrium salinity (restoring targets)
  S_1_eq: number  // Box 1 equilibrium salinity (psu)
  S_2_eq: number  // Box 2 equilibrium salinity (psu)

  // Initial conditions
  S_1_init: number  // Box 1 initial salinity (psu)
  S_2_init: number  // Box 2 initial salinity (psu)

  // Physical parameters (Stommel 1961 values)
  alpha: number    // Thermal expansion (1/°C)
  beta: number     // Haline contraction (1/psu)
  k: number        // Circulation coefficient (1/s)
  lam: number      // Relaxation rate (1/s)

  // Integration
  t_max: number   // Maximum time (years)
  dt: number      // Output time step (years)

  // Stochastic
  noise_amplitude: number  // Gaussian noise std (psu/s)
}

export interface SimulationResult {
  time: number[]
  S_1: number[]      // Box 1 salinity time series (psu)
  S_2: number[]      // Box 2 salinity time series (psu)
  q: number[]        // Circulation strength time series (1/s)
  q_sv: number[]     // Circulation in Sverdrups
  steady_state_reached: boolean
  final_state: [number, number]  // [S_1_final, S_2_final]
  metadata: Record<string, unknown>
}

export interface BifurcationResult {
  T_2_values: number[]    // T_2 values swept (°C)
  delta_T_values: number[] // ΔT = T_1 - T_2 values (°C)
  q_forward: number[]      // Forward sweep steady-state circulation (1/s)
  q_backward: number[]     // Backward sweep steady-state circulation (1/s)
  tipping_points: Array<{
    T_2: number
    delta_T: number
    q: number
    direction: string
  }>
}

export interface PresetConfig {
  name: string
  description: string
  params: Partial<SimulationParams>
}

export type PresetName = 'normal_amoc' | 'weakened_amoc' | 'collapsed_amoc' | 'stommel_original'

export const DEFAULT_PARAMS: SimulationParams = {
  T_1: 25.0,
  T_2: 5.0,
  S_1_eq: 36.0,
  S_2_eq: 34.0,
  S_1_init: 36.0,
  S_2_init: 34.0,
  alpha: 2.0e-4,
  beta: 1.0e-3,
  k: 3.0e-9,
  lam: 3.0e-11,
  t_max: 3000,
  dt: 1.0,
  noise_amplitude: 0.0,
}
