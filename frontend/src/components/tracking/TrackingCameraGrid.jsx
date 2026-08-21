import React from "react";
import "./TrackingCameraGrid.css";
export default function TrackingCameraGrid({ cameraIds, onSelectShopper }) {
  return <div className="tracking-grid">{cameraIds.map((id,index)=>
    <div className="tracking-camera" key={id}>
      <div className="tracking-camera-bar"><strong>{id.replace("-"," ").toUpperCase()}</strong><span>● ONLINE</span></div>
      <div className="tracking-feed">
        <button className="shopper-dot shopper-one" onClick={()=>onSelectShopper(104)}>104</button>
        {index!==2 && <button className="shopper-dot shopper-two" onClick={()=>onSelectShopper(117)}>117</button>}
        <div className="tracking-shelf">Shelf A</div>
      </div>
    </div>
  )}</div>;
}
