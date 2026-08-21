import React, { useEffect, useState } from "react";
import { ArrowLeft, Plus, Save, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import PageHeader from "../components/PageHeader";
import { listResource, createResource, updateResource, deleteResource } from "../api/resources";
import "./ShelfMapping.css";

const EMPTY = {
  store_id: "",
  zone_id: "",
  camera_id: "",
  name: "",
  category: "",
  tier_count: 1,
  roi_polygon: "[[120,80],[420,80],[420,240],[120,240]]",
};

export default function ShelfMapping() {
  const navigate = useNavigate();
  const [rows, setRows] = useState([]);
  const [stores, setStores] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [zones, setZones] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const load = async () => {
    try {
      setRows(await listResource("shelves"));
      setStores(await listResource("stores"));
      setCameras(await listResource("cameras"));
      setZones(await listResource("zones"));
    } catch (e) {
      setError(e.response?.data?.detail || "Unable to load mapping records.");
    }
  };

  useEffect(() => { load(); }, []);

  const save = async (event) => {
    event.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...form,
        tier_count: Number(form.tier_count),
        roi_polygon: JSON.parse(form.roi_polygon),
      };
      if (editing) await updateResource("shelves", editing.id, payload);
      else await createResource("shelves", payload);
      setForm(EMPTY);
      setEditing(null);
      await load();
    } catch (e) {
      setError(e.response?.data?.detail || "Unable to save shelf mapping.");
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id) => {
    if (!window.confirm("Delete this shelf mapping?")) return;
    try { await deleteResource("shelves", id); await load(); }
    catch (e) { setError(e.response?.data?.detail || "Unable to delete shelf."); }
  };

  return (
    <div className="shelf-mapping-page">
      <PageHeader
        title="Shelf mapping"
        description="Create, update and delete shelf ROIs, tiers and camera relationships."
        actions={
          <Button variant="outline" onClick={() => navigate("/mapping")}>
            <ArrowLeft size={15} /> Mapping overview
          </Button>
        }
      />

      {error && <div className="shelf-mapping-error">{error}</div>}

      <div className="shelf-mapping-grid">
        <section className="shelf-editor">
          <div className="shelf-editor-head">
            <div><span>EDITOR</span><h2>{editing ? "Update shelf" : "Create shelf"}</h2></div>
            {editing && <button onClick={() => { setEditing(null); setForm(EMPTY); }}>Clear</button>}
          </div>

          <form onSubmit={save} className="shelf-form">
            <Field label="Shelf name"><input value={form.name} required onChange={e => setForm({...form,name:e.target.value})} /></Field>
            <Field label="Store"><select value={form.store_id} required onChange={e => setForm({...form,store_id:e.target.value})}><option value="">Select</option>{stores.map(x=><option key={x.id} value={x.id}>{x.name}</option>)}</select></Field>
            <Field label="Zone"><select value={form.zone_id} onChange={e => setForm({...form,zone_id:e.target.value})}><option value="">None</option>{zones.map(x=><option key={x.id} value={x.id}>{x.name}</option>)}</select></Field>
            <Field label="Camera"><select value={form.camera_id} onChange={e => setForm({...form,camera_id:e.target.value})}><option value="">None</option>{cameras.map(x=><option key={x.id} value={x.id}>{x.name || x.id}</option>)}</select></Field>
            <Field label="Category"><input value={form.category} onChange={e => setForm({...form,category:e.target.value})} /></Field>
            <Field label="Tier count"><input type="number" min="1" value={form.tier_count} onChange={e => setForm({...form,tier_count:e.target.value})} /></Field>
            <Field label="ROI polygon JSON" full><textarea rows="5" value={form.roi_polygon} required onChange={e => setForm({...form,roi_polygon:e.target.value})} /></Field>
            <Button type="submit" disabled={saving}><Save size={15}/>{saving ? "Saving..." : editing ? "Save changes" : "Create shelf"}</Button>
          </form>
        </section>

        <section className="shelf-list">
          <div className="shelf-editor-head"><div><span>REGISTERED SHELVES</span><h2>Store shelf map</h2></div><b>{rows.length}</b></div>
          <div className="shelf-table">
            {rows.map((row) => (
              <div className="shelf-row" key={row.id}>
                <div><strong>{row.name || row.shelf_name}</strong><small>{row.category || "Uncategorized"} · {row.tier_count ?? 1} tiers</small></div>
                <span>{row.camera_id || "No camera"}</span>
                <div className="shelf-actions">
                  <button onClick={() => { setEditing(row); setForm({...row,roi_polygon:JSON.stringify(row.roi_polygon ?? [])}); }}>Edit</button>
                  <button className="danger" onClick={() => remove(row.id)}><Trash2 size={14}/></button>
                </div>
              </div>
            ))}
            {!rows.length && <div className="shelf-empty"><Plus size={20}/><p>No shelves mapped yet.</p></div>}
          </div>
        </section>
      </div>
    </div>
  );
}

function Field({label,children,full}) {
  return <label className={full ? "shelf-field shelf-field-full" : "shelf-field"}><span>{label}</span>{children}</label>;
}
