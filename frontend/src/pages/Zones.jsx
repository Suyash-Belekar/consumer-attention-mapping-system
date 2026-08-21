import React from "react";
import ResourcePage from "../components/ResourcePage";
import "./Zones.css";
export default function Zones(){return <ResourcePage resource="zones" title="Zones" description="Create and maintain store zones used by shelf and camera mappings." columns={[{key:"name",label:"Zone",render:r=>r.name||r.zone_name},{key:"store_id",label:"Store"},{key:"description",label:"Description"},{key:"is_active",label:"Status",render:r=><span className="text-emerald-600">{r.is_active===false?"Inactive":"Active"}</span>}]} fields={[{key:"name",label:"Zone name"},{key:"store_id",label:"Store ID"},{key:"description",label:"Description",required:false}]} normalize={f=>({store_id:f.store_id,zone_name:f.name,description:f.description||null})}/> }
