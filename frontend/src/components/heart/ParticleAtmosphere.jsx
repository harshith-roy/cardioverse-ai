import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

/**
 * Cinematic Floating Particle Atmosphere
 * Ambient bioluminescent particles drifting around the 3D heart.
 */
export function ParticleAtmosphere({ count = 400, riskProbability = 0.1 }) {
  const pointsRef = useRef()

  const isHighRisk = riskProbability > 0.5
  const baseColor = useMemo(() => {
    return isHighRisk ? new THREE.Color('#FB7185') : new THREE.Color('#22D3EE')
  }, [isHighRisk])

  const [positions, speeds, phases] = useMemo(() => {
    const pos = new Float32Array(count * 3)
    const spd = new Float32Array(count)
    const phs = new Float32Array(count)

    for (let i = 0; i < count; i++) {
      // Distribute in a spherical shell around the heart
      const radius = 1.8 + Math.random() * 2.2
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)

      pos[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
      pos[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
      pos[i * 3 + 2] = radius * Math.cos(phi)

      spd[i] = 0.2 + Math.random() * 0.6
      phs[i] = Math.random() * Math.PI * 2
    }

    return [pos, spd, phs]
  }, [count])

  useFrame((state, delta) => {
    if (!pointsRef.current) return
    const time = state.clock.elapsedTime
    const posAttr = pointsRef.current.geometry.attributes.position
    const array = posAttr.array

    for (let i = 0; i < count; i++) {
      const idx = i * 3
      // Gentle vertical wave drift
      array[idx + 1] += Math.sin(time * speeds[i] + phases[i]) * 0.002
      // Gentle orbital slow rotate
      const x = array[idx]
      const z = array[idx + 2]
      const angle = delta * 0.05 * speeds[i]
      array[idx] = x * Math.cos(angle) - z * Math.sin(angle)
      array[idx + 2] = x * Math.sin(angle) + z * Math.cos(angle)
    }

    posAttr.needsUpdate = true
    pointsRef.current.rotation.y += delta * 0.02
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.035}
        color={baseColor}
        transparent
        opacity={0.45}
        sizeAttenuation
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  )
}

export default ParticleAtmosphere