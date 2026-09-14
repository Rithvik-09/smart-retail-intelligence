import React from 'react';
import { Badge } from '../common/Badge';

export function KPICard({ 
  label, 
  value, 
  subtext, 
  status, 
  icon: Icon, 
  variant = 'cyan',
  trendText,
  onClick
}) {
  const getIconBackground = () => {
    switch (variant) {
      case 'emerald':
        return 'rgba(16, 185, 129, 0.12)';
      case 'amber':
        return 'rgba(245, 158, 11, 0.12)';
      case 'rose':
        return 'rgba(239, 68, 68, 0.12)';
      case 'cyan':
      default:
        return 'rgba(6, 182, 212, 0.12)';
    }
  };

  const getIconColor = () => {
    switch (variant) {
      case 'emerald':
        return 'var(--emerald)';
      case 'amber':
        return 'var(--amber)';
      case 'rose':
        return 'var(--rose)';
      case 'cyan':
      default:
        return 'var(--cyan)';
    }
  };

  return (
    <div 
      className="card kpi-card" 
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <div className="kpi-top">
        <span className="kpi-label">{label}</span>
        <div 
          className="kpi-icon-wrap"
          style={{ backgroundColor: getIconBackground() }}
        >
          {Icon && <Icon size={18} color={getIconColor()} />}
        </div>
      </div>

      <div className="kpi-value">
        {value}
      </div>

      <div className="kpi-footer">
        <span className="kpi-subtext">
          {trendText ? trendText : subtext}
        </span>
        {status && (
          <Badge variant={status}>
            {status}
          </Badge>
        )}
      </div>
    </div>
  );
}
