import React,{useEffect,useState} from "react";
import {useNavigate} from "react-router-dom";
import {Users,Clock3,Package,Store,ArrowUpRight,Layers3,Camera} from "lucide-react";
import PageHeader from "../components/PageHeader";
import StatCard from "../components/StatCard";
import {Button} from "@/components/ui/button";
import {fetchSummary,fetchProductRankings,fetchTraffic} from "../api/analyticsApi";
import "./Dashboard.css";
export default function Dashboard(){
 const navigate=useNavigate(); const [summary,setSummary]=useState(null),[products,setProducts]=useState([]),[traffic,setTraffic]=useState([]),[error,setError]=useState("");
 useEffect(()=>{Promise.all([fetchSummary(),fetchProductRankings(),fetchTraffic()]).then(([s,p,t])=>{setSummary(s);setProducts(p);setTraffic(t)}).catch(e=>setError(e.response?.data?.detail||e.message||"Analytics unavailable."))},[]);
 const max=Math.max(...traffic.map(x=>x.visitors||0),1);
 return <div><PageHeader title="Operations overview" description="A compact view of store health, customer attention and product performance." actions={<Button onClick={()=>navigate("/analytics")}>Open analytics <ArrowUpRight size={15}/></Button>}/>
 {error&&<div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">{error}</div>}
 <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><StatCard label="Current visitors" value={summary?.current_visitors??"—"} meta="Live tracked shoppers" icon={Users}/><StatCard label="24h visitors" value={summary?.total_visitors??"—"} meta="Unique tracked visitors" icon={Store}/><StatCard label="Average dwell" value={summary?.average_dwell_time?`${summary.average_dwell_time}s`:"—"} meta="Attention engagement" icon={Clock3}/><StatCard label="Top product" value={summary?.top_product??"—"} meta={summary?.peak_hour?`Peak ${summary.peak_hour}`:"No peak yet"} icon={Package}/></section>
 <section className="mt-5 grid gap-5 lg:grid-cols-[1.6fr_1fr]">
  <div className="rounded-xl border bg-white p-5 shadow-sm"><div className="flex items-center justify-between"><div><h2 className="font-semibold">Traffic today</h2><p className="text-xs text-slate-500">Hourly visitor volume</p></div><Button variant="outline" size="sm" onClick={()=>navigate("/analytics")}>Details</Button></div><div className="mt-6 flex h-48 items-end gap-2">{traffic.slice(-18).map((x,i)=><div key={i} className="flex min-w-0 flex-1 flex-col items-center justify-end gap-1"><div title={`${x.visitors} visitors`} className="w-full rounded-t bg-slate-800" style={{height:`${Math.max(6,(x.visitors/max)*150)}px`}}/><span className="text-[9px] text-slate-400">{x.hour?.slice(0,5)}</span></div>)}</div></div>
  <div className="rounded-xl border bg-white p-5 shadow-sm"><div className="flex items-center justify-between"><div><h2 className="font-semibold">Top products</h2><p className="text-xs text-slate-500">Attention score</p></div><Button variant="outline" size="sm" onClick={()=>navigate("/mapping/products")}>Mapping</Button></div><div className="mt-4 divide-y">{products.slice(0,6).map((p,i)=><div key={i} className="flex items-center justify-between py-3"><div className="flex items-center gap-3"><span className="text-xs text-slate-400">0{i+1}</span><div><b className="block text-sm">{p.product||p.product_name}</b><span className="text-xs text-slate-500">{p.customers??0} customers</span></div></div><b className="text-sm">{p.attention_score??p.score??"—"}</b></div>)}</div></div>
 </section>
 <section className="mt-5 grid gap-3 md:grid-cols-4"><Quick title="Stores" text="Manage locations" icon={Store} go={()=>navigate("/stores")}/><Quick title="Zones" text="CRUD + spatial layout" icon={Layers3} go={()=>navigate("/zones")}/><Quick title="Shelves" text="ROI + tiers" icon={Layers3} go={()=>navigate("/shelves")}/><Quick title="Cameras" text="CV sources" icon={Camera} go={()=>navigate("/cameras")}/></section>
 </div>;
}
function Quick({title,text,icon:Icon,go}){return <button onClick={go} className="rounded-xl border bg-white p-4 text-left shadow-sm hover:border-slate-300"><Icon size={18}/><b className="mt-3 block text-sm">{title}</b><span className="text-xs text-slate-500">{text}</span></button>}
