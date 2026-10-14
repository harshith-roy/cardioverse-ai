import { useMemo } from 'react'

const FEATURE_NAMES = {
  age: 'Age',
  sex: 'Biological Sex',
  cp: 'Chest Pain Pattern',
  trestbps: 'Resting Blood Pressure',
  chol: 'Serum Cholesterol',
  fbs: 'Fasting Blood Sugar',
  restecg: 'Resting ECG State'
}

const FEATURE_METRICS = {
  age: 'Years',
  sex: '0: Female, 1: Male',
  cp: '1: Typical, 2: Atypical, 3: Non-anginal, 4: Asymptomatic',
  trestbps: 'mm Hg systolic',
  chol: 'mg/dl total',
  fbs: '> 120 mg/dl indicator',
  restecg: '0: Normal, 1: ST-T, 2: LVH'
}

export function ExplainabilityDashboard({ explanation, loading }) {
  const allContributions = useMemo(() => {
    if (!explanation) return []

    const positive = explanation.positive_contributors || {}
    const negative = explanation.negative_contributors || {}
    const list = []

    Object.entries(positive).forEach(([feature, val]) => {
      list.push({
        feature,
        val: Number(val),
        absVal: Math.abs(Number(val)),
        direction: 'positive'
      })
    })

    Object.entries(negative).forEach(([feature, val]) => {
      list.push({
        feature,
        val: Number(val),
        absVal: Math.abs(Number(val)),
        direction: 'negative'
      })
    })

    return list.sort((a, b) => b.absVal - a.absVal)
  }, [explanation])

  const maxContribution = useMemo(() => {
    if (!allContributions.length) return 1
    return Math.max(...allContributions.map((c) => c.absVal), 0.001)
  }, [allContributions])

  if (loading) {
    return (
      <div className="explainability-card loading-card">
        <div className="card-header-line">
          <h4>Explainability Telemetry</h4>
          <span className="badge-pulse">Decomposing Log-Odds</span>
        </div>
        <div className="loading-body">
          <div className="hud-spinner" />
          <p className="loading-label">Calculating feature weights & SHAP-style contributions...</p>
        </div>
      </div>
    )
  }

  if (!explanation) {
    return (
      <div className="explainability-card empty-card">
        <div className="card-header-line">
          <h4>Explainability & Feature Weights</h4>
          <span className="badge-idle">Standby</span>
        </div>
        <div className="empty-body">
          <p className="empty-title">Awaiting Prediction</p>
          <p className="empty-sub">Feature log-odds decomposition will illuminate individual biomarker impacts once analyzed.</p>
        </div>
      </div>
    )
  }

  const topFactors = explanation.top_factors || []

  return (
    <div className="explainability-card">
      <div className="card-header-line">
        <div>
          <h4>Feature Impact Breakdown</h4>
          <span className="model-sub">Log-Odds Linear Additive Contribution</span>
        </div>
        <div className="log-odds-pill">
          <span className="pill-tag">Σ Log-Odds</span>
          <span className="pill-val">{(explanation.log_odds || 0).toFixed(3)}</span>
        </div>
      </div>

      {/* Feature Contributions Bars */}
      <div className="contributions-stack">
        {allContributions.map((item, index) => {
          const pct = Math.min((item.absVal / maxContribution) * 100, 100)
          const isPositive = item.direction === 'positive'
          const name = FEATURE_NAMES[item.feature] || item.feature
          const desc = FEATURE_METRICS[item.feature] || ''

          return (
            <div key={item.feature} className={`feature-bar-row ${item.direction}`}>
              <div className="bar-label-line">
                <span className="feature-rank">#{index + 1}</span>
                <span className="feature-name">{name}</span>
                <span className="feature-desc">{desc}</span>
                <span className={`feature-val ${isPositive ? 'pos' : 'neg'}`}>
                  {isPositive ? '+' : ''}{item.val.toFixed(3)}
                </span>
              </div>

              <div className="bar-track">
                <div
                  className={`bar-fill ${isPositive ? 'pos-fill' : 'neg-fill'}`}
                  style={{ width: `${Math.max(pct, 4)}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>

      {/* Top 3 Key Factors */}
      {topFactors.length > 0 && (
        <div className="top-factors-box">
          <h5 className="factors-heading">Dominant Clinical Drivers</h5>
          <div className="factors-grid">
            {topFactors.map((factor, i) => {
              const name = FEATURE_NAMES[factor.feature] || factor.feature
              const contrib = Number(factor.contribution)
              const isPos = contrib > 0

              return (
                <div key={i} className={`factor-chip ${isPos ? 'risk-chip' : 'protective-chip'}`}>
                  <div className="chip-header">
                    <span className="chip-badge">#{i + 1}</span>
                    <span className="chip-name">{name}</span>
                  </div>
                  <span className="chip-weight">
                    {isPos ? '+' : ''}{contrib.toFixed(3)} log-odds
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Clinical Consultation Narrative */}
      {explanation.clinical_text && (
        <div className="clinical-narrative-box">
          <div className="narrative-header">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
            <span>Model Behavioral Interpretation</span>
          </div>
          <p className="narrative-text">{explanation.clinical_text}</p>
        </div>
      )}
    </div>
  )
}

export default ExplainabilityDashboard
