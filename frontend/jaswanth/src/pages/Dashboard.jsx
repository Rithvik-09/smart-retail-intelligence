import React from 'react';
import { 
  Users, 
  CreditCard, 
  Package, 
  AlertTriangle, 
  Sparkles, 
  RefreshCw 
} from 'lucide-react';
import { useStore } from '../context/StoreContext';
import { KPICard } from '../components/dashboard/KPICard';
import { FootfallChart } from '../components/dashboard/FootfallChart';
import { OccupancyCard } from '../components/dashboard/OccupancyCard';
import { ZoneCrowding } from '../components/dashboard/ZoneCrowding';
import { QueueStatus } from '../components/dashboard/QueueStatus';
import { InventoryRisk } from '../components/dashboard/InventoryRisk';
import { AlertsPanel } from '../components/dashboard/AlertsPanel';
import { AIRecommendations } from '../components/dashboard/AIRecommendations';
import { PriorityTasks } from '../components/dashboard/PriorityTasks';
import { Skeleton } from '../components/common/Skeleton';

export function Dashboard() {
  const { kpis, isLoading, hasError, setHasError, polling } = useStore();

  // Greeting time logic
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  if (hasError) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '60px 20px', margin: '40px auto', maxWidth: 500 }}>
        <AlertTriangle size={48} color="var(--rose)" style={{ marginBottom: 16 }} />
        <h2 style={{ fontSize: 20, color: 'var(--text-white)', marginBottom: 8 }}>Unable to retrieve store data.</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 20 }}>
          The telemetry connection to the store sensor gateway failed or timed out.
        </p>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => {
            setHasError(false);
            polling.triggerPoll();
          }}
        >
          <RefreshCw size={15} />
          <span>Retry Connection</span>
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Top Greeting & Hero */}
      <div className="dashboard-hero">
        <div>
          <h1 className="greeting-title">{getGreeting()}</h1>
          <p className="greeting-subtitle">
            Here's what's happening in your store right now.
          </p>
        </div>
      </div>

      {/* 4 Primary KPI Cards */}
      <div className="kpi-grid">
        <KPICard
          label={kpis.customersNow.label}
          value={isLoading ? <Skeleton width="80px" height="38px" /> : kpis.customersNow.value}
          subtext={kpis.customersNow.subtext}
          status={kpis.customersNow.status}
          icon={Users}
          variant="cyan"
        />

        <KPICard
          label={kpis.checkoutQueue.label}
          value={isLoading ? <Skeleton width="80px" height="38px" /> : kpis.checkoutQueue.value}
          subtext={kpis.checkoutQueue.subtext}
          status={kpis.checkoutQueue.status}
          icon={CreditCard}
          variant="amber"
        />

        <KPICard
          label={kpis.stockRisks.label}
          value={isLoading ? <Skeleton width="80px" height="38px" /> : kpis.stockRisks.value}
          subtext={kpis.stockRisks.subtext}
          status={kpis.stockRisks.status}
          icon={Package}
          variant="amber"
        />

        <KPICard
          label={kpis.criticalAlerts.label}
          value={isLoading ? <Skeleton width="80px" height="38px" /> : kpis.criticalAlerts.value}
          subtext={kpis.criticalAlerts.subtext}
          status={kpis.criticalAlerts.status}
          icon={AlertTriangle}
          variant="rose"
        />
      </div>

      {/* AI Recommendations Highlight (Crucial Command Center Core) */}
      <AIRecommendations />

      {/* Traffic Chart & Occupancy Radial Gauge */}
      <div className="grid-2col">
        <FootfallChart />
        <OccupancyCard />
      </div>

      {/* Zone Crowding & Checkout Monitoring */}
      <div className="grid-equal">
        <ZoneCrowding />
        <QueueStatus />
      </div>

      {/* Inventory Risks & Operational Task / Alert Grids */}
      <div className="grid-2col">
        <InventoryRisk limit={4} showViewAll={true} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <PriorityTasks limit={3} showViewAll={true} />
          <AlertsPanel maxDisplay={3} showFilters={false} />
        </div>
      </div>
    </div>
  );
}
