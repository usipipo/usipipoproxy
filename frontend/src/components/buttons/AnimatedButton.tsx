import type { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface Props {
  children: ReactNode;
  variant?: 'primary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

const sizeClass = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-5 py-2.5 text-base',
  lg: 'px-7 py-3.5 text-lg',
} as const;

const variantClass = {
  primary: 'bg-blue-600 text-white hover:bg-blue-500 shadow-lg',
  ghost:   'bg-transparent border border-blue-500/30 text-blue-400 hover:bg-blue-500/10',
  danger:  'bg-red-600/80 text-white hover:bg-red-500',
} as const;

const buttonHover = {
  scale: 1.03,
  transition: { type: 'spring', stiffness: 400, damping: 25 },
} as const;

export default function AnimatedButton({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  onClick,
  disabled,
  type,
}: Props) {
  return (
    <motion.button
      whileHover={variant === 'danger' ? { scale: 1.02 } : buttonHover}
      whileTap={{ scale: 0.97 }}
      className={`
        rounded-xl font-semibold font-body cursor-pointer
        disabled:opacity-40 disabled:cursor-not-allowed
        transition-colors duration-200
        ${sizeClass[size]} ${variantClass[variant]} ${className}
      `.trim()}
      onClick={onClick}
      disabled={disabled}
      type={type}
    >
      {children}
    </motion.button>
  );
}
