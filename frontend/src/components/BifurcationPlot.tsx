import React from 'react'
import PlotlyChart from './PlotlyChart'
import { useSimulation } from '../hooks/useSimulation'

const BifurcationPlot: React.FC = () => {
  const { bifurcation, params } = useSimulation()

  if (!bifurcation) {
    return (
      <div
        style={{
          padding: '2rem',
          backgroundColor: '#161b22',
          borderRadius: '0.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '400px',
        }}
      >
        <p style={{ color: '#8b949e' }}>Run bifurcation analysis to see diagram</p>
      </div>
    )
  }

  const deltaT = bifurcation.delta_T_values
  const q_forward = bifurcation.q_forward  // Already in 1/s
  const q_backward = bifurcation.q_backward

  // Find tipping points
  const tippingPoints = bifurcation.tipping_points
    .sort((a, b) => a.delta_T - b.delta_T)

  // Infer unstable middle branch (between tipping points if they exist)
  let unstable_deltaT: number[] = []
  let unstable_q: number[] = []

  if (tippingPoints.length >= 2) {
    const dt_start = tippingPoints[0].delta_T
    const dt_end = tippingPoints[tippingPoints.length - 1].delta_T

    const midIndices = deltaT.reduce((acc, dt, i) => {
      if (dt >= dt_start && dt <= dt_end) {
        acc.push(i)
      }
      return acc
    }, [] as number[])

    if (midIndices.length > 0) {
      unstable_deltaT = midIndices.map((i) => deltaT[i])
      unstable_q = midIndices.map((i) => {
        // Interpolate middle branch
        return (q_forward[i] + q_backward[i]) / 2
      })
    }
  }

  return (
    <div style={{ backgroundColor: '#161b22', borderRadius: '0.5rem', padding: '1rem' }}>
      <h3 style={{ marginBottom: '1rem', color: '#58a6ff' }}>Bifurcation Diagram (ΔT-sweep)</h3>

      <PlotlyChart
        data={[
          {
            x: deltaT,
            y: q_forward,
            type: 'scatter',
            mode: 'lines',
            name: 'Forward sweep (ΔT↑)',
            line: { color: '#58a6ff', width: 3 },
          },
          {
            x: deltaT,
            y: q_backward,
            type: 'scatter',
            mode: 'lines',
            name: 'Backward sweep (ΔT↓)',
            line: { color: '#ffa94d', width: 3 },
          },
          ...(unstable_deltaT.length > 0
            ? [
                {
                  x: unstable_deltaT,
                  y: unstable_q,
                  type: 'scatter',
                  mode: 'lines',
                  name: 'Unstable branch (inferred)',
                  line: { color: '#8b949e', width: 2, dash: 'dash' as const },
                },
              ]
            : []),
          // Hysteresis window shading
          ...(unstable_deltaT.length > 0 && tippingPoints.length >= 2
            ? [
                {
                  x: [tippingPoints[0].delta_T, tippingPoints[tippingPoints.length - 1].delta_T],
                  y: [
                    Math.min(...q_forward.slice(0, 100)),
                    Math.min(...q_forward.slice(0, 100)),
                  ],
                  type: 'scatter',
                  mode: 'none',
                  fill: 'tozeroy',
                  fillcolor: 'rgba(255, 165, 77, 0.1)',
                  name: 'Hysteresis window',
                } as any,
              ]
            : []),
          // Reference lines
          {
            x: deltaT,
            y: Array(deltaT.length).fill(0),
            type: 'scatter',
            mode: 'lines',
            name: 'q = 0 (Collapse)',
            line: { color: '#ff6b6b', width: 2 },
          },
          {
            x: deltaT,
            y: Array(deltaT.length).fill(1e-6),
            type: 'scatter',
            mode: 'lines',
            name: 'Typical modern (~1e-6)',
            line: { color: '#8b949e', width: 1, dash: 'dash' },
          },
          // Current state marker
          {
            x: [params.T_1 - params.T_2],
            y: [0],
            type: 'scatter',
            mode: 'markers',
            name: `Current ΔT (${(params.T_1 - params.T_2).toFixed(1)}°C)`,
            marker: { size: 10, color: '#ffa94d', symbol: 'x' },
          },
          // Tipping points
          ...tippingPoints.map((tp) => ({
            x: [tp.delta_T],
            y: [tp.q],
            type: 'scatter' as const,
            mode: 'markers' as const,
            name: `Bifurcation (ΔT=${tp.delta_T.toFixed(1)}°C)`,
            marker: { size: 10, color: '#ff6b6b', symbol: 'diamond' as const },
          })),
        ]}
        layout={{
          title: '',
          hovermode: 'x unified',
          paper_bgcolor: '#0d1117',
          plot_bgcolor: '#0d1117',
          font: { color: '#c9d1d9', family: 'monospace', size: 11 },
          margin: { l: 60, r: 60, t: 20, b: 40 },
          height: 400,
          xaxis: {
            title: 'Temperature difference ΔT = T₁ - T₂ (°C)',
            gridcolor: '#30363d',
            zeroline: false,
          },
          yaxis: {
            title: 'Steady-state q (1/s)',
            gridcolor: '#30363d',
            zeroline: true,
            zerolinecolor: '#ff6b6b',
          },
          legend: {
            x: 0,
            y: 1,
            bgcolor: 'rgba(0,0,0,0)',
            bordercolor: '#30363d',
            borderwidth: 1,
          },
        }}
        config={{ responsive: true, displayModeBar: true }}
      />
    </div>
  )
}

export default BifurcationPlot
