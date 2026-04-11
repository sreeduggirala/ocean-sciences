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

let debounceTimer: ReturnType<typeof setTimeout> | null = null

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
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      const current = get()
      if (current.result) {
        current.runSimulation()
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
        T_1: params.T_1,
        T_2: params.T_2,
        S_1_eq: params.S_1_eq,
        S_2_eq: params.S_2_eq,
        alpha: params.alpha,
        beta: params.beta,
        k: params.k,
        lam: params.lam,
        T_2_min: 0,
        T_2_max: 20,
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
