import React, { useEffect, useRef, useMemo } from 'react'
import { useSimulation } from '../hooks/useSimulation'

const OceanBoxDiagram: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null)
  const animationRef = useRef<number | null>(null)
  const { result, params } = useSimulation()

  const boxData = useMemo(() => {
    if (!result || result.S_e.length === 0) {
      return null
    }

    const idx = result.S_e.length - 1
    const S_e = result.S_e[idx]
    const S_p = result.S_p[idx]
    const q_sv = result.q_sv[idx]

    // Determine regime
    let regime = 'Neutral'
    if (q_sv > 10) regime = 'Thermally Driven'
    else if (q_sv < -5) regime = 'Reversed'
    else if (Math.abs(q_sv) < 5) regime = 'Collapsed'

    // Box colors: blue (cold/fresh) to red (warm/salty)
    const colorE = `rgb(${Math.min(255, Math.max(0, Math.round(50 + (S_e - 34) * 15)))}, ${Math.min(255, Math.max(0, Math.round(150 - (S_e - 34) * 30)))}, 255)`
    const colorP = `rgb(${Math.min(255, Math.max(0, Math.round(50 + (S_p - 34) * 15)))}, ${Math.min(255, Math.max(0, Math.round(150 - (S_p - 34) * 30)))}, 255)`

    return {
      S_e,
      S_p,
      q_sv,
      regime,
      colorE,
      colorP,
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

  const arrowDirection = boxData.q_sv >= 0 ? 1 : -1

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
        {/* Equatorial Box */}
        <rect x="50" y="50" width="120" height="100" fill={boxData.colorE} stroke="#58a6ff" strokeWidth="2" />
        <text x="110" y="85" textAnchor="middle" fill="#fff" fontSize="12" fontWeight="bold">
          Equatorial
        </text>
        <text x="110" y="105" textAnchor="middle" fill="#fff" fontSize="10">
          T_e = {params.T_e.toFixed(1)}°C
        </text>
        <text x="110" y="125" textAnchor="middle" fill="#fff" fontSize="10">
          S = {boxData.S_e.toFixed(2)} psu
        </text>

        {/* Polar Box */}
        <rect x="330" y="50" width="120" height="100" fill={boxData.colorP} stroke="#58a6ff" strokeWidth="2" />
        <text x="390" y="85" textAnchor="middle" fill="#fff" fontSize="12" fontWeight="bold">
          Polar
        </text>
        <text x="390" y="105" textAnchor="middle" fill="#fff" fontSize="10">
          T_p = {params.T_p.toFixed(1)}°C
        </text>
        <text x="390" y="125" textAnchor="middle" fill="#fff" fontSize="10">
          S = {boxData.S_p.toFixed(2)} psu
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
          stroke={boxData.q_sv >= 0 ? '#ff6b6b' : '#4dabf7'}
          strokeWidth={Math.min(8, Math.max(2, Math.abs(boxData.q_sv) / 5))}
          fill="none"
          strokeDasharray="10,5"
          markerEnd="url(#arrowhead)"
        />

        {/* Return flow */}
        <path
          className="flow-arrow"
          d={`M 330 150 L 190 150`}
          stroke={boxData.q_sv >= 0 ? '#4dabf7' : '#ff6b6b'}
          strokeWidth={Math.min(8, Math.max(2, Math.abs(boxData.q_sv) / 5))}
          fill="none"
          strokeDasharray="10,5"
          markerEnd="url(#arrowhead)"
        />

        {/* Circulation strength label */}
        <text x="260" y="85" textAnchor="middle" fill="#c9d1d9" fontSize="12" fontWeight="bold">
          q = {boxData.q_sv.toFixed(2)} Sv
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
