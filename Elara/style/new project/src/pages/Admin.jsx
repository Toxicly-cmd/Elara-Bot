import { motion } from 'framer-motion'
import { Users, Activity, AlertTriangle, CheckCircle, BarChart2 } from 'lucide-react'

export default function Admin() {
  const stats = [
    { label: 'Total Users', value: '12,840', icon: <Users />, color: 'bg-blue-500' },
    { label: 'Volume (24h)', value: '$1.2M', icon: <BarChart2 />, color: 'bg-green-500' },
    { label: 'Active Trades', value: '450', icon: <Activity />, color: 'bg-yellow-500' },
    { label: 'Pending Disputes', value: '3', icon: <AlertTriangle />, color: 'bg-red-500' },
  ]

  const recentActivities = [
    { user: 'user_992', action: 'KYC Verified', time: '5m ago', status: 'Success' },
    { user: 'trader_x', action: 'Large Deposit ($50k)', time: '12m ago', status: 'Flagged' },
    { user: 'crypto_fan', action: 'New P2P Dispute', time: '45m ago', status: 'Review' },
  ]

  return (
    <div className="min-h-screen bg-[#050505] pt-24 pb-12 px-6">
      <div className="max-w-7xl mx-auto">
        
        <div className="mb-12">
          <h1 className="text-4xl font-black text-white mb-2">Admin Panel</h1>
          <p className="text-gray-400">System overview and management dashboard.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {stats.map((s, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl"
            >
              <div className={`p-3 rounded-2xl ${s.color} text-white w-fit mb-6`}>
                {s.icon}
              </div>
              <div className="text-gray-500 text-sm font-bold uppercase">{s.label}</div>
              <div className="text-3xl font-black text-white mt-1">{s.value}</div>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Activity Feed */}
          <div className="lg:col-span-2 p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
            <h3 className="text-white font-bold mb-8">System Activity</h3>
            <div className="space-y-6">
              {recentActivities.map((act, i) => (
                <div key={i} className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white">
                      {act.user[0].toUpperCase()}
                    </div>
                    <div>
                      <div className="text-white font-bold">{act.user}</div>
                      <div className="text-gray-500 text-xs">{act.action}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-gray-500 text-xs mb-1">{act.time}</div>
                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase ${
                      act.status === 'Success' ? 'bg-green-500/10 text-green-500' :
                      act.status === 'Flagged' ? 'bg-red-500/10 text-red-500' : 'bg-yellow-500/10 text-yellow-500'
                    }`}>
                      {act.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full mt-8 py-4 text-gray-400 font-bold hover:text-white transition-colors">
              View All Logs
            </button>
          </div>

          {/* User Requests / Support */}
          <div className="p-8 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-xl">
            <h3 className="text-white font-bold mb-8">Pending Actions</h3>
            <div className="space-y-4">
              <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/20">
                <div className="flex items-center gap-3 text-red-500 font-bold mb-2">
                  <AlertTriangle size={18} /> High Priority
                </div>
                <p className="text-sm text-gray-400 mb-4">Dispute #882: Payment proof mismatch reported by seller.</p>
                <button className="w-full py-2 bg-red-500 text-white text-xs font-black rounded-lg">Resolve Now</button>
              </div>
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                <div className="text-white font-bold mb-2">KYC Requests</div>
                <p className="text-xs text-gray-500 mb-4">12 new identities pending verification.</p>
                <button className="w-full py-2 bg-white/10 text-white text-xs font-black rounded-lg">Review Batch</button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
