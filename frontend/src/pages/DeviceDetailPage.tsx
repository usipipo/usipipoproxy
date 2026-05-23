'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Copy, Check, ArrowLeft, Download, Smartphone } from 'lucide-react';
import GlassCard from '@/components/glass/GlassCard';
import { devices } from '@/api/client';
import Spinner from '@/components/feedback/Spinner';
import { QRCodeSVG } from 'qrcode.react';
import type { DeviceResponse } from '@/types';

function formatBytes(n: number): string {
  if (n === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(n) / Math.log(1024));
  return `${(n / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

export default function DeviceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const nav = useNavigate();
  const [device, setDevice] = useState<DeviceResponse | null>(null);
  const [conf, setConf] = useState<string | null>(null);
  const [showConf, setShowConf] = useState(false);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');

  // Fetch device from /devices list
  useEffect(() => {
    if (!id) return;
    setLoading(true);
    devices
      .list()
      .then(all => setDevice(all.find(d => d.id === Number(id)) ?? null))
      .catch((e: unknown) => setErr(e instanceof Error ? e.message : 'Error'))
      .finally(() => setLoading(false));
  }, [id]);

  const loadConf = useCallback(async () => {
    if (!id) return;
    try {
      // FetchWireGuard .conf file content
      const raw = await devices.conf(Number(id));
      setConf(raw);
      setShowConf(true);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'No se pudo cargar la configuración';
      setErr(msg);
    }
  }, [id]);

  const copyConf = useCallback(() => {
    if (!conf) return;
    navigator.clipboard.writeText(conf);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [conf]);

  if (loading) return <div className="flex justify-center py-20"><Spinner size={40} /></div>;
  if (err) return <div className="text-red-400 text-center py-20">{err}</div>;
  if (!device) return <div className="text-slate-400 text-center py-20">Dispositivo no encontrado.</div>;

  // WireGuard URI QR encodes the .conf content
  const qrData = conf ?? `wg://${device.public_key}`;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      {/* Back */}
      <button
        onClick={() => nav('/#/dashboard')}
        className="flex items-center gap-2 text-sm text-slate-400 hover:text-blue-400 transition-colors cursor-pointer bg-transparent border-none"
      >
        <ArrowLeft size={14} /> Volver al panel
      </button>

      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
          <Smartphone size={24} className="text-blue-400" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-white">{device.name}</h1>
          <p className="text-slate-500 text-xs mt-0.5">
            {device.enabled ? '● Activo' : '○ Inactivo'} · IP {device.assigned_ip}
          </p>
        </div>
      </div>

      {/* Stats strip */}
      <motion.div
        variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.06 } } }}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        {[
          { label: 'RX', value: formatBytes(device.bytes_rx) },
          { label: 'TX', value: formatBytes(device.bytes_tx) },
          { label: 'Creado', value: new Date(device.created_at).toLocaleDateString('es-CU') },
          { label: 'IP pública', value: device.assigned_ip },
        ].map(s => (
          <GlassCard key={s.label} className="text-center" variant="flat">
            <p className="text-xs text-slate-500 uppercase tracking-widest">{s.label}</p>
            <p className="text-lg font-bold text-white mt-1">{s.value}</p>
          </GlassCard>
        ))}
      </motion.div>

      {/* Action buttons */}
      <div className="flex flex-wrap gap-3">
        <AnimatedButton variant="primary" onClick={loadConf}>
          <Download size={16} className="inline mr-2" />
          Descargar .conf
        </AnimatedButton>
        <AnimatedButton
          variant="ghost"
          onClick={async () => {
            if (!id) return;
            await devices.remove(Number(id));
            nav('/#/dashboard');
          }}
        >
          Revocar dispositivo
        </AnimatedButton>
      </div>

      {/* .conf panel */}
      <AnimatePresence>
        {showConf && conf && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <GlassCard className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-display font-semibold text-blue-300 text-sm">
                  Configuración WireGuard
                </h3>
                <button
                  onClick={copyConf}
                  className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 bg-blue-500/10 px-3 py-1.5 rounded-lg cursor-pointer transition-colors"
                >
                  {copied ? <><Check size={13} /> Copiado</> : <><Copy size={13} /> Copiar</>}
                </button>
              </div>

              <pre className="bg-slate-900/80 rounded-xl p-4 text-xs font-mono text-slate-300 overflow-auto max-h-60 custom-scrollbar whitespace-pre">
                {conf}
              </pre>

              {/* QR code */}
              <div className="flex flex-col items-center gap-2 pt-2">
                <p className="text-xs text-slate-500">Escanea para configurar WireGuard</p>
                <div className="p-4 bg-white rounded-xl">
                  <QRCodeSVG value={qrData} size={180} />
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
