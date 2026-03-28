import { useToasts, Toast } from '@/hooks/useToast';

const variantStyles: Record<Toast['variant'], string> = {
  success: 'bg-green-900 border-green-600 text-green-200',
  error: 'bg-red-900 border-red-600 text-red-200',
  info: 'bg-blue-900 border-blue-600 text-blue-200',
};

const variantIcons: Record<Toast['variant'], string> = {
  success: '✓',
  error: '✕',
  info: 'ℹ',
};

function ToastItem({ toast }: { toast: Toast }) {
  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg ${variantStyles[toast.variant]}`}
      role="alert"
    >
      <span className="text-base">{variantIcons[toast.variant]}</span>
      <span>{toast.message}</span>
    </div>
  );
}

export function ToastContainer() {
  const toasts = useToasts();
  if (toasts.length === 0) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 items-end max-w-sm">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} />
      ))}
    </div>
  );
}
