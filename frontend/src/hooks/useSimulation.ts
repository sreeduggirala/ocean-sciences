import { create } from 'zustand'
import { api } from '../api'
import { SimulationParams, SimulationResult, BifurcationResult, DEFAULT_PARAMS } from '../types'

interface SimulationState {
  params: SimulationParams
  result: SimulationResult | null
  bifurcation: BifurcationResult | null
  isLoading: boolean
  error: string | null
  lastRunTime: number | null

  // Actions
  setParams: (updates: Partial<SimulationParams>) => void
  runSimulation: () => Promise<void>
  runBifurcation: () => Promise<void>
  loadPreset: (presetName: string) => Promise<void>
  reset: () => void
  clearError: () => void
  exportResults: () => void
}

export const useSimulation = create<SimulationState>((set, get) => ({
  params: DEFAULT_PARAMS,
  result: null,
  bifurcation: null,
  isLoading: false,
  error: null,
  lastRunTime: null,

  setParams: (updates) => {
    set((state) => ({
      params: { ...state.params, ...updates },
      error: null,
    }))
    // Auto-run with debounce (500ms)
    const state = get()
    setTimeout(() => {
      if (state.result) {
        state.runSimulation()
      }
    }, 500)
  },

  runSimulation: async () => {
    const { params } = get()
    set({ isLoading: true, error: null })
    const startTime = performance.now()

    try {
      const result = await api.simulate(params)
      const endTime = performance.now()
      set({
        result,
        isLoading: false,
        lastRunTime: endTime - startTime,
      })
    } catch (err) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      })
    }
  },

  runBifurcation: async () => {
    const { params } = get()
    set({ isLoading: true, error: null })

    try {
      const bifurcation = await api.bifurcation({
        T_e: params.T_e,
        T_p: params.T_p,
        S_e0: params.S_e0,
        S_p0: params.S_p0,
        alpha: params.alpha,
        beta: params.beta,
        k: params.k,
        F_min: 0,
        F_max: 5e-4,
        n_points: 200,
      })
      set({
        bifurcation,
        isLoading: false,
      })
    } catch (err) {
      set({
        isLoading: false,
        error: err instanceof Error ? err.message : 'Unknown error',
      })
    }
  },

  loadPreset: async (presetName) => {
    try {
      const presets = await api.getPresets()
      const preset = presets.find((p) => p.name === presetName)
      if (preset) {
        set((state) => ({
          params: { ...state.params, ...preset.params },
          error: null,
        }))
        // Run simulation immediately
        await get().runSimulation()
      }
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to load preset',
      })
    }
  },

  reset: () => {
    set({
      params: DEFAULT_PARAMS,
      result: null,
      bifurcation: null,
      error: null,
      lastRunTime: null,
    })
  },

  clearError: () => {
    set({ error: null })
  },

  exportResults: () => {
    const { result } = get()
    if (!result) {
      alert('No results to export')
      return
    }

    const json = JSON.stringify(result, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `stommel-results-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  },
}))
