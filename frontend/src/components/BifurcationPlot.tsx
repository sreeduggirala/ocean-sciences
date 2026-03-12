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

  const F = bifurcation.F_values
  const q_forward = bifurcation.q_forward.map((q) => q * 3e17 / 1e6)
  const q_backward = bifurcation.q_backward.map((q) => q * 3e17 / 1e6)

  // Find tipping points
  const tippingPoints = bifurcation.tipping_points
    .map((tp) => ({
      ...tp,
      q_sv: tp.q * 3e17 / 1e6,
    }))
    .sort((a, b) => a.F - b.F)

  // Infer unstable middle branch (between tipping points if they exist)
  let unstable_F = []
  let unstable_q = []

  if (tippingPoints.length >= 2) {
    const f_start = tippingPoints[0].F
    const f_end = tippingPoints[tippingPoints.length - 1].F

    const midIndices = F.reduce((acc, f, i) => {
      if (f >= f_start && f <= f_end) {
        acc.push(i)
      }
      return acc
    }, [] as number[])

    if (midIndices.length > 0) {
      unstable_F = midIndices.map((i) => F[i])
      unstable_q = midIndices.map((i) => {
        // Interpolate middle branch
        return (q_forward[i] + q_backward[i]) / 2
      })
    }
  }

  return (
    <div style={{ backgroundColor: '#161b22', borderRadius: '0.5rem', padding: '1rem' }}>
      <h3 style={{ marginBottom: '1rem', color: '#58a6ff' }}>Bifurcation Diagram (F-sweep)</h3>

      <PlotlyChart
        data={[
          {
            x: F,
            y: q_forward,
            type: 'scatter',
            mode: 'lines',
            name: 'Forward sweep',
            line: { color: '#58a6ff', width: 3 },
          },
          {
            x: F,
            y: q_backward,
            type: 'scatter',
            mode: 'lines',
            name: 'Backward sweep',
            line: { color: '#ffa94d', width: 3 },
          },
          ...(unstable_F.length > 0
            ? [
                {
                  x: unstable_F,
                  y: unstable_q,
                  type: 'scatter',
                  mode: 'lines',
                  name: 'Unstable branch (inferred)',
                  line: { color: '#8b949e', width: 2, dash: 'dash' as const },
                },
              ]
            : []),
          // Hysteresis window shading
          ...(unstable_F.length > 0 && tippingPoints.length >= 2
            ? [
                {
                  x: [tippingPoints[0].F, tippingPoints[tippingPoints.length - 1].F],
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
          // AMOC reference lines
          {
            x: F,
            y: Array(F.length).fill(15),
            type: 'scatter',
            mode: 'lines',
            name: 'Present-day AMOC',
            line: { color: '#8b949e', width: 1, dash: 'dash' },
          },
          {
            x: F,
            y: Array(F.length).fill(5),
            type: 'scatter',
            mode: 'lines',
            name: 'Weakened state',
            line: { color: '#8b949e', width: 1, dash: 'dot' },
          },
          {
            x: F,
            y: Array(F.length).fill(0),
            type: 'scatter',
            mode: 'lines',
            name: 'Collapse',
            line: { color: '#ff6b6b', width: 2 },
          },
          // Current state marker
          {
            x: [params.F],
            y: [0],
            type: 'scatter',
            mode: 'markers',
            name: 'Current F',
            marker: { size: 10, color: '#ffa94d', symbol: 'x' },
          },
          // Tipping points
          ...tippingPoints.map((tp) => ({
            x: [tp.F],
            y: [tp.q_sv],
            type: 'scatter' as const,
            mode: 'markers' as const,
            name: `Tipping (F=${tp.F.toExponential(1)})`,
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
            title: 'Freshwater flux F (psu/s)',
            gridcolor: '#30363d',
            zeroline: false,
          },
          yaxis: {
            title: 'Steady-state q (Sv)',
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
