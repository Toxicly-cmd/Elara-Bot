import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Filter, ShieldCheck, Star } from 'lucide-react'

export default function Marketplace() {
  const [filter, setFilter] = useState('buy')
  
  const listings = [
    { user: 'CryptoKing', rating: 4.9, trades: 1240, price: '64,200', min: '500', max: '10,000', method: 'Bank Transfer' },
    { user: 'AlphaTrader', rating: 4.7, trades: 850, price: '64,150', min: '100', max: '5,000', method: 'PayPal' },
    { user: 'SecureSwap', rating: 5.0, trades: 210, price: '64,300', min: '1,000', max: '50,000', method: 'Wise' },
    { user: 'FastFiller', rating: 4.5, trades: 3400, price: '64,100', min: '50', max: '2,000', method: 'Credit Card' },
  ]

  return (
    <div className="min-h-screen bg-[#050505] pt-24 pb-12 px-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-12 gap-6">
          <div>
            <h1 className="text-4xl font-black text-white mb-2">P2P Marketplace</h1>
            <p className="text-gray-400">Trade directly with verified users with zero fees.</p>
          </div>
          <div className="flex bg-white/5 p-1 rounded-2xl border border-white/10">
            <button 
              onClick={() => setFilter('buy')}
              className={`px-8 py-3 rounded-xl font-bold transition-all ${filter === 'buy' ? 'bg-yellow-500 text-black' : 'text-gray-400 hover:text-white'}`}
            >
              Buy
            </button>
            <button 
              onClick={() => setFilter('sell')}
              className={`px-8 py-3 rounded-xl font-bold transition-all ${filter === 'sell' ? 'bg-yellow-500 text-black' : 'text-gray-400 hover:text-white'}`}
            >
              Sell
            </button>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="md:col-span-2 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
            <input 
              type="text" 
              placeholder="Search by amount or currency..." 
              className="w-full pl-12 pr-4 py-4 rounded-2xl bg-white/5 border border-white/10 text-white outline-none focus:border-yellow-500 transition-colors"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
            <select className="w-full pl-12 pr-4 py-4 rounded-2xl bg-white/5 border border-white/10 text-white outline-none appearance-none cursor-pointer">
              <option>All Payment Methods</option>
              <option>Bank Transfer</option>
              <option>PayPal</option>
            </select>
          </div>
          <button className="py-4 bg-white/10 text-white font-bold rounded-2xl border border-white/10 hover:bg-white/20">
            More Filters
          </button>
        </div>

        {/* Listings Table */}
        <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 backdrop-blur-xl">
          <div className="hidden md:grid grid-cols-5 p-6 border-b border-white/10 text-gray-500 text-sm font-bold uppercase tracking-wider">
            <span>Advertiser</span>
            <span>Price</span>
            <span>Limit/Available</span>
            <span>Payment Method</span>
            <span className="text-right">Action</span>
          </div>
          
          <div className="divide-y divide-white/5">
            {listings.map((ad, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="grid grid-cols-1 md:grid-cols-5 p-6 gap-4 items-center hover:bg-white/5 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-yellow-500 to-yellow-700 flex items-center justify-center text-black font-bold text-xl">
                    {ad.user[0]}
                  </div>
                  <div>
                    <div className="text-white font-bold flex items-center gap-1">
                      {ad.user} <ShieldCheck size={14} className="text-green-500" />
                    </div>
                    <div className="text-xs text-gray-500 flex items-center gap-1">
                      <Star size={10} className="text-yellow-500 fill-yellow-500" /> {ad.rating} | {ad.trades} Trades
                    </div>
                  </div>
                </div>

                <div className="text-2xl font-black text-white">
                  {ad.price} <span className="text-xs text-gray-500 ml-1">USD</span>
                </div>

                <div>
                  <div className="text-gray-400 text-sm">Limit: ${ad.min} - ${ad.max}</div>
                  <div className="text-white text-sm font-bold">0.85 BTC</div>
                </div>

                <div>
                  <span className="px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-500 text-xs font-bold border border-yellow-500/20">
                    {ad.method}
                  </span>
                </div>

                <div className="text-right">
                  <button className={`px-8 py-3 rounded-xl font-bold transition-all ${filter === 'buy' ? 'bg-green-500 text-white hover:bg-green-400' : 'bg-red-500 text-white hover:bg-red-400'}`}>
                    {filter === 'buy' ? 'Buy BTC' : 'Sell BTC'}
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}
