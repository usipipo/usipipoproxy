'use client';

import { useState, type FormEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import GlassCard from '@/components/glass/GlassCard';
import GlassInput from '@/components/form/GlassInput';
import Spinner from '@/components/feedback/Spinner';
import AnimatedButton from '@/components/buttons/AnimatedButton';
import { devices } from '@/api/client';
import type { ClientConfig } from '@/types';

interface Props {
  onClose: () => void;
  onCreated: (conf: ClientConfig) => void;
}

export default function CreateDeviceModal({ onClose, onCreated }: Props) {
  const [name, setName] = useState('');
  const [psk, setPsk] = useState('');
  const [showPsk, setShowPsk] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [conf, setConf] = useState<ClientConfig | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;
    setLoading(true);
    setError('');
    try {
      const resp = await devices.create({ name: trimmed, psk: showPsk ? psk : undefined });
      setConf(resp.conf as ClientConfig);
      onCreated(resp.conf);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al crear dispositivo');
    } finally {
      setLoading(false);
    }
  }

  // Step 2: show .conf content and copy button
  if (conf) {
    const confString = `[Interface]
PrivateKey = ${conf.privateKey}
Address = ${conf.address}
DNS = ${conf.dns}

[Peer]
PublicKey = ${conf.public_key}
${conf.psk ? `PresharedKey = ${conf.psk}` : '# PresharedKey = (none)'}
Endpoint = ${conf.endpoint}
AllowedIPs = ${conf.allowed_ips}`;

    const handleCopy = async () => {
      await navigator.clipboard.writeText(confString);
    };

    return (
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={onClose}
        >
          <GlassCard className="w-full max-w-lg p-6 space-y-4">
            <h2 className="text-xl font-display font-bold text-blue-400">Dispositivo creado</h2>
            <p className="text-sm text-slate-400">
              Guarda tu archivo de configuración <strong className="text-white">en un lugar seguro</strong>.
              La clave privada no volverá a mostrarse.
            </p>
            <pre className="bg-slate-900/80 rounded-xl p-4 text-xs font-mono text-slate-300 overflow-auto max-h-60 custom-scrollbar">
              {confString}
            </pre>
            <div className="flex gap-3">
              <AnimatedButton onClick={onClose} variant="primary" className="flex-1">
                Cerrar
              </AnimatedButton>
              <AnimatedButton onClick={handleCopy} variant="ghost" className="flex-1">
                Copiar configuración
              </AnimatedButton>
            </div>
          </GlassCard>
        </motion.div>
      </AnimatePresence>
    );
  }

  // Step 1: form
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <GlassCard
          className="w-full max-w-md p-6 space-y-5"
        >
          <h2 className="text-xl font-display font-bold text-blue-400">
            Nuevo dispositivo VPN
          </h2>

          {error && (
            <div className="bg-red-500/10 border border-red-500/25 rounded-xl px-4 py-3 text-red-400 text-sm" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <GlassInput
              label="Nombre"
              placeholder="Mi laptop"
              required
              value={name}
              onChange={e => setName(e.target.value)}
              autoFocus
            />

            <div className="space-y-2">
              <button
                type="button"
                onClick={() => setShowPsk(s => !s)}
                className="text-xs text-blue-400/80 hover:text-blue-300 cursor-pointer"
              >
                {showPsk ? '✕ Ocultar clave precompartida' : '+ Añadir clave precompartida (PSK)'}
              </button>
              {showPsk && (
                <GlassInput
                  label="Clave precompartida (PSK)"
                  placeholder="Opcional"
                  type="password"
                  value={psk}
                  onChange={e => setPsk(e.target.value)}
                />
              )}
            </div>

            <AnimatedButton type="submit" variant="primary" className="w-full" disabled={loading}>
              {loading ? <><Spinner size={18} className="mr-2 inline" /> Creando…</> : 'Crear dispositivo'}
            </AnimatedButton>
          </form>
        </GlassCard>
      </motion.div>
    </AnimatePresence>
  );
}
