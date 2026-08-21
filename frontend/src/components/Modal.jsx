import React from "react";
import { X } from "lucide-react";
export default function Modal({open,onClose,title,children}) {
 if(!open)return null;
 return <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/30 p-4 backdrop-blur-sm">
  <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white shadow-2xl">
   <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4"><h2 className="font-semibold">{title}</h2><button onClick={onClose}><X size={18}/></button></div>
   <div className="p-5">{children}</div>
  </div>
 </div>;
}
