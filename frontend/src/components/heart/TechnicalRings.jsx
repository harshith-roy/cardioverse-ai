import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

/**
 * Animated orbital technical rings for holographic medical visualization.
 * Rotates on multiple axes to create a cinematic sci-fi telemetry gimbal.
 */
export function TechnicalRings({ riskProbability = 0.1 }) {
  const ring1Ref = useRef()
  const ring2Ref = useRef()
  const ring3Ref = useRef()

  const isHighRisk = riskProbability > 0.5
  const primaryColor = isHighRisk ? '#FB7185' : '#22D3EE'
  const secondaryColor = isHighRisk ? '#FDA4AF' : '#2DD4BF'
  const speedMultiplier = isHighRisk ? 1.6 : 1.0

  useFrame((state, delta) => {
    if (ring1Ref.current) {
      ring1Ref.current.rotation.z += 0.25 * delta * speedMultiplier
      ring1Ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.4) * 0.15
    }
    if (ring2Ref.current) {
      ring2Ref.current.rotation.z -= 0.35 * delta * speedMultiplier
      ring2Ref.current.rotation.y = Math.cos(state.clock.elapsedTime * 0.3) * 0.2
    }
    if (ring3Ref.current) {
      ring3Ref.current.rotation.x += 0.15 * delta * speedMultiplier
      ring3Ref.current.rotation.y += 0.2 * delta * speedMultiplier
    }
  })

  return (
    <group position={[0, 0.1, 0]}>
      {/* Outer Equator Ring */}
      <mesh ref={ring1Ref} rotation={[Math.PI / 2.3, 0, 0]}>
        <torusGeometry args={[2.3, 0.007, 16, 120]} />
        <meshBasicMaterial
          color={primaryColor}
          transparent
          opacity={0.35}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Middle Tilted Gimbal Ring */}
      <mesh ref={ring2Ref} rotation={[-Math.PI / 3, Math.PI / 6, 0]}>
        <torusGeometry args={[2.6, 0.006, 16, 120]} />
        <meshBasicMaterial
          color={secondaryColor}
          transparent
          opacity={0.25}
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Outer Data Orbit Ring */}
      <mesh ref={ring3Ref} rotation={[Math.PI / 4, -Math.PI / 4, 0]}>
        <torusGeometry args={[2.9, 0.005, 16, 120]} />
        <meshBasicMaterial
          color={primaryColor}
          transparent
          opacity={0.18}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
    </group>
  )
}

export default TechnicalRings