import React, { useState } from 'react';
import { Package, Search, PlusCircle, RefreshCw, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { useStore } from '../context/StoreContext';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';

export function Inventory() {
  const {
  inventory,
  inventoryRiskPredictions,
  replenishStock,
  isLoading
} = useStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [restockAmount, setRestockAmount] = useState(30);

  const filteredInventory = inventory.filter(item => {
    const matchesSearch = item.product.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All' || item.status.toLowerCase() === statusFilter.toLowerCase();
    return matchesSearch && matchesStatus;
  });

  const getRiskColor = (risk) => {
    if (risk > 80) return 'var(--rose)';
    if (risk > 60) return 'var(--amber)';
    if (risk > 30) return 'var(--cyan)';
    return 'var(--emerald)';
  };

  const handleRestockConfirm = () => {
    if (selectedProduct) {
      replenishStock(selectedProduct.product, Number(restockAmount));
      setSelectedProduct(null);
    }
  };

  return (
    <div className="dashboard-container">
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Package size={24} color="var(--cyan)" />
          <h1 className="greeting-title" style={{ fontSize: 22 }}>Inventory & Predictive Stock Risks</h1>
        </div>
        <p className="greeting-subtitle">
          Computer vision shelf monitoring, demand forecasting, and automated stockout prevention.
        </p>
      </div>

      <div className="card">
        {/* Search & Filter Toolbar */}
        <div className="card-header-row" style={{ flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
          {/* Search Box */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              background: 'var(--bg-base)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '6px 12px',
              minWidth: '260px'
            }}
          >
            <Search size={15} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Search products or categories..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: 'var(--text-primary)',
                fontSize: '13px',
                width: '100%'
              }}
            />
          </div>

          {/* Status Filter Buttons */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {['All', 'Critical', 'High', 'Medium', 'Low'].map(st => (
              <button
                key={st}
                type="button"
                onClick={() => setStatusFilter(st)}
                style={{
                  padding: '5px 12px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: '1px solid',
                  borderColor: statusFilter === st ? 'var(--cyan)' : 'var(--border-subtle)',
                  background: statusFilter === st ? 'var(--cyan-dim)' : 'transparent',
                  color: statusFilter === st ? 'var(--cyan)' : 'var(--text-muted)'
                }}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        {/* Full Inventory Table */}
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Product & SKU</th>
                <th>Category</th>
                <th>Current Stock</th>
                <th>Predicted Demand</th>
                <th>Stockout Risk</th>
                <th>Shelf Life</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Replenish</th>
              </tr>
            </thead>
            <tbody>
              {filteredInventory.map(item => (
                <tr key={item.id}>
                  <td>
                    <div className="product-name-cell">
                      <span className="product-name">{item.product}</span>
                      <span className="product-category">ID: {item.id}</span>
                    </div>
                  </td>
                  <td>{item.category}</td>
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
                      <span style={{ fontWeight: 700, color: getRiskColor(item.risk) }}>
                        {item.risk}%
                      </span>
                    </div>
                  </td>
                  <td style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    {item.shelfLife || '14 days'}
                  </td>
                  <td>
                    <Badge variant={item.status.toLowerCase()}>
                      {item.status}
                    </Badge>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <Button
                      variant="primary"
                      size="sm"
                      icon={PlusCircle}
                      onClick={() => setSelectedProduct(item)}
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

            {/* AI Stock-out Predictions */}
      <div className="card" style={{ marginTop: 20 }}>
        <div className="card-header-row" style={{ marginBottom: 16 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <AlertTriangle size={20} color="var(--amber)" />
              <h2 style={{ fontSize: 17, margin: 0 }}>
                AI Stock-out Predictions
              </h2>
            </div>

            <p
              style={{
                fontSize: 12,
                color: 'var(--text-muted)',
                marginTop: 5
              }}
            >
              Machine learning predictions from the inventory risk engine.
            </p>
          </div>

          <Badge variant="high">
            ML POWERED
          </Badge>
        </div>

        {inventoryRiskPredictions?.length > 0 ? (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Product ID</th>
                  <th>Stock-out Probability</th>
                  <th>Risk Level</th>
                  <th>Anomaly</th>
                  <th>Recommended Action</th>
                </tr>
              </thead>

              <tbody>
                {inventoryRiskPredictions.map(prediction => {
                  const probability =
                    Math.round(
                      (prediction.stockoutProbability ?? 0) * 100
                    );

                  return (
                    <tr key={prediction.id}>
                      <td>
                        <span style={{ fontWeight: 700 }}>
                          {prediction.productId}
                        </span>
                      </td>

                      <td>
                        <div className="risk-bar-container">
                          <div className="risk-bar-track">
                            <div
                              style={{
                                height: '100%',
                                width: `${probability}%`,
                                backgroundColor: getRiskColor(probability),
                                borderRadius: 'var(--radius-full)'
                              }}
                            />
                          </div>

                          <span
                            style={{
                              fontWeight: 700,
                              color: getRiskColor(probability)
                            }}
                          >
                            {probability}%
                          </span>
                        </div>
                      </td>

                      <td>
                        <Badge
                          variant={
                            prediction.riskLevel?.toLowerCase() || 'medium'
                          }
                        >
                          {prediction.riskLevel}
                        </Badge>
                      </td>

                      <td>
                        {prediction.anomaly ? (
                          <span
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: 5,
                              color: 'var(--rose)',
                              fontWeight: 700,
                              fontSize: 12
                            }}
                          >
                            <AlertTriangle size={14} />
                            YES
                          </span>
                        ) : (
                          <span
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: 5,
                              color: 'var(--emerald)',
                              fontWeight: 700,
                              fontSize: 12
                            }}
                          >
                            <CheckCircle2 size={14} />
                            NO
                          </span>
                        )}
                      </td>

                      <td>
                        <span
                          style={{
                            fontWeight: 700,
                            color: 'var(--cyan)'
                          }}
                        >
                          {prediction.recommendedAction}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div
            style={{
              padding: 24,
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: 13
            }}
          >
            No ML inventory predictions available.
          </div>
        )}
      </div> it shutme to start

      {/* Restock Order Dispatch Modal */}
      {selectedProduct && (
        <Modal
          isOpen={Boolean(selectedProduct)}
          onClose={() => setSelectedProduct(null)}
          title={`Restock: ${selectedProduct.product}`}
          footer={
            <>
              <Button variant="secondary" onClick={() => setSelectedProduct(null)}>
                Cancel
              </Button>
              <Button variant="primary" onClick={handleRestockConfirm}>
                Confirm Dispatch
              </Button>
            </>
          }
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Dispatch an immediate stock transfer from the warehouse storage cooler to the sales floor shelf.
            </p>

            <div style={{ padding: 12, background: 'rgba(255,255,255,0.02)', borderRadius: 6, border: '1px solid var(--border-light)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 6 }}>
                <span style={{ color: 'var(--text-muted)' }}>Current Shelf Units:</span>
                <span style={{ fontWeight: 700 }}>{selectedProduct.currentStock}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 6 }}>
                <span style={{ color: 'var(--text-muted)' }}>Predicted Peak Demand:</span>
                <span style={{ fontWeight: 700 }}>{selectedProduct.predictedDemand}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                <span style={{ color: 'var(--text-muted)' }}>Predicted Stockout Risk:</span>
                <span style={{ fontWeight: 700, color: getRiskColor(selectedProduct.risk) }}>
                  {selectedProduct.risk}%
                </span>
              </div>
            </div>

            <div>
              <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                Units to Restock:
              </label>
              <input
                type="number"
                min="10"
                max="150"
                value={restockAmount}
                onChange={(e) => setRestockAmount(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  backgroundColor: 'var(--bg-base)',
                  border: '1px solid var(--border-medium)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-white)',
                  fontSize: '14px',
                  fontWeight: 600
                }}
              />
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
