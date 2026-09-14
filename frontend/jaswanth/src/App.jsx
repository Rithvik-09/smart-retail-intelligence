import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { StoreProvider } from './context/StoreContext';
import { Layout } from './components/layout/Layout';

// Pages
import { Dashboard } from './pages/Dashboard';
import { Analytics } from './pages/Analytics';
import { Occupancy } from './pages/Occupancy';
import { Checkout } from './pages/Checkout';
import { Inventory } from './pages/Inventory';
import { Alerts } from './pages/Alerts';
import { Recommendations } from './pages/Recommendations';
import { Tasks } from './pages/Tasks';

export function App() {
  return (
    <StoreProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="occupancy" element={<Occupancy />} />
            <Route path="checkout" element={<Checkout />} />
            <Route path="inventory" element={<Inventory />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="recommendations" element={<Recommendations />} />
            <Route path="tasks" element={<Tasks />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </StoreProvider>
  );
}

export default App;
