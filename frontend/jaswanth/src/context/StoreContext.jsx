import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useMemo,
  useEffect
} from 'react';

import { INITIAL_STORE_DATA } from '../data/mockData';
import { usePolling } from '../hooks/usePolling';
import { storeApi } from '../services/api';

const StoreContext = createContext(null);

export function StoreProvider({ children }) {
  const [currentStore, setCurrentStore] = useState(
    INITIAL_STORE_DATA.storeInfo
  );

  const [kpis, setKpis] = useState(INITIAL_STORE_DATA.kpis);

  const [occupancy, setOccupancy] = useState(
    INITIAL_STORE_DATA.occupancy
  );

  const [trafficData, setTrafficData] = useState(
    INITIAL_STORE_DATA.trafficData
  );

  const [zones, setZones] = useState(
    INITIAL_STORE_DATA.zones
  );

  const [shopperEvents, setShopperEvents] = useState([]);

  const [checkouts, setCheckouts] = useState(
    INITIAL_STORE_DATA.checkouts
  );

  const [inventory, setInventory] = useState(
    INITIAL_STORE_DATA.inventoryRisks
  );

  const [inventoryRiskPredictions, setInventoryRiskPredictions] =
    useState([]);

  const [alerts, setAlerts] = useState(
    INITIAL_STORE_DATA.alerts
  );

  const [recommendations, setRecommendations] = useState(
    INITIAL_STORE_DATA.aiRecommendations
  );

  const [tasks, setTasks] = useState(
    INITIAL_STORE_DATA.priorityTasks
  );

  // UI states
  const [toasts, setToasts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isSimulatingSpike, setIsSimulatingSpike] = useState(false);

  const [queueSummary, setQueueSummary] = useState(
    INITIAL_STORE_DATA.queueSummary
  );

  // =========================================================
  // TOAST HELPERS
  // =========================================================

  const addToast = useCallback((toast) => {
    const id =
      Date.now() + Math.random().toString(36).substr(2, 4);

    const newToast = {
      id,
      type: 'info',
      duration: 4000,
      ...toast
    };

    setToasts(prev => [...prev, newToast]);

    setTimeout(() => {
      setToasts(prev =>
        prev.filter(t => t.id !== id)
      );
    }, newToast.duration || 4000);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev =>
      prev.filter(t => t.id !== id)
    );
  }, []);

  // =========================================================
  // DEMO POLLING SIMULATION
  // =========================================================

  const handlePollTick = useCallback(async () => {
    if (hasError) return;

    setKpis(prev => {
      const delta =
        Math.floor(Math.random() * 5) - 2;

      const baseCustomers =
        isSimulatingSpike ? 118 : 87;

      const nextCust = Math.min(
        145,
        Math.max(65, baseCustomers + delta)
      );

      const queueDelta =
        Math.floor(Math.random() * 3) - 1;

      const baseQueue =
        isSimulatingSpike ? 24 : 14;

      const nextQueue = Math.min(
        30,
        Math.max(8, baseQueue + queueDelta)
      );

      return {
        ...prev,

        customersNow: {
          ...prev.customersNow,
          value: nextCust,
          deltaPercent: Math.round(
            ((nextCust - 78) / 78) * 100
          )
        },

        checkoutQueue: {
          ...prev.checkoutQueue,
          value: nextQueue,
          avgWaitMinutes:
            nextQueue > 16
              ? 4
              : nextQueue < 10
                ? 2
                : 3,
          status:
            nextQueue > 16
              ? 'CRITICAL'
              : nextQueue > 12
                ? 'BUSY'
                : 'NORMAL'
        }
      };
    });

    // Demo occupancy simulation
    setOccupancy(prev => {
      const current = isSimulatingSpike
        ? 118
        : 87 + Math.floor(Math.random() * 5) - 2;

      const percent = Math.round(
        (current / prev.capacity) * 100
      );

      let status = 'Normal';

      if (percent >= 80) {
        status = 'Crowded';
      } else if (percent >= 60) {
        status = 'Busy';
      }

      return {
        ...prev,
        current,
        occupancyPercent: percent,
        status
      };
    });

    // Demo zone fluctuation
    setZones(prev =>
      prev.map(zone => {
        const shift =
          Math.floor(Math.random() * 3) - 1;

        const newCust = Math.min(
          zone.capacity,
          Math.max(4, zone.customers + shift)
        );

        const percent = Math.round(
          (newCust / zone.capacity) * 100
        );

        let status = 'Normal';

        if (percent >= 80) {
          status = 'Crowded';
        } else if (percent >= 60) {
          status = 'Busy';
        }

        return {
          ...zone,
          customers: newCust,
          percent,
          status
        };
      })
    );
  }, [hasError, isSimulatingSpike]);

  // =========================================================
  // LOAD REAL DASHBOARD DATA FROM JAVA
  // =========================================================

  const loadDashboardData = useCallback(async () => {
    try {
      const response =
        await storeApi.getDashboardSummary(
          currentStore.id
        );

      const data =
        response?.data ?? response;

      if (!data) {
        return;
      }

      // Update dashboard KPIs
      setKpis(prev => ({
        ...prev,

        customersNow: {
          ...prev.customersNow,
          value: data.currentPeopleCount
        },

        checkoutQueue: {
          ...prev.checkoutQueue,
          value: data.currentQueueLength,

          avgWaitMinutes: Math.round(
            data.averageEstimatedWaitTime ?? 0
          )
        },

        criticalAlerts: {
          ...prev.criticalAlerts,
          value: data.criticalAlerts
        },

        stockRisks: {
          ...prev.stockRisks,
          value: data.stockoutRiskItems
        }
      }));

      // Update queue summary
      setQueueSummary(prev => ({
        ...prev,
        currentQueueLength:
          data.currentQueueLength,

        averageQueueLength:
          data.averageQueueLength,

        currentEstimatedWaitTime:
          data.currentEstimatedWaitTime,

        averageEstimatedWaitTime:
          data.averageEstimatedWaitTime
      }));

    } catch (error) {
      console.error(
        'Failed to load dashboard data:',
        error
      );
    }
  }, [currentStore.id]);

  const polling = usePolling(
    loadDashboardData,
    5000,
    true
  );

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // =========================================================
  // LOAD ALERTS
  // =========================================================

  const loadAlertsData = useCallback(async () => {
    try {
      const response =
        await storeApi.getAlerts();

      const data =
        response?.data ?? response;

      if (!data) {
        return;
      }

      setAlerts(data);

    } catch (error) {
      console.error(
        'Failed to load alerts data:',
        error
      );
    }
  }, []);

  useEffect(() => {
    loadAlertsData();
  }, [loadAlertsData]);

  // =========================================================
  // LOAD RECOMMENDATIONS
  // =========================================================

  const loadRecommendationsData =
    useCallback(async () => {
      try {
        const response =
          await storeApi.getRecommendations();

        const data =
          response?.data ?? response;

        if (!data) {
          return;
        }

        const mappedRecommendations = data
          .filter(item => !item.completed)
          .map(item => ({
            id: item.id,

            title: item.title,

            badge:
              item.category ||
              'AI RECOMMENDATION',

            category:
              item.category ||
              'General',

            confidence:
              item.priority?.toLowerCase() === 'high'
                ? 90
                : 80,

            estimatedImpact:
              item.description ||
              'Recommended action based on current store conditions.',

            reason:
              item.description || '',

            actionType:
              item.actionKey ||
              'RECOMMENDATION',

            buttonText:
              item.actionLabel ||
              'TAKE ACTION',

            aiRationale:
              item.description || '',

            priority:
              item.priority || 'Medium',

            completed:
              item.completed
          }));

        setRecommendations(
          mappedRecommendations
        );

      } catch (error) {
        console.error(
          'Failed to load recommendations data:',
          error
        );
      }
    }, []);

  useEffect(() => {
    loadRecommendationsData();
  }, [loadRecommendationsData]);

  // =========================================================
  // LOAD REAL SHOPPER EVENTS FROM JAVA
  // =========================================================

  const loadShopperData = useCallback(async () => {
    try {
      const response =
        await storeApi.getShopperEvents();

      const data =
        response?.data ?? response;

      if (!data) {
        return;
      }

      setShopperEvents(data);

    } catch (error) {
      console.error(
        'Failed to load shopper events:',
        error
      );
    }
  }, []);

  useEffect(() => {
    loadShopperData();
  }, [loadShopperData]);

  // =========================================================
  // UPDATE ZONES USING REAL CV SHOPPER EVENTS
  // =========================================================
  //
  // IMPORTANT:
  // This useEffect is OUTSIDE loadInventoryData.
  //

  useEffect(() => {
    if (
      !shopperEvents ||
      shopperEvents.length === 0
    ) {
      return;
    }

    const latestByZone = {};

    shopperEvents.forEach(event => {
      if (event.zoneId == null) {
        return;
      }

      const existing =
        latestByZone[event.zoneId];

      if (
        !existing ||
        new Date(event.timestamp) >
          new Date(existing.timestamp)
      ) {
        latestByZone[event.zoneId] = event;
      }
    });

    setZones(prev =>
      prev.map(zone => {

        // CV Zone 1 = Entrance
        if (
          zone.id === 'zone-entrance' &&
          latestByZone[1]
        ) {
          const customers =
            latestByZone[1].peopleCount;

          const percent = Math.round(
            (customers / zone.capacity) * 100
          );

          return {
            ...zone,

            customers,

            percent,

            status:
              percent >= 80
                ? 'Crowded'
                : percent >= 60
                  ? 'Busy'
                  : 'Normal'
          };
        }

        return zone;
      })
    );

  }, [shopperEvents]);

  // =========================================================
  // LOAD INVENTORY
  // =========================================================

  const loadInventoryData =
    useCallback(async () => {
      try {
        const response =
          await storeApi.getInventory();

        const data =
          response?.data ?? response;

        if (!data) {
          return;
        }

        const mappedInventory =
          data.map(item => ({
            id: item.id,

            product:
              item.productName,

            category:
              'General',

            currentStock:
              item.currentStock,

            predictedDemand:
              item.reorderLevel,

            risk: Math.round(
              (item.predictedStockoutRisk ?? 0) *
                100
            ),

            status:
              (item.predictedStockoutRisk ?? 0) >= 0.70
                ? 'High'
                : (item.predictedStockoutRisk ?? 0) >= 0.30
                  ? 'Medium'
                  : 'Low',

            shelfLife:
              'N/A'
          }));

        setInventory(
          mappedInventory
        );

      } catch (error) {
        console.error(
          'Failed to load inventory data:',
          error
        );
      }
    }, []);

  // =========================================================
  // LOAD ML INVENTORY RISK PREDICTIONS
  // =========================================================

  const loadInventoryRiskPredictions =
    useCallback(async () => {
      try {
        const response =
          await storeApi.getInventoryRiskPredictions();

        const data =
          response?.data ?? response;

        if (!data) {
          return;
        }

        setInventoryRiskPredictions(data);

      } catch (error) {
        console.error(
          'Failed to load ML inventory risk predictions:',
          error
        );
      }
    }, []);

  useEffect(() => {
    loadInventoryRiskPredictions();
  }, [loadInventoryRiskPredictions]);

  useEffect(() => {
    loadInventoryData();
  }, [loadInventoryData]);

  // =========================================================
  // SWITCH STORE
  // =========================================================

  const switchStore = useCallback(
    (storeId) => {
      const found =
        INITIAL_STORE_DATA.availableStores.find(
          s => s.id === storeId
        );

      if (found) {
        setCurrentStore({
          ...INITIAL_STORE_DATA.storeInfo,
          id: found.id,
          code: found.code,
          name: found.name
        });

        addToast({
          title: 'Store Switched',
          message:
            `Connected to ${found.code} (${found.name}) live telemetry.`,
          type: 'success'
        });

        polling.triggerPoll();
      }
    },
    [addToast, polling]
  );

  // =========================================================
  // OPEN CHECKOUT LANE
  // =========================================================

  const openCheckoutLane =
    useCallback(
      async (laneId = 3) => {
        setIsLoading(true);

        try {
          await storeApi.openCheckoutLane(
            currentStore.id,
            laneId
          );

          setCheckouts(prev =>
            prev.map(lane => {
              if (lane.id === laneId) {
                return {
                  ...lane,
                  status: 'OPEN',
                  customers: 2,
                  waitMinutes: 1,
                  cashier:
                    'Elena S. (Dispatched)',
                  efficiency: '96%'
                };
              }

              return lane;
            })
          );

          setKpis(prev => ({
            ...prev,

            checkoutQueue: {
              ...prev.checkoutQueue,

              value: Math.max(
                8,
                prev.checkoutQueue.value - 4
              ),

              avgWaitMinutes: 2,

              openCheckouts: 4,

              status: 'NORMAL'
            }
          }));

          setTasks(prev =>
            prev.map(t =>
              t.task
                .toLowerCase()
                .includes('checkout')
                ? {
                    ...t,
                    completed: true
                  }
                : t
            )
          );

          setAlerts(prev =>
            prev.map(a =>
              a.category === 'Queue'
                ? {
                    ...a,
                    resolved: true
                  }
                : a
            )
          );

          addToast({
            title:
              `Lane ${laneId} Activated`,

            message:
              `Checkout Lane ${laneId} opened. Cashier Elena S. logged in. Average wait dropping to ~1.8 min.`,

            type: 'success'
          });

        } catch (err) {
          addToast({
            title: 'Action Failed',

            message:
              'Could not communicate with checkout hardware.',

            type: 'error'
          });

        } finally {
          setIsLoading(false);
        }
      },
      [currentStore.id, addToast]
    );

  // =========================================================
  // REPLENISH STOCK
  // =========================================================

  const replenishStock =
    useCallback(
      async (productId, quantity = 50) => {
        setIsLoading(true);

        try {
          await storeApi.replenishStock(
            productId,
            quantity
          );

          setInventory(prev =>
            prev.map(item => {
              if (
                item.id === productId ||
                item.product
                  .toLowerCase()
                  .includes(
                    productId.toLowerCase()
                  )
              ) {
                const newStock =
                  item.currentStock +
                  quantity;

                const newRisk = Math.max(
                  5,
                  Math.round(
                    (
                      (item.predictedDemand -
                        newStock) /
                      item.predictedDemand
                    ) * 100
                  )
                );

                return {
                  ...item,

                  currentStock:
                    newStock,

                  risk:
                    Math.max(
                      10,
                      newRisk
                    ),

                  status:
                    newRisk > 60
                      ? 'High'
                      : newRisk > 30
                        ? 'Medium'
                        : 'Low'
                };
              }

              return item;
            })
          );

          setKpis(prev => ({
            ...prev,

            stockRisks: {
              ...prev.stockRisks,

              value: Math.max(
                1,
                prev.stockRisks.value - 1
              ),

              criticalCount:
                Math.max(
                  0,
                  prev.stockRisks.criticalCount - 1
                ),

              status:
                prev.stockRisks.criticalCount <= 1
                  ? 'NORMAL'
                  : 'ATTENTION'
            }
          }));

          setTasks(prev =>
            prev.map(t =>
              t.task
                .toLowerCase()
                .includes(
                  productId.toLowerCase()
                )
                ? {
                    ...t,
                    completed: true
                  }
                : t
            )
          );

          setAlerts(prev =>
            prev.map(a =>
              a.description
                .toLowerCase()
                .includes(
                  productId.toLowerCase()
                )
                ? {
                    ...a,
                    resolved: true
                  }
                : a
            )
          );

          addToast({
            title:
              'Stock Replenished',

            message:
              `Dispatched +${quantity} units to sales floor cooler. Stockout risk mitigated.`,

            type: 'success'
          });

        } catch (err) {
          addToast({
            title:
              'Replenishment Failed',

            message:
              'Unable to dispatch inventory task.',

            type: 'error'
          });

        } finally {
          setIsLoading(false);
        }
      },
      [addToast]
    );

  // =========================================================
  // RESOLVE ALERT
  // =========================================================

  const resolveAlert =
    useCallback(
      async (alertId) => {
        await storeApi.resolveAlert(
          alertId
        );

        setAlerts(prev =>
          prev.map(a =>
            a.id === alertId
              ? {
                  ...a,
                  resolved: true
                }
              : a
          )
        );

        setKpis(prev => ({
          ...prev,

          criticalAlerts: {
            ...prev.criticalAlerts,

            value: Math.max(
              0,
              prev.criticalAlerts.value - 1
            ),

            status:
              prev.criticalAlerts.value <= 1
                ? 'NORMAL'
                : 'CRITICAL'
          }
        }));

        addToast({
          title:
            'Alert Acknowledged',

          message:
            'Incident marked as resolved by store manager.',

          type: 'info'
        });
      },
      [addToast]
    );

  // =========================================================
  // TOGGLE TASK
  // =========================================================

  const toggleTask =
    useCallback(
      (taskId) => {
        setTasks(prev =>
          prev.map(t => {
            if (t.id === taskId) {
              const nextState =
                !t.completed;

              addToast({
                title:
                  nextState
                    ? 'Task Completed'
                    : 'Task Reopened',

                message:
                  `"${t.task}" marked as ${
                    nextState
                      ? 'done'
                      : 'active'
                  }.`,

                type:
                  nextState
                    ? 'success'
                    : 'info'
              });

              return {
                ...t,
                completed: nextState
              };
            }

            return t;
          })
        );
      },
      [addToast]
    );

  // =========================================================
  // EXECUTE AI RECOMMENDATION
  // =========================================================

  const executeRecommendation =
    useCallback(
      async (rec) => {

        // 1. Mark recommendation complete
        try {
          await storeApi.completeRecommendation(
            rec.id
          );

        } catch (error) {
          console.error(
            'Failed to complete recommendation:',
            error
          );

          addToast({
            title:
              'Action Failed',

            message:
              'Could not update the recommendation in the backend.',

            type: 'error'
          });

          return;
        }

        // 2. Execute frontend action
        if (
          rec.actionType ===
          'open_checkout'
        ) {
          openCheckoutLane(3);

        } else if (
          rec.actionType ===
          'replenish_milk'
        ) {
          replenishStock(
            'Milk',
            40
          );

        } else if (
          rec.actionType ===
          'verify_bread'
        ) {
          replenishStock(
            'Bread',
            25
          );

          addToast({
            title:
              'Audit Complete',

            message:
              'Bread physical stock count reconciled with POS inventory model.',

            type: 'success'
          });

        } else if (
          rec.actionType ===
          'rebalance_staff'
        ) {
          setZones(prev =>
            prev.map(z => {

              if (
                z.id ===
                'zone-dairy'
              ) {
                return {
                  ...z,
                  percent: 62,
                  status: 'Busy',
                  customers: 19
                };
              }

              if (
                z.id ===
                'zone-bakery'
              ) {
                return {
                  ...z,
                  percent: 36,
                  customers: 9
                };
              }

              return z;
            })
          );

          addToast({
            title:
              'Staff Rebalanced',

            message:
              'Floor Associate Marcus reallocated from Bakery to Dairy zone.',

            type: 'success'
          });
        }

        // 3. Remove completed recommendation
        setRecommendations(prev =>
          prev.filter(
            r => r.id !== rec.id
          )
        );
      },
      [
        openCheckoutLane,
        replenishStock,
        addToast
      ]
    );

  // =========================================================
  // DEMO SPIKE SIMULATION
  // =========================================================

  const toggleSpikeSimulation =
    useCallback(() => {

      setIsSimulatingSpike(prev => {
        const next = !prev;

        if (next) {
          addToast({
            title:
              'Rush Hour Spike Simulated',

            message:
              'Simulating heavy footfall surge (+35 shoppers, +10 queue). Alerts & warnings elevated.',

            type: 'warning'
          });

        } else {
          addToast({
            title:
              'Standard Traffic Restored',

            message:
              'Store traffic returned to normal baseline values.',

            type: 'info'
          });
        }

        return next;
      });

      setTimeout(
        () => handlePollTick(),
        200
      );

    }, [
      addToast,
      handlePollTick
    ]);

  // =========================================================
  // CONTEXT VALUE
  // =========================================================

  const value = useMemo(
    () => ({
      currentStore,

      switchStore,

      availableStores:
        INITIAL_STORE_DATA.availableStores,

      kpis,

      occupancy,

      trafficData,

      trafficStats:
        INITIAL_STORE_DATA.trafficStats,

      zones,

      shopperEvents,

      checkouts,

      queueSummary,

      inventory,

      inventoryRiskPredictions,

      alerts,

      recommendations,

      tasks,

      toasts,

      addToast,

      removeToast,

      isLoading,

      setIsLoading,

      hasError,

      setHasError,

      polling,

      openCheckoutLane,

      replenishStock,

      resolveAlert,

      toggleTask,

      executeRecommendation,

      isSimulatingSpike,

      toggleSpikeSimulation
    }),

    [
      currentStore,
      switchStore,
      kpis,
      occupancy,
      trafficData,
      zones,
      shopperEvents,
      checkouts,
      queueSummary,
      inventory,
      inventoryRiskPredictions,
      alerts,
      recommendations,
      tasks,
      toasts,
      addToast,
      removeToast,
      isLoading,
      hasError,
      polling,
      openCheckoutLane,
      replenishStock,
      resolveAlert,
      toggleTask,
      executeRecommendation,
      isSimulatingSpike,
      toggleSpikeSimulation
    ]
  );

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  );
}

export function useStore() {
  const ctx = useContext(StoreContext);

  if (!ctx) {
    throw new Error(
      'useStore must be used within a StoreProvider'
    );
  }

  return ctx;
}