import React from "react";
import "./MappingCameraGrid.css";

const ITEMS = [
  { id:"shelf-a", type:"shelf", label:"Shelf A", x:"16%", y:"22%", w:"42%", h:"32%" },
  { id:"shelf-b", type:"shelf", label:"Shelf B", x:"62%", y:"49%", w:"26%", h:"25%" },
];

export default function MappingCameraGrid({ cameraIds, onSelectEntity }) {
  return (
    <div className={`mapping-camera-grid count-${Math.min(cameraIds.length,4)}`}>
      {cameraIds.map((cameraId) => (
        <div className="mapping-camera" key={cameraId}>
          <div className="mapping-camera-bar"><strong>{cameraId.replace("-", " ").toUpperCase()}</strong><span>LIVE PREVIEW</span></div>
          <div className="mapping-canvas">
            <span className="mapping-placeholder">Camera feed</span>
            {ITEMS.map((item) => (
              <button key={item.id} className="mapping-roi" style={{left:item.x,top:item.y,width:item.w,height:item.h}} onClick={() => onSelectEntity(item)}>
                {item.label}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
