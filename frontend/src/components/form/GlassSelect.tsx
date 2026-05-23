'use client';
import type { SelectHTMLAttributes, ReactNode } from 'react';

interface Props extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'className'> {
  label?: string;
  error?: string;
  className?: string;
  children: ReactNode;
}

export default function GlassSelect({
  label,
  error,
  className = '',
  children,
  id,
  ...rest
}: Props) {
  const selectId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={selectId} className="text-xs font-medium text-slate-400">
          {label}
          {rest.required && <span className="text-red-400 ml-0.5">*</span>}
        </label>
      )}
      <select
        id={selectId}
        className={`glass-select text-sm ${error ? 'border-red-500/50 focus:border-red-500' : ''} ${className}`.trim()}
        {...rest}
      >
        {children}
      </select>
      {error && (
        <span className="text-xs text-red-400" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
