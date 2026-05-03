import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Canvas } from '@react-three/fiber'
import Stars from '../components/canvas/Stars'

export default function Login() {
  return (
    <div className="relative w-full h-screen overflow-hidden bg-[#050505] flex items-center justify-center">
      <div className="absolute inset-0 z-0">
        <Canvas>
          <Stars />
        </Canvas>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-md p-10 mx-4 border rounded-3xl border-white/10 bg-white/5 backdrop-blur-xl"
      >
        <h2 className="mb-8 text-4xl font-bold text-center text-white">Welcome Back</h2>
        
        <form className="space-y-6">
          <div>
            <label className="block mb-2 text-sm font-medium text-gray-400">Email Address</label>
            <input 
              type="email" 
              className="w-full px-4 py-3 text-white transition-all border rounded-xl bg-white/5 border-white/10 focus:border-yellow-500 focus:outline-none"
              placeholder="name@example.com"
            />
          </div>
          
          <div>
            <label className="block mb-2 text-sm font-medium text-gray-400">Password</label>
            <input 
              type="password" 
              className="w-full px-4 py-3 text-white transition-all border rounded-xl bg-white/5 border-white/10 focus:border-yellow-500 focus:outline-none"
              placeholder="••••••••"
            />
          </div>

          <button className="w-full py-4 font-bold text-black transition-all bg-yellow-500 rounded-xl hover:bg-yellow-400">
            Sign In
          </button>
        </form>

        <p className="mt-8 text-center text-gray-400">
          Don't have an account? <Link to="/register" className="text-yellow-500 hover:underline">Sign up</Link>
        </p>
      </motion.div>
    </div>
  )
}
