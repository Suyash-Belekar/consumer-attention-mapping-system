import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Camera as CameraIcon, RefreshCw } from "lucide-react";

import PageHeader from "../components/PageHeader";
import { mappingApi } from "../api/mappingApi";

export default function CameraPage() {
  const [cameras, setCameras] = useState([]);
  const [cameraId, setCameraId] = useState("");
  const [snapshotUrl, setSnapshotUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const selectedCamera = useMemo(
    () => cameras.find((camera) => String(camera.id) === String(cameraId)),
    [cameras, cameraId]
  );

  const getErrorMessage = (error, fallback) =>
    error?.response?.data?.detail || fallback;

  const loadCameras = useCallback(async () => {
    try {
      setError("");

      const rows = await mappingApi.listCameras();
      const cameraList = Array.isArray(rows) ? rows : [];

      setCameras(cameraList);

      setCameraId((currentId) => {
        if (currentId && cameraList.some((camera) => camera.id === currentId)) {
          return currentId;
        }

        return cameraList[0]?.id ? String(cameraList[0].id) : "";
      });
    } catch (error) {
      setError(getErrorMessage(error, "Unable to load cameras."));
      setCameras([]);
    }
  }, []);

  const captureSnapshot = useCallback(async () => {
    if (!cameraId) {
      return;
    }

    try {
      setLoading(true);
      setError("");

      const blob = await mappingApi.snapshot(cameraId);

      if (!(blob instanceof Blob)) {
        throw new Error("Invalid camera snapshot response.");
      }

      const nextUrl = URL.createObjectURL(blob);

      setSnapshotUrl((currentUrl) => {
        if (currentUrl) {
          URL.revokeObjectURL(currentUrl);
        }

        return nextUrl;
      });
    } catch (error) {
      setError(
        getErrorMessage(error, "Unable to capture a camera frame.")
      );
    } finally {
      setLoading(false);
    }
  }, [cameraId]);

  useEffect(() => {
    loadCameras();
  }, [loadCameras]);

  useEffect(() => {
    if (cameraId) {
      captureSnapshot();
    } else {
      setSnapshotUrl("");
    }
  }, [cameraId, captureSnapshot]);

  useEffect(() => {
    return () => {
      setSnapshotUrl((currentUrl) => {
        if (currentUrl) {
          URL.revokeObjectURL(currentUrl);
        }

        return "";
      });
    };
  }, []);

  const handleCameraChange = (event) => {
    setCameraId(event.target.value);
    setError("");
  };

  return (
    <div className="mx-auto max-w-7xl">
      <PageHeader
        title="Camera Monitor"
        description="Preview a registered CAMS camera through the authenticated backend snapshot endpoint."
        actions={
          <button
            type="button"
            onClick={captureSnapshot}
            disabled={!cameraId || loading}
            className="inline-flex items-center gap-2 rounded-lg bg-slate-950 px-4 py-2 text-sm text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCw
              size={14}
              className={loading ? "animate-spin" : ""}
            />
            {loading ? "Refreshing..." : "Refresh frame"}
          </button>
        }
      />

      {error && (
        <div
          role="alert"
          className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
        <section
          aria-label="Camera preview"
          className="overflow-hidden rounded-xl border bg-black shadow-sm"
        >
          {snapshotUrl ? (
            <img
              src={snapshotUrl}
              alt={
                selectedCamera
                  ? `${selectedCamera.name || selectedCamera.id} snapshot`
                  : "Camera snapshot"
              }
              className="aspect-video w-full object-contain"
            />
          ) : (
            <div className="grid aspect-video place-items-center text-slate-500">
              <div className="flex flex-col items-center gap-2">
                <CameraIcon size={32} />
                <span className="text-sm">
                  {cameraId
                    ? "Waiting for camera frame..."
                    : "Select a camera to preview"}
                </span>
              </div>
            </div>
          )}
        </section>

        <aside className="rounded-xl border bg-white p-5">
          <label className="block">
            <span className="mb-2 block text-xs font-medium text-slate-600">
              Registered camera
            </span>

            <select
              value={cameraId}
              onChange={handleCameraChange}
              className="w-full rounded-lg border border-slate-300 bg-white p-2 text-sm outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
            >
              <option value="">Select camera</option>

              {cameras.map((camera) => (
                <option key={camera.id} value={camera.id}>
                  {camera.name || camera.id}
                </option>
              ))}
            </select>
          </label>

          {selectedCamera && (
            <div className="mt-5 space-y-3 text-sm text-slate-600">
              <div className="flex items-center justify-between gap-4">
                <span className="font-medium text-slate-700">Status</span>
                <span>{selectedCamera.status || "—"}</span>
              </div>

              <div className="flex items-center justify-between gap-4">
                <span className="font-medium text-slate-700">Source</span>
                <span>{selectedCamera.source_type || "—"}</span>
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

