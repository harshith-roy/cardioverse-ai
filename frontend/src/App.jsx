import { useState, useEffect } from 'react'
import { HeartViewer } from './components/heart/HeartViewer'
import { PatientInputForm } from './components/forms/PatientInputForm'
import { PredictionDashboard } from './components/dashboard/PredictionDashboard'
import { ExplainabilityDashboard } from './components/dashboard/ExplainabilityDashboard'
import { GlassPanel } from './components/ui/GlassPanel'
import './App.css'

function App() {
  const [patientData, setPatientData] = useState({
    age: 63,
    sex: 1,
    cp: 1,
    trestbps: 145,
    chol: 233,
    fbs: 1,
    restecg: 0
  })
  const [prediction, setPrediction] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [backendOnline, setBackendOnline] = useState(false)

  const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')

  // API Call to predict and explain
  const handlePredict = async (data) => {
    setLoading(true)
    setError(null)

    try {
      // 1. Predict
      const predRes = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })

      if (!predRes.ok) {
        const errJson = await predRes.json().catch(() => ({}))
        throw new Error(errJson.detail || `Prediction error (${predRes.status})`)
      }

      const predData = await predRes.json()
      setPrediction(predData)
      setBackendOnline(true)

      // 2. Explain
      try {
        const expRes = await fetch(`${API_BASE_URL}/api/explain`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ patient_features: data })
        })

        if (expRes.ok) {
          const expData = await expRes.json()
          setExplanation(expData)
        }
      } catch (expErr) {
        console.warn('Explainability endpoint notice:', expErr)
      }
    } catch (err) {
      console.error('API Error:', err)
      setError(err.message || 'Unable to reach cardiovascular inference backend')
      setBackendOnline(false)
    } finally {
      setLoading(false)
    }
  }

  // Initial load: trigger baseline prediction on start
  useEffect(() => {
    // Check health & run initial prediction
    fetch(`${API_BASE_URL}/health`)
      .then((res) => res.json())
      .then((h) => {
        if (h.status === 'healthy') {
          setBackendOnline(true)
        }
      })
      .catch(() => setBackendOnline(false))

    handlePredict(patientData)
  }, [])

  const handleSubmit = (newData) => {
    setPatientData(newData)
    handlePredict(newData)
  }

  return (
    <div className="cardioverse-app">
      {/* Cinematic Top Navigation Header */}
      <header className="app-header">
        <div className="header-inner">
          <div className="header-branding">
            <div className="brand-logo-hex">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="pulse-svg">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
            </div>
            <div className="brand-titles">
              <div className="brand-primary">
                CARDIO<span className="brand-accent">VERSE</span> <span className="ai-tag">AI</span>
              </div>
              <div className="brand-sub">PRECISION CARDIAC RISK INTELLIGENCE</div>
            </div>
          </div>

          <div className="header-telemetry">
            <div className={`status-pill ${backendOnline ? 'online' : 'offline'}`}>
              <span className="status-orb" />
              <span className="status-label">
                Backend {backendOnline ? 'Active (FastAPI)' : 'Disconnected'}
              </span>
            </div>

            <div className="engine-badge">
              <span className="badge-code">R3F + Three.js PBR</span>
            </div>

            <div className="model-badge-header">
              <span className="badge-name">LR-Screening v1.0</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main 3-Column Glassmorphism Workspace */}
      <div className="dashboard-content-grid">
        {/* Left Column: Clinical Parameters */}
        <section className="col-left">
          <GlassPanel className="panel-patient-input">
            <div className="panel-title-bar">
              <div className="bar-icon-wrap">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="8.5" cy="7.5" r="4" />
                  <line x1="20" y1="8" x2="20" y2="14" />
                  <line x1="23" y1="11" x2="17" y2="11" />
                </svg>
              </div>
              <div>
                <h3 className="panel-heading">Patient Clinical Vector</h3>
                <span className="panel-caption">7-factor historical screening inputs</span>
              </div>
            </div>

            <PatientInputForm
              initialData={patientData}
              onSubmit={handleSubmit}
              disabled={loading}
            />
          </GlassPanel>
        </section>

        {/* Center Column: 3D Holographic Heart Visualization */}
        <section className="col-center">
          <GlassPanel className="panel-heart-vis">
            <div className="heart-header-bar">
              <span className="live-indicator">
                <span className="live-dot" />
                REAL-TIME 3D MYOCARDIUM
              </span>
              <span className="vis-notice">
                Illustrative 3D Geometry • Responsive Biometric Shader
              </span>
            </div>

            <HeartViewer
              patientData={patientData}
              prediction={prediction}
            />
          </GlassPanel>
        </section>

        {/* Right Column: Prediction & Explainability */}
        <section className="col-right">
          <GlassPanel className="panel-prediction">
            <PredictionDashboard
              prediction={prediction}
              loading={loading}
              error={error}
            />
          </GlassPanel>

          <GlassPanel className="panel-explainability">
            <ExplainabilityDashboard
              explanation={explanation}
              loading={loading}
            />
          </GlassPanel>
        </section>
      </div>

      {/* Global Clinical Disclaimer Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="disclaimer-bullet">RESEARCH & EDUCATIONAL EVALUATION ONLY</div>
          <p className="disclaimer-text">
            CardioVerse AI calculates statistical probability estimates from historical clinical observations (UCI 1980s Heart Disease cohort).
            This system does not diagnose coronary heart disease, localize arterial stenosis, or predict 10-year major adverse cardiac events.
            Never use for unassisted clinical diagnosis or patient triage. All medical decisions must be guided by licensed healthcare professionals.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App