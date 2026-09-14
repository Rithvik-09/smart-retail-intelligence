import React from 'react';
import { Layers } from 'lucide-react';
import { useStore } from '../../context/StoreContext';
import { Badge } from '../common/Badge';

export function ZoneCrowding() {
  const { zones } = useStore();

  const getStatusFillClass = (status) => {
    switch (status) {
      case 'Crowded': return 'fill-crowded';
      case 'Busy': return 'fill-busy';
      default: return 'fill-normal';
    }
  };

  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'Crowded': return 'critical';
      case 'Busy': return 'busy';
      default: return 'normal';
    }
  };

  return (
    <div className="card">
      <div className="card-header-row">
        <div>
          <div className="card-title">
            <Layers size={18} color="var(--cyan)" />
            <span>Zone Crowding</span>
          </div>
          <div className="card-subtitle">Real-time floor density by department</div>
        </div>
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          {zones.length} Active Zones
        </span>
      </div>

      <div className="zone-list" style={{ marginTop: 14 }}>
        {zones.map(zone => (
          <div key={zone.id} className="zone-item">
            <div className="zone-item-header">
              <div className="zone-name-group">
                <span>{zone.name}</span>
                {zone.description && (
                  <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 400 }}>
                    ({zone.description})
                  </span>
                )}
              </div>

              <div className="zone-metrics">
                <span style={{ fontWeight: 700, color: 'var(--text-white)' }}>
                  {zone.customers} <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>/ {zone.capacity}</span>
                </span>
                <span style={{ fontWeight: 700, minWidth: 32, textAlign: 'right' }}>
                  {zone.percent}%
                </span>
                <Badge variant={getStatusBadgeVariant(zone.status)}>
                  {zone.status}
                </Badge>
              </div>
            </div>

            <div className="progress-track">
              <div
                className={`progress-fill ${getStatusFillClass(zone.status)}`}
                style={{ width: `${Math.min(100, zone.percent)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
