import React, { useMemo } from 'react'
import PlotlyChart from './PlotlyChart'
import { useSimulation } from '../hooks/useSimulation'

const AMOCComparison: React.FC = () => {
  const { result } = useSimulation()

  // RAPID Array mean values (2004-2020)
  const RAPID_MEAN = 16.9

  const plotData = useMemo(() => {
    if (!result) return null

    const finalQ = result.q_sv[result.q_sv.length - 1]

    // Classify regime
    let regime = 'Neutral'
    let regimeColor = '#8b949e'

    if (finalQ > 10) {
      regime = 'Thermally Driven (Normal)'
      regimeColor = '#58a6ff'
    } else if (finalQ > 0 && finalQ <= 10) {
      regime = 'Weakened AMOC'
      regimeColor = '#ffa94d'
    } else if (finalQ <= 0) {
      regime = 'Collapsed/Reversed'
      regimeColor = '#ff6b6b'
    }

    return {
      finalQ,
      regime,
      regimeColor,
    }
  }, [result])

  if (!plotData) {
    return (
      <div
        style={{
          padding: '2rem',
          backgroundColor: '#161b22',
          borderRadius: '0.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '300px',
        }}
      >
        <p style={{ color: '#8b949e' }}>Run a simulation to see AMOC comparison</p>
      </div>
    )
  }

  return (
    <div style={{ backgroundColor: '#161b22', borderRadius: '0.5rem', padding: '1rem' }}>
      <h3 style={{ marginBottom: '1rem', color: '#58a6ff' }}>Model vs Observations</h3>

      <PlotlyChart
        data={[
          {
            x: ['Stommel Model', 'RAPID Array\n(2004-2020)'],
            y: [plotData.finalQ, RAPID_MEAN],
            type: 'bar',
            marker: {
              color: [plotData.regimeColor, '#58a6ff'],
            },
            text: [
              `${plotData.finalQ.toFixed(1)} Sv`,
              `${RAPID_MEAN.toFixed(1)} Sv`,
            ],
            textposition: 'outside',
          },
        ]}
        layout={{
          title: '',
          paper_bgcolor: '#0d1117',
          plot_bgcolor: '#0d1117',
          font: { color: '#c9d1d9', family: 'monospace', size: 11 },
          margin: { l: 60, r: 60, t: 20, b: 40 },
          height: 300,
          yaxis: {
            title: 'Circulation Strength (Sv)',
            gridcolor: '#30363d',
            zeroline: true,
            zerolinecolor: '#ff6b6b',
          },
          showlegend: false,
        }}
        config={{ responsive: true, displayModeBar: false }}
      />

      <div
        style={{
          marginTop: '1.5rem',
          padding: '1rem',
          backgroundColor: '#0d1117',
          borderRadius: '0.3rem',
          borderLeft: `4px solid ${plotData.regimeColor}`,
        }}
      >
        <p style={{ marginBottom: '0.5rem', color: plotData.regimeColor, fontWeight: 600 }}>
          Regime: {plotData.regime}
        </p>
        <p style={{ color: '#8b949e', fontSize: '0.9rem', lineHeight: 1.5 }}>
          The Stommel (1961) model captures the essential physics of Atlantic Meridional Overturning
          Circulation (AMOC) tipping points via thermal-haline instability. The model's simple two-box
          structure reveals how freshwater forcing (from ice sheet melt, Arctic sea ice loss) can
          flip the circulation between stable states, with profound climate consequences.
        </p>
      </div>
    </div>
  )
}

export default AMOCComparison
