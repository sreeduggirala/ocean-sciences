import React, { useEffect, useRef, useMemo } from 'react'
import { useSimulation } from '../hooks/useSimulation'

const OceanBoxDiagram: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null)
  const animationRef = useRef<number | null>(null)
  const { result, params } = useSimulation()

  const boxData = useMemo(() => {
    if (!result || result.S_1.length === 0) {
      return null
    }

    const idx = result.S_1.length - 1
    const S_1 = result.S_1[idx]
    const S_2 = result.S_2[idx]
    const q = result.q[idx]  // q in 1/s
    const q_sv = result.q_sv[idx]  // q in Sv

    // Determine regime based on circulation mode
    let regime = 'Neutral'
    if (q > 5e-7) regime = 'Thermally Driven'
    else if (q < -2e-7) regime = 'Reversed/Haline'
    else if (Math.abs(q) < 2e-7) regime = 'Collapsed'

    // Box colors: blue (cold/fresh) to red (warm/salty)
    const color1 = `rgb(${Math.min(255, Math.max(0, Math.round(50 + (S_1 - 34) * 15)))}, ${Math.min(255, Math.max(0, Math.round(150 - (S_1 - 34) * 30)))}, 255)`
    const color2 = `rgb(${Math.min(255, Math.max(0, Math.round(50 + (S_2 - 34) * 15)))}, ${Math.min(255, Math.max(0, Math.round(150 - (S_2 - 34) * 30)))}, 255)`

    return {
      S_1,
      S_2,
      q,
      q_sv,
      regime,
      color1,
      color2,
    }
  }, [result])

  useEffect(() => {
    if (!svgRef.current || !boxData) return

    let offset = 0
    const animate = () => {
      offset += 2
      if (offset > 20) offset = 0

      const svg = svgRef.current
      if (!svg) return

      // Update stroke-dashoffset for arrow animation
      const arrows = svg.querySelectorAll('.flow-arrow')
      arrows.forEach((arrow) => {
        const strokeWidth = Math.abs(boxData.q_sv) / 5
        ;(arrow as SVGElement).setAttribute(
          'stroke-dashoffset',
          boxData.q_sv < 0 ? String(offset) : String(-offset)
        )
        ;(arrow as SVGElement).setAttribute('stroke-width', String(Math.min(8, Math.max(2, strokeWidth))))
      })

      animationRef.current = requestAnimationFrame(animate)
    }

    animationRef.current = requestAnimationFrame(animate)

    return () => {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [boxData])

  if (!boxData) {
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
        <p style={{ color: '#8b949e' }}>Run a simulation to see the ocean boxes</p>
      </div>
    )
  }

  return (
    <div
      style={{
        padding: '2rem',
        backgroundColor: '#161b22',
        borderRadius: '0.5rem',
      }}
    >
      <h3 style={{ marginBottom: '1rem', color: '#58a6ff' }}>Two-Box Thermohaline System</h3>

      <svg
        ref={svgRef}
        viewBox="0 0 500 300"
        width="100%"
        height="300"
        style={{ maxWidth: '100%' }}
      >
        {/* Box 1 (Equatorial) */}
        <rect x="50" y="50" width="120" height="100" fill={boxData.color1} stroke="#58a6ff" strokeWidth="2" />
        <text x="110" y="85" textAnchor="middle" fill="#fff" fontSize="12" fontWeight="bold">
          Box 1
        </text>
        <text x="110" y="105" textAnchor="middle" fill="#fff" fontSize="10">
          T₁ = {params.T_1.toFixed(1)}°C
        </text>
        <text x="110" y="125" textAnchor="middle" fill="#fff" fontSize="10">
          S = {boxData.S_1.toFixed(2)} psu
        </text>

        {/* Box 2 (Polar) */}
        <rect x="330" y="50" width="120" height="100" fill={boxData.color2} stroke="#58a6ff" strokeWidth="2" />
        <text x="390" y="85" textAnchor="middle" fill="#fff" fontSize="12" fontWeight="bold">
          Box 2
        </text>
        <text x="390" y="105" textAnchor="middle" fill="#fff" fontSize="10">
          T₂ = {params.T_2.toFixed(1)}°C
        </text>
        <text x="390" y="125" textAnchor="middle" fill="#fff" fontSize="10">
          S = {boxData.S_2.toFixed(2)} psu
        </text>

        {/* Flow Arrow */}
        <defs>
          <marker
            id="arrowhead"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
          >
            <polygon points="0 0, 10 3, 0 6" fill="#58a6ff" />
          </marker>
        </defs>

        <path
          className="flow-arrow"
          d={`M 190 100 L 330 100`}
          stroke={boxData.q >= 0 ? '#ff6b6b' : '#4dabf7'}
          strokeWidth={Math.min(8, Math.max(2, Math.abs(boxData.q) / 1e-7))}
          fill="none"
          strokeDasharray="10,5"
          markerEnd="url(#arrowhead)"
        />

        {/* Return flow */}
        <path
          className="flow-arrow"
          d={`M 330 150 L 190 150`}
          stroke={boxData.q >= 0 ? '#4dabf7' : '#ff6b6b'}
          strokeWidth={Math.min(8, Math.max(2, Math.abs(boxData.q) / 1e-7))}
          fill="none"
          strokeDasharray="10,5"
          markerEnd="url(#arrowhead)"
        />

        {/* Circulation strength label */}
        <text x="260" y="85" textAnchor="middle" fill="#c9d1d9" fontSize="12" fontWeight="bold">
          q = {boxData.q.toExponential(2)} (1/s)
        </text>

        {/* Regime label */}
        <text x="260" y="250" textAnchor="middle" fill="#58a6ff" fontSize="14" fontWeight="bold">
          {boxData.regime}
        </text>
      </svg>
    </div>
  )
}

export default OceanBoxDiagram
