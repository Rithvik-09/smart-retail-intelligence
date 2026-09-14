import React from 'react';
import { Sparkles } from 'lucide-react';

export function EmptyState({ icon: Icon = Sparkles, title, subtitle, action }) {
  return (
    <div className="empty-state">
      <Icon className="empty-icon" />
      <div className="empty-title">{title}</div>
      {subtitle && <div className="empty-subtitle">{subtitle}</div>}
      {action && <div style={{ marginTop: 14 }}>{action}</div>}
    </div>
  );
}
