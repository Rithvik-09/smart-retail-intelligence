import React from 'react';

export function Badge({ children, variant = 'normal', icon: Icon, className = '' }) {
  const getVariantClass = () => {
    switch (variant.toLowerCase()) {
      case 'live':
        return 'badge-live';
      case 'busy':
        return 'badge-busy';
      case 'attention':
        return 'badge-attention';
      case 'critical':
        return 'badge-critical';
      case 'high':
        return 'badge-high';
      case 'medium':
        return 'badge-medium';
      case 'low':
      case 'normal':
        return 'badge-normal';
      case 'cyan':
        return 'badge-cyan';
      default:
        return 'badge-normal';
    }
  };

  return (
    <span className={`badge ${getVariantClass()} ${className}`}>
      {Icon && <Icon size={12} strokeWidth={2.5} />}
      {children}
    </span>
  );
}
