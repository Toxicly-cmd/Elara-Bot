import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Float, MeshDistortMaterial, MeshWobbleMaterial } from '@react-three/drei'

export default function FloatingCoin({ color = "#fcc203", position = [0, 0, 0], speed = 1 }) {
  const mesh = useRef()

  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    mesh.current.rotation.y = time * speed
    mesh.current.position.y = position[1] + Math.sin(time) * 0.1
  })

  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={1}>
      <mesh ref={mesh} position={position}>
        <cylinderGeometry args={[0.5, 0.5, 0.1, 32]} />
        <meshStandardMaterial 
          color={color} 
          metalness={0.8} 
          roughness={0.2} 
          emissive={color}
          emissiveIntensity={0.2}
        />
      </mesh>
    </Float>
  )
}
