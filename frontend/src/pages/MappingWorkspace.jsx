import React, { useCallback, useEffect, useMemo, useState } from "react";
import { MapPinned, Save, Trash2 } from "lucide-react";

import PageHeader from "../components/PageHeader";
import RoiMappingCanvas from "../components/mapping/RoiMappingCanvas";
import { mappingApi } from "../api/mappingApi";
import { listResource } from "../api/resources";

import "./MappingWorkspace.css";

// ---------------------------------------------------------------------
// Constants & helpers
// ---------------------------------------------------------------------
const EMPTY_FORM = {
  name: "",
  store_id: "",
  zone_id: "",
  camera_id: "",
  category: "",
  tier_count: 1,
  roi_polygon: [],
};

const MIN_ROI_POINTS = 4;

const normalizeId = (value) => (value == null ? "" : String(value));
const normalizeArray = (value) => (Array.isArray(value) ? value : []);
const getPolygon = (item) =>
  Array.isArray(item?.roi_polygon)
    ? item.roi_polygon
    : Array.isArray(item?.zone_coordinates)
    ? item.zone_coordinates
    : [];
const getItemName = (item) =>
  item?.name || item?.shelf_name || item?.zone_name || "Unnamed mapping";

const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const messages = detail.map((d) => d?.msg).filter(Boolean);
    if (messages.length) return messages.join(", ");
  }
  return error?.message?.trim() || fallback;
};

// ---------------------------------------------------------------------
// Custom Hook: useMappingWorkspace
// ---------------------------------------------------------------------
function useMappingWorkspace() {
  // ---- Data ----
  const [stores, setStores] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [zones, setZones] = useState([]);
  const [shelves, setShelves] = useState([]);

  // ---- Selections ----
  const [storeId, setStoreId] = useState("");
  const [cameraId, setCameraId] = useState("");
  const [tab, setTab] = useState("zone");

  // ---- Form / Editor ----
  const [form, setForm] = useState(EMPTY_FORM);
  const [editing, setEditing] = useState(null);

  // ---- UI states ----
  const [loading, setLoading] = useState(true);
  const [loadingStoreData, setLoadingStoreData] = useState(false);
  const [loadingShelves, setLoadingShelves] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");

  // ---- Derived ----
  const availableCameras = useMemo(() => {
    if (!storeId) return cameras;
    return cameras.filter((c) => normalizeId(c.store_id) === normalizeId(storeId));
  }, [cameras, storeId]);

  const selectedCamera = useMemo(
    () => cameras.find((c) => normalizeId(c.id) === normalizeId(cameraId)) || null,
    [cameras, cameraId]
  );

  const currentList = useMemo(
    () => (tab === "zone" ? zones : shelves),
    [tab, zones, shelves]
  );

  // ---- Reset editor ----
  const resetEditor = useCallback(() => {
    setEditing(null);
    setForm({ ...EMPTY_FORM, store_id: storeId, camera_id: cameraId });
    setError("");
  }, [storeId, cameraId]);

  // ---- Begin editing ----
  const beginEditing = useCallback(
    (item) => {
      if (!item) return;
      const polygon = getPolygon(item);
      setEditing(item);
      setForm({
        ...EMPTY_FORM,
        ...item,
        store_id: item.store_id || storeId,
        camera_id: item.camera_id || cameraId,
        roi_polygon: polygon,
        tier_count: Number(item.tier_count || 1),
      });
      if (item.camera_id) setCameraId(normalizeId(item.camera_id));
      setError("");
    },
    [storeId, cameraId]
  );

  // ---- Load initial data ----
  useEffect(() => {
    let cancelled = false;

    async function init() {
      setLoading(true);
      setError("");
      try {
        const [storeResult, cameraResult] = await Promise.all([
          listResource("stores"),
          mappingApi.listCameras(),
        ]);
        if (cancelled) return;

        const nextStores = normalizeArray(storeResult);
        const nextCameras = normalizeArray(cameraResult);
        setStores(nextStores);
        setCameras(nextCameras);

        if (nextStores.length) setStoreId(normalizeId(nextStores[0].id));
        if (nextCameras.length) setCameraId(normalizeId(nextCameras[0].id));
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err, "Unable to load workspace."));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    init();
    return () => { cancelled = true; };
  }, []);

  // ---- Load store‑specific data (zones + cameras) ----
  useEffect(() => {
    if (!storeId) {
      setZones([]);
      setCameras([]);
      setShelves([]);
      setCameraId("");
      return;
    }

    let cancelled = false;

    async function loadStoreData() {
      setLoadingStoreData(true);
      try {
        const [zoneResult, cameraResult] = await Promise.all([
          mappingApi.listZones({ store_id: storeId }),
          mappingApi.listCameras(storeId),
        ]);
        if (cancelled) return;

        const nextZones = normalizeArray(zoneResult);
        const nextCameras = normalizeArray(cameraResult);
        setZones(nextZones);
        setCameras((prev) => {
          // Merge with existing cameras but keep the ones for this store
          // We'll simply replace to ensure consistency.
          return nextCameras;
        });

        // If current cameraId not in this store's list, pick first or clear
        const exists = nextCameras.some((c) => normalizeId(c.id) === normalizeId(cameraId));
        if (!exists) {
          setCameraId(nextCameras.length ? normalizeId(nextCameras[0].id) : "");
        }
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err, "Unable to load store data."));
      } finally {
        if (!cancelled) setLoadingStoreData(false);
      }
    }

    loadStoreData();
    return () => { cancelled = true; };
  }, [storeId]); // No cameraId dependency to avoid loops

  // ---- Load shelves when camera changes ----
  useEffect(() => {
    if (!cameraId) {
      setShelves([]);
      return;
    }

    let cancelled = false;

    async function loadShelvesForCamera() {
      setLoadingShelves(true);
      try {
        const params = { camera_id: cameraId };
        if (storeId) params.store_id = storeId;
        const result = await mappingApi.listShelves(params);
        if (!cancelled) setShelves(normalizeArray(result));
      } catch (err) {
        if (!cancelled) setError(getErrorMessage(err, "Unable to load shelves."));
      } finally {
        if (!cancelled) setLoadingShelves(false);
      }
    }

    loadShelvesForCamera();
    return () => { cancelled = true; };
  }, [cameraId, storeId]);

  // ---- Handlers ----
  const handleStoreChange = useCallback(
    (e) => {
      const newStoreId = e.target.value;
      setStoreId(newStoreId);
      setCameraId("");
      setZones([]);
      setShelves([]);
      setEditing(null);
      setForm({ ...EMPTY_FORM, store_id: newStoreId });
      setError("");
    },
    []
  );

  const handleCameraChange = useCallback(
    (e) => {
      const newCameraId = e.target.value;
      setCameraId(newCameraId);
      setEditing(null);
      setForm((prev) => ({ ...prev, camera_id: newCameraId, roi_polygon: [] }));
      setError("");
    },
    []
  );

  const handleTabChange = useCallback(
    (newTab) => {
      if (newTab === tab) return;
      setTab(newTab);
      setEditing(null);
      setForm({ ...EMPTY_FORM, store_id: storeId, camera_id: cameraId });
      setError("");
    },
    [tab, storeId, cameraId]
  );

  const handleFieldChange = useCallback((field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setError("");
  }, []);

  const handlePolygonChange = useCallback((points) => {
    setForm((prev) => ({ ...prev, roi_polygon: points }));
    setError("");
  }, []);

  // ---- Persistence ----
  const refreshCurrentList = useCallback(async () => {
    try {
      if (tab === "zone") {
        const result = await mappingApi.listZones({ store_id: storeId });
        setZones(normalizeArray(result));
      } else {
        const params = {};
        if (storeId) params.store_id = storeId;
        if (cameraId) params.camera_id = cameraId;
        const result = await mappingApi.listShelves(params);
        setShelves(normalizeArray(result));
      }
    } catch (err) {
      setError(getErrorMessage(err, "Unable to refresh mappings."));
    }
  }, [tab, storeId, cameraId]);

  const validate = useCallback(() => {
    if (!storeId) return "Please select a store.";
    if (!cameraId) return "Please select a camera.";
    if (!form.name?.trim()) return `Please enter a ${tab} name.`;
    if (form.roi_polygon.length < MIN_ROI_POINTS)
      return `Draw at least ${MIN_ROI_POINTS} ROI points.`;
    if (tab === "shelf" && Number(form.tier_count) < 1)
      return "Tier count must be at least 1.";
    return null;
  }, [storeId, cameraId, form.name, form.roi_polygon, form.tier_count, tab]);

  const saveZone = useCallback(
    async (payload) => {
      const zone = editing
        ? await mappingApi.updateZone(editing.id, payload)
        : await mappingApi.createZone(payload);
      // Create/update zone mapping
      const mappings = await mappingApi.listZoneMappings({
        camera_id: cameraId,
        zone_id: zone.id,
      });
      const mappingPayload = {
        camera_id: cameraId,
        zone_id: zone.id,
        roi_polygon: form.roi_polygon,
        calibration: {},
      };
      if (mappings?.[0]?.id) {
        await mappingApi.updateZoneMapping(mappings[0].id, mappingPayload);
      } else {
        await mappingApi.createZoneMapping(mappingPayload);
      }
      return zone;
    },
    [editing, cameraId, form.roi_polygon]
  );

  const saveShelf = useCallback(
    async (payload) => {
      const shelfPayload = {
        ...payload,
        camera_id: cameraId,
        tier_count: Number(form.tier_count || 1),
      };
      const shelf = editing
        ? await mappingApi.updateShelf(editing.id, shelfPayload)
        : await mappingApi.createShelf(shelfPayload);
      // Create/update shelf mapping
      const mappings = await mappingApi.listShelfMappings({
        camera_id: cameraId,
        shelf_id: shelf.id,
      });
      const mappingPayload = {
        camera_id: cameraId,
        shelf_id: shelf.id,
        roi_polygon: form.roi_polygon,
        calibration: {},
      };
      if (mappings?.[0]?.id) {
        await mappingApi.updateShelfMapping(mappings[0].id, mappingPayload);
      } else {
        await mappingApi.createShelfMapping(mappingPayload);
      }
      return shelf;
    },
    [editing, cameraId, form.roi_polygon, form.tier_count]
  );

  const handleSave = useCallback(async () => {
    if (saving) return;
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setSaving(true);
    setError("");
    try {
      const payload = {
        ...form,
        name: form.name.trim(),
        store_id: storeId,
        camera_id: cameraId,
      };
      if (tab === "zone") {
        await saveZone(payload);
      } else {
        await saveShelf(payload);
      }
      resetEditor();
      await refreshCurrentList();
    } catch (err) {
      setError(getErrorMessage(err, "Unable to save mapping."));
    } finally {
      setSaving(false);
    }
  }, [saving, validate, form, storeId, cameraId, tab, saveZone, saveShelf, resetEditor, refreshCurrentList]);

  const handleDelete = useCallback(async () => {
    if (!editing || deleting) return;
    if (!window.confirm(`Delete this ${tab}? This cannot be undone.`)) return;

    setDeleting(true);
    setError("");
    try {
      if (tab === "zone") {
        await mappingApi.deleteZone(editing.id);
      } else {
        await mappingApi.deleteShelf(editing.id);
      }
      resetEditor();
      await refreshCurrentList();
    } catch (err) {
      setError(getErrorMessage(err, `Unable to delete ${tab}.`));
    } finally {
      setDeleting(false);
    }
  }, [editing, deleting, tab, resetEditor, refreshCurrentList]);

  return {
    stores,
    cameras,
    zones,
    shelves,
    storeId,
    cameraId,
    tab,
    form,
    editing,
    loading,
    loadingStoreData,
    loadingShelves,
    saving,
    deleting,
    error,
    availableCameras,
    selectedCamera,
    currentList,
    handleStoreChange,
    handleCameraChange,
    handleTabChange,
    handleFieldChange,
    handlePolygonChange,
    beginEditing,
    resetEditor,
    handleSave,
    handleDelete,
  };
}

// ---------------------------------------------------------------------
// Sub‑components
// ---------------------------------------------------------------------
function Controls({
  stores,
  storeId,
  cameras,
  cameraId,
  tab,
  loadingStoreData,
  availableCameras,
  onStoreChange,
  onCameraChange,
  onTabChange,
}) {
  return (
    <section className="mapping-controls">
      <label>
        <span>Store</span>
        <select value={storeId} onChange={onStoreChange} disabled={loadingStoreData}>
          <option value="">Select store</option>
          {stores.map((store) => (
            <option key={store.id} value={store.id}>
              {store.name || store.id}
            </option>
          ))}
        </select>
      </label>

      <label>
        <span>Camera</span>
        <select
          value={cameraId}
          onChange={onCameraChange}
          disabled={!availableCameras.length || loadingStoreData}
        >
          <option value="">Select camera</option>
          {availableCameras.map((cam) => (
            <option key={cam.id} value={cam.id}>
              {cam.name || cam.id}
            </option>
          ))}
        </select>
      </label>

      <div className="mapping-tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "zone"}
          className={tab === "zone" ? "active" : ""}
          onClick={() => onTabChange("zone")}
        >
          <MapPinned size={15} /> Zones
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "shelf"}
          className={tab === "shelf" ? "active" : ""}
          onClick={() => onTabChange("shelf")}
        >
          <MapPinned size={15} /> Shelves
        </button>
      </div>
    </section>
  );
}

function EditorPanel({
  tab,
  form,
  editing,
  deleting,
  saving,
  currentList,
  loadingShelves,
  onFieldChange,
  onPolygonChange,
  onReset,
  onDelete,
  onBeginEdit,
}) {
  const isSaveDisabled =
    saving ||
    !form.camera_id ||
    !form.name?.trim() ||
    form.roi_polygon.length < MIN_ROI_POINTS;

  return (
    <div className="mapping-editor-panel">
      <h3>{editing ? `Edit ${tab}` : `New ${tab}`}</h3>

      <div className="form-group">
        <label htmlFor="mapping-name">Name</label>
        <input
          id="mapping-name"
          type="text"
          value={form.name}
          onChange={(e) => onFieldChange("name", e.target.value)}
          placeholder={`Enter ${tab} name`}
        />
      </div>

      {tab === "shelf" && (
        <div className="form-group">
          <label htmlFor="mapping-tiers">Tier Count</label>
          <input
            id="mapping-tiers"
            type="number"
            min="1"
            value={form.tier_count}
            onChange={(e) => onFieldChange("tier_count", Number(e.target.value))}
          />
        </div>
      )}

      <div className="editor-actions">
        <button type="button" className="btn-secondary" onClick={onReset}>
          Reset
        </button>
        {editing && (
          <button
            type="button"
            className="btn-danger"
            onClick={onDelete}
            disabled={deleting}
          >
            <Trash2 size={15} />
            {deleting ? "Deleting..." : "Delete"}
          </button>
        )}
        <button
          type="button"
          className="mapping-save"
          onClick={onSave}
          disabled={isSaveDisabled}
        >
          <Save size={15} />
          {saving ? "Saving..." : "Save mapping"}
        </button>
      </div>

      <div className="mapping-items-list">
        <h4>Existing {tab === "zone" ? "Zones" : "Shelves"}</h4>
        {loadingShelves && tab === "shelf" ? (
          <p>Loading shelves...</p>
        ) : currentList.length === 0 ? (
          <p>No items found.</p>
        ) : (
          <ul>
            {currentList.map((item) => (
              <li
                key={item.id}
                className={editing?.id === item.id ? "selected" : ""}
                onClick={() => onBeginEdit(item)}
              >
                {getItemName(item)}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------
export default function MappingWorkspace() {
  const {
    stores,
    storeId,
    cameraId,
    tab,
    form,
    editing,
    loading,
    loadingStoreData,
    loadingShelves,
    saving,
    deleting,
    error,
    availableCameras,
    selectedCamera,
    currentList,
    handleStoreChange,
    handleCameraChange,
    handleTabChange,
    handleFieldChange,
    handlePolygonChange,
    beginEditing,
    resetEditor,
    handleSave,
    handleDelete,
  } = useMappingWorkspace();

  if (loading) {
    return (
      <div className="mapping-workspace-page">
        <PageHeader
          title="Camera mapping workspace"
          description="Use synchronized camera views to draw the spatial hierarchy: zones → shelves → products."
        />
        <div className="mapping-loading">
          <div className="mapping-loading-spinner" />
          <span>Loading mapping workspace...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="mapping-workspace-page">
      <PageHeader
        title="Camera mapping workspace"
        description="Use synchronized camera views to draw the spatial hierarchy: zones → shelves → products."
      />

      {error && (
        <div className="mapping-error" role="alert">
          {error}
        </div>
      )}

      <Controls
        stores={stores}
        storeId={storeId}
        cameraId={cameraId}
        tab={tab}
        loadingStoreData={loadingStoreData}
        availableCameras={availableCameras}
        onStoreChange={handleStoreChange}
        onCameraChange={handleCameraChange}
        onTabChange={handleTabChange}
      />

      <section className="mapping-workspace-content">
        <EditorPanel
          tab={tab}
          form={form}
          editing={editing}
          deleting={deleting}
          saving={saving}
          currentList={currentList}
          loadingShelves={loadingShelves}
          onFieldChange={handleFieldChange}
          onPolygonChange={handlePolygonChange}
          onReset={resetEditor}
          onDelete={handleDelete}
          onSave={handleSave}
          onBeginEdit={beginEditing}
        />

        <div className="mapping-canvas-panel">
          <RoiMappingCanvas
            camera={selectedCamera}
            points={form.roi_polygon}
            onChange={handlePolygonChange}
          />
        </div>
      </section>
    </div>
  );
}