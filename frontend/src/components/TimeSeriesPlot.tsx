import React, { useRef } from 'react'
import Plotly from 'plotly.js-dist-min'
import PlotlyChart from './PlotlyChart'
import { useSimulation } from '../hooks/useSimulation'

const TimeSeriesPlot: React.FC = () => {
  const { result } = useSimulation()
  const containerRef = useRef<HTMLDivElement>(null)

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
  const S_1 = result.S_1
  const S_2 = result.S_2

  return (
    <div ref={containerRef} style={{ backgroundColor: '#161b22', borderRadius: '0.5rem', padding: '1rem' }}>
      <h3 style={{ marginBottom: '1rem', color: '#58a6ff' }}>Time Series Evolution</h3>

      <PlotlyChart
        data={[
          {
            x: time,
            y: q_sv,
            type: 'scatter',
            mode: 'lines',
            name: 'Circulation (1/s)',
            line: { color: '#58a6ff', width: 2 },
            yaxis: 'y1',
          },
          {
            x: time,
            y: Array(time.length).fill(0),
            type: 'scatter',
            mode: 'lines',
            name: 'q=0',
            line: { color: '#ff6b6b', width: 1, dash: 'dash' },
            yaxis: 'y1',
          },
          {
            x: time,
            y: Array(time.length).fill(1e-6),
            type: 'scatter',
            mode: 'lines',
            name: 'Typical modern (~1e-6)',
            line: { color: '#8b949e', width: 1, dash: 'dash' },
            yaxis: 'y1',
          },
          {
            x: time,
            y: S_1,
            type: 'scatter',
            mode: 'lines',
            name: 'S_1 (Box 1)',
            line: { color: '#ffd500', width: 2 },
            yaxis: 'y2',
          },
          {
            x: time,
            y: S_2,
            type: 'scatter',
            mode: 'lines',
            name: 'S_2 (Box 2)',
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
            title: 'Circulation (1/s)',
            gridcolor: '#30363d',
            zeroline: false,
          },
          yaxis2: {
            title: 'S_1, S_2 (psu)',
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
          const plotDiv = containerRef.current?.querySelector('.js-plotly-plot') as HTMLElement | null
          if (plotDiv) {
            Plotly.downloadImage(plotDiv, {
              format: 'png',
              width: 1200,
              height: 600,
              filename: `stommel-timeseries-${Date.now()}`,
            })
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
