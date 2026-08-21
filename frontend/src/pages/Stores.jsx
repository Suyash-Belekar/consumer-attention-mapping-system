import React from "react";
import ResourcePage from "../components/ResourcePage";
import "./Stores.css";
export default function Stores(){return <ResourcePage resource="stores" title="Stores" description="Manage retail locations and their operational metadata." columns={[{key:"name",label:"Store",render:r=>r.name||r.store_name},{key:"location",label:"Location"},{key:"is_active",label:"Status",render:r=><span className="rounded-full bg-emerald-50 px-2 py-1 text-xs text-emerald-700">{r.is_active===false?"Inactive":"Active"}</span>}]} fields={[{key:"name",label:"Store name"},{key:"location",label:"Location"}]} normalize={f=>({name:f.name,location:f.location})}/> }
