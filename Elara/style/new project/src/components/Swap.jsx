import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowDownUp } from 'lucide-react'

export default function Swap() {
  const [fromAmount, setFromAmount] = useState('')
  const [toAmount, setToAmount] = useState('')
  const [rate] = useState(65000.42) // Static BTC/USD rate for MVP

  const handleFromChange = (val) => {
    setFromAmount(val)
    setToAmount(val ? (parseFloat(val) / rate).toFixed(6) : '')
  }

  return (
    <div className="w-full max-w-lg p-8 mx-auto border rounded-3xl border-white/10 bg-white/5 backdrop-blur-xl">
      <h3 className="mb-6 text-2xl font-bold text-white">Swap Tokens</h3>
      
      <div className="space-y-4">
        <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
          <label className="block mb-2 text-sm text-gray-400">You Pay</label>
          <div className="flex items-center justify-between">
            <input 
              type="number" 
              value={fromAmount}
              onChange={(e) => handleFromChange(e.target.value)}
              className="text-3xl font-bold text-white bg-transparent outline-none w-2/3"
              placeholder="0.0"
            />
            <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-white/10 border border-white/20">
              <span className="font-bold text-white">USD</span>
            </div>
          </div>
        </div>

        <div className="flex justify-center -my-4 relative z-10">
          <button className="p-3 rounded-xl bg-yellow-500 text-black hover:scale-110 transition-transform shadow-lg">
            <ArrowDownUp size={20} />
          </button>
        </div>

        <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
          <label className="block mb-2 text-sm text-gray-400">You Get</label>
          <div className="flex items-center justify-between">
            <input 
              type="text" 
              value={toAmount}
              readOnly
              className="text-3xl font-bold text-white bg-transparent outline-none w-2/3"
              placeholder="0.0"
            />
            <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-white/10 border border-white/20">
              <span className="font-bold text-white">BTC</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/20">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Exchange Rate</span>
          <span className="text-yellow-500 font-medium">1 BTC = {rate.toLocaleString()} USD</span>
        </div>
      </div>

      <button className="w-full py-4 mt-8 font-bold text-black transition-all bg-yellow-500 rounded-2xl hover:bg-yellow-400 hover:shadow-[0_0_20px_rgba(234,179,8,0.3)]">
        Swap Now
      </button>
    </div>
  )
}
