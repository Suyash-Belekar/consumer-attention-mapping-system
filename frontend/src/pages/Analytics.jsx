import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import VisitorCard from "../components/analytics/VisitorCard";
import ProductRanking from "../components/analytics/ProductRanking";
import HeatMap from "../components/analytics/HeatMap";
import TrafficChart from "../components/analytics/TrafficChart";

import { Button } from "@/components/ui/button";

import api from "../services/api";

const POLL_INTERVAL_MS = 15000;

export default function Analytics() {
  const navigate = useNavigate();

  const [visitors, setVisitors] = useState(null);
  const [products, setProducts] = useState([]);
  const [heatmap, setHeatmap] = useState([]);
  const [traffic, setTraffic] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
        navigate("/", { replace: true });
    }
  }, [navigate]);

  const loadAll = useCallback(async () => {
    try {
      const [visitorsRes, productsRes, heatmapRes, trafficRes] = await Promise.all([
        api.get("/analytics/current-visitors").then(res => res.data),
        api.get("/analytics/products").then(res => res.data),
        api.get("/analytics/heatmap").then(res => res.data),
        api.get("/analytics/traffic").then(res => res.data),
      ]);
      setVisitors(visitorsRes.count);
      setProducts(productsRes);
      setHeatmap(heatmapRes);
      setTraffic(trafficRes);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadAll();
    const id = setInterval(loadAll, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [loadAll]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 px-5 py-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="rounded-[32px] border border-slate-800 bg-slate-900/95 px-8 py-8 shadow-2xl shadow-slate-950/40 sm:flex sm:items-center sm:justify-between">
          <div>
              <h1 className="text-3xl font-semibold text-white">
              Consumer Attention Mapping
              </h1>
              <p className="mt-3 text-slate-400">Live store analytics</p>
          </div>
          <Button className="mt-6 sm:mt-0" onClick={() => navigate("/dashboard")}>
            Back to Dashboard
        </Button>
      </header>

      {error && (
        <div className="rounded-3xl border border-red-500/20 bg-red-500/10 px-5 py-4 text-sm text-red-200">
          Couldn't refresh dashboard data: {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <VisitorCard count={visitors} />
        <div className="rounded-[32px] border border-slate-800 bg-slate-900/95 p-6 shadow-lg shadow-slate-950/20">
          <TrafficChart data={traffic} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <ProductRanking products={products} />
        <HeatMap points={heatmap} />
      </div>
    </div>
  );
}
