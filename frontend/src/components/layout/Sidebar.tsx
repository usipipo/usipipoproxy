'use client';
import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { NavLink } from 'react-router-dom';

import { LayoutDashboard, Smartphone, CreditCard, LogOut } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Panel',      href: '#/dashboard',   icon: 'LayoutDashboard' },
  { label: 'Dispositivos', href: '#/devices',   icon: 'Smartphone'      },
  { label: 'Pagos',      href: '#/payments',    icon: 'CreditCard'      },
] as const;

const iconMap: Record<string, ReactNode> = {
  LayoutDashboard: <LayoutDashboard size={18} />,
  Smartphone:      <Smartphone size={18} />,
  CreditCard:      <CreditCard size={18} />,
};

export default function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -60, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="fixed left-0 top-0 h-full w-60 glass border-r border-blue-500/10 z-40 flex flex-col p-6"
    >
      {/* Logo */}
      <div className="text-2xl font-bold font-display text-blue-400 mb-10 tracking-tight select-none">
        uSipipo
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1 flex-1" aria-label="Navegación principal">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            end={item.href === '#/dashboard'}
            className={({ isActive }) => `
              flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium
              transition-all duration-200
              ${isActive
                ? 'bg-blue-600/20 text-blue-300 border border-blue-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-blue-500/5'}
            `}
          >
            <span className="opacity-70">{iconMap[item.icon]}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Version footer */}
      <div className="mt-auto pt-6 border-t border-blue-500/10">
        <span className="text-xs text-slate-500 select-none">
          uSipipo Proxy v1.0.0
        </span>
      </div>
    </motion.aside>
  );
}
