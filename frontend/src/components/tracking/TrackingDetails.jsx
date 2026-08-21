import React from "react";
import "./TrackingDetails.css";
export default function TrackingDetails({ shopperId }) {
  return <aside className="tracking-details">
    <div className="tracking-detail-head"><span>GLOBAL SHOPPER</span><h2>#{shopperId}</h2><b>ACTIVE</b></div>
    <div className="tracking-metrics"><div><small>CAMERAS</small><strong>01 → 02</strong></div><div><small>DWELL</small><strong>14.2s</strong></div><div><small>ATTENTION</small><strong>0.82</strong></div></div>
    <section><label>Current location</label><strong>Shelf A · Camera 02</strong></section>
    <section><label>Product attention</label><strong>Coca-Cola 500ml</strong><small>Mapped product · 82% attention confidence</small></section>
    <section><label>Session</label><div className="session-line"><span>Entry</span><b>14:40:03</b></div><div className="session-line"><span>Last seen</span><b>14:40:17</b></div></section>
  </aside>;
}
