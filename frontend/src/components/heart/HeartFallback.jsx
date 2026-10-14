import { useState, useEffect } from 'react'

/**
 * Graceful Holographic Medical HUD Fallback
 * Renders an animated clinical HUD if WebGL context is lost, 3D GLTF fails, or performance mode is active.
 */
export function HeartFallback({ prediction = null, error = null, onRetry = null }) {
  const [pulsePhase, setPulsePhase] = useState(0)

  const probability = prediction?.disease_probability || 0.15
  const isHighRisk = probability > 0.5
  const bpm = isHighRisk ? 96 : 72
  const statusColor = isHighRisk ? '#FB7185' : '#22D3EE'

  useEffect(() => {
    const interval = setInterval(() => {
      setPulsePhase((prev) => (prev + 1) % 100)
    }, 50)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="heart-fallback-container">
      {/* Background Holographic Grid */}
      <div className="hud-grid-overlay" />

      {/* Holographic Concentric Ticks */}
      <div className="fallback-gimbal">
        <div className={`radar-sweep ${isHighRisk ? 'alert' : ''}`} />
        <div className="radar-circle circle-1" />
        <div className="radar-circle circle-2" />
        <div className="radar-circle circle-3" />
      </div>

      {/* Pulsing Anatomical Schematic Heart Icon */}
      <div className={`schematic-heart-wrapper ${isHighRisk ? 'alert-pulse' : 'normal-pulse'}`}>
        <svg viewBox="0 0 200 200" className="schematic-heart-svg">
          <defs>
            <linearGradient id="fallbackHeartGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={statusColor} stopOpacity="0.9" />
              <stop offset="100%" stopColor={isHighRisk ? '#E11D48' : '#0284C7'} stopOpacity="0.4" />
            </linearGradient>
            <filter id="fallbackGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Holographic Wireframe Heart Contour */}
          <path
            d="M100 170 C40 120, 20 80, 50 45 C75 15, 100 40, 100 55 C100 40, 125 15, 150 45 C180 80, 160 120, 100 170 Z"
            fill="url(#fallbackHeartGrad)"
            stroke={statusColor}
            strokeWidth="2.5"
            strokeDasharray="4 2"
            filter="url(#fallbackGlow)"
          />

          {/* Internal Chamber Dividers */}
          <path
            d="M100 55 Q98 110 100 170"
            stroke={statusColor}
            strokeWidth="1.5"
            strokeDasharray="3 3"
            opacity="0.7"
          />
          <path
            d="M50 100 Q100 115 150 100"
            stroke={statusColor}
            strokeWidth="1.5"
            strokeDasharray="3 3"
            opacity="0.5"
          />

          {/* Central Vital Core Node */}
          <circle cx="100" cy="105" r="7" fill={statusColor} filter="url(#fallbackGlow)" />
        </svg>
      </div>

      {/* Holographic HUD Metrics Bar */}
      <div className="fallback-hud-data">
        <div className="hud-metric-pill">
          <span className="metric-label">TELEMETRY</span>
          <span className="metric-value" style={{ color: statusColor }}>
            {isHighRisk ? 'ELEVATED STRAIN' : 'HOMEOSTASIS'}
          </span>
        </div>
        <div className="hud-metric-pill">
          <span className="metric-label">CALCULATED BPM</span>
          <span className="metric-value">{bpm} BPM</span>
        </div>
        <div className="hud-metric-pill">
          <span className="metric-label">CARDIO RHYTHM</span>
          <span className="metric-value">{isHighRisk ? 'SINUS TACHYCARDIA' : 'NORMAL SINUS'}</span>
        </div>
      </div>

      {/* Notice & Optional Retry Action */}
      <div className="fallback-footer">
        <span className="fallback-notice">
          {error ? `3D Fallback Mode (${error.message || 'WebGL context'})` : 'Holographic Fallback HUD Active'}
        </span>
        {onRetry && (
          <button className="retry-3d-btn" onClick={onRetry}>
            Reload 3D Engine
          </button>
        )}
      </div>
    </div>
  )
}

export default HeartFallback
