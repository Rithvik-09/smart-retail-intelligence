import React, { useState } from 'react';
import { 
  AlertTriangle, 
  AlertCircle, 
  Info, 
  CheckCircle2, 
  Check, 
  Filter 
} from 'lucide-react';
import { useStore } from '../../context/StoreContext';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { EmptyState } from '../common/EmptyState';

export function AlertsPanel({ maxDisplay = 4, showFilters = true }) {
  const { alerts, resolveAlert, executeRecommendation, recommendations } = useStore();
  const [filter, setFilter] = useState('All');

  const getSeverityIcon = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return <AlertCircle size={18} color="var(--rose)" />;
      case 'high':
        return <AlertTriangle size={18} color="var(--rose)" />;
      case 'medium':
        return <AlertTriangle size={18} color="var(--amber)" />;
      default:
        return <Info size={18} color="var(--cyan)" />;
    }
  };

  const getSeverityBg = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'rgba(239, 68, 68, 0.12)';
      case 'medium':
        return 'rgba(245, 158, 11, 0.12)';
      default:
        return 'rgba(6, 182, 212, 0.12)';
    }
  };

  const filteredAlerts = alerts
    .filter(a => !a.resolved)
    .filter(a => filter === 'All' || a.severity.toLowerCase() === filter.toLowerCase());

  const displayedAlerts = maxDisplay ? filteredAlerts.slice(0, maxDisplay) : filteredAlerts;

  const handleAlertAction = (alert) => {
    if (alert.actionKey) {
      const matchRec = recommendations.find(r => r.actionType === alert.actionKey);
      if (matchRec) {
        executeRecommendation(matchRec);
      }
    }
    resolveAlert(alert.id);
  };

  return (
    <div className="card">
      <div className="card-header-row" style={{ flexWrap: 'wrap', gap: 10 }}>
        <div>
          <div className="card-title">
            <AlertTriangle size={18} color="var(--rose)" />
            <span>Store Alerts</span>
          </div>
          <div className="card-subtitle">Immediate operational exceptions</div>
        </div>

        {showFilters && (
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            {['All', 'Critical', 'High', 'Medium'].map(cat => (
              <button
                key={cat}
                type="button"
                onClick={() => setFilter(cat)}
                style={{
                  padding: '3px 8px',
                  borderRadius: 4,
                  fontSize: 11,
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: '1px solid',
                  borderColor: filter === cat ? 'var(--cyan)' : 'var(--border-subtle)',
                  background: filter === cat ? 'var(--cyan-dim)' : 'transparent',
                  color: filter === cat ? 'var(--cyan)' : 'var(--text-muted)'
                }}
              >
                {cat}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="alerts-list" style={{ marginTop: 12 }}>
        {displayedAlerts.length === 0 ? (
          <EmptyState
            icon={CheckCircle2}
            title="No Critical Alerts"
            subtitle="Store operations are currently normal."
          />
        ) : (
          displayedAlerts.map(alt => (
            <div key={alt.id} className={`alert-item severity-${alt.severity.toLowerCase()}`}>
              <div 
                className="alert-icon-box"
                style={{ backgroundColor: getSeverityBg(alt.severity) }}
              >
                {getSeverityIcon(alt.severity)}
              </div>

              <div className="alert-content">
                <div className="alert-title-row">
                  <span className="alert-title">{alt.title}</span>
                  <Badge variant={alt.severity.toLowerCase()}>
                    {alt.severity}
                  </Badge>
                </div>

                <div className="alert-desc">{alt.description}</div>

                <div className="alert-meta">
                  <span>{alt.timestamp} • {alt.category}</span>

                  <div style={{ display: 'flex', gap: 6 }}>
                    {alt.actionLabel && (
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleAlertAction(alt)}
                        style={{ padding: '3px 8px', fontSize: 11 }}
                      >
                        {alt.actionLabel}
                      </Button>
                    )}
                    <Button
                      variant="secondary"
                      size="sm"
                      icon={Check}
                      onClick={() => resolveAlert(alt.id)}
                      style={{ padding: '3px 8px', fontSize: 11 }}
                    >
                      Dismiss
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
