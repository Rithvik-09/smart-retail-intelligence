// Comprehensive mock store intelligence data
export const INITIAL_STORE_DATA = {
  storeInfo: {
    id: "store-001",
    code: "Store #001",
    name: "Downtown Flagship",
    manager: "Alex Rivera",
    role: "Store General Manager",
    shift: "Morning / Afternoon",
    lastUpdated: new Date().toISOString(),
  },
  availableStores: [
    { id: "store-001", code: "Store #001", name: "Downtown Flagship", address: "450 Grand Central Ave" },
    { id: "store-002", code: "Store #002", name: "Metro Center", address: "128 Market Plaza" },
    { id: "store-003", code: "Store #003", name: "West End Express", address: "890 Sunset Blvd" },
  ],
  kpis: {
    customersNow: {
      value: 87,
      previousHour: 78,
      deltaPercent: 12,
      deltaType: "increase",
      status: "LIVE",
      label: "CUSTOMERS NOW",
      subtext: "↑ 12% from previous hour",
    },
    checkoutQueue: {
      value: 14,
      avgWaitMinutes: 3,
      openCheckouts: 3,
      totalCheckouts: 4,
      status: "BUSY",
      label: "CHECKOUT QUEUE",
      subtext: "Average wait: 3 min",
    },
    stockRisks: {
      value: 6,
      criticalCount: 2,
      highCount: 2,
      status: "ATTENTION",
      label: "STOCK RISKS",
      subtext: "2 critical",
    },
    criticalAlerts: {
      value: 3,
      status: "CRITICAL",
      label: "CRITICAL ALERTS",
      subtext: "Requires attention",
    }
  },
  occupancy: {
    current: 87,
    capacity: 150,
    peakToday: 121,
    occupancyPercent: 58,
    status: "Normal", // <60% Normal, 60-80% Busy, >80% Crowded
    thresholds: {
      normalMax: 60,
      busyMax: 80,
    }
  },
  trafficData: {
    today: [
      { time: "09:00", customers: 32, changePercent: "+5%", dwellTime: 18 },
      { time: "10:00", customers: 48, changePercent: "+12%", dwellTime: 22 },
      { time: "11:00", customers: 61, changePercent: "+15%", dwellTime: 25 },
      { time: "12:00", customers: 75, changePercent: "+18%", dwellTime: 29 },
      { time: "13:00", customers: 87, changePercent: "+12%", dwellTime: 31 },
      { time: "14:00", customers: 79, changePercent: "-9%", dwellTime: 28 },
      { time: "15:00", customers: 92, changePercent: "+16%", dwellTime: 34 },
      { time: "16:00", customers: 87, changePercent: "-5%", dwellTime: 30 },
    ],
    sevenDays: [
      { day: "Mon", customers: 840, peak: 110, avgWait: 2.8 },
      { day: "Tue", customers: 920, peak: 118, avgWait: 3.1 },
      { day: "Wed", customers: 880, peak: 105, avgWait: 2.9 },
      { day: "Thu", customers: 1040, peak: 130, avgWait: 3.5 },
      { day: "Fri", customers: 1250, peak: 145, avgWait: 4.2 },
      { day: "Sat", customers: 1480, peak: 155, avgWait: 4.8 },
      { day: "Sun (Today)", customers: 1120, peak: 121, avgWait: 3.0 },
    ],
    thirtyDays: [
      { week: "Week 1", footfall: 6850, stockoutsAvoided: 24, avgWait: 3.2 },
      { week: "Week 2", footfall: 7120, stockoutsAvoided: 31, avgWait: 3.0 },
      { week: "Week 3", footfall: 7450, stockoutsAvoided: 28, avgWait: 2.9 },
      { week: "Week 4", footfall: 7890, stockoutsAvoided: 38, avgWait: 2.8 },
    ]
  },
  trafficStats: {
    current: 87,
    peak: 92,
    average: 68
  },
  zones: [
    { id: "zone-entrance", name: "Entrance", customers: 12, capacity: 25, percent: 48, status: "Normal", trend: "stable" },
    { id: "zone-aisle-a", name: "Aisle A", description: "Produce & Fresh", customers: 18, capacity: 30, percent: 60, status: "Busy", trend: "up" },
    { id: "zone-aisle-b", name: "Aisle B", description: "Pantry & Snacks", customers: 11, capacity: 25, percent: 44, status: "Normal", trend: "down" },
    { id: "zone-dairy", name: "Dairy", description: "Chilled & Milk", customers: 24, capacity: 30, percent: 80, status: "Crowded", trend: "up" },
    { id: "zone-bakery", name: "Bakery", description: "Fresh Baked", customers: 8, capacity: 25, percent: 32, status: "Normal", trend: "stable" },
    { id: "zone-care", name: "Personal Care", description: "Hygiene & Pharmacy", customers: 7, capacity: 20, percent: 35, status: "Normal", trend: "down" },
    { id: "zone-checkout", name: "Checkout", description: "Lanes 1-4", customers: 14, capacity: 20, percent: 70, status: "Busy", trend: "up" },
  ],
  checkouts: [
    {
      id: 1,
      name: "Checkout 1",
      status: "OPEN",
      customers: 5,
      waitMinutes: 3,
      cashier: "Sarah M.",
      efficiency: "94%"
    },
    {
      id: 2,
      name: "Checkout 2",
      status: "OPEN",
      customers: 4,
      waitMinutes: 2,
      cashier: "David L.",
      efficiency: "98%"
    },
    {
      id: 3,
      name: "Checkout 3",
      status: "CLOSED",
      customers: 0,
      waitMinutes: 0,
      cashier: "Unassigned",
      efficiency: "—"
    },
    {
      id: 4,
      name: "Checkout 4",
      status: "OPEN",
      customers: 5,
      waitMinutes: 4,
      cashier: "Alex R.",
      efficiency: "89%"
    },
  ],
  queueSummary: {
    totalQueue: 14,
    avgWait: 3,
    recommendation: "Open additional checkout",
    bottleneckAlert: "Lane 3 is currently closed while lanes 1, 2, 4 operate near capacity."
  },
  inventoryRisks: [
    {
      id: "inv-milk",
      product: "Milk",
      category: "Dairy",
      currentStock: 18,
      predictedDemand: 42,
      risk: 87,
      status: "Critical",
      reorderLevel: 25,
      supplierLeadTime: "2 hrs",
      shelfLife: "5 days"
    },
    {
      id: "inv-bread",
      product: "Bread",
      category: "Bakery",
      currentStock: 34,
      predictedDemand: 51,
      risk: 62,
      status: "High",
      reorderLevel: 40,
      supplierLeadTime: "3 hrs",
      shelfLife: "3 days"
    },
    {
      id: "inv-soap",
      product: "Soap",
      category: "Personal Care",
      currentStock: 85,
      predictedDemand: 30,
      risk: 15,
      status: "Low",
      reorderLevel: 35,
      supplierLeadTime: "24 hrs",
      shelfLife: "365 days"
    },
    {
      id: "inv-eggs",
      product: "Fresh Eggs (Dozen)",
      category: "Dairy",
      currentStock: 22,
      predictedDemand: 45,
      risk: 76,
      status: "High",
      reorderLevel: 30,
      supplierLeadTime: "4 hrs",
      shelfLife: "14 days"
    },
    {
      id: "inv-yogurt",
      product: "Greek Yogurt 500g",
      category: "Dairy",
      currentStock: 14,
      predictedDemand: 38,
      risk: 84,
      status: "Critical",
      reorderLevel: 20,
      supplierLeadTime: "3 hrs",
      shelfLife: "7 days"
    },
    {
      id: "inv-olive-oil",
      product: "Extra Virgin Olive Oil 1L",
      category: "Pantry",
      currentStock: 28,
      predictedDemand: 35,
      risk: 42,
      status: "Medium",
      reorderLevel: 25,
      supplierLeadTime: "48 hrs",
      shelfLife: "180 days"
    }
  ],
  alerts: [
    {
      id: "alt-1",
      title: "Milk inventory predicted to run out soon",
      description: "Current stock of 18 units will deplete in ~90 minutes based on predicted evening footfall demand (42 units needed).",
      severity: "Critical",
      priority: "Critical",
      category: "Inventory",
      timestamp: "4 mins ago",
      resolved: false,
      actionLabel: "Restock Now",
      actionKey: "replenish_milk"
    },
    {
      id: "alt-2",
      title: "Checkout queue exceeds recommended threshold",
      description: "14 customers in queue across 3 active lanes. Average wait time reached 3.2 minutes, breaching the 3.0 min threshold.",
      severity: "High",
      priority: "High",
      category: "Queue",
      timestamp: "8 mins ago",
      resolved: false,
      actionLabel: "Open Lane 3",
      actionKey: "open_checkout"
    },
    {
      id: "alt-3",
      title: "Dairy section experiencing high crowd density",
      description: "Dairy zone capacity has reached 80% (24/30 shoppers). Congestion detected between cooler aisles 3 and 4.",
      severity: "Medium",
      priority: "Medium",
      category: "Occupancy",
      timestamp: "15 mins ago",
      resolved: false,
      actionLabel: "Dispatch Floor Associate",
      actionKey: "rebalance_staff"
    },
    {
      id: "alt-4",
      title: "Greek Yogurt stock velocity spiking",
      description: "Sell-through rate is 2.4x higher than standard Sunday benchmark. Reorder recommendation queued.",
      severity: "High",
      priority: "High",
      category: "Inventory",
      timestamp: "24 mins ago",
      resolved: false,
      actionLabel: "Order Restock",
      actionKey: "order_yogurt"
    }
  ],
  aiRecommendations: [
    {
      id: "rec-1",
      title: "REPLENISH MILK",
      badge: "STOCK-OUT RISK 87%",
      category: "Inventory Optimization",
      confidence: 96,
      estimatedImpact: "Prevents ~$420 lost revenue & retains 35 shoppers",
      reason: "Current milk inventory has an 87% stock-out risk based on predicted demand.",
      actionType: "replenish_milk",
      buttonText: "TAKE ACTION",
      aiRationale: "Camera sensor telemetry in Dairy cooler detects 18 units remaining. Velocity model predicts 42 units needed before 19:00.",
      priority: "Critical"
    },
    {
      id: "rec-2",
      title: "OPEN ADDITIONAL CHECKOUT",
      badge: "QUEUE SPIKE PREDICTED",
      category: "Checkout Throughput",
      confidence: 92,
      estimatedImpact: "Reduces queue wait time from 3.2m to 1.8m",
      reason: "Checkout queue has exceeded the recommended threshold.",
      actionType: "open_checkout",
      buttonText: "OPEN CHECKOUT",
      aiRationale: "Vision AI observes 14 queued customers. Lane 3 is powered on and cashier Elena S. is on floor standby.",
      priority: "High"
    },
    {
      id: "rec-3",
      title: "VERIFY BREAD INVENTORY",
      badge: "DISCREPANCY DETECTED",
      category: "Audit & Loss Prevention",
      confidence: 88,
      estimatedImpact: "Reconciles 17-unit phantom inventory variance",
      reason: "Inventory prediction differs from expected stock.",
      actionType: "verify_bread",
      buttonText: "VERIFY",
      aiRationale: "POS register logs show 51 units forecasted, but shelf weight scale sensors indicate approximately 34 items remaining.",
      priority: "Medium"
    },
    {
      id: "rec-4",
      title: "REBALANCE STAFF TO DAIRY ZONE",
      badge: "CONGESTION MITIGATION",
      category: "Workforce Allocation",
      confidence: 84,
      estimatedImpact: "Relieves aisle crowding by 28% in 10 minutes",
      reason: "Dairy zone density is at 80% while Bakery operates at 32%. Shift 1 associate to assist shoppers.",
      actionType: "rebalance_staff",
      buttonText: "DEPLOY STAFF",
      aiRationale: "Computer vision heatmaps indicate bottle-necking near refrigerated dairy doors. Associate Marcus is available from bakery.",
      priority: "Medium"
    }
  ],
  priorityTasks: [
    {
      id: "task-1",
      priority: "CRITICAL",
      task: "Replenish Milk",
      department: "Dairy / Cooler",
      assignee: "Marcus T.",
      due: "Immediate (15m)",
      completed: false,
      systemGenerated: true
    },
    {
      id: "task-2",
      priority: "HIGH",
      task: "Open additional checkout",
      department: "Front-End",
      assignee: "Elena S. (Lane 3)",
      due: "Immediate (5m)",
      completed: false,
      systemGenerated: true
    },
    {
      id: "task-3",
      priority: "MEDIUM",
      task: "Verify Bread inventory",
      department: "Bakery",
      assignee: "Jordan K.",
      due: "17:00 Today",
      completed: false,
      systemGenerated: true
    },
    {
      id: "task-4",
      priority: "LOW",
      task: "Cycle count Personal Care aisle",
      department: "Pharmacy & Care",
      assignee: "Rachel B.",
      due: "19:00 Today",
      completed: false,
      systemGenerated: false
    },
    {
      id: "task-5",
      priority: "LOW",
      task: "Sanitize shopping carts and entrance bay",
      department: "Operations",
      assignee: "Chris W.",
      due: "20:00 Today",
      completed: true,
      systemGenerated: false
    }
  ]
};
