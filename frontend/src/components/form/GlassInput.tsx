'use client';
import type { InputHTMLAttributes } from 'react';

interface Props extends Omit<InputHTMLAttributes<HTMLInputElement>, 'className'> {
  label?: string;
  error?: string;
  className?: string;
}

export default function GlassInput({
  label,
  error,
  className = '',
  id,
  ...rest
}: Props) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-xs font-medium text-slate-400">
          {label}
          {rest.required && <span className="text-red-400 ml-0.5">*</span>}
        </label>
      )}
      <input
        id={inputId}
        className={`
          glass-input text-sm placeholder:text-slate-600
          ${error ? 'border-red-500/50 focus:border-red-500' : ''}
          ${className}
        `.trim()}
        {...rest}
      />
      {error && (
        <span className="text-xs text-red-400" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
