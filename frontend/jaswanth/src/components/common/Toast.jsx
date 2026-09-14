import React from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';
import { useStore } from '../../context/StoreContext';

export function ToastContainer() {
  const { toasts, removeToast } = useStore();

  if (!toasts || toasts.length === 0) return null;

  const getIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle2 size={18} color="var(--emerald)" />;
      case 'error': return <AlertCircle size={18} color="var(--rose)" />;
      case 'warning': return <AlertTriangle size={18} color="var(--amber)" />;
      default: return <Info size={18} color="var(--cyan)" />;
    }
  };

  return (
    <div className="toast-container" aria-live="polite">
      {toasts.map(toast => (
        <div key={toast.id} className={`toast toast-${toast.type || 'info'}`}>
          <div style={{ flexShrink: 0, marginTop: 2 }}>
            {getIcon(toast.type)}
          </div>
          <div style={{ flex: 1 }}>
            <div className="toast-title">{toast.title}</div>
            {toast.message && <div className="toast-message">{toast.message}</div>}
          </div>
          <button
            type="button"
            onClick={() => removeToast(toast.id)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: 4,
              display: 'flex'
            }}
            aria-label="Close notification"
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}
