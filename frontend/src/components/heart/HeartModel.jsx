import { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'

/**
 * Anatomical 3D Heart Model with Dynamic Biometric Rhythms & AI State Shader
 */
export function HeartModel({
  path = '/heart.glb',
  prediction = null,
  isInteracting = false,
  wireframe = false,
  onLoad
}) {
  const { scene } = useGLTF(path)
  const groupRef = useRef()

  const probability = prediction?.disease_probability || 0.15
  const isHighRisk = probability > 0.5
  // Calculate simulated BPM: higher risk / higher blood pressure increases heart rate
  const bpm = isHighRisk ? 92 : 72
  const beatSpeed = (bpm / 60) * Math.PI * 2

  // Process & center GLTF scene
  const clonedScene = useMemo(() => {
    if (!scene) return null
    const clone = scene.clone(true)

    // Compute bounding box
    const box = new THREE.Box3().setFromObject(clone)
    const center = box.getCenter(new THREE.Vector3())
    const size = box.getSize(new THREE.Vector3())
    const maxDim = Math.max(size.x, size.y, size.z) || 1

    // Normalize to target height ~2.7 units
    const targetScale = 2.7 / maxDim
    clone.scale.setScalar(targetScale)
    clone.position.sub(center.clone().multiplyScalar(targetScale))
    clone.position.y += 0.15

    return clone
  }, [scene])

  // Update materials based on prediction risk and wireframe state
  useEffect(() => {
    if (!clonedScene) return

    const primaryColor = isHighRisk
      ? new THREE.Color('#E11D48')
      : new THREE.Color('#0284C7')

    const emissiveColor = isHighRisk
      ? new THREE.Color('#881337')
      : new THREE.Color('#082F49')

    clonedScene.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true
        child.receiveShadow = true

        if (child.material) {
          const mats = Array.isArray(child.material) ? child.material : [child.material]
          mats.forEach((mat) => {
            mat.wireframe = wireframe
            mat.needsUpdate = true

            if (mat.isMeshStandardMaterial || mat.isMeshPhysicalMaterial) {
              mat.roughness = isHighRisk ? 0.45 : 0.65
              mat.metalness = isHighRisk ? 0.25 : 0.1
              mat.emissive = emissiveColor
              mat.emissiveIntensity = isHighRisk ? 0.6 : 0.2
            }
          })
        }
      }
    })

    if (onLoad) {
      onLoad(true)
    }
  }, [clonedScene, isHighRisk, wireframe, onLoad])

  // Anatomical dual-phase heartbeat (Systole contraction + Diastole filling)
  useFrame((state, delta) => {
    if (!groupRef.current) return
    const t = state.clock.elapsedTime

    // Dual-peak heartbeat curve
    const cycle = (t * (beatSpeed / 2)) % (Math.PI * 2)
    const primaryPulse = Math.pow(Math.sin(cycle), 10) * 0.04
    const secondaryPulse = Math.pow(Math.sin(cycle + 0.4), 8) * 0.02
    const totalBeat = primaryPulse + secondaryPulse

    const baseScale = 1.0 + totalBeat
    groupRef.current.scale.set(baseScale, baseScale, baseScale)

    // Gentle atmospheric sway when user is not manually orbiting
    if (!isInteracting) {
      groupRef.current.position.y = 0.15 + Math.sin(t * 1.2) * 0.03
      groupRef.current.rotation.y += delta * 0.1
    }
  })

  if (!clonedScene) return null

  return (
    <group ref={groupRef}>
      <primitive object={clonedScene} />
    </group>
  )
}

export default HeartModel