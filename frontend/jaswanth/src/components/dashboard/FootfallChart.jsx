import React, { useState } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { TrendingUp, Users, Clock, Award } from 'lucide-react';
import { useStore } from '../../context/StoreContext';

export function FootfallChart() {
  const { trafficData, trafficStats, kpis } = useStore();
  const [filter, setFilter] = useState('today');

  // Active chart dataset depending on filter
  const getChartData = () => {
    if (filter === '7days') return trafficData.sevenDays;
    if (filter === '30days') return trafficData.thirtyDays;
    return trafficData.today;
  };

  const chartData = getChartData();

  // Custom tooltips for Recharts
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div
          style={{
            backgroundColor: '#0f172a',
            border: '1px solid #334155',
            borderRadius: 'var(--radius-sm)',
            padding: '10px 14px',
            boxShadow: '0 8px 20px rgba(0,0,0,0.5)',
            fontSize: '12px'
          }}
        >
          <div style={{ color: '#94a3b8', marginBottom: 4, fontWeight: 600 }}>
            {filter === 'today' ? `Hour: ${data.time}` : (filter === '7days' ? data.day : data.week)}
          </div>
          <div style={{ color: '#f8fafc', fontSize: '14px', fontWeight: 800 }}>
            {data.customers || data.footfall} Customers
          </div>
          {data.changePercent && (
            <div style={{ color: data.changePercent.startsWith('+') ? 'var(--emerald)' : 'var(--rose)', marginTop: 2, fontWeight: 700 }}>
              {data.changePercent} vs prior period
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Top Header & Range Filters */}
      <div className="card-header-row" style={{ flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div className="card-title">
            <Users size={18} color="var(--cyan)" />
            <span>Customer Traffic</span>
          </div>
          <div className="card-subtitle">Real-time shopper activity</div>
        </div>

        {/* Filter Tabs */}
        <div
          style={{
            display: 'flex',
            backgroundColor: 'var(--bg-base)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '3px'
          }}
        >
          {['today', '7days', '30days'].map(tab => {
            const labelMap = { today: 'Today', '7days': '7 Days', '30days': '30 Days' };
            const isActive = filter === tab;
            return (
              <button
                key={tab}
                type="button"
                onClick={() => setFilter(tab)}
                style={{
                  background: isActive ? 'var(--bg-surface)' : 'transparent',
                  border: 'none',
                  borderRadius: 'var(--radius-sm)',
                  padding: '5px 12px',
                  color: isActive ? 'var(--text-white)' : 'var(--text-muted)',
                  fontSize: '12px',
                  fontWeight: isActive ? 600 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {labelMap[tab]}
              </button>
            );
          })}
        </div>
      </div>

      {/* Summary Statistics Bar */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 12,
          padding: '12px 16px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-sm)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ padding: 6, borderRadius: 6, background: 'rgba(6,182,212,0.1)' }}>
            <Clock size={16} color="var(--cyan)" />
          </div>
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Current</div>
            <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-white)' }}>
              {kpis.customersNow.value}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ padding: 6, borderRadius: 6, background: 'rgba(245,158,11,0.1)' }}>
            <Award size={16} color="var(--amber)" />
          </div>
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Peak</div>
            <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-white)' }}>
              {trafficStats.peak}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ padding: 6, borderRadius: 6, background: 'rgba(16,185,129,0.1)' }}>
            <TrendingUp size={16} color="var(--emerald)" />
          </div>
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>Average</div>
            <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-white)' }}>
              {trafficStats.average}
            </div>
          </div>
        </div>
      </div>

      {/* Main Recharts Area */}
      <div style={{ width: '100%', height: 260, marginTop: 4 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
          >
            <defs>
              <linearGradient id="trafficGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey={filter === 'today' ? 'time' : (filter === '7days' ? 'day' : 'week')}
              stroke="#64748b"
              fontSize={12}
              tickLine={false}
              axisLine={{ stroke: '#1e293b' }}
            />
            <YAxis
              stroke="#64748b"
              fontSize={12}
              tickLine={false}
              axisLine={{ stroke: '#1e293b' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey={filter === '30days' ? 'footfall' : 'customers'}
              stroke="#06b6d4"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#trafficGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
