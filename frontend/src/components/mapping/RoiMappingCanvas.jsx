import React, { useEffect, useRef, useState } from "react";
import { mappingApi } from "../../api/mappingApi";
import "./RoiMappingCanvas.css";

/**
 * Camera-backed ROI editor.
 * Coordinates are stored in the camera's native frame coordinate system.
 * The same editor can draw zone/shelf polygons or product rectangles.
 */
export default function RoiMappingCanvas({
  camera,
  mode = "polygon",
  initialPoints = [],
  onChange,
  title = "Camera mapping",
}) {
  const stageRef = useRef(null);
  const [points, setPoints] = useState(initialPoints);
  const [imageUrl, setImageUrl] = useState("");
  const [mediaError, setMediaError] = useState(false);

  useEffect(() => setPoints(initialPoints ?? []), [JSON.stringify(initialPoints)]);

  useEffect(() => {
    onChange?.(points);
  }, [points, onChange]);

  useEffect(() => {
    let current = "";
    let disposed = false;
    const load = async () => {
      if (!camera?.id) { setImageUrl(""); return; }
      try {
        const blob = await mappingApi.snapshot(camera.id);
        if (disposed) return;
        current = URL.createObjectURL(blob);
        setImageUrl(current);
        setMediaError(false);
      } catch {
        if (!disposed) { setImageUrl(""); setMediaError(true); }
      }
    };
    load();
    const timer = camera?.id ? setInterval(load, 3000) : null;
    return () => { disposed = true; if (timer) clearInterval(timer); if (current) URL.revokeObjectURL(current); };
  }, [camera?.id]);
  const addPoint = (event) => {
    if (mode === "rectangle" && points.length >= 2) return;
    const rect = stageRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.round(((event.clientX - rect.left) / rect.width) * (camera?.frame_width || 1280)));
    const y = Math.max(0, Math.round(((event.clientY - rect.top) / rect.height) * (camera?.frame_height || 720)));
    setPoints((current) => [...current, [x, y]]);
  };

  const undo = () => setPoints((p) => p.slice(0, -1));
  const clear = () => setPoints([]);
  const polygon = points.map((p) => p.join(",")).join(" ");
  const rectangle =
    points.length >= 2
      ? `${Math.min(points[0][0], points[1][0])},${Math.min(points[0][1], points[1][1])} ${Math.max(points[0][0], points[1][0])},${Math.min(points[0][1], points[1][1])} ${Math.max(points[0][0], points[1][0])},${Math.max(points[0][1], points[1][1])} ${Math.min(points[0][0], points[1][0])},${Math.max(points[0][1], points[1][1])}`
      : "";

  return (
    <section className="roi-editor">
      <header className="roi-editor-head">
        <div><span>CAMERA ROI EDITOR</span><h2>{title}</h2></div>
        <div className="roi-tools">
          <button type="button" onClick={undo} disabled={!points.length}>Undo</button>
          <button type="button" onClick={clear} disabled={!points.length}>Clear</button>
        </div>
      </header>
      <div ref={stageRef} className="roi-stage" onClick={addPoint}>
        {imageUrl && !mediaError ? (
          <img className="roi-media" src={imageUrl} alt={`${camera?.name || camera?.id || "Camera"} snapshot`} />
        ) : (
          <div className="roi-placeholder">
            <strong>{camera?.name || camera?.id || "Select a camera"}</strong>
            <small>{camera ? "Camera snapshot unavailable" : "Select a camera"}</small>
          </div>
        )}
        <svg className="roi-svg" viewBox={`0 0 ${camera?.frame_width || 1280} ${camera?.frame_height || 720}`} preserveAspectRatio="none">
          {mode === "rectangle" && rectangle && <polygon points={rectangle} className="roi-shape product-roi" />}
          {mode !== "rectangle" && polygon && <polygon points={polygon} className="roi-shape" />}
          {points.map((p, i) => <circle key={`${p[0]}-${p[1]}-${i}`} cx={p[0]} cy={p[1]} r="7" className="roi-point" />)}
        </svg>
      </div>
      <footer className="roi-editor-foot">
        <span>{mode === "rectangle" ? "Click two opposite corners." : "Click each polygon vertex; close the polygon by clicking near the first point."}</span>
        <b>{points.length} points</b>
      </footer>
    </section>
  );
}
