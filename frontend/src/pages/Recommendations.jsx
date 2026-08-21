import React, { useEffect, useState } from "react";
import { AlertTriangle, ArrowRight, CheckCircle2, Lightbulb } from "lucide-react";
import PageHeader from "../components/PageHeader";
import { fetchRecommendations } from "../api/analyticsApi";
import "./Recommendations.css";

const fallback=[
 {priority:"High",message:"High eye attention but low pickup/conversion. Suggest reviewing pricing or promotional offer."},
 {priority:"Medium",message:"Strong traffic with low dwell. Consider improving shelf placement and product visibility."},
 {priority:"Medium",message:"High dwell concentration detected. Review adjacent shelf layout for comparison behavior."},
];

export default function Recommendations(){
 const [rows,setRows]=useState(fallback),[hours,setHours]=useState(24),[error,setError]=useState("");
 useEffect(()=>{fetchRecommendations(hours).then(x=>Array.isArray(x)&&x.length&&setRows(x)).catch(e=>setError(e.response?.data?.detail||"Unable to load recommendation rules."))},[hours]);
 return <div className="recommendation-page">
  <PageHeader title="Recommendations" description="Automated retail actions generated from product scores, attention anomalies and shopper behavior." actions={<select value={hours} onChange={e=>setHours(Number(e.target.value))}><option value="6">6 hours</option><option value="24">24 hours</option><option value="168">7 days</option></select>}/>
  {error&&<div className="recommendation-note">{error}</div>}
  <section className="recommendation-banner"><div><span>MILESTONE 3 / TASK 4</span><h2>From anomaly → action</h2><p>Recommendations should explain what changed and what a store manager can do next.</p></div><Lightbulb size={28}/></section>
  <div className="recommendation-list">{rows.map((r,i)=><article key={i} className={`recommendation-card ${String(r.priority).toLowerCase()}`}><div className="recommendation-icon">{r.priority==="High"?<AlertTriangle size={18}/>:<CheckCircle2 size={18}/>}</div><div className="recommendation-body"><div><span>{r.priority} priority</span><small>Rule result · #{String(i+1).padStart(2,"0")}</small></div><p>{r.message}</p><button>Review in product intelligence <ArrowRight size={13}/></button></div></article>)}</div>
 </div>
}
