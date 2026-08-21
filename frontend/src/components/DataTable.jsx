import React from "react";
export default function DataTable({columns,rows,loading,empty="No records found.",onRow}) {
 if(loading) return <div className="p-8 text-center text-sm text-slate-500">Loading...</div>;
 return <div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500"><tr>{columns.map(c=><th key={c.key} className="px-4 py-3 font-semibold">{c.label}</th>)}</tr></thead><tbody className="divide-y divide-slate-100">{rows.length?rows.map((r,i)=><tr key={r.id??i} onClick={()=>onRow?.(r)} className={onRow?"cursor-pointer hover:bg-slate-50":""}>{columns.map(c=><td key={c.key} className="px-4 py-3 text-slate-700">{c.render?c.render(r):r[c.key]??"—"}</td>)}</tr>):<tr><td colSpan={columns.length} className="p-10 text-center text-slate-400">{empty}</td></tr>}</tbody></table></div>;
}
