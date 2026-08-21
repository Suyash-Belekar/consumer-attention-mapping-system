import React from "react";
export default function StatCard({label,value,meta,icon:Icon}) {
 return <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
  <div className="flex items-start justify-between"><span className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</span>{Icon&&<span className="rounded-lg bg-slate-100 p-2 text-slate-600"><Icon size={16}/></span>}</div>
  <div className="mt-3 text-2xl font-semibold text-slate-950">{value}</div>{meta&&<div className="mt-1 text-xs text-slate-500">{meta}</div>}
 </div>;
}
