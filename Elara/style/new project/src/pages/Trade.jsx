import { motion } from 'framer-motion'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Text, Float } from '@react-three/drei'
import { useRef } from 'react'

function DepthChart3D() {
  const buyData = [0.8, 1.2, 1.5, 2.0, 2.5, 3.2]
  const sellData = [3.5, 2.8, 2.2, 1.8, 1.3, 0.9]

  return (
    <Canvas camera={{ position: [10, 10, 10] }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      
      {/* Buy Side */}
      <group position={[-3, 0, 0]}>
        {buyData.map((h, i) => (
          <mesh key={i} position={[i * 0.6, h/2, 0]}>
            <boxGeometry args={[0.5, h, 2]} />
            <meshStandardMaterial color="#22c55e" transparent opacity={0.6} metalness={0.8} roughness={0.2} />
          </mesh>
        ))}
      </group>

      {/* Sell Side */}
      <group position={[1, 0, 0]}>
        {sellData.map((h, i) => (
          <mesh key={i} position={[i * 0.6, h/2, 0]}>
            <boxGeometry args={[0.5, h, 2]} />
            <meshStandardMaterial color="#ef4444" transparent opacity={0.6} metalness={0.8} roughness={0.2} />
          </mesh>
        ))}
      </group>

      <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.2} />
    </Canvas>
  )
}

export default function Trade() {
  return (
    <div className="min-h-screen bg-[#050505] pt-24 pb-12 px-6">
      <div className="max-w-[1600px] mx-auto grid grid-cols-1 xl:grid-cols-4 gap-6">
        
        {/* Left Column: Order Book */}
        <div className="xl:col-span-1 space-y-6">
          <div className="p-6 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
            <h3 className="text-white font-bold mb-6">Order Book</h3>
            <div className="space-y-2">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="flex justify-between text-xs">
                  <span className="text-red-500 font-bold">64,520.{i}</span>
                  <span className="text-gray-400">0.0245</span>
                  <span className="text-gray-500">$1,580.42</span>
                </div>
              ))}
              <div className="py-4 text-center border-y border-white/5 my-4">
                <span className="text-2xl font-black text-white">64,510.80</span>
                <div className="text-xs text-gray-500">Last Price</div>
              </div>
              {[...Array(8)].map((_, i) => (
                <div key={i} className="flex justify-between text-xs">
                  <span className="text-green-500 font-bold">64,500.{i}</span>
                  <span className="text-gray-400">0.1082</span>
                  <span className="text-gray-500">$6,980.12</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Middle: 3D Chart */}
        <div className="xl:col-span-2 space-y-6">
          <div className="h-[600px] rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl relative overflow-hidden">
            <div className="absolute top-6 left-6 z-10">
              <div className="flex items-center gap-4">
                <h2 className="text-2xl font-black text-white">BTC / USD</h2>
                <span className="text-green-500 font-bold">+2.45%</span>
              </div>
            </div>
            <DepthChart3D />
          </div>

          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
            <div className="flex gap-8 border-b border-white/10 mb-6 pb-2">
              {['Open Orders', 'Trade History', 'Balances'].map((tab, i) => (
                <button key={i} className={`text-sm font-bold ${i === 0 ? 'text-yellow-500 border-b-2 border-yellow-500' : 'text-gray-500'}`}>
                  {tab}
                </button>
              ))}
            </div>
            <div className="text-center py-12 text-gray-500 italic">
              No active orders found.
            </div>
          </div>
        </div>

        {/* Right: Trade Form */}
        <div className="xl:col-span-1 space-y-6">
          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
            <div className="flex bg-black/20 p-1 rounded-2xl mb-8">
              <button className="flex-1 py-3 rounded-xl bg-green-500 text-white font-bold">Buy</button>
              <button className="flex-1 py-3 rounded-xl text-gray-400 font-bold">Sell</button>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="text-xs text-gray-500 font-bold uppercase mb-2 block">Price</label>
                <div className="relative">
                  <input type="text" value="64,510.80" className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white font-bold outline-none focus:border-yellow-500 transition-colors" />
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 text-xs">USD</span>
                </div>
              </div>

              <div>
                <label className="text-xs text-gray-500 font-bold uppercase mb-2 block">Amount</label>
                <div className="relative">
                  <input type="text" placeholder="0.0" className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white font-bold outline-none focus:border-yellow-500 transition-colors" />
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 text-xs">BTC</span>
                </div>
              </div>

              <div className="flex justify-between text-xs text-gray-500 font-bold">
                <span>0%</span>
                <span>25%</span>
                <span>50%</span>
                <span>75%</span>
                <span>100%</span>
              </div>

              <button className="w-full py-5 bg-green-500 text-white font-black rounded-2xl hover:bg-green-400 transition-all shadow-[0_10px_30px_rgba(34,197,94,0.2)]">
                Buy BTC
              </button>
            </div>
          </div>

          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
            <h3 className="text-white font-bold mb-4">Asset Info</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between text-gray-400"><span>Market Cap</span><span className="text-white">$1.2T</span></div>
              <div className="flex justify-between text-gray-400"><span>24h Volume</span><span className="text-white">$45.8B</span></div>
              <div className="flex justify-between text-gray-400"><span>Circulating Supply</span><span className="text-white">19.5M BTC</span></div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
