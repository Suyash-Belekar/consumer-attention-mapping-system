import React, { useEffect, useState } from "react";
import { Brain, Compass, GitCompare, Zap } from "lucide-react";
import PageHeader from "../components/PageHeader";
import { fetchBehaviorSegments } from "../api/analyticsApi";
import { listResource } from "../api/resources";
import "./BehaviorAnalytics.css";

export default function BehaviorAnalytics() {
  const [rows, setRows] = useState([]), [stores, setStores] = useState([]), [storeId, setStoreId] = useState(""), [hours, setHours] = useState(24), [error, setError] = useState("");
  const load = async () => { if (!storeId) return; try { setRows(await fetchBehaviorSegments(hours, storeId)); setError(""); } catch (e) { setError(e.response?.data?.detail || "Unable to load behavior segments."); } };
  useEffect(() => { listResource("stores").then((x) => { setStores(x); if (x[0]?.id) setStoreId(x[0].id); }).catch(() => setError("Unable to load stores.")); }, []);
  useEffect(() => { load(); }, [storeId, hours]);
  const icons = { Explorer: Compass, "Quick Buyer": Zap, "Comparison Shopper": GitCompare };
  return <div className="behavior-page">
    <PageHeader title="Behavior intelligence" description="Classify completed shopper sessions using behavioral segments persisted by the backend." actions={<div className="flex gap-2"><select value={storeId} onChange={e=>setStoreId(e.target.value)}><option value="">Store</option>{stores.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select><select value={hours} onChange={e=>setHours(Number(e.target.value))}><option value="6">6 hours</option><option value="24">24 hours</option><option value="168">7 days</option></select></div>}/>
    {error&&<div className="behavior-note">{error}</div>}
    <div className="behavior-grid">{rows.map((r,i)=>{const Icon=icons[r.segment]||Brain;return <article className="behavior-card" key={r.segment}><div className="behavior-icon"><Icon size={19}/></div><div className="behavior-card-top"><div><span>SEGMENT {String(i+1).padStart(2,"0")}</span><h2>{r.segment}</h2></div><strong>{r.share??0}%</strong></div><p>{r.description||"Persisted shopper sessions grouped into this behavioral segment."}</p><div className="behavior-metrics"><Metric label="Shoppers" value={r.shoppers??0}/><Metric label="Share" value={`${r.share??0}%`}/></div></article>})}</div>
    {!rows.length&&!error&&<div className="behavior-note">No tagged behavioral sessions are available for the selected store/window yet.</div>}
    <section className="behavior-method"><div><span>MILESTONE 3 / TASK 1</span><h2>Behavior classification pipeline</h2></div><div className="behavior-pipeline"><b>Tracking sessions</b><i>→</i><b>Trajectory + dwell</b><i>→</i><b>Segmentation</b><i>→</i><b>PostgreSQL tag</b></div></section>
  </div>;
}
function Metric({label,value}){return <div><span>{label}</span><b>{value}</b></div>}
