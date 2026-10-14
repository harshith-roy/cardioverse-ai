import { useState } from 'react'
import { Html } from '@react-three/drei'

/**
 * Interactive 3D Holographic Medical Labels
 * Rendered strictly inside the R3F Canvas context via Drei's <Html>.
 */
const ANATOMY_MARKERS = [
  {
    id: 'aorta',
    name: 'Ascending Aorta',
    sub: 'Systemic Outflow (High Pressure)',
    position: [0.25, 1.25, 0.2],
    tag: 'AO'
  },
  {
    id: 'pulmonary_artery',
    name: 'Pulmonary Trunk',
    sub: 'Deoxygenated Outflow to Lungs',
    position: [-0.4, 0.95, 0.45],
    tag: 'PA'
  },
  {
    id: 'left_ventricle',
    name: 'Left Ventricle',
    sub: 'Systemic Muscular Myocardium',
    position: [0.85, -0.2, 0.35],
    tag: 'LV'
  },
  {
    id: 'right_ventricle',
    name: 'Right Ventricle',
    sub: 'Anterior Pulmonary Pump',
    position: [-0.8, -0.35, 0.3],
    tag: 'RV'
  },
  {
    id: 'apex',
    name: 'Cardiac Apex',
    sub: 'Inferior Myocardial Tip',
    position: [0.05, -1.35, 0.25],
    tag: 'APX'
  }
]

export function MedicalLabels({ visible = true, isHighRisk = false }) {
  const [activeMarker, setActiveMarker] = useState(null)

  if (!visible) return null

  return (
    <group>
      {ANATOMY_MARKERS.map((marker) => {
        const isSelected = activeMarker === marker.id
        const accent = isHighRisk ? '#FB7185' : '#22D3EE'

        return (
          <group key={marker.id} position={marker.position}>
            {/* 3D Anchor Dot */}
            <mesh>
              <sphereGeometry args={[0.045, 16, 16]} />
              <meshBasicMaterial color={accent} />
            </mesh>

            {/* Glowing Anchor Halo */}
            <mesh>
              <ringGeometry args={[0.06, 0.09, 24]} />
              <meshBasicMaterial
                color={accent}
                transparent
                opacity={0.5}
                side={2}
              />
            </mesh>

            {/* Drei HTML Overlay Pin */}
            <Html
              center
              distanceFactor={7}
              zIndexRange={[100, 0]}
              style={{
                pointerEvents: 'auto',
                cursor: 'pointer',
                transform: 'translate3d(0, -10px, 0)'
              }}
            >
              <div
                className={`hud-anatomy-tag ${isSelected ? 'active' : ''}`}
                onClick={(e) => {
                  e.stopPropagation()
                  setActiveMarker(isSelected ? null : marker.id)
                }}
                onMouseEnter={() => setActiveMarker(marker.id)}
                onMouseLeave={() => setActiveMarker(null)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: isSelected
                    ? 'rgba(5, 11, 24, 0.92)'
                    : 'rgba(5, 11, 24, 0.75)',
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${isSelected ? accent : 'rgba(34, 211, 238, 0.3)'}`,
                  borderRadius: '20px',
                  padding: '3px 8px',
                  boxShadow: isSelected
                    ? `0 0 15px ${isHighRisk ? 'rgba(251, 113, 133, 0.5)' : 'rgba(34, 211, 238, 0.5)'}`
                    : '0 2px 8px rgba(0,0,0,0.4)',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  userSelect: 'none',
                  whiteSpace: 'nowrap'
                }}
              >
                <span
                  style={{
                    display: 'inline-block',
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: accent,
                    boxShadow: `0 0 6px ${accent}`
                  }}
                />
                <span
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '11px',
                    fontWeight: 600,
                    letterSpacing: '0.04em',
                    color: '#F1F5F9'
                  }}
                >
                  {marker.name}
                </span>

                {isSelected && (
                  <span
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: '9px',
                      color: isHighRisk ? '#FDA4AF' : '#67E8F9',
                      marginLeft: '4px',
                      paddingLeft: '6px',
                      borderLeft: '1px solid rgba(255,255,255,0.2)'
                    }}
                  >
                    {marker.sub}
                  </span>
                )}
              </div>
            </Html>
          </group>
        )
      })}
    </group>
  )
}

export default MedicalLabels