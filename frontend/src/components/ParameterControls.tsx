import React, { useState } from 'react'
import * as Collapsible from '@radix-ui/react-collapsible'
import { useSimulation } from '../hooks/useSimulation'

const ParameterControls: React.FC = () => {
  const { params, setParams, runSimulation, reset, bifurcation, isLoading, loadPreset } =
    useSimulation()
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    ocean: true,
    physics: true,
    forcing: false,
    integration: false,
  })

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const handleSliderChange = (key: keyof typeof params, value: number) => {
    setParams({ [key]: value })
  }

  const formatScientific = (value: number): string => {
    if (Math.abs(value) < 1e-2 || Math.abs(value) > 1e4) {
      return value.toExponential(2)
    }
    return value.toFixed(4)
  }

  const SliderInput = ({
    label,
    key,
    value,
    min,
    max,
    step,
    logScale = false,
  }: {
    label: string
    key: keyof typeof params
    value: number
    min: number
    max: number
    step: number
    logScale?: boolean
  }) => {
    const logValue = logScale ? Math.log10(value) : value
    const logMin = logScale ? Math.log10(min) : min
    const logMax = logScale ? Math.log10(max) : max
    const logStep = logScale ? (logMax - logMin) / 100 : step

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const rawValue = parseFloat(e.target.value)
      const actualValue = logScale ? Math.pow(10, rawValue) : rawValue
      handleSliderChange(key, actualValue)
    }

    return (
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <label style={{ fontSize: '0.9rem', fontWeight: 500 }}>{label}</label>
          <span style={{ fontSize: '0.9rem', fontFamily: 'monospace', color: '#58a6ff' }}>
            {formatScientific(value)}
          </span>
        </div>
        <input
          type="range"
          min={logMin}
          max={logMax}
          step={logStep}
          value={logValue}
          onChange={handleChange}
          style={{
            width: '100%',
            cursor: 'pointer',
          }}
        />
      </div>
    )
  }

  return (
    <div
      style={{
        padding: '1.5rem',
        backgroundColor: '#161b22',
        borderRadius: '0.5rem',
        height: '100%',
        overflowY: 'auto',
      }}
    >
      <h2 style={{ marginBottom: '1.5rem', color: '#58a6ff' }}>Control Panel</h2>

      {/* Presets */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
          <button
            onClick={() => loadPreset('normal_amoc')}
            style={{
              padding: '0.6rem',
              backgroundColor: '#238636',
              color: '#fff',
              border: 'none',
              borderRadius: '0.3rem',
              cursor: 'pointer',
              fontSize: '0.85rem',
            }}
          >
            Normal AMOC
          </button>
          <button
            onClick={() => loadPreset('weakened_amoc')}
            style={{
              padding: '0.6rem',
              backgroundColor: '#238636',
              color: '#fff',
              border: 'none',
              borderRadius: '0.3rem',
              cursor: 'pointer',
              fontSize: '0.85rem',
            }}
          >
            Weakened
          </button>
          <button
            onClick={() => loadPreset('collapsed_amoc')}
            style={{
              padding: '0.6rem',
              backgroundColor: '#238636',
              color: '#fff',
              border: 'none',
              borderRadius: '0.3rem',
              cursor: 'pointer',
              fontSize: '0.85rem',
            }}
          >
            Collapsed
          </button>
          <button
            onClick={() => loadPreset('stommel_original')}
            style={{
              padding: '0.6rem',
              backgroundColor: '#238636',
              color: '#fff',
              border: 'none',
              borderRadius: '0.3rem',
              cursor: 'pointer',
              fontSize: '0.85rem',
            }}
          >
            Stommel 1961
          </button>
        </div>
      </div>

      {/* Ocean State */}
      <Collapsible.Root
        open={expandedSections.ocean}
        onOpenChange={() => toggleSection('ocean')}
      >
        <Collapsible.Trigger
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#0d1117',
            border: '1px solid #30363d',
            borderRadius: '0.3rem',
            color: '#c9d1d9',
            cursor: 'pointer',
            marginBottom: '1rem',
            fontSize: '0.95rem',
            fontWeight: 600,
          }}
        >
          {expandedSections.ocean ? '▼' : '▶'} Ocean State
        </Collapsible.Trigger>
        <Collapsible.Content>
          <SliderInput
            label="T_e (Equatorial °C)"
            key="T_e"
            value={params.T_e}
            min={15}
            max={35}
            step={0.1}
          />
          <SliderInput
            label="T_p (Polar °C)"
            key="T_p"
            value={params.T_p}
            min={-2}
            max={15}
            step={0.1}
          />
          <SliderInput
            label="S_e0 (Equatorial psu)"
            key="S_e0"
            value={params.S_e0}
            min={30}
            max={40}
            step={0.1}
          />
          <SliderInput
            label="S_p0 (Polar psu)"
            key="S_p0"
            value={params.S_p0}
            min={28}
            max={40}
            step={0.1}
          />
        </Collapsible.Content>
      </Collapsible.Root>

      {/* Physics */}
      <Collapsible.Root
        open={expandedSections.physics}
        onOpenChange={() => toggleSection('physics')}
      >
        <Collapsible.Trigger
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#0d1117',
            border: '1px solid #30363d',
            borderRadius: '0.3rem',
            color: '#c9d1d9',
            cursor: 'pointer',
            marginBottom: '1rem',
            fontSize: '0.95rem',
            fontWeight: 600,
          }}
        >
          {expandedSections.physics ? '▼' : '▶'} Physics Parameters
        </Collapsible.Trigger>
        <Collapsible.Content>
          <SliderInput
            label="α (Thermal expansion)"
            key="alpha"
            value={params.alpha}
            min={0.5e-4}
            max={3e-4}
            step={0.1e-4}
          />
          <SliderInput
            label="β (Haline contraction)"
            key="beta"
            value={params.beta}
            min={2e-4}
            max={1.5e-3}
            step={0.1e-4}
          />
          <SliderInput
            label="k (Circulation coefficient, log)"
            key="k"
            value={params.k}
            min={5e-8}
            max={1e-5}
            step={0.01}
            logScale
          />
        </Collapsible.Content>
      </Collapsible.Root>

      {/* Forcing */}
      <Collapsible.Root
        open={expandedSections.forcing}
        onOpenChange={() => toggleSection('forcing')}
      >
        <Collapsible.Trigger
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#0d1117',
            border: '1px solid #30363d',
            borderRadius: '0.3rem',
            color: '#c9d1d9',
            cursor: 'pointer',
            marginBottom: '1rem',
            fontSize: '0.95rem',
            fontWeight: 600,
          }}
        >
          {expandedSections.forcing ? '▼' : '▶'} Forcing
        </Collapsible.Trigger>
        <Collapsible.Content>
          <SliderInput
            label="F (Freshwater flux, psu/s)"
            key="F"
            value={params.F}
            min={0}
            max={5e-4}
            step={0.1e-4}
          />
          <SliderInput
            label="Noise amplitude (psu/s)"
            key="noise_amplitude"
            value={params.noise_amplitude}
            min={0}
            max={5e-5}
            step={0.1e-5}
          />
        </Collapsible.Content>
      </Collapsible.Root>

      {/* Integration */}
      <Collapsible.Root
        open={expandedSections.integration}
        onOpenChange={() => toggleSection('integration')}
      >
        <Collapsible.Trigger
          style={{
            width: '100%',
            padding: '0.75rem',
            backgroundColor: '#0d1117',
            border: '1px solid #30363d',
            borderRadius: '0.3rem',
            color: '#c9d1d9',
            cursor: 'pointer',
            marginBottom: '1rem',
            fontSize: '0.95rem',
            fontWeight: 600,
          }}
        >
          {expandedSections.integration ? '▼' : '▶'} Integration
        </Collapsible.Trigger>
        <Collapsible.Content>
          <SliderInput
            label="t_max (Maximum years)"
            key="t_max"
            value={params.t_max}
            min={100}
            max={10000}
            step={100}
          />
          <SliderInput
            label="dt (Output step, years)"
            key="dt"
            value={params.dt}
            min={0.1}
            max={100}
            step={0.1}
          />
        </Collapsible.Content>
      </Collapsible.Root>

      {/* Action Buttons */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '2rem' }}>
        <button
          onClick={() => runSimulation()}
          disabled={isLoading}
          style={{
            padding: '0.75rem',
            backgroundColor: '#238636',
            color: '#fff',
            border: 'none',
            borderRadius: '0.3rem',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontWeight: 600,
            opacity: isLoading ? 0.6 : 1,
          }}
        >
          {isLoading ? 'Running...' : 'Run Simulation'}
        </button>
        <button
          onClick={() => reset()}
          style={{
            padding: '0.75rem',
            backgroundColor: '#da3633',
            color: '#fff',
            border: 'none',
            borderRadius: '0.3rem',
            cursor: 'pointer',
            fontWeight: 600,
          }}
        >
          Reset
        </button>
      </div>

      {/* Bifurcation Button */}
      <button
        onClick={() => useSimulation.getState().runBifurcation()}
        disabled={isLoading}
        style={{
          width: '100%',
          padding: '0.75rem',
          backgroundColor: '#58a6ff',
          color: '#000',
          border: 'none',
          borderRadius: '0.3rem',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          fontWeight: 600,
          marginTop: '0.5rem',
          opacity: isLoading ? 0.6 : 1,
        }}
      >
        {isLoading ? 'Computing...' : 'Compute Bifurcation'}
      </button>
    </div>
  )
}

export default ParameterControls
