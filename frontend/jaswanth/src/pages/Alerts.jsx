import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, History, ShieldAlert } from 'lucide-react';
import { useStore } from '../context/StoreContext';
import { AlertsPanel } from '../components/dashboard/AlertsPanel';
import { Badge } from '../components/common/Badge';

export function Alerts() {
  const { alerts, kpis } = useStore();
  const [tab, setTab] = useState('active');

  const activeAlerts = alerts.filter(a => !a.resolved);
  const resolvedAlerts = alerts.filter(a => a.resolved);

  return (
    <div className="dashboard-container">
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <AlertTriangle size={24} color="var(--rose)" />
          <h1 className="greeting-title" style={{ fontSize: 22 }}>Store Incident & Alert Center</h1>
        </div>
        <p className="greeting-subtitle">
          Critical store exceptions flagged by camera sensors, POS streams, and inventory models.
        </p>
      </div>

      {/* Tab Switcher: Active vs Resolved History */}
      <div style={{ display: 'flex', gap: 10 }}>
        <button
          type="button"
          onClick={() => setTab('active')}
          className={`btn ${tab === 'active' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <ShieldAlert size={15} />
          <span>Active Alerts ({activeAlerts.length})</span>
        </button>

        <button
          type="button"
          onClick={() => setTab('resolved')}
          className={`btn ${tab === 'resolved' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <History size={15} />
          <span>Resolved Audit Log ({resolvedAlerts.length})</span>
        </button>
      </div>

      {tab === 'active' ? (
        <AlertsPanel maxDisplay={null} showFilters={true} />
      ) : (
        <div className="card">
          <div className="card-header-row">
            <div>
              <div className="card-title">
                <CheckCircle2 size={18} color="var(--emerald)" />
                <span>Resolved Incident History</span>
              </div>
              <div className="card-subtitle">Alerts acknowledged and resolved in this shift</div>
            </div>
          </div>

          <div className="alerts-list" style={{ marginTop: 12 }}>
            {resolvedAlerts.length === 0 ? (
              <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No resolved incidents recorded yet during this shift.
              </div>
            ) : (
              resolvedAlerts.map(alt => (
                <div
                  key={alt.id}
                  className="alert-item"
                  style={{ opacity: 0.65, borderLeft: '3px solid var(--emerald)' }}
                >
                  <div className="alert-content">
                    <div className="alert-title-row">
                      <span className="alert-title" style={{ textDecoration: 'line-through' }}>
                        {alt.title}
                      </span>
                      <Badge variant="normal">Resolved</Badge>
                    </div>
                    <div className="alert-desc">{alt.description}</div>
                    <div className="alert-meta">
                      <span>Acknowledged by Store Manager • {alt.timestamp}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
