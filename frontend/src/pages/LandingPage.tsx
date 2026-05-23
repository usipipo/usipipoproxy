'use client';

import { useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Shield, Zap, Smartphone, CreditCard, Lock, TrendingUp
} from 'lucide-react';
import AnimatedButton from '@/components/buttons/AnimatedButton';
import GlassCard from '@/components/glass/GlassCard';

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.6, ease: [0.22, 1, 0.36, 1] }
  })
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.15 }
  }
};

function Hero() {
  const nav = useNavigate();
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });

  return (
    <motion.header
      ref={ref}
      role="banner"
      className="min-h-screen flex items-center justify-center px-4 py-20 relative overflow-hidden bg-gradient-to-b from-slate-900/50 via-slate-950 to-slate-900"
    >
      <a
        href="#features"
        className={
          'absolute left-2 -top-16 z-50 rounded-md bg-white text-blue-600 px-3 py-2 shadow transition-all ' +
          'focus:top-4 focus:left-4 focus:opacity-100 focus:outline-none focus:ring-4 focus:ring-blue-400'
        }
        aria-label="Saltar al contenido principal"
      >
        Saltar al contenido
      </a>

      <div className="absolute inset-0 pointer-events-none">
        <motion.div
          animate={{ scale: [1, 1.15, 1], opacity: [0.4, 0.7, 0.4] }}
          transition={{ repeat: Infinity, duration: 14, ease: 'linear' }}
          className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-gradient-to-br from-blue-600/20 to-cyan-500/10 blur-3xl"
        />
        <motion.div
          animate={{ x: [0, 30, 0], y: [0, -20, 0], scale: [1, 1.1, 1] }}
          transition={{ repeat: Infinity, duration: 16, ease: 'linear' }}
          className="absolute bottom-20 -left-20 w-80 h-80 rounded-full bg-gradient-to-br from-indigo-600/15 to-blue-600/10 blur-3xl"
        />
      </div>

      <motion.div
        className="max-w-5xl mx-auto text-center relative z-10"
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 1 } : { opacity: 0 }}
        transition={{ duration: 0.8 }}
      >
        <motion.h1
          custom={0}
          variants={fadeUp}
          initial="hidden"
          animate={inView ? 'visible' : 'hidden'}
          className="text-5xl sm:text-6xl lg:text-7xl font-display font-bold bg-gradient-to-r from-blue-400 via-blue-300 to-cyan-400 bg-clip-text text-transparent mb-6 leading-tight"
        >
          VPN Segura para Latinoamérica
        </motion.h1>

        <motion.p
          custom={1}
          variants={fadeUp}
          initial="hidden"
          animate={inView ? 'visible' : 'hidden'}
          className="text-lg sm:text-xl text-slate-300 mb-4 max-w-2xl mx-auto"
        >
          Accede a herramientas internacionales desde Cuba y Latinoamérica. WireGuard ultrarrápido,
          sin registros, suscripción prepagada en USDT.
        </motion.p>

        <motion.div
          custom={2}
          variants={fadeUp}
          initial="hidden"
          animate={inView ? 'visible' : 'hidden'}
          className="flex flex-col sm:flex-row gap-4 justify-center mb-8"
        >
          <AnimatedButton
            variant="primary"
            size="lg"
            onClick={() => nav('/login')}
            aria-label="Iniciar sesión con Telegram"
            className="focus:outline-none focus:ring-4 focus:ring-blue-400"
          >
            Comenzar Ahora
          </AnimatedButton>
          <AnimatedButton
            variant="ghost"
            size="lg"
            onClick={() => {
              const el = document.getElementById('features');
              el?.scrollIntoView({ behavior: 'smooth' });
            }}
            aria-label="Conocer más características"
            className="focus:outline-none focus:ring-4 focus:ring-blue-400"
          >
            Conocer Más
          </AnimatedButton>
        </motion.div>

        <motion.p
          custom={3}
          variants={fadeUp}
          initial="hidden"
          animate={inView ? 'visible' : 'hidden'}
          className="text-xs sm:text-sm text-slate-500"
        >
          Sin contraseñas. Autenticación vía Telegram. Suscripción desde $0.07 USD/día.
        </motion.p>
      </motion.div>
    </motion.header>
  );
}

function Features() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-100px' });

  const features = [
    {
      icon: Shield,
      title: 'WireGuard VPN',
      description: 'Protocolo ultramoderno y seguro. Encriptación de clase militar.'
    },
    {
      icon: CreditCard,
      title: 'Pago en USDT',
      description: 'Suscripción prepagada en USDT BEP-20. Blockchain en lugar de tarjetas.'
    },
    {
      icon: Zap,
      title: 'Auto-sweep',
      description: 'TronDealer auto-transfiere fondos. Cero comisiones.'
    },
    {
      icon: Smartphone,
      title: 'Gestión Sencilla',
      description: 'Agrega y revoca dispositivos. Monitorea tráfico en tiempo real.'
    },
    {
      icon: Lock,
      title: 'Login Telegram',
      description: 'Acceso instantáneo. Sin contraseñas. Máxima seguridad.'
    },
    {
      icon: TrendingUp,
      title: 'Dashboard',
      description: 'Visualiza uso, historial de invoices y estado de suscripción.'
    }
  ];

  return (
    <motion.section
      id="features"
      ref={ref}
      className="py-20 px-4 bg-slate-950"
      initial={{ opacity: 0 }}
      animate={inView ? { opacity: 1 } : { opacity: 0 }}
      transition={{ duration: 0.8 }}
    >
      <div className="max-w-6xl mx-auto">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-display font-bold text-center text-blue-400 mb-16"
        >
          Características
        </motion.h2>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate={inView ? 'visible' : 'hidden'}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={i}
                custom={i}
                variants={fadeUp}
                className="group"
              >
                <GlassCard className="h-full flex flex-col p-6 hover:border-blue-400/40 transition-colors">
                  <Icon className="w-12 h-12 text-blue-400 mb-4 group-hover:scale-110 transition-transform" />
                  <h3 className="text-xl font-display font-semibold text-slate-100 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-slate-400 text-sm flex-grow">
                    {feature.description}
                  </p>
                </GlassCard>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </motion.section>
  );
}

function Pricing() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-100px' });

  return (
    <motion.section
      ref={ref}
      className="py-20 px-4 bg-gradient-to-b from-slate-900 to-slate-950"
      initial={{ opacity: 0 }}
      animate={inView ? { opacity: 1 } : { opacity: 0 }}
      transition={{ duration: 0.8 }}
    >
      <div className="max-w-4xl mx-auto">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
          transition={{ duration: 0.6 }}
          className="text-4xl sm:text-5xl font-display font-bold text-center text-blue-400 mb-16"
        >
          Planes
        </motion.h2>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate={inView ? 'visible' : 'hidden'}
          className="grid grid-cols-1 md:grid-cols-2 gap-8"
        >
          <motion.div custom={0} variants={fadeUp}>
            <GlassCard className="h-full p-8">
              <h3 className="text-2xl font-display font-bold text-slate-100 mb-4">
                Plan Básico
              </h3>
              <div className="mb-6">
                <div className="text-4xl font-bold text-blue-400 mb-2">
                  $0.066
                </div>
                <p className="text-slate-400 text-sm">
                  USDT/día (∼ $2 USD/mes)
                </p>
              </div>
              <ul className="space-y-3 mb-8 text-slate-300 text-sm">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-400 rounded-full" />
                  Dispositivos ilimitados
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-400 rounded-full" />
                  Tráfico ilimitado
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-400 rounded-full" />
                  Dashboard completo
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-400 rounded-full" />
                  Soporte 24/7
                </li>
              </ul>
              <AnimatedButton
                variant="ghost"
                className="w-full focus:outline-none focus:ring-4 focus:ring-blue-400"
              >
                Seleccionar Plan
              </AnimatedButton>
            </GlassCard>
          </motion.div>

          <motion.div custom={1} variants={fadeUp}>
            <GlassCard
              className="h-full p-8 border-2 border-blue-400/50"
            >
              <div className="inline-block bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-4 py-1 rounded-full text-xs font-semibold mb-4">
                EARLY ADOPTER
              </div>
              <h3 className="text-2xl font-display font-bold text-slate-100 mb-4">
                Plan Premium
              </h3>
              <div className="mb-6">
                <div className="text-4xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text mb-2">
                  $0.013
                </div>
                <p className="text-slate-400 text-sm">
                  USDT/día (∼ $0.40 USD/mes)
                </p>
                <p className="text-xs text-blue-300 mt-2">
                  Descuento de 80% para usuarios tempranos
                </p>
              </div>
              <ul className="space-y-3 mb-8 text-slate-300 text-sm">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full" />
                  Todo del plan básico +
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full" />
                  Hosting prioritario
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full" />
                  Tokens de referido
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full" />
                  Acceso a beta features
                </li>
              </ul>
              <AnimatedButton
                variant="primary"
                className="w-full focus:outline-none focus:ring-4 focus:ring-blue-400"
              >
                Activar Ahora
              </AnimatedButton>
            </GlassCard>
          </motion.div>
        </motion.div>
      </div>
    </motion.section>
  );
}

function Footer() {
  return (
    <footer className="bg-slate-950 border-t border-blue-500/10 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="font-display font-bold text-slate-100 mb-4">
              uSipipo
            </h3>
            <p className="text-xs text-slate-500">
              VPN segura para Latinoamérica.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-200 mb-4">
              Producto
            </h4>
            <ul className="space-y-2 text-xs text-slate-500 hover:text-slate-400 transition-colors">
              <li><a href="#features">Características</a></li>
              <li><a href="#pricing">Planes</a></li>
              <li><a href="#faq">FAQ</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-200 mb-4">
              Legal
            </h4>
            <ul className="space-y-2 text-xs text-slate-500 hover:text-slate-400 transition-colors">
              <li><a href="#">Términos</a></li>
              <li><a href="#">Privacidad</a></li>
              <li><a href="#">Cookies</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-200 mb-4">
              Social
            </h4>
            <ul className="space-y-2 text-xs text-slate-500 hover:text-slate-400 transition-colors">
              <li><a href="#">Telegram</a></li>
              <li><a href="#">Twitter</a></li>
              <li><a href="#">GitHub</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-blue-500/10 pt-8 text-center text-xs text-slate-500">
          <p>
            © {new Date().getFullYear()} uSipipo Proxy. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </footer>
  );
}

export default function LandingPage() {
  useEffect(() => {
    document.title = 'uSipipo Proxy — VPN Segura para Latinoamérica';
  }, []);

  return (
    <div className="bg-slate-950 text-slate-100 selection:bg-blue-400/30 selection:text-slate-100">
      <Hero />
      <Features />
      <Pricing />
      <Footer />
    </div>
  );
}
