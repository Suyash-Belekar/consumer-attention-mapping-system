import React,{useEffect,useState} from "react";
import {Plus,Pencil,Trash2} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import PageHeader from "../components/PageHeader";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import api from "../services/api";

import "./Shelves.css";
const empty={store_id:"",zone_id:"",camera_id:"",name:"",category:"",tier_count:1,roi_polygon:"[[0,0],[640,0],[640,400],[0,400]]"};
export default function Shelves(){
 const [rows,setRows]=useState([]),[form,setForm]=useState(empty),[editing,setEditing]=useState(null),[open,setOpen]=useState(false),[loading,setLoading]=useState(true),[error,setError]=useState("");
 const load=async()=>{try{setLoading(true);const {data}=await api.get("/shelves");setRows(data||[])}catch(e){setError(e.response?.data?.detail||"Unable to load shelves.")}finally{setLoading(false)}};
 useEffect(()=>{load()},[]);
 const save=async e=>{e.preventDefault();try{const payload={...form,store_id:form.store_id,zone_id:form.zone_id||null,camera_id:form.camera_id||null,tier_count:Number(form.tier_count),roi_polygon:typeof form.roi_polygon==="string"?JSON.parse(form.roi_polygon):form.roi_polygon};editing?await api.put(`/shelves/${editing.id}`,payload):await api.post("/shelves",payload);setOpen(false);await load()}catch(e){setError(e.response?.data?.detail||"Invalid shelf data. ROI must be valid JSON.")}};
 const remove=async id=>{if(!confirm("Delete this shelf?"))return;try{await api.delete(`/shelves/${id}`);await load()}catch(e){setError(e.response?.data?.detail||"Unable to delete shelf.")}};
 return <div><PageHeader title="Shelves" description="Manage shelf definitions, ROI geometry, tiers and camera assignments." actions={<Button onClick={()=>{setEditing(null);setForm(empty);setOpen(true)}}><Plus size={16}/>Add shelf</Button>}/>
 {error&&<div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
 <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"><DataTable loading={loading} rows={rows} columns={[
  {key:"name",label:"Shelf",render:r=><b>{r.name||r.shelf_name}</b>},{key:"store_id",label:"Store"},{key:"zone_id",label:"Zone"},{key:"camera_id",label:"Camera"},{key:"tier_count",label:"Tiers"},
  {key:"roi",label:"ROI",render:r=><span className="text-xs text-slate-500">{r.roi_polygon?.length??0} points</span>},
  {key:"actions",label:"",render:r=><div className="flex justify-end gap-1"><button onClick={()=>{setEditing(r);setForm({...empty,...r,roi_polygon:JSON.stringify(r.roi_polygon??[]) });setOpen(true)}} className="p-2 hover:bg-slate-100"><Pencil size={15}/></button><button onClick={()=>remove(r.id)} className="p-2 text-red-500 hover:bg-red-50"><Trash2 size={15}/></button></div>}
 ]}/></div>
 <Modal open={open} onClose={()=>setOpen(false)} title={editing?"Edit shelf":"Create shelf"}><form onSubmit={save} className="grid gap-4 sm:grid-cols-2">
 {["store_id","zone_id","camera_id","name","category","tier_count"].map(k=><label key={k}><span className="mb-1 block text-xs font-medium text-slate-600">{k.replace("_"," ")}</span><Input value={form[k]??""} onChange={e=>setForm({...form,[k]:e.target.value})} required={k!=="zone_id"&&k!=="camera_id"}/></label>)}
 <label className="sm:col-span-2"><span className="mb-1 block text-xs font-medium text-slate-600">ROI polygon JSON</span><textarea value={form.roi_polygon} onChange={e=>setForm({...form,roi_polygon:e.target.value})} className="min-h-24 w-full rounded-lg border border-slate-200 p-3 font-mono text-xs outline-none focus:ring-2 focus:ring-slate-300"/></label>
 <div className="sm:col-span-2 flex justify-end gap-2"><Button type="button" variant="outline" onClick={()=>setOpen(false)}>Cancel</Button><Button type="submit">Save shelf</Button></div>
 </form></Modal></div>;
}
