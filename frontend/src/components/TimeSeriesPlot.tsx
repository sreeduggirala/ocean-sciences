import React from 'react'
import PlotlyChart from './PlotlyChart'
import { useSimulation } from '../hooks/useSimulation'

const TimeSeriesPlot: React.FC = () => {
  const { result } = useSimulation()

  if (!result) {
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
        <p style={{ color: '#8b949e' }}>Run a simulation to see time series</p>
      </div>
    )
  }

  const time = result.time
  const q_sv = result.q_sv
  const S_e = result.S_e
  const S_p = result.S_p

  return (
    <div style={{ backgroundColor: '#161b22', borderRadius: '0.5rem', padding: '1rem' }}>
      <h3 style={{ marginBottom: '1rem', color: '#58a6ff' }}>Time Series Evolution</h3>

      <PlotlyChart
        data={[
          {
            x: time,
            y: q_sv,
            type: 'scatter',
            mode: 'lines',
            name: 'AMOC (Sv)',
            line: { color: '#58a6ff', width: 2 },
            yaxis: 'y1',
          },
          {
            x: time,
            y: Array(time.length).fill(0),
            type: 'scatter',
            mode: 'lines',
            name: 'Collapse (q=0)',
            line: { color: '#ff6b6b', width: 1, dash: 'dash' },
            yaxis: 'y1',
          },
          {
            x: time,
            y: Array(time.length).fill(15),
            type: 'scatter',
            mode: 'lines',
            name: 'Present-day',
            line: { color: '#8b949e', width: 1, dash: 'dash' },
            yaxis: 'y1',
          },
          {
            x: time,
            y: S_e,
            type: 'scatter',
            mode: 'lines',
            name: 'S_e (Equatorial)',
            line: { color: '#ffd500', width: 2 },
            yaxis: 'y2',
          },
          {
            x: time,
            y: S_p,
            type: 'scatter',
            mode: 'lines',
            name: 'S_p (Polar)',
            line: { color: '#79c0ff', width: 2 },
            yaxis: 'y3',
          },
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
            title: 'Time (years)',
            gridcolor: '#30363d',
            zeroline: false,
          },
          yaxis: {
            title: 'AMOC (Sv)',
            gridcolor: '#30363d',
            zeroline: false,
          },
          yaxis2: {
            title: 'S_e, S_p (psu)',
            overlaying: 'y',
            side: 'right',
            gridcolor: '#30363d',
            zeroline: false,
          },
          yaxis3: {
            title: '',
            overlaying: 'y',
            side: 'right',
            visible: false,
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

      <button
        onClick={() => {
          const png = document.querySelector('svg') as SVGElement
          if (png) {
            const url = png.outerHTML
            console.log('Export feature requires plotly download image')
          }
        }}
        style={{
          marginTop: '1rem',
          padding: '0.5rem 1rem',
          backgroundColor: '#238636',
          color: '#fff',
          border: 'none',
          borderRadius: '0.3rem',
          cursor: 'pointer',
          fontSize: '0.85rem',
        }}
      >
        Export PNG
      </button>
    </div>
  )
}

export default TimeSeriesPlot
