import { useEffect } from 'react'
import { useSimulation } from './hooks/useSimulation'
import ParameterControls from './components/ParameterControls'
import OceanBoxDiagram from './components/OceanBoxDiagram'
import TimeSeriesPlot from './components/TimeSeriesPlot'
import PhaseSpacePlot from './components/PhaseSpacePlot'
import BifurcationPlot from './components/BifurcationPlot'
import AMOCComparison from './components/AMOCComparison'

function App() {
  const { error, clearError } = useSimulation()

  useEffect(() => {
    // Run initial simulation on mount
    useSimulation.getState().runSimulation()
  }, [])

  return (
    <div
      style={{
        backgroundColor: '#0d1117',
        color: '#c9d1d9',
        minHeight: '100vh',
        padding: '2rem',
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ color: '#58a6ff', marginBottom: '0.5rem' }}>
          Stommel 1961 Thermohaline Circulation
        </h1>
        <p style={{ color: '#8b949e', fontSize: '0.95rem' }}>
          Interactive exploration of AMOC tipping points and hysteresis dynamics
        </p>
      </div>

      {/* Error banner */}
      {error && (
        <div
          style={{
            marginBottom: '2rem',
            padding: '1rem',
            backgroundColor: '#da3633',
            borderRadius: '0.5rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>{error}</span>
          <button
            onClick={clearError}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              color: '#fff',
              cursor: 'pointer',
              fontSize: '1.2rem',
            }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Main layout: 2 columns */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '300px 1fr',
          gap: '2rem',
          maxWidth: '1600px',
          margin: '0 auto',
        }}
      >
        {/* Left column: Controls */}
        <div>
          <ParameterControls />
        </div>

        {/* Right column: Visualization grid (2x3) */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '1.5rem',
          }}
        >
          {/* Row 1 */}
          <div style={{ gridColumn: '1' }}>
            <OceanBoxDiagram />
          </div>
          <div style={{ gridColumn: '2' }}>
            <AMOCComparison />
          </div>

          {/* Row 2 */}
          <div style={{ gridColumn: '1 / -1' }}>
            <TimeSeriesPlot />
          </div>

          {/* Row 3 */}
          <div style={{ gridColumn: '1' }}>
            <PhaseSpacePlot />
          </div>
          <div style={{ gridColumn: '2' }}>
            <BifurcationPlot />
          </div>
        </div>
      </div>

      {/* Footer */}
      <div
        style={{
          marginTop: '4rem',
          padding: '2rem',
          textAlign: 'center',
          color: '#8b949e',
          borderTop: '1px solid #30363d',
        }}
      >
        <p style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>
          Based on Stommel, H. (1961). A Mathematical Model of the Atlantic Meridional Overturning
          Circulation.
        </p>
        <p style={{ fontSize: '0.85rem' }}>
          Educational tool for understanding climate tipping points | Built with React + FastAPI
        </p>
      </div>
    </div>
  )
}

export default App
