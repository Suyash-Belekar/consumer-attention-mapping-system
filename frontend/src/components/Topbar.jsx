import React from "react";
import { Bell, Search, ChevronDown } from "lucide-react";

export default function Topbar() {
  return <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur sm:px-6 lg:px-8">
    <div className="hidden items-center gap-3 lg:flex">
      <div className="text-sm font-medium text-slate-700">Retail workspace</div>
      <span className="text-slate-300">/</span>
      <span className="text-sm text-slate-500">Flagship operations</span>
    </div>
    <div className="ml-12 flex flex-1 items-center justify-end gap-2 sm:gap-4 lg:ml-0">
      <label className="hidden items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 sm:flex sm:w-64">
        <Search size={16} className="text-slate-400"/><input className="w-full bg-transparent text-sm outline-none" placeholder="Search..."/>
      </label>
      <button className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"><Bell size={18}/></button>
      <button className="flex items-center gap-2 rounded-lg border border-slate-200 px-2.5 py-1.5">
        <span className="grid h-7 w-7 place-items-center rounded-full bg-slate-900 text-xs font-semibold text-white">A</span>
        <span className="hidden text-left sm:block"><b className="block text-xs">Administrator</b><small className="text-[10px] text-slate-500">Operations</small></span>
        <ChevronDown size={14} className="text-slate-400"/>
      </button>
    </div>
  </header>;
}
