import React, { useCallback, useEffect, useState } from "react";
import { Camera as CameraIcon, Play, Square, Trash2, Upload, Video } from "lucide-react";

import PageHeader from "../components/PageHeader";
import { mappingApi } from "../api/mappingApi";
import { createResource, listResource } from "../api/resources";
import "./Cameras.css";

// =============================================================================
// Helpers
// =============================================================================
const getErrorMessage = (error, fallback) =>
  error?.response?.data?.detail || error?.response?.data?.message || error?.message || fallback;

const revokeUrl = (url) => {
  if (url) URL.revokeObjectURL(url);
};

const EMPTY_FORM = {
  id: "",
  name: "",
  store_id: "",
  source_type: "rtsp",
  source_url: "",
  frame_width: 1280,
  frame_height: 720,
};

// =============================================================================
// Custom Hook: useCameras
// =============================================================================
function useCameras() {
  const [rows, setRows] = useState([]);
  const [stores, setStores] = useState([]);
  const [error, setError] = useState("");
  const [busyAction, setBusyAction] = useState("");
  const [uploading, setUploading] = useState(false);

  // Load data
  const load = useCallback(async () => {
    try {
      setError("");
      const [cameraRows, storeRows] = await Promise.all([
        listResource("cameras"),
        listResource("stores"),
      ]);
      setRows(Array.isArray(cameraRows) ? cameraRows : []);
      setStores(Array.isArray(storeRows) ? storeRows : []);
    } catch (err) {
      setError(getErrorMessage(err, "Unable to load cameras."));
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Create camera + upload
  const createCameraWithUpload = useCallback(
    async (formData, selectedFile) => {
      setError("");
      if (formData.source_type === "upload" && !selectedFile) {
        setError("Please select a video file before registering.");
        return false;
      }

      try {
        setUploading(true);
        const camera = await createResource("cameras", formData);
        if (formData.source_type === "upload" && selectedFile) {
          await mappingApi.uploadCamera(camera.id, selectedFile);
        }
        await load();
        return true;
      } catch (err) {
        setError(getErrorMessage(err, "Unable to register/upload camera."));
        return false;
      } finally {
        setUploading(false);
      }
    },
    [load]
  );

  // Start/Stop
  const controlCamera = useCallback(
    async (id, action) => {
      if (busyAction) return;
      const actionKey = `${id}:${action}`;
      setBusyAction(actionKey);
      setError("");
      try {
        if (action === "start") await mappingApi.startCamera(id);
        else await mappingApi.stopCamera(id);
        await load();
      } catch (err) {
        setError(getErrorMessage(err, `Unable to ${action} camera.`));
      } finally {
        setBusyAction("");
      }
    },
    [busyAction, load]
  );

  // Delete
  const deleteCamera = useCallback(
    async (id, name) => {
      if (busyAction) return;
      if (!window.confirm(`Delete camera "${name || id}"?\n\nThis action cannot be undone.`)) return;

      setBusyAction(`${id}:delete`);
      setError("");
      try {
        await mappingApi.deleteCamera(id);
        await load();
      } catch (err) {
        setError(getErrorMessage(err, "Unable to delete camera."));
      } finally {
        setBusyAction("");
      }
    },
    [busyAction, load]
  );

  return {
    rows,
    stores,
    error,
    setError,
    busyAction,
    uploading,
    load,
    createCameraWithUpload,
    controlCamera,
    deleteCamera,
  };
}

// =============================================================================
// UI Components (all inside the same file)
// =============================================================================

// -----------------------------------------------------------------------------
// Field
// -----------------------------------------------------------------------------
function Field({ label, children, required = false }) {
  return (
    <label className="camera-field">
      <span>
        {label}
        {required && <em aria-hidden="true">*</em>}
      </span>
      {children}
    </label>
  );
}

// -----------------------------------------------------------------------------
// LocalVideoPreview
// -----------------------------------------------------------------------------
function LocalVideoPreview({ file, previewUrl }) {
  if (!file || !previewUrl) {
    return (
      <section className="camera-local-preview">
        <div className="camera-local-preview-header">
          <div>
            <span>LOCAL SOURCE PREVIEW</span>
            <h2>No video selected</h2>
            <small>Select a video file above to preview it before registering the camera.</small>
          </div>
        </div>
        <div className="camera-preview-empty">
          <Video size={32} />
          <strong>Video preview</strong>
          <span>Your selected camera video will appear here.</span>
        </div>
      </section>
    );
  }

  return (
    <section className="camera-local-preview">
      <div className="camera-local-preview-header">
        <div>
          <span>LOCAL SOURCE PREVIEW</span>
          <h2>Video selected for mapping</h2>
          <small>{file.name}</small>
        </div>
        <span className="camera-preview-live">LOCAL</span>
      </div>
      <div className="camera-preview-container">
        <video
          className="camera-preview-video"
          src={previewUrl}
          controls
          muted
          playsInline
          preload="metadata"
        >
          Your browser does not support HTML5 video.
        </video>
      </div>
      <div className="camera-preview-meta">
        <span>File: {file.name}</span>
        <span>Size: {(file.size / 1024 / 1024).toFixed(2)} MB</span>
        <span>Type: {file.type || "Unknown"}</span>
      </div>
    </section>
  );
}

// -----------------------------------------------------------------------------
// CameraForm
// -----------------------------------------------------------------------------
function CameraForm({
  stores,
  form,
  setForm,
  selectedFile,
  localVideo,
  uploading,
  onSourceTypeChange,
  onVideoSelect,
  onSubmit,
}) {
  const updateForm = useCallback(
    (field, value) => {
      setForm((current) => ({ ...current, [field]: value }));
    },
    [setForm]
  );

  const handleSubmit = useCallback(
    (event) => {
      event.preventDefault();
      onSubmit();
    },
    [onSubmit]
  );

  const isUpload = form.source_type === "upload";

  return (
    <section className="camera-register">
      <div className="camera-register-header">
        <span>CAMERA SOURCE</span>
        <h2>Add a camera feed</h2>
        <p>
          Use RTSP/HTTP for live cameras or upload a video for camera mapping and analytics.
        </p>
      </div>

      <form className="camera-form" onSubmit={handleSubmit}>
        <Field label="Camera ID" required>
          <input
            type="text"
            required
            value={form.id}
            onChange={(e) => updateForm("id", e.target.value)}
            placeholder="CAM-001"
            autoComplete="off"
          />
        </Field>

        <Field label="Name" required>
          <input
            type="text"
            required
            value={form.name}
            onChange={(e) => updateForm("name", e.target.value)}
            placeholder="Shelf Camera 1"
            autoComplete="off"
          />
        </Field>

        <Field label="Store" required>
          <select
            required
            value={form.store_id}
            onChange={(e) => updateForm("store_id", e.target.value)}
          >
            <option value="">Select store</option>
            {stores.map((store) => (
              <option key={store.id} value={store.id}>
                {store.name}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Source type" required>
          <select value={form.source_type} onChange={onSourceTypeChange}>
            <option value="rtsp">RTSP camera</option>
            <option value="http">HTTP/HLS</option>
            <option value="upload">Uploaded video</option>
          </select>
        </Field>

        {!isUpload && (
          <Field label="Stream / video URL">
            <input
              type="text"
              value={form.source_url}
              placeholder="rtsp://... or /media/video.mp4"
              onChange={(e) => updateForm("source_url", e.target.value)}
            />
          </Field>
        )}

        {isUpload && (
          <div className="camera-upload-wrapper">
            <label className="camera-upload">
              <span>
                <Upload size={14} />
                Upload camera video
              </span>
              <input
                type="file"
                accept="video/*,.mp4,.webm,.ogg,.mov"
                onChange={onVideoSelect}
              />
              <small>
                Select a video file to use as the camera source for ROI mapping and analytics.
              </small>
              {selectedFile && (
                <small className="camera-selected-file">
                  Selected: <strong>{selectedFile.name}</strong>
                </small>
              )}
            </label>

            <LocalVideoPreview file={selectedFile} previewUrl={localVideo} />
          </div>
        )}

        <button
          type="submit"
          disabled={uploading}
          aria-busy={uploading}
          className="camera-submit"
        >
          <CameraIcon size={15} />
          {uploading
            ? isUpload
              ? "Uploading video..."
              : "Registering..."
            : "Register camera"}
        </button>
      </form>
    </section>
  );
}

// -----------------------------------------------------------------------------
// CameraItem
// -----------------------------------------------------------------------------
function CameraItem({ camera, busyAction, onStart, onStop, onDelete }) {
  const { id, name, source_type, source_url, video_path, is_active } = camera;
  const isStarting = busyAction === `${id}:start`;
  const isStopping = busyAction === `${id}:stop`;
  const isDeleting = busyAction === `${id}:delete`;
  const isBusy = Boolean(busyAction);

  const source = source_url || (video_path ? "Uploaded video" : "No source configured");
  const isOffline = is_active === false;

  return (
    <article className="camera-item">
      <div className="camera-icon" aria-hidden="true">
        <CameraIcon size={18} />
      </div>

      <div className="camera-details">
        <strong>{name || id}</strong>
        <small>
          {id} · {source_type || "camera"} · {source}
        </small>
      </div>

      <span className={`camera-status ${isOffline ? "offline" : "ready"}`}>
        {isOffline ? "OFFLINE" : "READY"}
      </span>

      <div className="camera-actions">
        <button type="button" onClick={() => onStart(id)} disabled={isBusy}>
          <Play size={14} />
          {isStarting ? "Starting" : "Start"}
        </button>
        <button type="button" onClick={() => onStop(id)} disabled={isBusy}>
          <Square size={14} />
          {isStopping ? "Stopping" : "Stop"}
        </button>
        <button
          type="button"
          className="camera-delete"
          onClick={() => onDelete(id, name)}
          disabled={isBusy}
        >
          <Trash2 size={14} />
          {isDeleting ? "Deleting" : "Delete"}
        </button>
      </div>
    </article>
  );
}

// -----------------------------------------------------------------------------
// CameraList
// -----------------------------------------------------------------------------
function CameraList({ rows, busyAction, onStart, onStop, onDelete }) {
  return (
    <section className="camera-list">
      <header className="camera-list-header">
        <div>
          <span>CAMERA TOPOLOGY</span>
          <h2>Registered sources</h2>
        </div>
        <b>{rows.length}</b>
      </header>

      {rows.length === 0 ? (
        <div className="camera-empty">No cameras have been registered yet.</div>
      ) : (
        <div className="camera-list-items">
          {rows.map((camera) => (
            <CameraItem
              key={camera.id}
              camera={camera}
              busyAction={busyAction}
              onStart={onStart}
              onStop={onStop}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </section>
  );
}

// =============================================================================
// Main Component
// =============================================================================
export default function Cameras() {
  const {
    rows,
    stores,
    error,
    setError,
    busyAction,
    uploading,
    createCameraWithUpload,
    controlCamera,
    deleteCamera,
  } = useCameras();

  // Local state for form and video preview
  const [form, setForm] = useState(EMPTY_FORM);
  const [selectedFile, setSelectedFile] = useState(null);
  const [localVideo, setLocalVideo] = useState(null);

  // Cleanup preview on unmount
  useEffect(() => {
    return () => {
      revokeUrl(localVideo);
    };
  }, [localVideo]);

  // ---- Handlers ----
  const handleSourceTypeChange = useCallback((event) => {
    const sourceType = event.target.value;
    setForm((current) => ({
      ...current,
      source_type: sourceType,
      source_url: sourceType === "upload" ? "" : current.source_url,
    }));
    setError("");
    if (sourceType !== "upload") {
      setSelectedFile(null);
      setLocalVideo((prev) => {
        revokeUrl(prev);
        return null;
      });
    }
  }, [setError]);

  const handleVideoSelect = useCallback((event) => {
    const file = event.target.files?.[0];
    setError("");

    if (!file) {
      setSelectedFile(null);
      setLocalVideo((prev) => {
        revokeUrl(prev);
        return null;
      });
      return;
    }

    if (!file.type.startsWith("video/")) {
      setError("Please select a valid video file.");
      event.target.value = "";
      setSelectedFile(null);
      setLocalVideo((prev) => {
        revokeUrl(prev);
        return null;
      });
      return;
    }

    const previewUrl = URL.createObjectURL(file);
    setLocalVideo((prev) => {
      revokeUrl(prev);
      return previewUrl;
    });
    setSelectedFile(file);
    setForm((current) => ({
      ...current,
      source_type: "upload",
      source_url: "",
    }));
  }, [setError]);

  const resetVideo = useCallback(() => {
    setSelectedFile(null);
    setLocalVideo((prev) => {
      revokeUrl(prev);
      return null;
    });
  }, []);

  const handleSave = useCallback(async () => {
    const success = await createCameraWithUpload(form, selectedFile);
    if (success) {
      resetVideo();
      setForm(EMPTY_FORM);
    }
  }, [createCameraWithUpload, form, selectedFile, resetVideo]);

  return (
    <div className="cameras-page">
      <PageHeader
        title="Camera registry"
        description="Register RTSP/HTTP feeds and uploaded videos. Cameras are the source for zone, shelf and product ROI mapping."
      />

      {error && (
        <div className="camera-error" role="alert" aria-live="polite">
          {error}
        </div>
      )}

      <CameraForm
        stores={stores}
        form={form}
        setForm={setForm}
        selectedFile={selectedFile}
        localVideo={localVideo}
        uploading={uploading}
        onSourceTypeChange={handleSourceTypeChange}
        onVideoSelect={handleVideoSelect}
        onSubmit={handleSave}
      />

      <CameraList
        rows={rows}
        busyAction={busyAction}
        onStart={(id) => controlCamera(id, "start")}
        onStop={(id) => controlCamera(id, "stop")}
        onDelete={deleteCamera}
      />
    </div>
  );
}