import { motion } from 'framer-motion'
import { Wallet, TrendingUp, ArrowUpRight, ArrowDownLeft, Clock } from 'lucide-react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, RoundedBox } from '@react-three/drei'

function BarChart3D() {
  const data = [1.2, 2.1, 1.5, 2.8, 1.9, 3.2, 2.5]
  return (
    <Canvas camera={{ position: [5, 5, 5] }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <group position={[-2, 0, 0]}>
        {data.map((h, i) => (
          <RoundedBox key={i} args={[0.5, h, 0.5]} radius={0.05} smoothness={4} position={[i * 0.7, h/2, 0]}>
            <meshStandardMaterial color={i % 2 === 0 ? "#eab308" : "#ffffff"} metalness={0.8} roughness={0.2} />
          </RoundedBox>
        ))}
      </group>
      <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
    </Canvas>
  )
}

export default function Dashboard() {
  const transactions = [
    { type: 'buy', coin: 'BTC', amount: '0.0024', status: 'Completed', date: '2 mins ago' },
    { type: 'sell', coin: 'ETH', amount: '1.20', status: 'Pending', date: '1 hour ago' },
    { type: 'swap', coin: 'SOL', amount: '45.0', status: 'Completed', date: '3 hours ago' },
  ]

  return (
    <div className="min-h-screen bg-[#050505] pt-24 pb-12 px-6">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Stats */}
        <div className="lg:col-span-2 space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl"
            >
              <div className="flex justify-between items-start mb-6">
                <div className="p-3 rounded-2xl bg-yellow-500/20 text-yellow-500">
                  <Wallet size={24} />
                </div>
                <span className="text-green-500 text-sm font-bold flex items-center gap-1">
                  +12.5% <TrendingUp size={14} />
                </span>
              </div>
              <h3 className="text-gray-400 text-sm font-medium mb-1">Total Balance</h3>
              <div className="text-4xl font-black text-white">$42,650.<span className="text-gray-500">80</span></div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl h-64 overflow-hidden relative"
            >
              <h3 className="text-white font-bold mb-4">Portfolio Activity</h3>
              <div className="absolute inset-0 pt-16">
                <BarChart3D />
              </div>
            </motion.div>
          </div>

          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
            <h3 className="text-white font-bold mb-6 flex items-center gap-2">
              <Clock size={20} className="text-yellow-500" /> Recent Transactions
            </h3>
            <div className="space-y-4">
              {transactions.map((tx, i) => (
                <div key={i} className="flex items-center justify-between p-4 rounded-2xl bg-white/5 hover:bg-white/10 transition-colors border border-transparent hover:border-white/5">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${tx.type === 'buy' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                      {tx.type === 'buy' ? <ArrowDownLeft size={20} /> : <ArrowUpRight size={20} />}
                    </div>
                    <div>
                      <div className="text-white font-bold">{tx.type.toUpperCase()} {tx.coin}</div>
                      <div className="text-gray-500 text-xs">{tx.date}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-white font-bold">{tx.amount} {tx.coin}</div>
                    <div className={`text-xs ${tx.status === 'Completed' ? 'text-green-500' : 'text-yellow-500'}`}>{tx.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Trade Panel */}
        <div className="space-y-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-8 rounded-3xl bg-yellow-500 text-black shadow-[0_0_50px_rgba(234,179,8,0.2)]"
          >
            <h3 className="text-xl font-black mb-6">Quick Swap</h3>
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-black/10">
                <div className="text-xs font-bold uppercase opacity-60 mb-2">Sell</div>
                <div className="flex justify-between items-center">
                  <input type="text" value="0.05" className="bg-transparent text-2xl font-bold outline-none w-1/2" />
                  <span className="font-black">BTC</span>
                </div>
              </div>
              <div className="p-4 rounded-2xl bg-black/10">
                <div className="text-xs font-bold uppercase opacity-60 mb-2">Get</div>
                <div className="flex justify-between items-center">
                  <input type="text" value="3,250.00" readOnly className="bg-transparent text-2xl font-bold outline-none w-1/2" />
                  <span className="font-black">USD</span>
                </div>
              </div>
              <button className="w-full py-4 bg-black text-white font-bold rounded-2xl hover:scale-[1.02] transition-transform">
                Swap Instantly
              </button>
            </div>
          </motion.div>

          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
            <h3 className="text-white font-bold mb-4">Market Trends</h3>
            {['Bitcoin', 'Ethereum', 'Solana'].map((coin, i) => (
              <div key={i} className="flex justify-between items-center py-3 border-b border-white/5 last:border-0">
                <span className="text-gray-400">{coin}</span>
                <span className={i === 2 ? "text-red-500" : "text-green-500"}>{i === 2 ? "-1.2%" : "+2.4%"}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}
