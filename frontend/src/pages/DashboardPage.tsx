'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { LayoutDashboard, Smartphone, ArrowDownToLine, ArrowUpFromLine, Plus } from 'lucide-react';
import GlassCard from '@/components/glass/GlassCard';
import { devices } from '@/api/client';
import Spinner from '@/components/feedback/Spinner';
import type { DeviceResponse } from '@/types';

const stagger = {
  visible: { transition: { staggerChildren: 0.08 } },
};

const cardUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } },
};

function TrafficStat({ label, value, icon, color }: { label: string; value: string; icon: React.ReactNode; color: string }) {
  return (
    <motion.div variants={cardUp} className="glass-card flex items-center gap-4">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`}>
        {icon}
      </div>
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-widest">{label}</p>
        <p className="text-xl font-bold text-white mt-0.5">{value}</p>
      </div>
    </motion.div>
  );
}

function formatBytes(n: number): string {
  if (n === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(n) / Math.log(1024));
  return `${(n / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
}

export default function DashboardPage() {
  const [devicesList, setDevicesList] = useState<DeviceResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState('');
  const [createOpen, setCreateOpen] = useState(false);

  const fetchDevices = useCallback(async () => {
    try {
      const data = await devices.list();
      setDevicesList(data);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Error cargando dispositivos';
      setErr(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchDevices(); }, [fetchDevices]);

  useEffect(() => {
    if (devicesList.length === 0) return;
    const id = setInterval(fetchDevices, 30_000);
    return () => clearInterval(id);
  }, [devicesList.length, fetchDevices]);

  const totalRx = devicesList.reduce((s, d) => s + d.bytes_rx, 0);
  const totalTx = devicesList.reduce((s, d) => s + d.bytes_tx, 0);

  async function handleDelete(id: number, name: string) {
    if (!confirm(`¿Eliminar "${name}"? Esta acción no se puede deshacer.`)) return;
    setDevicesList(prev => prev.filter(d => d.id !== id));
    try {
      await devices.remove(id);
    } catch {
      fetchDevices();
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Spinner size={40} />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-blue-400">Panel</h1>
          <p className="text-slate-500 text-sm mt-1">Gestiona tus dispositivos VPN</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => setCreateOpen(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-xl font-semibold text-sm shadow-lg cursor-pointer hover:bg-blue-500 transition-colors"
        >
          <Plus size={18} /> Nuevo dispositivo
        </motion.button>
      </div>

      {/* Error banner */}
      {err && (
        <div className="bg-red-500/10 border border-red-500/25 rounded-xl px-4 py-3 text-red-400 text-sm">
          {err}
        </div>
      )}

      {/* Summary cards */}
      <motion.div variants={stagger} initial="hidden" animate="visible" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <TrafficStat label="Dispositivos" value={`${devicesList.length}`} icon={<Smartphone size={18} className="text-blue-400" />} color="bg-blue-500/10" />
        <TrafficStat label="Total RX" value={formatBytes(totalRx)} icon={<ArrowDownToLine size={18} className="text-cyan-400" />} color="bg-cyan-500/10" />
        <TrafficStat label="Total TX" value={formatBytes(totalTx)} icon={<ArrowUpFromLine size={18} className="text-emerald-400" />} color="bg-emerald-500/10" />
        <TrafficStat label="Estado" value={devicesList.length > 0 ? 'Activo' : 'Inactivo'} icon={<LayoutDashboard size={18} className="text-slate-400" />} color="bg-slate-500/10" />
      </motion.div>

      {/* Device table */}
      <GlassCard variant="hover-glow" className="overflow-hidden">
        <table className="w-full text-sm" role="table" aria-label="Mis dispositivos">
          <thead>
            <tr className="border-b border-blue-500/10">
              <th className="text-left p-4 text-slate-400 font-medium">Nombre</th>
              <th className="text-left p-4 text-slate-400 font-medium">IP</th>
              <th className="text-right p-4 text-slate-400 font-medium">RX</th>
              <th className="text-right p-4 text-slate-400 font-medium">TX</th>
              <th className="text-right p-4 text-slate-400 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {devicesList.length === 0 ? (
              <tr>
                <td colSpan={5} className="p-8 text-center text-slate-500">
                  No hay dispositivos.{' '}
                  <button onClick={() => setCreateOpen(true)} className="text-blue-400 hover:underline cursor-pointer">
                    Crear uno ahora
                  </button>
                </td>
              </tr>
            ) : (
              devicesList.map((d) => (
                <tr key={d.id} className="border-b border-blue-500/5 hover:bg-blue-500/5 transition-colors">
                  <td className="p-4 text-white font-medium">{d.name}</td>
                  <td className="p-4 text-slate-400 font-mono text-xs">{d.assigned_ip}</td>
                  <td className="p-4 text-right text-slate-400 text-xs">{formatBytes(d.bytes_rx)}</td>
                  <td className="p-4 text-right text-slate-400 text-xs">{formatBytes(d.bytes_tx)}</td>
                  <td className="p-4 text-right flex items-center justify-end gap-2">
                    <a
                      href={`${import.meta.env.VITE_API_BASE ?? '/proxy'}/devices/${d.id}/conf`}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-500/10 text-blue-300 hover:bg-blue-500/20 transition-colors cursor-pointer"
                      title="Descargar .conf"
                    >
                      <ArrowDownToLine size={13} /> .conf
                    </a>
                    <button
                      onClick={() => handleDelete(d.id, d.name)}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors cursor-pointer"
                      title="Eliminar"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </GlassCard>

      {/* Create Device Modal */}
      {createOpen && (
        <CreateDeviceModal
          onClose={() => setCreateOpen(false)}
          onCreated={() => { setCreateOpen(false); fetchDevices(); }}
        />
      )}
    </motion.div>
  );
}
