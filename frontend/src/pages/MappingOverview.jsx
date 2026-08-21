import React, { useEffect, useMemo, useState } from "react";
import { ArrowRight, CheckCircle2, Layers3, MapPinned, Save } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import PageHeader from "../components/PageHeader";
import { listResource } from "../api/resources";
import { mappingApi } from "../api/mappingApi";
import "./MappingOverview.css";

export default function MappingOverview() {
  const navigate = useNavigate();
  const [stores, setStores] = useState([]);
  const [storeId, setStoreId] = useState("");
  const [cameras, setCameras] = useState([]);
  const [selected, setSelected] = useState([]);
  const [shelves, setShelves] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    listResource("stores")
      .then((rows) => {
        setStores(rows);
        if (rows[0]?.id) setStoreId(rows[0].id);
      })
      .catch(() => setError("Unable to load stores."));
  }, []);

  useEffect(() => {
    if (!storeId) return;

    Promise.all([
      mappingApi.listCameras(storeId),
      mappingApi.listShelves(storeId).catch(() => []),
    ]).then(([cameraRows, shelfRows]) => {
      setCameras(cameraRows);
      setSelected((current) => current.length ? current.filter(id => cameraRows.some(c => String(c.id) === String(id))) : cameraRows.slice(0, 2).map(c => c.id));
      setShelves(shelfRows);
    });
  }, [storeId]);

  const coverage = useMemo(() => {
    if (!cameras.length) return 0;
    return Math.round((selected.length / cameras.length) * 100);
  }, [cameras, selected]);

  const toggle = (id) =>
    setSelected((current) =>
      current.includes(id) ? current.filter((x) => x !== id) : [...current, id]
    );

  return (
    <div className="mapping-overview-page">
      <PageHeader
        title="Store mapping"
        description="Configure spatial relationships between stores, cameras, zones, shelves and products."
        actions={
          <Button onClick={() => navigate("/mapping/workspace")}>
            Open mapping workspace <ArrowRight size={15} />
          </Button>
        }
      />

      {error && <div className="mapping-alert">{error}</div>}

      <section className="mapping-overview-summary">
        <div>
          <span>STORE</span>
          <select value={storeId} onChange={(e) => setStoreId(e.target.value)}>
            <option value="">Select store</option>
            {stores.map((store) => (
              <option key={store.id} value={store.id}>{store.name}</option>
            ))}
          </select>
        </div>
        <Metric label="CAMERAS" value={`${selected.length}/${cameras.length}`} />
        <Metric label="SHELVES" value={shelves.length} />
        <Metric label="COVERAGE" value={`${coverage}%`} />
        <Metric label="MODE" value="Mapping only" />
      </section>

      <section className="mapping-camera-strip">
        <div className="mapping-section-heading">
          <div>
            <span>CAMERA TOPOLOGY</span>
            <h2>Choose synchronized mapping views</h2>
          </div>
          <span className="mapping-ready"><CheckCircle2 size={15} /> Ready</span>
        </div>

        <div className="mapping-camera-options">
          {cameras.map((camera) => {
            const active = selected.includes(camera.id);
            return (
              <button
                key={camera.id}
                className={`mapping-camera-card ${active ? "selected" : ""}`}
                onClick={() => toggle(camera.id)}
              >
                <div className="mapping-camera-preview">
                  <span>{camera.id}</span>
                  <span className="mapping-online">●</span>
                </div>
                <div className="mapping-camera-meta">
                  <strong>{camera.name || camera.id}</strong>
                  <small>{active ? "Included in workspace" : "Click to include"}</small>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      <section className="mapping-flow">
        <Step icon={MapPinned} title="Map zones" text="Define store regions and camera coverage." />
        <Step icon={Layers3} title="Map shelves" text="Draw ROI, tiers and shelf-camera relationships." />
        <Step icon={Save} title="Map products" text="Bind individual SKUs to shelf positions." />
      </section>
    </div>
  );
}

function Metric({ label, value }) {
  return <div><span>{label}</span><strong>{value}</strong></div>;
}

function Step({ icon: Icon, title, text }) {
  return (
    <div className="mapping-flow-step">
      <span><Icon size={18} /></span>
      <div><strong>{title}</strong><small>{text}</small></div>
      <ArrowRight size={16} />
    </div>
  );
}
