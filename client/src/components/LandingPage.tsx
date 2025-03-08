import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { scrollYProgress } = useScroll();
  
  const backgroundY = useTransform(scrollYProgress, [0, 1], ['0%', '100%']);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <div className="min-h-screen bg-slate-900 relative overflow-hidden">
      {/* Animated Background */}
      <motion.div 
        className="fixed inset-0 z-0"
        style={{
          background: 'radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 25%, rgba(17, 24, 39, 0) 50%)',
          y: backgroundY,
          opacity
        }}
      />
      <div className="absolute inset-0 overflow-hidden">
        {/* Fine Grid */}
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(rgb(59 130 246 / 0.1) 1px, transparent 1px)`,
          backgroundSize: '24px 24px',
          maskImage: 'linear-gradient(to bottom, white, transparent)'
        }} />
        {/* Large Grid */}
        <div className="absolute inset-0" style={{
          backgroundImage: `linear-gradient(to right, rgb(59 130 246 / 0.1) 1px, transparent 1px),
                           linear-gradient(to bottom, rgb(59 130 246 / 0.1) 1px, transparent 1px)`,
          backgroundSize: '96px 96px',
          maskImage: 'linear-gradient(to bottom, white, transparent)'
        }} />
      </div>
      
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-900/80">
        {/* Glow Effects */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl" />
      </div>
      {/* Background Animation */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full bg-white/5 backdrop-blur-3xl"
            style={{
              width: `${Math.random() * 400 + 200}px`,
              height: `${Math.random() * 400 + 200}px`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              x: [0, Math.random() * 100 - 50],
              y: [0, Math.random() * 100 - 50],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              repeatType: "reverse",
            }}
          />
        ))}
      </div>
      {/* Navigation */}
      <motion.nav 
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="fixed top-0 w-full py-6 px-4 md:px-8 backdrop-blur-sm bg-slate-900/80 border-b border-slate-800 z-50"
      >
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-blue-200 bg-clip-text text-transparent">ScrumBot</div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/chat')}
            className="bg-blue-500/10 backdrop-blur-lg text-blue-400 px-6 py-2 rounded-full 
                     hover:bg-blue-500/20 border-2 border-blue-400 hover:border-blue-300 
                     transition-all duration-300 shadow-[0_0_15px_rgba(59,130,246,0.5)] 
                     hover:shadow-[0_0_20px_rgba(59,130,246,0.7)]"
          >
            Launch App
          </motion.button>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <motion.section 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden pt-24"
      >
        {/* Background Circles */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute w-[800px] h-[800px] rounded-full bg-blue-500/20 blur-3xl -top-[400px] -right-[400px]"></div>
          <div className="absolute w-[600px] h-[600px] rounded-full bg-orange-500/20 blur-3xl -bottom-[300px] -left-[300px]"></div>
        </div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-6xl mx-auto text-center text-white"
        >
          <motion.h1 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-6xl md:text-8xl font-bold mb-8 leading-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-blue-200 to-blue-400 tracking-tight"
          >
            Transform Your Daily
            <span className="relative inline-block">
              <span className="absolute inset-0 bg-gradient-to-r from-blue-500 to-blue-400 blur-2xl opacity-30" />
              <span className="relative bg-gradient-to-r from-blue-400 to-blue-300 bg-clip-text text-transparent inline-block transform hover:scale-105 transition-transform duration-300">
                {' '}Standups
              </span>
            </span>
          </motion.h1>
          <motion.p 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="text-xl md:text-2xl mb-16 text-slate-400 max-w-3xl mx-auto font-light tracking-wide"
          >
            Experience the future of team collaboration with our AI-powered Scrum Assistant.
            Streamline your meetings and boost productivity.
          </motion.p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/chat')}
            className="relative inline-flex items-center justify-center px-12 py-5 overflow-hidden text-xl 
                     font-medium text-blue-300 border-2 border-blue-400 rounded-full group 
                     hover:bg-blue-500/10 transition-all duration-300 
                     shadow-[0_0_20px_rgba(59,130,246,0.5)] hover:shadow-[0_0_30px_rgba(59,130,246,0.7)] 
                     hover:border-blue-300 hover:text-blue-200"
          >
            <span className="absolute w-0 h-0 transition-all duration-500 ease-out bg-blue-500 rounded-full group-hover:w-72 group-hover:h-72 opacity-10" />
            <span className="relative">
              Get Started Free
            </span>
          </motion.button>
        </motion.div>
      </motion.section>

      {/* Features Section */}
      <motion.section 
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 1 }}
        viewport={{ once: true }}
        className="py-32 px-4 bg-slate-900/50 backdrop-blur-sm border-t border-b border-slate-800 relative z-10"
      >
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center bg-gradient-to-r from-blue-400 to-blue-200 bg-clip-text text-transparent mb-16">
            Powerful Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { icon: "🎤", title: "Voice Enabled", description: "Natural conversations with advanced speech recognition for seamless interaction" },
              { icon: "🤖", title: "AI Assistant", description: "Intelligent responses and insights powered by advanced AI technology" },
              { icon: "📊", title: "Smart Analytics", description: "Track progress and get insights from your team's daily updates" }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                whileHover={{ scale: 1.05 }}
                className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8 text-white hover:bg-slate-800/70 transition-colors duration-300"
              >
                <motion.div 
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ 
                    type: "spring",
                    stiffness: 260,
                    damping: 20,
                    delay: 0.8 + i * 0.1
                  }}
                  className="text-5xl mb-6 transform hover:scale-110 transition-transform duration-200"
                >
                  {feature.icon}
                </motion.div>
                <h3 className="text-2xl font-semibold mb-4">{feature.title}</h3>
                <p className="text-blue-100">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Footer */}
      <motion.footer 
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ duration: 1 }}
        viewport={{ once: true }}
        className="bg-slate-900/80 backdrop-blur-sm border-t border-slate-800 text-slate-400 py-16 relative z-10"
      >
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-2xl font-bold mb-4">ScrumBot</h3>
              <p className="text-blue-100">
                Making daily standups more productive and engaging
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-blue-100">
                <li>Features</li>
                <li>Pricing</li>
                <li>Documentation</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-blue-100">
                <li>About Us</li>
                <li>Contact</li>
                <li>Privacy Policy</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Connect</h4>
              <div className="flex space-x-4">
                <motion.a
                  whileHover={{ scale: 1.1 }}
                  href="#"
                  className="text-blue-100 hover:text-orange-400"
                >
                  <span className="text-2xl">💻</span>
                </motion.a>
                <motion.a
                  whileHover={{ scale: 1.1 }}
                  href="#"
                  className="text-blue-100 hover:text-orange-400"
                >
                  <span className="text-2xl">💬</span>
                </motion.a>
                <motion.a
                  whileHover={{ scale: 1.1 }}
                  href="#"
                  className="text-blue-100 hover:text-orange-400"
                >
                  <span className="text-2xl">👥</span>
                </motion.a>
              </div>
            </div>
          </div>
          <div className="border-t border-white/10 mt-12 pt-8 text-center text-blue-100">
            <p>© 2025 ScrumBot. All rights reserved.</p>
          </div>
        </div>
      </motion.footer>
    </div>
  );
};
