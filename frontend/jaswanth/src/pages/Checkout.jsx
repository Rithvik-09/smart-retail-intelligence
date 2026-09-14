import React from 'react';
import { CreditCard, Users, Clock, Zap, CheckCircle2 } from 'lucide-react';
import { useStore } from '../context/StoreContext';
import { QueueStatus } from '../components/dashboard/QueueStatus';
import { Badge } from '../components/common/Badge';

export function Checkout() {
  const { checkouts, queueSummary, kpis } = useStore();

  const cashierData = [
    { name: 'Sarah M.', lane: 'Checkout 1', itemsPerMin: 22, satisfaction: '97%', status: 'Active' },
    { name: 'David L.', lane: 'Checkout 2', itemsPerMin: 26, satisfaction: '99%', status: 'Active' },
    { name: 'Elena S.', lane: 'Checkout 3', itemsPerMin: 24, satisfaction: '96%', status: checkouts.find(c => c.id === 3)?.status === 'OPEN' ? 'Active' : 'On Break' },
    { name: 'Alex R.', lane: 'Checkout 4', itemsPerMin: 19, satisfaction: '94%', status: 'Active' },
  ];

  return (
    <div className="dashboard-container">
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <CreditCard size={24} color="var(--cyan)" />
          <h1 className="greeting-title" style={{ fontSize: 22 }}>Checkout & Register Telemetry</h1>
        </div>
        <p className="greeting-subtitle">
          Real-time lane throughput, waiting queues, and cashier performance telemetry.
        </p>
      </div>

      {/* Main Queue Status Component */}
      <QueueStatus />

      {/* Cashier Team Productivity Table */}
      <div className="card">
        <div className="card-header-row">
          <div>
            <div className="card-title">
              <Users size={18} color="var(--cyan)" />
              <span>Cashier Productivity Benchmarks</span>
            </div>
            <div className="card-subtitle">Scan speed and customer service rating</div>
          </div>
          <Badge variant="cyan">Vision AI POS</Badge>
        </div>

        <div className="table-container" style={{ marginTop: 12 }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Cashier Name</th>
                <th>Assigned Lane</th>
                <th>Scanning Rate</th>
                <th>Satisfaction Score</th>
                <th>Shift Status</th>
              </tr>
            </thead>
            <tbody>
              {cashierData.map((cashier, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600, color: 'var(--text-white)' }}>
                    {cashier.name}
                  </td>
                  <td>{cashier.lane}</td>
                  <td>
                    <span style={{ fontWeight: 700, color: 'var(--emerald)' }}>
                      {cashier.itemsPerMin}
                    </span> items/min
                  </td>
                  <td>
                    <span style={{ fontWeight: 700, color: 'var(--cyan)' }}>
                      {cashier.satisfaction}
                    </span>
                  </td>
                  <td>
                    <Badge variant={cashier.status === 'Active' ? 'normal' : 'busy'}>
                      {cashier.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
