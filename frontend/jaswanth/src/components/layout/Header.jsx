import React, { useState } from 'react';
import { 
  Bell, 
  RotateCw, 
  ChevronDown, 
  Menu, 
  Zap, 
  Radio, 
  Check, 
  Store
} from 'lucide-react';
import { useStore } from '../../context/StoreContext';

export function Header({ onMenuToggle }) {
  const { 
    currentStore, 
    switchStore, 
    availableStores, 
    polling, 
    alerts, 
    isSimulatingSpike, 
    toggleSpikeSimulation 
  } = useStore();

  const [isStoreDropdownOpen, setIsStoreDropdownOpen] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);

  const unreadAlerts = alerts.filter(a => !a.resolved);

  return (
    <header className="top-header">
      {/* Left Section */}
      <div className="header-left">
        <button
          type="button"
          className="action-icon-btn mobile-menu-btn"
          style={{ display: 'none' }}
          onClick={onMenuToggle}
          aria-label="Toggle navigation"
        >
          <Menu size={18} />
        </button>

        <div className="header-title-wrapper">
          <div className="header-title">
            <Radio size={16} color="var(--cyan)" />
            <span>Store Intelligence</span>
          </div>
          <span className="header-subtitle">
            Autonomous Vision & Inventory Neural Grid
          </span>
        </div>
      </div>

      {/* Center Section: Store Selector & Live Indicators */}
      <div className="header-center">
        {/* Store Selector Dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            type="button"
            className="store-selector"
            onClick={() => setIsStoreDropdownOpen(prev => !prev)}
          >
            <Store size={15} color="var(--cyan)" />
            <span>{currentStore.code}</span>
            <ChevronDown size={14} style={{ color: 'var(--text-muted)' }} />
          </button>

          {isStoreDropdownOpen && (
            <div
              style={{
                position: 'absolute',
                top: 'calc(100% + 6px)',
                left: 0,
                width: '260px',
                backgroundColor: '#0f172a',
                border: '1px solid #334155',
                borderRadius: 'var(--radius-sm)',
                boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
                zIndex: 60,
                padding: '6px'
              }}
            >
              <div style={{ fontSize: 10, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', padding: '6px 10px' }}>
                Select Store Location
              </div>
              {availableStores.map(st => (
                <button
                  key={st.id}
                  type="button"
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: 4,
                    background: currentStore.id === st.id ? 'rgba(6,182,212,0.1)' : 'transparent',
                    border: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    color: currentStore.id === st.id ? 'var(--cyan)' : 'var(--text-primary)',
                    textAlign: 'left'
                  }}
                  onClick={() => {
                    switchStore(st.id);
                    setIsStoreDropdownOpen(false);
                  }}
                >
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600 }}>{st.code}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{st.name}</div>
                  </div>
                  {currentStore.id === st.id && <Check size={14} color="var(--cyan)" />}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Live Pulse Badge */}
        <div className="live-badge-group">
          <div className="live-indicator">
            <div className="pulse-dot" />
            <span>LIVE</span>
          </div>
          <span style={{ color: 'rgba(255,255,255,0.2)' }}>|</span>
          <span className="updated-time">{polling.lastUpdatedText}</span>
        </div>

        {/* Manual Refresh / Heartbeat Trigger */}
        <button
          type="button"
          className="action-icon-btn"
          title="Force Telemetry Sync"
          onClick={() => polling.triggerPoll()}
          style={{ width: 34, height: 34 }}
        >
          <RotateCw size={14} />
        </button>

        {/* Hackathon Spike Simulator Button */}
        <button
          type="button"
          className={`btn btn-sm ${isSimulatingSpike ? 'btn-danger' : 'btn-secondary'}`}
          onClick={toggleSpikeSimulation}
          title="Simulate sudden store surge for hackathon demo"
          style={{ fontSize: 11, padding: '5px 10px' }}
        >
          <Zap size={13} color={isSimulatingSpike ? '#ffffff' : '#f59e0b'} />
          <span>{isSimulatingSpike ? 'Reset Traffic' : 'Simulate Surge'}</span>
        </button>
      </div>

      {/* Right Section: Notifications & Manager Profile */}
      <div className="header-right">
        {/* Notification Bell with Dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            type="button"
            className="action-icon-btn"
            onClick={() => setIsNotificationOpen(prev => !prev)}
            aria-label="View notifications"
          >
            <Bell size={17} />
            {unreadAlerts.length > 0 && <span className="notification-badge-dot" />}
          </button>

          {isNotificationOpen && (
            <div
              style={{
                position: 'absolute',
                top: 'calc(100% + 8px)',
                right: 0,
                width: '320px',
                backgroundColor: '#0f172a',
                border: '1px solid #334155',
                borderRadius: 'var(--radius-sm)',
                boxShadow: '0 12px 30px rgba(0,0,0,0.6)',
                zIndex: 60,
                overflow: 'hidden'
              }}
            >
              <div
                style={{
                  padding: '12px 16px',
                  borderBottom: '1px solid #1e293b',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <span style={{ fontSize: 13, fontWeight: 700, color: '#f8fafc' }}>
                  Live Store Alerts
                </span>
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    backgroundColor: 'rgba(239,68,68,0.2)',
                    color: 'var(--rose)',
                    padding: '2px 6px',
                    borderRadius: 4
                  }}
                >
                  {unreadAlerts.length} Active
                </span>
              </div>

              <div style={{ maxHeight: '280px', overflowY: 'auto' }}>
                {unreadAlerts.length === 0 ? (
                  <div style={{ padding: '20px', textAlign: 'center', fontSize: 12, color: 'var(--text-muted)' }}>
                    No active notifications
                  </div>
                ) : (
                  unreadAlerts.map(alt => (
                    <div
                      key={alt.id}
                      style={{
                        padding: '10px 14px',
                        borderBottom: '1px solid rgba(255,255,255,0.05)',
                        fontSize: 12
                      }}
                    >
                      <div style={{ fontWeight: 600, color: '#f1f5f9' }}>{alt.title}</div>
                      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{alt.timestamp}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Manager Profile Pill */}
        <div className="profile-pill">
          <div className="profile-avatar">AR</div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span className="profile-name">Alex Rivera</span>
            <span className="profile-role">Store Manager</span>
          </div>
        </div>
      </div>
    </header>
  );
}
