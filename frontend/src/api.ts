import axios, { CancelTokenSource } from 'axios'
import { SimulationParams, SimulationResult, BifurcationResult, PresetConfig } from './types'

const API_BASE = '/api'

let cancelSource: CancelTokenSource | null = null

export const api = {
  async simulate(params: SimulationParams): Promise<SimulationResult> {
    // Cancel previous request if in flight
    if (cancelSource) {
      cancelSource.cancel('New request initiated')
    }
    cancelSource = axios.CancelToken.source()

    try {
      const response = await axios.post<SimulationResult>(
        `${API_BASE}/simulate`,
        params,
        { cancelToken: cancelSource.token }
      )
      return response.data
    } catch (error) {
      if (axios.isCancel(error)) {
        throw new Error('Request cancelled')
      }
      throw error
    }
  },

  async bifurcation(params: {
    T_1: number
    T_2: number
    S_1_eq: number
    S_2_eq: number
    alpha: number
    beta: number
    k: number
    lam: number
    T_2_min: number
    T_2_max: number
    n_points: number
  }): Promise<BifurcationResult> {
    if (cancelSource) {
      cancelSource.cancel('New request initiated')
    }
    cancelSource = axios.CancelToken.source()

    try {
      const response = await axios.post<BifurcationResult>(
        `${API_BASE}/bifurcation`,
        params,
        { cancelToken: cancelSource.token }
      )
      return response.data
    } catch (error) {
      if (axios.isCancel(error)) {
        throw new Error('Request cancelled')
      }
      throw error
    }
  },

  async getPresets(): Promise<PresetConfig[]> {
    const response = await axios.get<{ presets: PresetConfig[] }>(
      `${API_BASE}/presets`
    )
    return response.data.presets
  },

  async health(): Promise<boolean> {
    try {
      const response = await axios.get(`${API_BASE}/health`)
      return response.status === 200
    } catch {
      return false
    }
  },
}
