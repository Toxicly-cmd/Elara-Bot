import Hero from '../components/Hero'
import Swap from '../components/Swap'

export default function Landing() {
  return (
    <div className="w-full min-h-screen bg-[#050505]">
      <Hero />
      
      <section className="py-20 bg-[#050505] text-white">
        <div className="container px-4 mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div className="text-left">
              <h2 className="text-4xl font-bold md:text-5xl leading-tight">Instant Swaps, <br/><span className="text-yellow-500">Zero Friction.</span></h2>
              <p className="mt-6 text-gray-400 text-lg">
                Trade between dozens of cryptocurrencies instantly with the best market rates. 
                Our platform ensures your trades are executed securely and efficiently.
              </p>
              <ul className="mt-8 space-y-4">
                {['Lowest Fees in the Industry', 'Secure P2P Escrow', '24/7 Live Support'].map((item, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-500">✓</div>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <Swap />
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-[#050505] text-white">
        <div className="container px-4 mx-auto text-center">
          <h2 className="text-4xl font-bold md:text-5xl">Why Choose CryptiSys?</h2>
          <div className="grid grid-cols-1 gap-8 mt-16 md:grid-cols-3">
            {[
              { title: "Immersive 3D UI", desc: "Interact with the market like never before with our cutting-edge 3D dashboard." },
              { title: "Secure P2P", desc: "Trade directly with other users with our integrated escrow service." },
              { title: "Real-time Data", desc: "Stay ahead with lightning-fast market updates and 3D price charts." }
            ].map((feature, i) => (
              <div key={i} className="p-8 border rounded-2xl border-white/10 bg-white/5 backdrop-blur-sm hover:border-yellow-500/50 transition-colors">
                <h3 className="mb-4 text-2xl font-bold text-yellow-500">{feature.title}</h3>
                <p className="text-gray-400">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 border-t border-white/10 bg-[#050505]">
        <div className="container px-4 mx-auto max-w-4xl">
          <div className="p-10 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-md">
            <h2 className="text-3xl font-bold text-white text-center mb-10">Get in Touch</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
              <div className="space-y-6">
                <p className="text-gray-400">Have questions? Our team is available 24/7 to assist you with any inquiries or support needs.</p>
                <div className="flex items-center gap-4 text-white">
                  <span className="text-yellow-500 font-bold">Email:</span> support@cryptisys.com
                </div>
                <div className="flex items-center gap-4 text-white">
                  <span className="text-yellow-500 font-bold">Discord:</span> join.cryptisys.gg
                </div>
              </div>
              <form className="space-y-4">
                <input type="text" placeholder="Your Name" className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:border-yellow-500 outline-none transition-all" />
                <input type="email" placeholder="Email Address" className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:border-yellow-500 outline-none transition-all" />
                <textarea placeholder="Message" rows={4} className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:border-yellow-500 outline-none transition-all"></textarea>
                <button className="w-full py-4 bg-yellow-500 text-black font-bold rounded-xl hover:bg-yellow-400 transition-all">Send Message</button>
              </form>
            </div>
          </div>
        </div>
      </section>

      <footer className="py-10 border-t border-white/10 text-center text-gray-500">
        <p>© 2024 CRYPTISYS. All rights reserved.</p>
      </footer>
    </div>
  )
}
