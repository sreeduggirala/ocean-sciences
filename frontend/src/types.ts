export interface SimulationParams {
  // Temperature
  T_e: number
  T_p: number

  // Initial salinity
  S_e0: number
  S_p0: number

  // Parameters
  alpha: number
  beta: number
  k: number
  F: number

  // Integration
  t_max: number
  dt: number

  // Stochastic
  noise_amplitude: number
}

export interface SimulationResult {
  time: number[]
  S_e: number[]
  S_p: number[]
  q: number[]
  q_sv: number[]
  steady_state_reached: boolean
  final_state: [number, number]
  metadata: Record<string, unknown>
}

export interface BifurcationResult {
  F_values: number[]
  q_forward: number[]
  q_backward: number[]
  tipping_points: Array<{
    F: number
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
  T_e: 25.0,
  T_p: 5.0,
  S_e0: 36.0,
  S_p0: 34.0,
  alpha: 1.5e-4,
  beta: 8.0e-4,
  k: 1.5e-6,
  F: 1.0e-4,
  t_max: 3000,
  dt: 1.0,
  noise_amplitude: 0.0,
}
