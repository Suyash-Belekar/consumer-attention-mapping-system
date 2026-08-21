import React, { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";
import PageHeader from "../components/PageHeader";
import { fetchAlerts, markAlertRead } from "../api/analyticsApi";
import { listResource } from "../api/resources";

export default function Alerts(){
 const [stores,setStores]=useState([]),[storeId,setStoreId]=useState(""),[rows,setRows]=useState([]),[error,setError]=useState("");
 const load=async()=>{try{setRows(await fetchAlerts(storeId,false));setError("")}catch(e){setError(e.response?.data?.detail||"Unable to load alerts.")}};
 useEffect(()=>{listResource("stores").then(x=>{setStores(x);if(x[0]?.id)setStoreId(x[0].id)}).catch(()=>setError("Unable to load stores."))},[]);useEffect(()=>{if(storeId)load()},[storeId]);
 const read=async(id)=>{try{await markAlertRead(id);load()}catch(e){setError(e.response?.data?.detail||"Unable to mark alert as read.")}};
 return <div className="mx-auto max-w-7xl"><PageHeader title="Alerts" description="Monitor platform, camera, traffic and shelf performance notifications." actions={<select value={storeId} onChange={e=>setStoreId(e.target.value)}><option value="">Store</option>{stores.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select>}/>{error&&<div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}<div className="space-y-3">{rows.map(a=><article key={a.id} className="flex items-start gap-4 rounded-xl border bg-white p-4 shadow-sm"><span className="rounded-lg bg-amber-50 p-2 text-amber-700"><AlertTriangle size={18}/></span><div className="min-w-0 flex-1"><div className="flex justify-between gap-3"><b>{a.title}</b><span className="text-xs uppercase text-slate-400">{a.severity}</span></div><p className="mt-1 text-sm text-slate-600">{a.message}</p><small className="text-xs text-slate-400">{new Date(a.created_at).toLocaleString()}</small></div>{!a.is_read&&<button onClick={()=>read(a.id)} className="inline-flex items-center gap-1 rounded-lg border px-3 py-2 text-xs"><CheckCircle2 size={13}/> Mark read</button>}</article>)}{!rows.length&&<div className="rounded-xl border border-dashed p-10 text-center text-sm text-slate-500">No alerts for this store.</div>}</div></div>
}
