import { useState, useEffect } from 'react'

const FEATURE_CONFIG = {
  age: {
    label: 'Age',
    type: 'number',
    min: 29,
    max: 77,
    unit: 'yrs',
    step: 1,
    desc: 'Patient age in completed years'
  },
  sex: {
    label: 'Biological Sex',
    type: 'select',
    options: [
      { value: 0, label: '0: Female' },
      { value: 1, label: '1: Male' }
    ],
    desc: 'Reported biological sex'
  },
  cp: {
    label: 'Chest Pain Pattern',
    type: 'select',
    options: [
      { value: 1, label: '1: Typical Angina' },
      { value: 2, label: '2: Atypical Angina' },
      { value: 3, label: '3: Non-Anginal Pain' },
      { value: 4, label: '4: Asymptomatic' }
    ],
    desc: 'Symptom classification'
  },
  trestbps: {
    label: 'Resting Blood Pressure',
    type: 'number',
    min: 94,
    max: 200,
    unit: 'mm Hg',
    step: 1,
    desc: 'Resting systolic arterial pressure'
  },
  chol: {
    label: 'Serum Cholesterol',
    type: 'number',
    min: 126,
    max: 564,
    unit: 'mg/dl',
    step: 1,
    desc: 'Total circulating fasting cholesterol'
  },
  fbs: {
    label: 'Fasting Blood Sugar',
    type: 'select',
    options: [
      { value: 0, label: '0: ≤ 120 mg/dl (Normal)' },
      { value: 1, label: '1: > 120 mg/dl (Elevated)' }
    ],
    desc: 'Blood glucose threshold'
  },
  restecg: {
    label: 'Resting Electrocardiogram',
    type: 'select',
    options: [
      { value: 0, label: '0: Normal Sinus' },
      { value: 1, label: '1: ST-T Wave Abnormality' },
      { value: 2, label: "2: Left Ventricular Hypertrophy" }
    ],
    desc: 'Resting baseline 12-lead ECG'
  }
}

const PRESETS = [
  {
    name: 'High Risk Preset',
    badge: 'High Alert',
    data: {
      age: 67,
      sex: 1,
      cp: 4,
      trestbps: 165,
      chol: 289,
      fbs: 1,
      restecg: 2
    }
  },
  {
    name: 'Baseline Low Risk',
    badge: 'Nominal',
    data: {
      age: 44,
      sex: 0,
      cp: 1,
      trestbps: 115,
      chol: 175,
      fbs: 0,
      restecg: 0
    }
  },
  {
    name: 'UCI Case Sample',
    badge: 'Default',
    data: {
      age: 63,
      sex: 1,
      cp: 1,
      trestbps: 145,
      chol: 233,
      fbs: 1,
      restecg: 0
    }
  }
]

export function PatientInputForm({ onSubmit, initialData = {}, disabled = false }) {
  const [formData, setFormData] = useState({
    age: 63,
    sex: 1,
    cp: 1,
    trestbps: 145,
    chol: 233,
    fbs: 1,
    restecg: 0,
    ...initialData
  })

  useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0) {
      setFormData((prev) => ({ ...prev, ...initialData }))
    }
  }, [initialData])

  const handleChange = (name, rawVal, type) => {
    let val
    if (type === 'number') {
      const num = parseFloat(rawVal)
      val = isNaN(num) ? 0 : num
    } else {
      val = parseInt(rawVal, 10)
    }
    setFormData((prev) => ({ ...prev, [name]: val }))
  }

  const handleApplyPreset = (presetData) => {
    setFormData(presetData)
    onSubmit(presetData)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    // Clamp numerical ranges before submitting
    const clamped = { ...formData }
    Object.entries(FEATURE_CONFIG).forEach(([k, cfg]) => {
      if (cfg.type === 'number') {
        clamped[k] = Math.min(Math.max(clamped[k], cfg.min), cfg.max)
      }
    })
    onSubmit(clamped)
  }

  return (
    <div className="patient-form-wrapper">
      {/* Quick Clinical Presets Bar */}
      <div className="presets-bar">
        <span className="presets-label">QUICK PRESETS:</span>
        <div className="preset-chips">
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-chip"
              disabled={disabled}
              onClick={() => handleApplyPreset(p.data)}
            >
              <span>{p.name}</span>
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="patient-form">
        <div className="fields-grid">
          {Object.entries(FEATURE_CONFIG).map(([key, config]) => {
            const isNumber = config.type === 'number'
            const currentVal = formData[key]

            return (
              <div key={key} className="form-field-group">
                <div className="field-label-line">
                  <label htmlFor={`field-${key}`} className="field-label">
                    {config.label}
                  </label>
                  {config.unit && <span className="unit-badge">{config.unit}</span>}
                </div>

                {isNumber ? (
                  <div className="input-with-controls">
                    <input
                      id={`field-${key}`}
                      type="number"
                      min={config.min}
                      max={config.max}
                      step={config.step}
                      value={currentVal}
                      disabled={disabled}
                      onChange={(e) => handleChange(key, e.target.value, 'number')}
                      className="form-num-input"
                      required
                    />
                    <div className="slider-container">
                      <input
                        type="range"
                        min={config.min}
                        max={config.max}
                        step={config.step}
                        value={currentVal}
                        disabled={disabled}
                        onChange={(e) => handleChange(key, e.target.value, 'number')}
                        className="form-range-slider"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="select-container">
                    <select
                      id={`field-${key}`}
                      value={currentVal}
                      disabled={disabled}
                      onChange={(e) => handleChange(key, e.target.value, 'select')}
                      className="form-select-input"
                    >
                      {config.options.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
                <span className="field-hint">Range: {config.min ? `${config.min}–${config.max}` : config.desc}</span>
              </div>
            )
          })}
        </div>

        <button
          type="submit"
          disabled={disabled}
          className={`submit-prediction-btn ${disabled ? 'loading' : ''}`}
        >
          {disabled ? (
            <>
              <span className="button-spinner" />
              <span>Analyzing Clinical Profile...</span>
            </>
          ) : (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
              <span>Run AI Risk Assessment</span>
            </>
          )}
        </button>
      </form>
    </div>
  )
}

export default PatientInputForm