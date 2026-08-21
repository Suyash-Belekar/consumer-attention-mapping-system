import React,{useCallback,useEffect,useState} from "react";
import {useNavigate} from "react-router-dom";
import {Activity,Brain,Clock3,MapPinned,Package,Users} from "lucide-react";
import PageHeader from "../components/PageHeader";
import StatCard from "../components/StatCard";
import {fetchSummary,fetchProductRankings,fetchTraffic,fetchRecommendations} from "../api/analyticsApi";
import "./AnalyticsDashboard.css";

export default function AnalyticsDashboard(){
 const navigate=useNavigate(); const [data,setData]=useState({summary:null,products:[],traffic:[],recommendations:[]}); const [hours,setHours]=useState(24); const [error,setError]=useState("");
 const load=useCallback(async()=>{try{const [summary,products,traffic,recommendations]=await Promise.all([fetchSummary(hours),fetchProductRankings(hours),fetchTraffic(hours),fetchRecommendations(hours)]);setData({summary,products,traffic,recommendations});setError("")}catch(e){setError(e.response?.data?.detail||e.message||"Unable to load analytics.")}},[hours]);
 useEffect(()=>{load();const id=setInterval(load,15000);return()=>clearInterval(id)},[load]);
 const max=Math.max(...data.traffic.map(x=>x.visitors||0),1);
 return <div className="analytics-hub">
  <PageHeader title="Analytics" description="Executive view of customer flow, attention and Milestone 3 retail intelligence." actions={<select value={hours} onChange={e=>setHours(Number(e.target.value))}><option value="6">6 hours</option><option value="24">24 hours</option><option value="168">7 days</option></select>}/>
  {error&&<div className="analytics-error">{error}</div>}
  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><StatCard label="Current visitors" value={data.summary?.current_visitors??"—"} icon={Users}/><StatCard label="Visitors" value={data.summary?.total_visitors??"—"} icon={Activity}/><StatCard label="Average dwell" value={data.summary?.average_dwell_time?`${data.summary.average_dwell_time}s`:"—"} icon={Clock3}/><StatCard label="Top product" value={data.summary?.top_product??"—"} icon={Package}/></div>
  <section className="analytics-hub-grid">
    <Panel title="Traffic flow" action={<button onClick={()=>navigate("/analytics/heatmaps")}>Heatmaps <MapPinned size={13}/></button>}><div className="traffic-bars">{data.traffic.slice(-18).map((x,i)=><div key={i}><i style={{height:`${Math.max(8,(x.visitors/max)*145)}px`}}/><small>{x.hour?.slice(0,5)}</small></div>)}</div></Panel>
    <Panel title="Top products" action={<button onClick={()=>navigate("/analytics/products")}>Product intelligence <Package size={13}/></button>}><div className="analytics-product-list">{data.products.slice(0,6).map((p,i)=><div key={i}><span>0{i+1}</span><b>{p.product||p.product_name}</b><strong>{p.score??p.attention_score??"—"}</strong></div>)}</div></Panel>
  </section>
  <section className="analytics-intelligence-links"><Link title="Behavior intelligence" text="Explorer · Quick Buyer · Comparison Shopper" icon={Brain} go={()=>navigate("/analytics/behavior")}/><Link title="Attention heatmaps" text="Traffic and dwell density by camera/store" icon={MapPinned} go={()=>navigate("/analytics/heatmaps")}/><Link title="Recommendations" text={`${data.recommendations.length} current optimization signals`} icon={Activity} go={()=>navigate("/recommendations")}/></section>
 </div>
}
function Panel({title,action,children}){return <section className="analytics-panel"><div className="analytics-panel-head"><h2>{title}</h2>{action}</div>{children}</section>}
function Link({title,text,icon:Icon,go}){return <button onClick={go} className="analytics-link"><Icon size={18}/><div><b>{title}</b><small>{text}</small></div></button>}
