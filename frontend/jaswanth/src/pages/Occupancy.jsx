import React from 'react';
import { Users2, Maximize2, AlertTriangle, ShieldCheck, MapPin } from 'lucide-react';
import { useStore } from '../context/StoreContext';
import { OccupancyCard } from '../components/dashboard/OccupancyCard';
import { ZoneCrowding } from '../components/dashboard/ZoneCrowding';
import { Badge } from '../components/common/Badge';

export function Occupancy() {
  const { occupancy, zones } = useStore();

  const getHeatmapColor = (percent) => {
    if (percent >= 80) return 'rgba(239, 68, 68, 0.25)';
    if (percent >= 60) return 'rgba(245, 158, 11, 0.25)';
    return 'rgba(16, 185, 129, 0.15)';
  };

  const getHeatmapBorder = (percent) => {
    if (percent >= 80) return 'rgba(239, 68, 68, 0.6)';
    if (percent >= 60) return 'rgba(245, 158, 11, 0.6)';
    return 'rgba(16, 185, 129, 0.4)';
  };

  return (
    <div className="dashboard-container">
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Users2 size={24} color="var(--cyan)" />
          <h1 className="greeting-title" style={{ fontSize: 22 }}>Store Occupancy & Floor Density</h1>
        </div>
        <p className="greeting-subtitle">
          Real-time headcounts, spatial floor heatmaps, and crowd management thresholds.
        </p>
      </div>

      <div className="grid-2col">
        {/* Visual 2D Store Floor Map Representation */}
        <div className="card">
          <div className="card-header-row">
            <div>
              <div className="card-title">
                <MapPin size={18} color="var(--cyan)" />
                <span>Store Floor Spatial Heatmap</span>
              </div>
              <div className="card-subtitle">Live vision sensor density mapping</div>
            </div>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Auto-updating</span>
          </div>

          {/* Interactive Visual Floor Layout Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: 12,
              marginTop: 16,
              background: 'rgba(0,0,0,0.25)',
              padding: 16,
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)'
            }}
          >
            {zones.map(z => (
              <div
                key={z.id}
                style={{
                  backgroundColor: getHeatmapColor(z.percent),
                  border: `1px solid ${getHeatmapBorder(z.percent)}`,
                  borderRadius: 'var(--radius-sm)',
                  padding: '14px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  minHeight: '105px',
                  transition: 'all 0.3s ease'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <span style={{ fontWeight: 700, fontSize: 13, color: 'var(--text-white)' }}>
                    {z.name}
                  </span>
                  <Badge variant={z.status === 'Crowded' ? 'critical' : (z.status === 'Busy' ? 'busy' : 'normal')}>
                    {z.percent}%
                  </Badge>
                </div>

                <div>
                  <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-white)' }}>
                    {z.customers} <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 400 }}>/ {z.capacity}</span>
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-secondary)', marginTop: 2 }}>
                    Cap: {z.capacity} pax max
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div
            style={{
              marginTop: 16,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: 12,
              color: 'var(--text-muted)'
            }}
          >
            <span>Total Surface Area: 18,500 sq ft</span>
            <div style={{ display: 'flex', gap: 14 }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--emerald)' }} />
                Normal (&lt;60%)
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--amber)' }} />
                Busy (60-80%)
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--rose)' }} />
                Crowded (&gt;80%)
              </span>
            </div>
          </div>
        </div>

        {/* Occupancy Radial Gauge Component */}
        <OccupancyCard />
      </div>

      {/* Full Zone Breakdown */}
      <ZoneCrowding />
    </div>
  );
}
