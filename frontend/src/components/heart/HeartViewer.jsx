import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, ContactShadows, Environment } from '@react-three/drei'
import { useState, useRef, Suspense } from 'react'
import * as THREE from 'three'
import { HeartModel } from './HeartModel'
import { TechnicalRings } from './TechnicalRings'
import { ParticleAtmosphere } from './ParticleAtmosphere'
import { MedicalLabels } from './MedicalLabels'
import { ErrorBoundary } from '../ui/ErrorBoundary'

/**
 * Premium Cinematic 3D Cardiovascular AI Viewer
 * Features R3F Canvas, Drei OrbitControls, 3-point lighting, holographic telemetry rings,
 * particle atmosphere, interactive medical callouts, and real-time biometric HUD.
 */
export function HeartViewer({ patientData = {}, prediction = null }) {
  const [modelLoaded, setModelLoaded] = useState(false)
  const [isInteracting, setIsInteracting] = useState(false)
  const [showMarkers, setShowMarkers] = useState(true)
  const [wireframe, setWireframe] = useState(false)
  const [autoRotate, setAutoRotate] = useState(true)
  const controlsRef = useRef()

  const probability = prediction?.disease_probability ?? 0.15
  const isHighRisk = probability > 0.5
  const calculatedBpm = isHighRisk ? 92 : 72
  const statusColor = isHighRisk ? '#FB7185' : '#22D3EE'

  const handleResetCamera = () => {
    if (controlsRef.current) {
      controlsRef.current.reset()
    }
  }

  return (
    <div className="heart-viewer-wrapper">
      <ErrorBoundary prediction={prediction}>
        {/* Holographic Medical HUD Overlays (DOM elements outside Canvas) */}
        <div className="hud-overlay-frame">
          {/* Top Left: Status Telemetry Pill */}
          <div className="hud-telemetry-badge">
            <span
              className="hud-beacon"
              style={{
                backgroundColor: statusColor,
                boxShadow: `0 0 10px ${statusColor}`
              }}
            />
            <span className="hud-beacon-text">
              {isHighRisk ? 'ALERT: ELEVATED RISK STATE' : 'BIOMETRIC SCAN: NOMINAL'}
            </span>
          </div>

          {/* Top Right: Interactive Controls Bar */}
          <div className="hud-controls-bar">
            <button
              className={`hud-btn ${showMarkers ? 'active' : ''}`}
              onClick={() => setShowMarkers((prev) => !prev)}
              title="Toggle Anatomical Landmarks"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <span>{showMarkers ? 'Markers ON' : 'Markers OFF'}</span>
            </button>

            <button
              className={`hud-btn ${wireframe ? 'active' : ''}`}
              onClick={() => setWireframe((prev) => !prev)}
              title="Toggle Holographic Wireframe"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="12 2 2 7 12 12 22 7 12 2" />
                <polyline points="2 17 12 22 22 17" />
                <polyline points="2 12 12 17 22 12" />
              </svg>
              <span>{wireframe ? 'Wireframe' : 'Solid'}</span>
            </button>

            <button
              className={`hud-btn ${autoRotate ? 'active' : ''}`}
              onClick={() => setAutoRotate((prev) => !prev)}
              title="Toggle Orbital Rotation"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
              </svg>
              <span>{autoRotate ? 'Orbiting' : 'Paused'}</span>
            </button>

            <button
              className="hud-btn reset-btn"
              onClick={handleResetCamera}
              title="Reset Camera View"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              <span>Reset</span>
            </button>
          </div>

          {/* Bottom Left: Real-time Animated SVG ECG Waveform */}
          <div className="hud-ecg-monitor">
            <div className="ecg-header">
              <span className="ecg-title">LEAD II ECG</span>
              <span className="ecg-rate" style={{ color: statusColor }}>
                {calculatedBpm} <small>BPM</small>
              </span>
            </div>
            <div className="ecg-wave-container">
              <svg className={`ecg-wave-svg ${isHighRisk ? 'fast' : ''}`} viewBox="0 0 280 40" preserveAspectRatio="none">
                <path
                  d="M0 20 L40 20 L50 20 L55 12 L60 28 L65 4 L72 36 L78 20 L88 20 L100 20 L140 20 L150 20 L155 12 L160 28 L165 4 L172 36 L178 20 L188 20 L200 20 L240 20 L250 20 L255 12 L260 28 L265 4 L272 36 L278 20 L280 20"
                  fill="none"
                  stroke={statusColor}
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
          </div>

          {/* Bottom Right: Biometric Telemetry Gauges */}
          <div className="hud-biometrics-panel">
            <div className="telemetry-item">
              <span className="telemetry-label">EST. BLOOD PRESSURE</span>
              <span className="telemetry-value">
                {patientData.trestbps || 120} <small>mmHg</small>
              </span>
            </div>
            <div className="telemetry-item">
              <span className="telemetry-label">CARDIAC RHYTHM</span>
              <span className="telemetry-value" style={{ color: statusColor }}>
                {patientData.restecg === 0 ? 'Normal Sinus' : patientData.restecg === 1 ? 'ST-T Wave Anomaly' : 'LV Hypertrophy'}
              </span>
            </div>
            <div className="telemetry-item">
              <span className="telemetry-label">MYOCARDIAL STRAIN</span>
              <span className="telemetry-value">
                {(probability * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Bottom Center: Interaction Notice */}
          <div className="hud-interaction-hint">
            <span>DRAG TO ROTATE • SCROLL TO ZOOM • CLICK MARKERS FOR DETAILS</span>
          </div>

          {/* Loading Indicator while GLTF mounts */}
          {!modelLoaded && (
            <div className="hud-loading-state">
              <div className="hud-spinner" />
              <div className="hud-loading-label">INITIALIZING 3D ANATOMICAL HEART...</div>
              <div className="hud-scanline-bar">
                <div className="hud-scanline-fill" />
              </div>
            </div>
          )}
        </div>

        {/* React Three Fiber Canvas */}
        <Canvas
          gl={{
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance',
            stencil: false,
            depth: true
          }}
          dpr={[1, 2]}
          camera={{ position: [0, 0, 6.2], fov: 45 }}
          onCreated={({ gl }) => {
            gl.toneMapping = THREE.ACESFilmicToneMapping
            gl.toneMappingExposure = 1.15
            gl.outputColorSpace = THREE.SRGBColorSpace
          }}
        >
          <PerspectiveCamera makeDefault position={[0, 0, 6.2]} fov={45} near={0.1} far={100} />

          {/* Cinematic Studio Lighting */}
          <ambientLight intensity={0.7} color="#0B1730" />

          {/* Key Light (Crisp high-angle highlight) */}
          <directionalLight
            position={[5, 7, 5]}
            intensity={2.8}
            castShadow
            shadow-mapSize={[1024, 1024]}
            color="#FFFFFF"
          />

          {/* Cold Cyan Holographic Rim Light */}
          <directionalLight
            position={[-4, 2, -3]}
            intensity={2.2}
            color="#22D3EE"
          />

          {/* Warm Crimson Cardiac Accent Rim Light */}
          <directionalLight
            position={[2, -4, -3]}
            intensity={1.8}
            color="#FB7185"
          />

          {/* Front Soft Fill Light */}
          <directionalLight
            position={[0, 1, 4]}
            intensity={1.0}
            color="#E0F2FE"
          />

          {/* Subtle Studio Reflections */}
          <Environment preset="city" />

          {/* 3D Heart Scene with Suspense */}
          <Suspense fallback={null}>
            <group position={[0, 0, 0]}>
              <HeartModel
                path="/heart.glb"
                prediction={prediction}
                isInteracting={isInteracting}
                wireframe={wireframe}
                onLoad={setModelLoaded}
              />

              {/* Animated Holographic Rings */}
              <TechnicalRings riskProbability={probability} />

              {/* Bioluminescent Micro-Particles */}
              <ParticleAtmosphere count={350} riskProbability={probability} />

              {/* 3D Anatomical Callout Labels (rendered inside Canvas via Drei Html) */}
              <MedicalLabels visible={showMarkers} isHighRisk={isHighRisk} />
            </group>
          </Suspense>

          {/* Orbit Controls */}
          <OrbitControls
            ref={controlsRef}
            enableZoom={true}
            enablePan={false}
            enableDamping={true}
            dampingFactor={0.06}
            minDistance={3.2}
            maxDistance={11.0}
            maxPolarAngle={Math.PI / 1.95}
            minPolarAngle={0.3}
            autoRotate={autoRotate && !isInteracting}
            autoRotateSpeed={0.8}
            onStart={() => setIsInteracting(true)}
            onEnd={() => setIsInteracting(false)}
          />

          {/* Ground Soft Contact Shadow */}
          <ContactShadows
            position={[0, -2.1, 0]}
            opacity={0.4}
            scale={7.5}
            blur={2.8}
            far={8}
            resolution={512}
            color="#0284C7"
          />

          {/* Depth Fog */}
          <fog attach="fog" args={['#050B18', 4, 25]} />
        </Canvas>
      </ErrorBoundary>
    </div>
  )
}

export default HeartViewer