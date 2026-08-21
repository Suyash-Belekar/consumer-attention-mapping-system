import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

import Stores from "./pages/Stores";
import Zones from "./pages/Zones";
import Shelves from "./pages/Shelves";
import Cameras from "./pages/Cameras";
import Products from "./pages/Products";

import MappingOverview from "./pages/MappingOverview";
import MappingWorkspace from "./pages/MappingWorkspace";
import ShelfMapping from "./pages/ShelfMapping";
import ProductMapping from "./pages/ProductMapping";

import LiveTracking from "./pages/LiveTracking";

import AnalyticsDashboard from "./pages/AnalyticsDashboard";
import BehaviorAnalytics from "./pages/BehaviorAnalytics";
import HeatmapAnalytics from "./pages/HeatmapAnalytics";
import ProductIntelligence from "./pages/ProductIntelligence";
import Recommendations from "./pages/Recommendations";

import Settings from "./pages/Settings";
import Reports from "./pages/Reports";
import Alerts from "./pages/Alerts";

function Protected({ children }) {
  return localStorage.getItem("token")
    ? <Layout>{children}</Layout>
    : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />

      <Route path="/stores" element={<Protected><Stores /></Protected>} />
      <Route path="/zones" element={<Protected><Zones /></Protected>} />
      <Route path="/shelves" element={<Protected><Shelves /></Protected>} />
      <Route path="/cameras" element={<Protected><Cameras /></Protected>} />
      <Route path="/products" element={<Protected><Products /></Protected>} />

      {/* Mapping is deliberately separate from tracking. */}
      <Route path="/mapping" element={<Protected><MappingOverview /></Protected>} />
      <Route path="/mapping/workspace" element={<Protected><MappingWorkspace /></Protected>} />
      <Route path="/mapping/shelves" element={<Protected><ShelfMapping /></Protected>} />
      <Route path="/mapping/products" element={<Protected><ProductMapping /></Protected>} />

      {/* Tracking is a separate multi-camera operational workflow. */}
      <Route path="/tracking" element={<Protected><LiveTracking /></Protected>} />

      {/* Milestone 3 intelligence surfaces. */}
      <Route path="/analytics" element={<Protected><AnalyticsDashboard /></Protected>} />
      <Route path="/analytics/behavior" element={<Protected><BehaviorAnalytics /></Protected>} />
      <Route path="/analytics/heatmaps" element={<Protected><HeatmapAnalytics /></Protected>} />
      <Route path="/analytics/products" element={<Protected><ProductIntelligence /></Protected>} />
      <Route path="/recommendations" element={<Protected><Recommendations /></Protected>} />

      <Route path="/reports" element={<Protected><Reports /></Protected>} />
      <Route path="/alerts" element={<Protected><Alerts /></Protected>} />
      <Route path="/settings" element={<Protected><Settings /></Protected>} />

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
