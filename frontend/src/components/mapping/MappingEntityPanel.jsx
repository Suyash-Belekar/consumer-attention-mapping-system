import React from "react";
import "./MappingEntityPanel.css";

export default function MappingEntityPanel({ entity }) {
  const type = entity?.type || "shelf";
  return (
    <aside className="mapping-entity-panel">
      <div className="mapping-panel-heading">
        <div><span>SELECTED OBJECT</span><h2>{entity?.id === "shelf-b" ? "Shelf B" : "Shelf A"}</h2></div>
        <button>⋯</button>
      </div>
      <label>Mapping type</label>
      <select value={type} readOnly><option>shelf</option><option>product</option></select>
      <label>Camera relationship</label>
      <div className="mapping-camera-links"><span>Camera 01 · Primary</span><span>Camera 02 · Side view</span></div>
      <label>Configuration</label>
      <div className="mapping-fields"><div><small>ROI</small><strong>Configured</strong></div><div><small>TIERS</small><strong>3</strong></div><div><small>PRODUCTS</small><strong>8</strong></div></div>
      <div className="mapping-panel-actions"><button>Delete</button><button className="save">Save changes</button></div>
    </aside>
  );
}
