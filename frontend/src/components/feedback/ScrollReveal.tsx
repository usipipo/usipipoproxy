'use client';
import type { ReactNode } from 'react';
import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

type Direction = 'up' | 'down' | 'left' | 'right';

interface Props {
  children: ReactNode;
  delay?: number;
  direction?: Direction;
  threshold?: number;
}

const hiddenMap: Record<Direction, object> = {
  up:   { opacity: 0, y: 40 },
  down: { opacity: 0, y: -40 },
  left: { opacity: 0, x: -40 },
  right:{ opacity: 0, x: 40 },
};

const ease = [0.22, 1, 0.36, 1] as const;

export default function ScrollReveal({
  children,
  delay = 0,
  direction = 'up',
  threshold = 0.16,
}: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, {
    once: true,
    margin: `-${Math.round(threshold * 100)}%`,
  });

  const animate = inView
    ? { opacity: 1, x: 0, y: 0 }
    : (hiddenMap[direction] ?? hiddenMap.up);

  return (
    <motion.div
      ref={ref}
      initial={hiddenMap[direction]}
      animate={animate}
      transition={{ duration: 0.65, delay, ease }}
    >
      {children}
    </motion.div>
  );
}
