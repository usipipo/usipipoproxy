import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'hover-glow' | 'flat';
  as?: 'div' | 'section' | 'article' | 'header' | 'footer' | 'main' | 'aside';
}

const baseClassMap: Record<string, string> = {
  div: 'glass',
  section: 'glass',
  article: 'glass',
  header: 'glass',
  footer: 'glass',
  main: 'glass',
  aside: 'glass',
};

export default function GlassCard({
  children,
  className = '',
  variant = 'default',
  as: Tag = 'div',
}: Props) {
  const base = baseClassMap[Tag] ?? 'glass';
  const variantClass = variant === 'flat' ? '' : 'glass-card';
  return (
    <Tag className={`${base} ${variantClass} ${className}`.trim()}>
      {children}
    </Tag>
  );
}
