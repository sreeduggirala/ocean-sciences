import React, { useMemo } from 'react'
import PlotlyChart from './PlotlyChart'
import { useSimulation } from '../hooks/useSimulation'

const PhaseSpacePlot: React.FC = () => {
  const { result, params } = useSimulation()

  const plotData = useMemo(() => {
    if (!result) return null

    const S_e = result.S_e
    const S_p = result.S_p
    const q_sv = result.q_sv

    // Compute trajectory
    const deltaS = S_e.map((se, i) => se - S_p[i])

    // Compute nullcline analytically: q = k[α·ΔT − β·ΔS]
    const deltaS_range = Array.from({ length: 100 }, (_, i) => {
      const minDeltaS = Math.min(...deltaS) - 2
      const maxDeltaS = Math.max(...deltaS) + 2
      return minDeltaS + (i / 100) * (maxDeltaS - minDeltaS)
    })

    const q_nullcline = deltaS_range.map((ds) => {
      return params.k * (params.alpha * (params.T_e - params.T_p) - params.beta * ds) * 3e17 / 1e6
    })

    // Color trajectory by time
    const colors = Array.from({ length: deltaS.length }, (_, i) => i)

    return {
      deltaS,
      q_sv,
      deltaS_range,
      q_nullcline,
      colors,
    }
  }, [result, params])

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
          minHeight: '400px',
        }}
      >
        <p style={{ color: '#8b949e' }}>Run a simulation to see phase space</p>
      </div>
    )
  }

  return (
    <div style={{ backgroundColor: '#161b22', borderRadius: '0.5rem', padding: '1rem' }}>
      <h3 style={{ marginBottom: '1rem', color: '#58a6ff' }}>Phase Space (ΔS - q)</h3>

      <PlotlyChart
        data={[
          {
            x: plotData.deltaS,
            y: plotData.q_sv,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Trajectory',
            line: { color: '#58a6ff', width: 2 },
            marker: {
              size: 3,
              color: plotData.colors,
              colorscale: 'Viridis',
              showscale: true,
              colorbar: {
                title: 'Time',
              },
            },
          },
          {
            x: plotData.deltaS_range,
            y: plotData.q_nullcline,
            type: 'scatter',
            mode: 'lines',
            name: 'Nullcline',
            line: { color: '#8b949e', width: 2, dash: 'dash' },
          },
          {
            x: [plotData.deltaS[0]],
            y: [plotData.q_sv[0]],
            type: 'scatter',
            mode: 'markers',
            name: 'Initial',
            marker: { size: 12, color: '#ff6b6b', symbol: 'star' },
          },
          {
            x: [plotData.deltaS[plotData.deltaS.length - 1]],
            y: [plotData.q_sv[plotData.q_sv.length - 1]],
            type: 'scatter',
            mode: 'markers',
            name: 'Final',
            marker: { size: 10, color: '#51cf66', symbol: 'circle' },
          },
        ]}
        layout={{
          title: '',
          hovermode: 'closest',
          paper_bgcolor: '#0d1117',
          plot_bgcolor: '#0d1117',
          font: { color: '#c9d1d9', family: 'monospace', size: 11 },
          margin: { l: 60, r: 60, t: 20, b: 40 },
          height: 400,
          xaxis: {
            title: 'ΔS = S_e - S_p (psu)',
            gridcolor: '#30363d',
            zeroline: false,
          },
          yaxis: {
            title: 'q (Sv)',
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

export default PhaseSpacePlot
