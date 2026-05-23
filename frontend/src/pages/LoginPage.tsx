'use client';

import { type FormEvent, useCallback, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { auth } from '@/api/client';
import type { LoginRequest } from '@/types';

// Parallax blob variants used in this page
const blobRest = {
  x: 0,
  y: 0,
  scale: 1,
  transition: { repeat: Infinity, duration: 14, ease: 'linear' as const },
};

function Blob({ className }: { className: string }) {
  return (
    <motion.div
      animate={{ x: [0, 30, 0], y: [0, -20, 0], scale: [1, 1.1, 1] }}
      transition={blobRest}
      className={className}
    />
  );
}

export default function LoginPage() {
  const nav = useNavigate();
  const [error, setError] = useState('');

  /** Production path: real Telegram Mini App initData from window.Telegram.WebApp.initData */
  const handleTelegramAuth = useCallback(
    async (authData: LoginRequest) => {
      try {
        // auth.setCookie() is called inside loginWithTelegram
        await auth.telegramLogin(authData);
        nav('/#/dashboard', { replace: true });
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : 'Error de autenticación';
        setError(msg);
      }
    },
    [nav],
  );

  /** Dev mock: allows testing without Telegram embed */
  const mockLogin = useCallback(async () => {
    await handleTelegramAuth({
      id: 891835105,
      first_name: 'Test',
      last_name: 'User',
      username: 'testuser',
      auth_date: Math.floor(Date.now() / 1000),
      hash: 'mock_hash_development_only',
    });
  }, [handleTelegramAuth]);

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    mockLogin();
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden"
    >
      {/* Animated background blobs */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <Blob className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-gradient-to-br from-blue-600/20 to-cyan-500/10 blur-3xl" />
        <Blob className="absolute bottom-20 -left-20 w-80 h-80 rounded-full bg-gradient-to-br from-indigo-600/15 to-blue-600/10 blur-3xl" />
      </div>

      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.7 }}
        className="glass rounded-2xl p-10 w-full max-w-md relative z-10"
      >
        <h1 className="text-3xl font-display font-bold text-blue-400 mb-2">
          Bienvenido
        </h1>
        <p className="text-slate-400 mb-8 text-sm leading-relaxed">
          Accede a tu VPN WireGuard segura con tu cuenta de Telegram.
        </p>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-500/10 border border-red-500/25 rounded-xl px-4 py-3 text-red-400 text-sm mb-5"
            role="alert"
          >
            {error}
          </motion.div>
        )}

        <form onSubmit={onSubmit}>
          <button type="submit" className="w-full px-5 py-3 bg-blue-600 text-white rounded-xl font-semibold font-body cursor-pointer transition-all hover:bg-blue-500 shadow-lg">
            Entrar con Telegram
          </button>
        </form>

        <p className="text-xs text-slate-500 text-center mt-4">
          Únete con tu cuenta de Telegram — sin contraseña.
        </p>

        {import.meta.env.DEV && (
          <p className="text-xs text-amber-500/70 text-center mt-2">
            ⚠ Dev mock active — hash disabled in development only
          </p>
        )}
      </motion.div>
    </motion.div>
  );
}
