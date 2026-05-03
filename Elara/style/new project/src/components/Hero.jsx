import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera } from '@react-three/drei'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import Stars from './canvas/Stars'
import FloatingCoin from './canvas/FloatingCoin'

export default function Hero() {
  return (
    <div className="relative w-full h-screen mx-auto overflow-hidden bg-[#050505]">
      {/* 3D Canvas Background */}
      <div className="absolute inset-0 z-0">
        <Canvas>
          <PerspectiveCamera makeDefault position={[0, 0, 5]} />
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <spotLight position={[-10, 10, 10]} angle={0.15} penumbra={1} />
          
          <Stars />
          <FloatingCoin position={[-2, 1, 0]} color="#fcc203" speed={0.5} />
          <FloatingCoin position={[2, -1, -1]} color="#627eea" speed={0.8} />
          <FloatingCoin position={[0, -2, 1]} color="#26a17b" speed={1.2} />
          
          <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
        </Canvas>
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center justify-center h-full px-4 text-center">
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-6xl font-extrabold tracking-tighter text-white md:text-8xl lg:text-9xl"
        >
          CRYPTI<span className="text-yellow-500">SYS</span>
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="max-w-2xl mt-6 text-lg text-gray-400 md:text-xl lg:text-2xl"
        >
          Experience the future of trading in a fully immersive 3D-animated marketplace. 
          Secure, fast, and visually stunning.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex flex-wrap items-center justify-center gap-4 mt-10"
        >
          <Link to="/login" className="px-8 py-4 text-lg font-bold text-black transition-all duration-300 bg-yellow-500 rounded-full hover:bg-yellow-400 hover:shadow-[0_0_20px_rgba(234,179,8,0.5)]">
            Start Trading
          </Link>
          <button className="px-8 py-4 text-lg font-bold text-white transition-all duration-300 border border-white/20 rounded-full bg-white/5 backdrop-blur-md hover:bg-white/10">
            View Marketplace
          </button>
        </motion.div>
      </div>

      {/* Bottom Gradient Overlay */}
      <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-[#050505] to-transparent z-10" />
    </div>
  )
}
