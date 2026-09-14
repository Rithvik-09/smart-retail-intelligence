import React, { useState } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';
import { BarChart3, TrendingUp, Clock, Users, ArrowUpRight, Calendar } from 'lucide-react';
import { useStore } from '../context/StoreContext';
import { FootfallChart } from '../components/dashboard/FootfallChart';
import { Badge } from '../components/common/Badge';

export function Analytics() {
  const { trafficData } = useStore();

  const dwellTimeData = [
    { zone: 'Entrance', avgMinutes: 3.2, visitors: 240 },
    { zone: 'Produce / Fresh', avgMinutes: 8.5, visitors: 310 },
    { zone: 'Dairy & Coolers', avgMinutes: 6.8, visitors: 345 },
    { zone: 'Bakery', avgMinutes: 4.2, visitors: 190 },
    { zone: 'Pantry & Snacks', avgMinutes: 7.1, visitors: 280 },
    { zone: 'Checkout', avgMinutes: 3.0, visitors: 380 },
  ];

  return (
    <div className="dashboard-container">
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <BarChart3 size={24} color="var(--cyan)" />
          <h1 className="greeting-title" style={{ fontSize: 22 }}>Footfall & Shopper Analytics</h1>
        </div>
        <p className="greeting-subtitle">
          Comprehensive customer behavior trends, dwell times, and hourly volume distributions.
        </p>
      </div>

      {/* Primary Traffic Explorer */}
      <FootfallChart />

      {/* 2-Column Analytics Deep Dive */}
      <div className="grid-equal">
        {/* Dwell Time by Department */}
        <div className="card">
          <div className="card-header-row">
            <div>
              <div className="card-title">
                <Clock size={18} color="var(--cyan)" />
                <span>Average Dwell Time by Zone</span>
              </div>
              <div className="card-subtitle">Minutes shoppers spend in each section</div>
            </div>
            <Badge variant="cyan">Vision AI</Badge>
          </div>

          <div style={{ width: '100%', height: 260, marginTop: 12 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dwellTimeData} layout="vertical" margin={{ top: 5, right: 20, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" fontSize={11} unit=" min" />
                <YAxis dataKey="zone" type="category" stroke="#94a3b8" fontSize={12} width={110} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 6 }}
                  formatter={(val) => [`${val} minutes`, 'Avg Dwell']}
                />
                <Bar dataKey="avgMinutes" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 7-Day Footfall Comparison */}
        <div className="card">
          <div className="card-header-row">
            <div>
              <div className="card-title">
                <TrendingUp size={18} color="var(--emerald)" />
                <span>7-Day Volume Trajectory</span>
              </div>
              <div className="card-subtitle">Daily peak vs average checkout wait</div>
            </div>
            <Badge variant="normal">Optimal Flow</Badge>
          </div>

          <div style={{ width: '100%', height: 260, marginTop: 12 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trafficData.sevenDays} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: 6 }}
                />
                <Line type="monotone" dataKey="customers" stroke="#10b981" strokeWidth={2.5} dot={{ r: 4 }} name="Total Visitors" />
                <Line type="monotone" dataKey="peak" stroke="#f59e0b" strokeWidth={2} strokeDasharray="4 4" dot={{ r: 3 }} name="Peak Capacity" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
