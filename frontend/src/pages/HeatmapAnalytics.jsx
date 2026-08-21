import React, { useEffect, useState } from "react";
import { Download, Layers3, RefreshCw } from "lucide-react";
import PageHeader from "../components/PageHeader";
import { fetchHeatmap, generateHeatmap, reportDownloadUrl } from "../api/analyticsApi";
import { listResource } from "../api/resources";
import "./HeatmapAnalytics.css";

export default function HeatmapAnalytics(){
 const [stores,setStores]=useState([]),[storeId,setStoreId]=useState(""),[hours,setHours]=useState(24),[points,setPoints]=useState([]),[image,setImage]=useState(""),[error,setError]=useState(""),[generating,setGenerating]=useState(false);
 const load=async()=>{if(!storeId)return;try{const p=await fetchHeatmap(hours,storeId);setPoints(p||[]);setError("")}catch(e){setError(e.response?.data?.detail||"Unable to load heatmap data.")}};
 const generate=async()=>{if(!storeId)return;setGenerating(true);try{const result=await generateHeatmap({store_id:storeId,heatmap_type:"traffic",since:new Date(Date.now()-hours*3600*1000).toISOString()});const base=import.meta.env.VITE_API_BASE||"http://localhost:8000";setImage(`${base.replace(/\/+$/u,"")}${result.image_url}`);await load();}catch(e){setError(e.response?.data?.detail||"Unable to generate heatmap image.")}finally{setGenerating(false)}};
 useEffect(()=>{listResource("stores").then(x=>{setStores(x);if(x[0]?.id)setStoreId(x[0].id)}).catch(()=>setError("Unable to load stores."))},[]);
 useEffect(()=>{load();setImage("")},[storeId,hours]);
 const max=Math.max(...points.map(p=>p.value||p.dwell||p.weight||0),1);
 return <div className="heatmap-page">
  <PageHeader title="Attention heatmaps" description="Visualize foot traffic and attention density from accumulated tracking coordinates." actions={<div className="flex gap-2"><select value={storeId} onChange={e=>setStoreId(e.target.value)}><option value="">Store</option>{stores.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select><select value={hours} onChange={e=>setHours(Number(e.target.value))}><option value="6">6 hours</option><option value="24">24 hours</option><option value="168">7 days</option></select><button className="heatmap-refresh" onClick={generate} disabled={!storeId||generating}><RefreshCw size={14}/>{generating?"Generating…":"Generate image"}</button></div>}/>
  {error&&<div className="heatmap-note">{error}</div>}
  <section className="heatmap-layout"><div className="heatmap-visual"><div className="heatmap-head"><div><span>STORE / SELECTED</span><h2>Attention density</h2></div><span className="heatmap-legend">LOW <i/> HIGH</span></div><div className="heatmap-canvas">{image?<img src={image} alt="Store attention heatmap"/>:points.slice(0,80).map((p,i)=><span key={i} className="heat-point" style={{left:`${Math.min(92,Math.max(5,(p.x??0)%100))}%`,top:`${Math.min(90,Math.max(7,(p.y??0)%100))}%`,opacity:.25+(p.value||p.dwell||1)/max*.7}}/>)}{!image&&!points.length&&<div className="heatmap-empty"><Layers3 size={25}/><p>No tracking points are available for the selected store/window.</p></div>}</div><div className="heatmap-caption"><span>Backend point density</span><span>Generated image is stored by the backend</span></div></div><aside className="heatmap-stats"><Stat label="Data window" value={`${hours}h`}/><Stat label="Coordinates" value={points.length}/><Stat label="Store" value={stores.find(s=>String(s.id)===String(storeId))?.name||"—"}/><Stat label="Generation" value={image?"Image":"Live points"}/><button className="heatmap-export" disabled={!storeId} onClick={()=>window.open(reportDownloadUrl("attention.csv",storeId,hours),"_blank")}><Download size={14}/> Export attention CSV</button></aside></section>
 </div>
}
function Stat({label,value}){return <div className="heatmap-stat"><span>{label}</span><b>{value}</b></div>}
