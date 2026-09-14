import React from 'react';
import { Link } from 'react-router-dom';
import { Package, ArrowRight, RefreshCw } from 'lucide-react';
import { useStore } from '../../context/StoreContext';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

export function InventoryRisk({ limit = 5, showViewAll = true }) {
  const { inventory, replenishStock, isLoading } = useStore();

  const getRiskColor = (risk) => {
    if (risk > 80) return 'var(--rose)';
    if (risk > 60) return 'var(--amber)';
    if (risk > 30) return 'var(--cyan)';
    return 'var(--emerald)';
  };

  const getRiskStatusVariant = (status) => {
    switch (status.toLowerCase()) {
      case 'critical': return 'critical';
      case 'high': return 'high';
      case 'medium': return 'medium';
      case 'low': return 'low';
      default: return 'normal';
    }
  };

  const displayedItems = limit ? inventory.slice(0, limit) : inventory;

  return (
    <div className="card">
      <div className="card-header-row">
        <div>
          <div className="card-title">
            <Package size={18} color="var(--cyan)" />
            <span>Inventory Risk</span>
          </div>
          <div className="card-subtitle">AI-predicted stock-out vulnerabilities</div>
        </div>

        {showViewAll && (
          <Link
            to="/inventory"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              fontSize: 12,
              fontWeight: 600,
              color: 'var(--cyan)',
              textDecoration: 'none'
            }}
          >
            <span>View All Inventory</span>
            <ArrowRight size={14} />
          </Link>
        )}
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Current Stock</th>
              <th>Predicted Demand</th>
              <th>Stockout Risk</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {displayedItems.map(item => (
              <tr key={item.id}>
                <td>
                  <div className="product-name-cell">
                    <span className="product-name">{item.product}</span>
                    <span className="product-category">{item.category}</span>
                  </div>
                </td>
                <td>
                  <span style={{ fontWeight: 700, fontSize: 14 }}>{item.currentStock}</span>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}> units</span>
                </td>
                <td>
                  <span style={{ fontWeight: 700, fontSize: 14 }}>{item.predictedDemand}</span>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}> units</span>
                </td>
                <td>
                  <div className="risk-bar-container">
                    <div className="risk-bar-track">
                      <div
                        style={{
                          height: '100%',
                          width: `${item.risk}%`,
                          backgroundColor: getRiskColor(item.risk),
                          borderRadius: 'var(--radius-full)'
                        }}
                      />
                    </div>
                    <span style={{ fontWeight: 700, color: getRiskColor(item.risk), minWidth: 32 }}>
                      {item.risk}%
                    </span>
                  </div>
                </td>
                <td>
                  <Badge variant={getRiskStatusVariant(item.status)}>
                    {item.status}
                  </Badge>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <Button
                    variant="secondary"
                    size="sm"
                    icon={RefreshCw}
                    onClick={() => replenishStock(item.product, 35)}
                    disabled={isLoading}
                  >
                    Restock
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
