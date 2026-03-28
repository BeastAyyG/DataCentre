import { useEffect, useRef, useState } from 'react';

export type ToastVariant = 'success' | 'error' | 'info';

export interface Toast {
  id: string;
  message: string;
  variant: ToastVariant;
}

let _toasts: Toast[] = [];
const _listeners: ((toasts: Toast[]) => void)[] = [];

function notify() {
  _listeners.forEach((l) => l([..._toasts]));
}

export const toast = {
  show: (message: string, variant: ToastVariant = 'info') => {
    const id = Math.random().toString(36).slice(2);
    _toasts = [..._toasts, { id, message, variant }];
    notify();
    setTimeout(() => {
      _toasts = _toasts.filter((t) => t.id !== id);
      notify();
    }, 4000);
  },
  success: (message: string) => toast.show(message, 'success'),
  error: (message: string) => toast.show(message, 'error'),
  info: (message: string) => toast.show(message, 'info'),
};

export function useToasts() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const ref = useRef((t: Toast[]) => setToasts(t));
  useEffect(() => {
    _listeners.push(ref.current);
    return () => {
      _listeners.splice(_listeners.indexOf(ref.current), 1);
    };
  }, []);
  return toasts;
}
