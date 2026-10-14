import { useEffect, useState } from 'react'

export function PredictionDashboard({ prediction, loading, error }) {
  const [animatedProbability, setAnimatedProbability] = useState(0)

  useEffect(() => {
    if (prediction) {
      const target = (prediction.disease_probability || 0) * 100
      let start = 0
      const duration = 800
      const startTime = performance.now()

      const step = (now) => {
        const elapsed = now - startTime
        const progress = Math.min(elapsed / duration, 1)
        // Ease out quad
        const current = target * (1 - Math.pow(1 - progress, 2))
        setAnimatedProbability(current)
        if (progress < 1) {
          requestAnimationFrame(step)
        }
      }

      requestAnimationFrame(step)
    } else {
      setAnimatedProbability(0)
    }
  }, [prediction])

  if (loading) {
    return (
      <div className="prediction-card loading-card">
        <div className="card-header-line">
          <h4>AI Model Screening</h4>
          <span className="badge-pulse">Inference In Progress</span>
        </div>
        <div className="loading-body">
          <div className="hud-spinner" />
          <p className="loading-label">Evaluating clinical vectors...</p>
          <span className="loading-sub">Calculating log-odds & sigmoid probability</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="prediction-card error-card">
        <div className="card-header-line">
          <h4>Inference Error</h4>
          <span className="badge-error">Offline</span>
        </div>
        <div className="error-body">
          <p className="error-text">{error}</p>
          <p className="error-hint">Verify backend connection or ensure inputs meet valid clinical ranges.</p>
        </div>
      </div>
    )
  }

  if (!prediction) {
    return (
      <div className="prediction-card empty-card">
        <div className="card-header-line">
          <h4>AI Risk Estimation</h4>
          <span className="badge-idle">Standby</span>
        </div>
        <div className="empty-body">
          <div className="empty-icon-pulse">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <p className="empty-title">Ready for Clinical Evaluation</p>
          <p className="empty-sub">Adjust patient parameters on the left and submit to compute real-time probability.</p>
        </div>
      </div>
    )
  }

  const probability = prediction.disease_probability || 0
  const isHighRisk = probability >= 0.75
  const isElevatedRisk = probability >= 0.5 && probability < 0.75
  const isLowerRisk = probability < 0.5

  const riskTierClass = isHighRisk ? 'risk-high' : isElevatedRisk ? 'risk-elevated' : 'risk-low'
  const riskColor = isHighRisk ? '#FB7185' : isElevatedRisk ? '#FBBF24' : '#22D3EE'
  const riskTitle = isHighRisk ? 'High Risk Tier' : isElevatedRisk ? 'Elevated Risk Tier' : 'Lower Risk Tier'

  // SVG circular gauge geometry
  const radius = 58
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (animatedProbability / 100) * circumference

  return (
    <div className={`prediction-card result-card ${riskTierClass}`}>
      <div className="card-header-line">
        <div>
          <h4>AI Screening Score</h4>
          <span className="model-sub">Logistic Regression • 7 Clinical Dimensions</span>
        </div>
        <span className={`risk-pill ${riskTierClass}`}>
          <span className="pill-dot" />
          {riskTitle}
        </span>
      </div>

      <div className="gauge-section">
        <div className="circular-gauge-wrapper">
          <svg className="circular-gauge-svg" viewBox="0 0 140 140">
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#22D3EE" />
                <stop offset="60%" stopColor={isHighRisk ? '#FB7185' : isElevatedRisk ? '#FBBF24' : '#2DD4BF'} />
                <stop offset="100%" stopColor={isHighRisk ? '#E11D48' : '#38BDF8'} />
              </linearGradient>
            </defs>

            {/* Background Track */}
            <circle
              className="gauge-track"
              cx="70"
              cy="70"
              r={radius}
              strokeWidth="9"
            />

            {/* Value Track */}
            <circle
              className="gauge-progress"
              cx="70"
              cy="70"
              r={radius}
              strokeWidth="9"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              stroke="url(#gaugeGradient)"
              strokeLinecap="round"
              transform="rotate(-90 70 70)"
            />
          </svg>

          {/* Centered Percentage Display */}
          <div className="gauge-center-content">
            <span className="gauge-number" style={{ color: riskColor }}>
              {animatedProbability.toFixed(1)}%
            </span>
            <span className="gauge-label">EST. PROBABILITY</span>
          </div>
        </div>

        {/* Prediction Summary Details */}
        <div className="prediction-quick-stats">
          <div className="stat-row">
            <span className="stat-name">Classification</span>
            <span className="stat-val highlight" style={{ color: riskColor }}>
              {prediction.predicted_class === 1 ? 'Positive Signal (1)' : 'Negative Signal (0)'}
            </span>
          </div>
          <div className="stat-row">
            <span className="stat-name">Decision Boundary</span>
            <span className="stat-val">P ≥ 0.50</span>
          </div>
          <div className="stat-row">
            <span className="stat-name">Clinical Action</span>
            <span className="stat-val">
              {prediction.predicted_class === 1 ? 'Diagnostic Follow-up' : 'Routine Monitoring'}
            </span>
          </div>
        </div>
      </div>

      <div className="prediction-disclaimer-box">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <p>
          Statistical estimate derived from UCI 1980s cardiovascular screening dataset. For educational & research evaluation only. Not a medical diagnosis.
        </p>
      </div>
    </div>
  )
}

export default PredictionDashboard