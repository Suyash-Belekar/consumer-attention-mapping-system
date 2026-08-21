import React from "react";
import "./CameraGrid.css";
import CameraFeed from "./CameraFeed";
export default function CameraGrid({cameraIds,mode}){return <div className={`camera-grid count-${Math.min(cameraIds.length,4)}`}>{cameraIds.map(id=><CameraFeed key={id} cameraId={id} mode={mode}/>)}</div>;}