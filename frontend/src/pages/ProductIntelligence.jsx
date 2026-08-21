import React, { useEffect, useState } from "react";
import { ArrowUpRight, Gauge, Package } from "lucide-react";
import PageHeader from "../components/PageHeader";
import { fetchProductScores } from "../api/analyticsApi";
import { listResource } from "../api/resources";
import "./ProductIntelligence.css";

export default function ProductIntelligence(){
 const [rows,setRows]=useState([]),[stores,setStores]=useState([]),[storeId,setStoreId]=useState(""),[hours,setHours]=useState(24),[error,setError]=useState("");
 const load=async()=>{if(!storeId)return;try{setRows(await fetchProductScores(hours,storeId));setError("")}catch(e){setError(e.response?.data?.detail||"Unable to load product attractiveness scores.")}};
 useEffect(()=>{listResource("stores").then(x=>{setStores(x);if(x[0]?.id)setStoreId(x[0].id)}).catch(()=>setError("Unable to load stores."))},[]);
 useEffect(()=>{load()},[storeId,hours]);
 return <div className="product-intelligence-page">
  <PageHeader title="Product intelligence" description="Weighted attractiveness scoring turns attention and interaction metrics into a 0–100 product performance signal." actions={<div className="flex gap-2"><select value={storeId} onChange={e=>setStoreId(e.target.value)}><option value="">Store</option>{stores.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select><select value={hours} onChange={e=>setHours(Number(e.target.value))}><option value="6">6 hours</option><option value="24">24 hours</option><option value="168">7 days</option></select></div>}/>
  {error&&<div className="product-intel-note">{error}</div>}
  <section className="score-formula"><div><span>MILESTONE 3 / TASK 3</span><h2>Attractiveness score</h2></div><div className="formula"><b>Attention</b><strong>35%</strong><b>Interaction</b><strong>25%</strong><b>Pickup</b><strong>20%</strong><b>Conversion</b><strong>15%</strong><b>Repeat</b><strong>5%</strong></div></section>
  <section className="score-grid">{rows.map((r,i)=>{const score=Math.round(r.score??r.attractiveness_score??0);const b=r.metrics_breakdown||{};return <article className="score-card" key={r.product_id||i}><div className="score-card-head"><div><Package size={16}/><b>{r.product_name||r.product||"Product"}</b></div><strong>{score}</strong></div><div className="score-meter"><span style={{width:`${Math.min(100,Math.max(0,score))}%`}}/></div><div className="score-metrics"><Metric label="Attention" value={b.attention_duration??"—"}/><Metric label="Interaction" value={b.interaction_frequency??"—"}/><Metric label="Pickup" value={b.pickup_rate!=null?`${Math.round(b.pickup_rate*100)}%`:"—"}/><Metric label="Conversion" value={b.conversion_rate!=null?`${Math.round(b.conversion_rate*100)}%`:"—"}/></div><div className="score-recommendations">{(r.recommendations||[]).slice(0,2).map((x,j)=><small key={j}>{x.message||x.action||JSON.stringify(x)}</small>)}</div><button className="score-link" onClick={()=>window.scrollTo({top:0,behavior:"smooth"})}>Open product <ArrowUpRight size={13}/></button></article>})}</section>
  {!rows.length&&<div className="score-empty"><Gauge size={22}/><p>{storeId?"No product score records are available for this store yet.":"Select a store to load product scores."}</p></div>}
 </div>
}
function Metric({label,value}){return <div><span>{label}</span><b>{value}</b></div>}
