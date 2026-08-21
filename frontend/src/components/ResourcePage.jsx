import React,{useEffect,useState} from "react";
import {Plus, Pencil, Trash2} from "lucide-react";
import PageHeader from "./PageHeader";
import DataTable from "./DataTable";
import Modal from "./Modal";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {listResource,createResource,updateResource,deleteResource} from "../api/resources";

export default function ResourcePage({resource,title,description,columns,fields=[],normalize={}}){
 const [rows,setRows]=useState([]),[loading,setLoading]=useState(true),[error,setError]=useState(""),[open,setOpen]=useState(false),[editing,setEditing]=useState(null),[form,setForm]=useState({});
 const load=async()=>{try{setLoading(true);setRows(await listResource(resource));setError("")}catch(e){setError(e.response?.data?.detail||"Unable to load records.")}finally{setLoading(false)}};
 useEffect(()=>{load()},[resource]);
 const submit=async e=>{e.preventDefault();try{const payload=normalize(form);editing?await updateResource(resource,editing.id,payload):await createResource(resource,payload);setOpen(false);setEditing(null);await load()}catch(e){setError(e.response?.data?.detail||"Unable to save record.")}};
 const remove=async id=>{if(!confirm("Delete this record?"))return;try{await deleteResource(resource,id);await load()}catch(e){setError(e.response?.data?.detail||"Unable to delete record.")}};
 const startEdit=r=>{setEditing(r);setForm(Object.fromEntries(fields.map(f=>[f.key,r[f.key]??""])));setOpen(true)};
 return <div>
  <PageHeader title={title} description={description} actions={<Button onClick={()=>{setEditing(null);setForm({});setOpen(true)}}><Plus size={16}/>Add</Button>}/>
  {error&&<div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
  <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
   <DataTable columns={[...columns,{key:"actions",label:"",render:r=><div className="flex justify-end gap-1"><button onClick={e=>{e.stopPropagation();startEdit(r)}} className="rounded-md p-2 hover:bg-slate-100"><Pencil size={15}/></button><button onClick={e=>{e.stopPropagation();remove(r.id)}} className="rounded-md p-2 text-red-500 hover:bg-red-50"><Trash2 size={15}/></button></div>}]} rows={rows} loading={loading}/>
  </div>
  <Modal open={open} onClose={()=>setOpen(false)} title={editing?`Edit ${title.slice(0,-1)}`:`Add ${title.slice(0,-1)}`}>
   <form onSubmit={submit} className="space-y-4">{fields.map(f=><label key={f.key} className="block"><span className="mb-1 block text-xs font-medium text-slate-600">{f.label}</span><Input value={form[f.key]??""} onChange={e=>setForm({...form,[f.key]:e.target.value})} required={f.required!==false}/></label>)}<div className="flex justify-end gap-2 pt-2"><Button type="button" variant="outline" onClick={()=>setOpen(false)}>Cancel</Button><Button type="submit">{editing?"Save changes":"Create"}</Button></div></form>
  </Modal>
 </div>;
}
