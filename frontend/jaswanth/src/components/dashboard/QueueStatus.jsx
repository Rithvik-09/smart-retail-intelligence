import React from 'react';
import { CreditCard, PlusCircle, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useStore } from '../../context/StoreContext';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

export function QueueStatus() {
  const { checkouts, queueSummary, openCheckoutLane, isLoading, kpis } = useStore();

  const isLane3Closed = checkouts.find(c => c.id === 3)?.status === 'CLOSED';

  return (
    <div className="card">
      {/* Header & Quick Summary */}
      <div className="card-header-row" style={{ flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="card-title">
            <CreditCard size={18} color="var(--cyan)" />
            <span>Checkout Monitoring</span>
          </div>
          <div className="card-subtitle">Front-end register queues and wait times</div>
        </div>

        {/* Action Button */}
        {isLane3Closed && (
          <Button
            variant="primary"
            size="sm"
            icon={PlusCircle}
            onClick={() => openCheckoutLane(3)}
            disabled={isLoading}
          >
            OPEN CHECKOUT
          </Button>
        )}
      </div>

      {/* Summary Banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12,
          padding: '12px 16px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-sm)',
          marginBottom: 16
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <div>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
              Total Queue
            </span>
            <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-white)' }}>
              {kpis.checkoutQueue.value} <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 400 }}>shoppers</span>
            </div>
          </div>

          <div style={{ borderLeft: '1px solid var(--border-subtle)', paddingLeft: 20 }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
              Average Wait
            </span>
            <div style={{ fontSize: 20, fontWeight: 800, color: kpis.checkoutQueue.avgWaitMinutes > 3 ? 'var(--rose)' : 'var(--emerald)' }}>
              {kpis.checkoutQueue.avgWaitMinutes} min
            </div>
          </div>
        </div>

        {isLane3Closed ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--amber)', fontSize: 12, fontWeight: 600 }}>
            <AlertCircle size={15} />
            <span>Recommendation: {queueSummary.recommendation}</span>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--emerald)', fontSize: 12, fontWeight: 600 }}>
            <CheckCircle2 size={15} />
            <span>All 4 Checkout Lanes Active (Optimal Throughput)</span>
          </div>
        )}
      </div>

      {/* 4 Checkout Cards */}
      <div className="checkout-grid">
        {checkouts.map(lane => {
          const isOpen = lane.status === 'OPEN';
          return (
            <div
              key={lane.id}
              className={`checkout-lane-card ${isOpen ? 'open' : 'closed'} ${lane.waitMinutes >= 4 ? 'high-wait' : ''}`}
            >
              <div className="lane-header">
                <span className="lane-name">{lane.name}</span>
                <Badge variant={isOpen ? 'normal' : 'high'}>
                  {lane.status}
                </Badge>
              </div>

              <div className="lane-stat-row">
                <div>
                  <div className="lane-customers">
                    {lane.customers}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    {lane.customers === 1 ? 'customer' : 'customers'}
                  </div>
                </div>

                {isOpen && (
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: 14, fontWeight: 700, color: lane.waitMinutes >= 4 ? 'var(--rose)' : 'var(--text-secondary)' }}>
                      {lane.waitMinutes} min
                    </div>
                    <div className="lane-wait">wait time</div>
                  </div>
                )}
              </div>

              <div className="lane-footer">
                <span>{lane.cashier}</span>
                <span>{lane.efficiency}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
