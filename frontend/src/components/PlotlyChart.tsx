import React, { useEffect, useRef } from 'react'
import Plotly from 'plotly.js-dist-min'

interface PlotlyChartProps {
  data: any[]
  layout: any
  config?: any
}

const PlotlyChart: React.FC<PlotlyChartProps> = ({ data, layout, config = {} }) => {
  const divRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!divRef.current) return

    Plotly.newPlot(divRef.current, data, layout, {
      responsive: true,
      displayModeBar: true,
      ...config,
    })

    return () => {
      if (divRef.current) {
        Plotly.purge(divRef.current)
      }
    }
  }, [data, layout, config])

  return <div ref={divRef} style={{ width: '100%', height: '100%' }} />
}

export default PlotlyChart
