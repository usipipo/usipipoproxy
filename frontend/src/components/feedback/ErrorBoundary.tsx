import type { ReactNode } from 'react';
import { type ReactElement, Component } from 'react';
import AnimatedButton from '../buttons/AnimatedButton.js';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(err: Error): State {
    return { error: err };
  }

  componentDidCatch(_err: Error, _info: unknown) {
    // In production: send to error tracking service
  }

  handleRetry = () => this.setState({ error: null });

  render(): ReactElement {
    if (this.state.error) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen gap-4 px-4">
          <div className="glass rounded-2xl p-8 max-w-md w-full text-center">
            <p className="text-lg font-semibold text-red-400 mb-2">
              Algo salió mal
            </p>
            <p className="text-sm text-slate-400 mb-6">
              {this.state.error.message ??
                'Error inesperado en la aplicación.'}
            </p>
            <AnimatedButton onClick={this.handleRetry} variant="primary">
              Reintentar
            </AnimatedButton>
          </div>
        </div>
      );
    }
    return this.props.children as ReactElement;
  }
}
