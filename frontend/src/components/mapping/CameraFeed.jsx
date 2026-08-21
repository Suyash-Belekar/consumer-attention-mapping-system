import React from "react";
import "./CameraFeed.css";
export default function CameraFeed({cameraId,mode}){
 return <div className="camera-feed"><div className="camera-feed-top"><strong>{cameraId.replace("-"," ").toUpperCase()}</strong><span>LIVE</span></div><div className="camera-feed-canvas"><span>Camera feed</span><div className="shelf-overlay shelf-a">Shelf A</div><div className="shelf-overlay shelf-b">Shelf B</div>{mode!=="select"&&<div className="mapping-crosshair"/>}</div></div>;
}