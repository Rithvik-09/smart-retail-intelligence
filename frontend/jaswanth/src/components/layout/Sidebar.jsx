import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  BarChart3,
  Users,
  CreditCard,
  Package,
  AlertTriangle,
  Sparkles,
  CheckSquare,
  Settings,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { useStore } from '../../context/StoreContext';

export function Sidebar({ mobileOpen, setMobileOpen }) {
  const { alerts, tasks, recommendations } = useStore();

  const activeAlertsCount = alerts.filter(a => !a.resolved).length;
  const pendingTasksCount = tasks.filter(t => !t.completed).length;

  const navItems = [
    {
      to: '/dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
    },
    {
      to: '/analytics',
      label: 'Analytics',
      icon: BarChart3,
    },
    {
      to: '/occupancy',
      label: 'Occupancy',
      icon: Users,
    },
    {
      to: '/checkout',
      label: 'Checkout',
      icon: CreditCard,
    },
    {
      to: '/inventory',
      label: 'Inventory',
      icon: Package,
    },
    {
      to: '/alerts',
      label: 'Alerts',
      icon: AlertTriangle,
      badge: activeAlertsCount > 0 ? activeAlertsCount : null,
      badgeVariant: 'critical'
    },
    {
      to: '/recommendations',
      label: 'AI Recommendations',
      icon: Sparkles,
      badge: recommendations.length > 0 ? recommendations.length : null,
      badgeVariant: 'cyan'
    },
    {
      to: '/tasks',
      label: 'Priority Tasks',
      icon: CheckSquare,
      badge: pendingTasksCount > 0 ? pendingTasksCount : null,
      badgeVariant: 'busy'
    },
  ];

  return (
    <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
      {/* Sidebar Header / Logo */}
      <div className="sidebar-header">
        <div className="brand-icon">
          <Cpu size={22} strokeWidth={2.2} />
        </div>
        <div className="brand-info">
          <div className="brand-title">Smart Retail</div>
          <div className="brand-subtitle">
            <span>Intelligence</span>
            <span style={{ fontSize: 9, padding: '1px 5px', background: 'rgba(6,182,212,0.2)', borderRadius: 4, color: '#06b6d4' }}>AI v2.4</span>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="sidebar-nav">
        <div className="nav-category">Command Center</div>
        {navItems.map(item => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setMobileOpen && setMobileOpen(false)}
            >
              <div className="nav-item-content">
                <Icon size={18} />
                <span>{item.label}</span>
              </div>
              {item.badge !== null && item.badge !== undefined && (
                <span
                  className="nav-badge"
                  style={{
                    backgroundColor:
                      item.badgeVariant === 'critical'
                        ? 'rgba(239, 68, 68, 0.2)'
                        : item.badgeVariant === 'cyan'
                        ? 'rgba(6, 182, 212, 0.2)'
                        : 'rgba(245, 158, 11, 0.2)',
                    color:
                      item.badgeVariant === 'critical'
                        ? 'var(--rose)'
                        : item.badgeVariant === 'cyan'
                        ? 'var(--cyan)'
                        : 'var(--amber)',
                    border: `1px solid ${
                      item.badgeVariant === 'critical'
                        ? 'rgba(239, 68, 68, 0.4)'
                        : item.badgeVariant === 'cyan'
                        ? 'rgba(6, 182, 212, 0.4)'
                        : 'rgba(245, 158, 11, 0.4)'
                    }`
                  }}
                >
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Sidebar Footer */}
      <div className="sidebar-footer">
        <div className="system-status-indicator">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <ShieldCheck size={16} color="var(--emerald)" />
            <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-secondary)' }}>Model Telemetry</span>
          </div>
          <span style={{ fontSize: 10, color: 'var(--emerald)', fontWeight: 700 }}>HEALTHY</span>
        </div>

        <button
          type="button"
          className="nav-item"
          style={{ width: '100%', background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left' }}
          onClick={() => alert('Store Settings & Hardware Telemetry (Camera & Sensor feeds active)')}
        >
          <div className="nav-item-content">
            <Settings size={18} />
            <span>Settings</span>
          </div>
        </button>
      </div>
    </aside>
  );
}
