import React from "react";
import "./CameraSelector.css";

const CAMERAS = [
  ["camera-01","Camera 01","online"],
  ["camera-02","Camera 02","online"],
  ["camera-03","Camera 03","online"],
  ["camera-04","Camera 04","offline"],
];

export default function CameraSelector({ selectedCameraIds, onChange }) {
  const toggle = (id) => {
    const next = selectedCameraIds.includes(id)
      ? selectedCameraIds.filter((value) => value !== id)
      : [...selectedCameraIds, id];
    onChange(next.length ? next : [id]);
  };

  return (
    <div className="camera-selector">
      <div><strong>Camera coverage</strong><span>Choose synchronized store views.</span></div>
      <div className="camera-selector-list">
        {CAMERAS.map(([id,name,status]) => (
          <button key={id} className={selectedCameraIds.includes(id) ? "camera-chip active" : "camera-chip"} onClick={() => toggle(id)}>
            <i className={`camera-status ${status}`} />{name}
          </button>
        ))}
      </div>
    </div>
  );
}
