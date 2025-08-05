import { useState, useCallback } from 'react';

interface Toast {
  id: string;
  title?: string;
  description?: string;
  type: 'success' | 'error' | 'warning' | 'info';
}

interface ToastState {
  toasts: Toast[];
}

export function useToast() {
  const [state, setState] = useState<ToastState>({ toasts: [] });

  const toast = useCallback(
    ({ title, description, type = 'info' }: Omit<Toast, 'id'>) => {
      const id = Math.random().toString(36).substr(2, 9);
      const newToast: Toast = { id, title, description, type };

      setState((prevState) => ({
        toasts: [...prevState.toasts, newToast],
      }));

      // Auto remove toast after 5 seconds
      setTimeout(() => {
        setState((prevState) => ({
          toasts: prevState.toasts.filter((t) => t.id !== id),
        }));
      }, 5000);
    },
    []
  );

  const dismissToast = useCallback((id: string) => {
    setState((prevState) => ({
      toasts: prevState.toasts.filter((t) => t.id !== id),
    }));
  }, []);

  return {
    toast,
    dismiss: dismissToast,
    toasts: state.toasts,
  };
}