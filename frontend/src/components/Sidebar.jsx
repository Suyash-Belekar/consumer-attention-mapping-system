import React, { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  Activity, BarChart3, Brain, Camera, ChevronRight, LayoutDashboard, FileBarChart2, Bell,
  Lightbulb, Map, Menu, Package, Settings, Store, X, Layers3
} from "lucide-react";

const groups = [
  { label:"Workspace", items:[
    ["Overview","/dashboard",LayoutDashboard],["Analytics","/analytics",BarChart3],["Recommendations","/recommendations",Lightbulb],["Reports","/reports",FileBarChart2],["Alerts","/alerts",Bell],
  ]},
  { label:"Store operations", items:[
    ["Stores","/stores",Store],["Zones","/zones",Map],["Shelves","/shelves",Layers3],["Cameras","/cameras",Camera],
  ]},
  { label:"Spatial operations", items:[
    ["Camera mapping","/mapping",Map],["Zone & shelf mapping","/mapping/workspace",Layers3],["Live tracking","/tracking",Activity],
  ]},
  { label:"Product intelligence", items:[
    ["Products","/products",Package],["Product mapping","/mapping/products",Layers3],["Product scores","/analytics/products",Brain],
  ]},
  { label:"Insights", items:[
    ["Behavior","/analytics/behavior",Brain],["Heatmaps","/analytics/heatmaps",Activity],
  ]},
];

export default function Sidebar() {
  const [mobile, setMobile] = useState(false);
  const location = useLocation();

  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/";
  };

  const content = (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center justify-between border-b border-slate-200 px-5">
        <NavLink to="/dashboard" className="flex items-center gap-3">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-slate-950 text-[10px] font-bold text-white">
            CAM
          </span>
          <span>
            <b className="block text-sm">Attention Mapping</b>
            <small className="text-[11px] text-slate-500">Enterprise console</small>
          </span>
        </NavLink>
        <button className="lg:hidden" onClick={() => setMobile(false)}><X size={19} /></button>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {groups.map((group) => (
          <div key={group.label} className="mb-5">
            <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-400">
              {group.label}
            </div>

            <div className="space-y-1">
              {group.items.map(([label, path, Icon]) => {
                const active =
                  location.pathname === path ||
                  (path !== "/dashboard" && location.pathname.startsWith(`${path}/`));

                return (
                  <NavLink
                    key={path}
                    to={path}
                    onClick={() => setMobile(false)}
                    className={`group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                      active
                        ? "bg-slate-950 text-white"
                        : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <Icon size={17} />
                    <span className="flex-1">{label}</span>
                    {active && <ChevronRight size={14} />}
                  </NavLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-slate-200 p-3">
        <NavLink
          to="/settings"
          className="mb-1 flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-600 hover:bg-slate-100"
        >
          <Settings size={17} /> Settings
        </NavLink>
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-600 hover:bg-red-50 hover:text-red-600"
        >
          Sign out
        </button>
      </div>
    </div>
  );

  return (
    <>
      <button
        className="fixed left-4 top-4 z-50 rounded-lg border bg-white p-2 shadow-sm lg:hidden"
        onClick={() => setMobile(true)}
      >
        <Menu size={19} />
      </button>

      <aside className={`fixed inset-y-0 left-0 z-40 w-64 border-r border-slate-200 bg-white transition-transform lg:translate-x-0 ${
        mobile ? "translate-x-0" : "-translate-x-full"
      }`}>
        {content}
      </aside>

      {mobile && (
        <div
          className="fixed inset-0 z-30 bg-slate-950/20 lg:hidden"
          onClick={() => setMobile(false)}
        />
      )}
    </>
  );
}
