import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 w-full z-50 px-6 py-4 flex items-center justify-between bg-black/10 backdrop-blur-md border-b border-white/5">
      <Link to="/" className="text-2xl font-black tracking-tighter text-white">
        CRYPTI<span className="text-yellow-500">SYS</span>
      </Link>
      
      <div className="hidden lg:flex items-center gap-8">
        <Link to="/dashboard" className="text-gray-400 hover:text-white transition-colors font-medium">Dashboard</Link>
        <Link to="/marketplace" className="text-gray-400 hover:text-white transition-colors font-medium">Marketplace</Link>
        <Link to="/trade" className="text-gray-400 hover:text-white transition-colors font-medium">Trade</Link>
        <Link to="/" className="text-gray-400 hover:text-white transition-colors font-medium">Features</Link>
      </div>

      <div className="flex items-center gap-4">
        <Link to="/login" className="px-6 py-2 text-sm font-bold text-white hover:text-yellow-500 transition-colors">
          Login
        </Link>
        <Link to="/register" className="px-6 py-2 text-sm font-bold text-black bg-yellow-500 rounded-full hover:bg-yellow-400 transition-all">
          Sign Up
        </Link>
      </div>
    </nav>
  )
}
