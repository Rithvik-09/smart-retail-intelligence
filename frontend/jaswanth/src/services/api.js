import { INITIAL_STORE_DATA } from '../data/mockData';

// Backend Base URL configured via environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Configuration flag: toggle between live Spring Boot backend and simulated mock data
// When false, the client will attempt real HTTP calls to the Spring Boot REST API
let FORCE_MOCK_MODE = false;

export const setMockMode = (enabled) => {
  FORCE_MOCK_MODE = enabled;
};

export const isMockModeActive = () => FORCE_MOCK_MODE;

/**
 * Standard HTTP helper with timeout and fallback support
 */
async function request(endpoint, options = {}) {
  if (FORCE_MOCK_MODE) {
    return null; // Signals fallback to local state/mock
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 4000);

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...(options.headers || {})
      },
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    console.warn(`[API] REST call to ${endpoint} failed or timed out. Falling back to local mock data.`, error.message);
    return null;
  }
}

/**
 * Smart Retail REST API Client
 * Designed for direct Spring Boot integration
 * Architecture: React Frontend -> Spring Boot REST API -> PostgreSQL
 */
export const storeApi = {
  // GET /api/v1/stores/{id}/dashboard/summary
  async getDashboardSummary(storeId = 1) {
    const backendStoreId = storeId === 'store-001' ? 1 : storeId;
    const data = await request(`/api/v1/stores/${backendStoreId}/dashboard/summary`);
    if (data) return { source: 'api', data };

    return {
      source: 'mock',
      data: {
        storeInfo: INITIAL_STORE_DATA.storeInfo,
        kpis: INITIAL_STORE_DATA.kpis,
        occupancy: INITIAL_STORE_DATA.occupancy,
        trafficData: INITIAL_STORE_DATA.trafficData,
        trafficStats: INITIAL_STORE_DATA.trafficStats,
        zones: INITIAL_STORE_DATA.zones,
      }
    };
  },

  // GET /api/v1/ingestion/shopper
async getShopperEvents() {
  const data = await request('/api/v1/ingestion/shopper');

  if (data) {
    return {
      source: 'api',
      data
    };
  }

  return {
    source: 'mock',
    data: []
  };
},

  // GET /api/v1/inventory
  async getInventory() {
    const data = await request('/api/v1/inventory');
    if (data) return { source: 'api', data };

    return {
      source: 'mock',
      data: INITIAL_STORE_DATA.inventoryRisks
    };
  },

  // GET /api/v1/inventory/risks
  async getInventoryRisks() {
    const data = await request('/api/v1/inventory/stockout-risk');
    if (data) return { source: 'api', data };

    return {
      source: 'mock',
      data: INITIAL_STORE_DATA.inventoryRisks.filter(i => i.risk > 30)
    };
  },

    // GET /api/v1/ingestion/inventory-risk
  async getInventoryRiskPredictions() {
  const data = await request(
    '/api/v1/ingestion/inventory-risk'
  );

  if (data) {
    // Keep only the latest risk record for each product
    const latestByProduct = new Map();

    data.forEach(item => {
      latestByProduct.set(item.productId, item);
    });

    return {
      source: 'api',
      data: Array.from(latestByProduct.values())
    };
  }

  return {
    source: 'mock',
    data: []
  };
},

  // GET /api/v1/alerts
  async getAlerts() {
    const data = await request('/api/v1/alerts');
    if (data) return { source: 'api', data };

    return {
      source: 'mock',
      data: INITIAL_STORE_DATA.alerts
    };
  },

  // GET /api/v1/alerts/critical
  async getCriticalAlerts() {
    const data = await request('/api/v1/alerts/critical');
    if (data) return { source: 'api', data };

    return {
      source: 'mock',
      data: INITIAL_STORE_DATA.alerts.filter(a => a.severity === 'Critical')
    };
  },

  // GET /api/v1/stores/{id}/queue/status
  // GET /api/v1/stores/{id}/queue/status
  async getQueueStatus(storeId = 'store-001') {
  const backendStoreId =
    typeof storeId === 'string' && storeId.startsWith('store-')
      ? parseInt(storeId.replace('store-', ''), 10)
      : storeId;

  const data = await request(
    `/api/v1/ingestion/queue/summary?storeId=${backendStoreId}`
  );

  if (data) {
    return {
      source: 'api',
      data: {
        summary: data
      }
    };
  }

  return {
    source: 'mock',
    data: {
      checkouts: INITIAL_STORE_DATA.checkouts,
      summary: INITIAL_STORE_DATA.queueSummary
    }
  };
},

  // POST /api/v1/stores/{id}/queue/{laneId}/open
  async openCheckoutLane(storeId = 'store-001', laneId = 3) {
    const data = await request(`/api/v1/stores/${storeId}/queue/${laneId}/open`, {
      method: 'POST'
    });
    return data || { success: true, laneId, status: 'OPEN' };
  },

  // POST /api/v1/inventory/replenish
  async replenishStock(productId, quantity = 50) {
    const data = await request('/api/v1/inventory/replenish', {
      method: 'POST',
      body: JSON.stringify({ productId, quantity })
    });
    return data || { success: true, productId, quantity, timestamp: new Date().toISOString() };
  },

  // PUT /api/v1/alerts/{id}/resolve
  async resolveAlert(alertId) {
    const data = await request(`/api/v1/alerts/${alertId}/resolve`, {
      method: 'PUT'
    });
    return data || { success: true, alertId, resolved: true };
  },

    // GET /api/v1/recommendations
  async getRecommendations() {
    const data = await request('/api/v1/recommendations');

    if (data) return { source: 'api', data };

    return {
      source: 'mock',
      data: INITIAL_STORE_DATA.aiRecommendations
    };
  },

  async completeRecommendation(id) {
  const data = await request(
    `/api/v1/recommendations/${id}/complete`,
    {
      method: 'PUT'
    }
  );

  return {
    source: 'api',
    data
  };
},
};
