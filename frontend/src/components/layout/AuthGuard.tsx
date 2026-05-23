'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import Spinner from '@/components/feedback/Spinner';

interface Props { children: ReactNode }

export default function AuthGuard({ children }: Props) {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [sessionOk, setSessionOk] = useState(false);

  useEffect(() => {
    if (!loading) {
      if (user) {
        setSessionOk(true);
      } else {
        navigate('/login', { replace: true });
      }
    }
  }, [loading, user, navigate]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen" role="status" aria-label="Cargando">
        <Spinner size={40} />
      </div>
    );
  }

  if (!sessionOk) return null;
  return <>{children}</>;
}
