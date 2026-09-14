import React from 'react';
import { Users2, ShieldAlert } from 'lucide-react';
import { useStore } from '../../context/StoreContext';
import { Badge } from '../common/Badge';

export function OccupancyCard() {
  const { occupancy } = useStore();

  const radius = 64;
  const strokeWidth = 12;
  const normalizedRadius = radius - strokeWidth / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  // We can do a 270 degree gauge or 360 circle. 360 circle is very clean:
  const strokeDashoffset = circumference - (occupancy.occupancyPercent / 100) * circumference;

  const getStatusColor = () => {
    if (occupancy.occupancyPercent >= 80) return 'var(--rose)';
    if (occupancy.occupancyPercent >= 60) return 'var(--amber)';
    return 'var(--emerald)';
  };

  const getStatusVariant = () => {
    if (occupancy.occupancyPercent >= 80) return 'critical';
    if (occupancy.occupancyPercent >= 60) return 'busy';
    return 'normal';
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div>
        <div className="card-header-row">
          <div>
            <div className="card-title">
              <Users2 size={18} color="var(--cyan)" />
              <span>Store Occupancy</span>
            </div>
            <div className="card-subtitle">Real-time store density</div>
          </div>
          <Badge variant={getStatusVariant()}>
            {occupancy.status}
          </Badge>
        </div>

        {/* Circular Progress Gauge */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '20px 0' }}>
          <div style={{ position: 'relative', width: radius * 2, height: radius * 2 }}>
            <svg
              height={radius * 2}
              width={radius * 2}
              style={{ transform: 'rotate(-90deg)' }}
            >
              {/* Background Track */}
              <circle
                stroke="rgba(255, 255, 255, 0.08)"
                fill="transparent"
                strokeWidth={strokeWidth}
                r={normalizedRadius}
                cx={radius}
                cy={radius}
              />
              {/* Animated Progress Fill */}
              <circle
                stroke={getStatusColor()}
                fill="transparent"
                strokeWidth={strokeWidth}
                strokeDasharray={circumference + ' ' + circumference}
                style={{
                  strokeDashoffset,
                  transition: 'stroke-dashoffset 0.6s ease, stroke 0.3s ease',
                  strokeLinecap: 'round'
                }}
                r={normalizedRadius}
                cx={radius}
                cy={radius}
              />
            </svg>

            {/* Inner Percentage Center */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <span style={{ fontSize: 26, fontWeight: 800, color: 'var(--text-white)' }}>
                {occupancy.occupancyPercent}%
              </span>
              <span style={{ fontSize: 10, textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                Occupancy
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Metric Breakdown Rows */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 8,
          borderTop: '1px solid var(--border-light)',
          paddingTop: 14,
          textAlign: 'center'
        }}
      >
        <div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>Current</div>
          <div style={{ fontSize: 16, fontWeight: 800, color: 'var(--text-white)', marginTop: 2 }}>
            {occupancy.current}
          </div>
        </div>

        <div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>Capacity</div>
          <div style={{ fontSize: 16, fontWeight: 800, color: 'var(--text-secondary)', marginTop: 2 }}>
            {occupancy.capacity}
          </div>
        </div>

        <div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>Peak</div>
          <div style={{ fontSize: 16, fontWeight: 800, color: 'var(--amber)', marginTop: 2 }}>
            {occupancy.peakToday}
          </div>
        </div>
      </div>

      {/* Threshold Status Guide */}
      <div
        style={{
          marginTop: 12,
          padding: '8px 10px',
          background: 'rgba(255, 255, 255, 0.02)',
          borderRadius: 'var(--radius-sm)',
          fontSize: 11,
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <span>&lt;60% Normal</span>
        <span>•</span>
        <span>60–80% Busy</span>
        <span>•</span>
        <span>&gt;80% Crowded</span>
      </div>
    </div>
  );
}
