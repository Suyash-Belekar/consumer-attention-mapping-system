import { useCallback, useEffect, useMemo, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";

import PageHeader from "../components/PageHeader";
import RoiMappingCanvas from "../components/mapping/RoiMappingCanvas";
import { mappingApi } from "../api/mappingApi";

import "./ProductMapping.css";

const MIN_ROI_POINTS = 4;

const EMPTY_FORM = {
  product_id: "",
  shelf_id: "",
  camera_id: "",
  store_id: "",
  tier: 1,
};

const createEmptyForm = () => ({ ...EMPTY_FORM });

const asArray = (value) => (Array.isArray(value) ? value : []);

const getId = (value) =>
  value === null || value === undefined ? "" : String(value);

const findById = (items, id, keys = ["id"]) => {
  const target = getId(id);
  if (!target) return null;

  return (
    asArray(items).find((item) =>
      keys.some((key) => getId(item?.[key]) === target)
    ) || null
  );
};

const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string" && detail.trim()) return detail;

  if (Array.isArray(detail)) {
    const messages = detail.map((item) => item?.msg).filter(Boolean);
    if (messages.length) return messages.join(", ");
  }

  return error?.message?.trim() || fallback;
};

const getProductName = (mapping, products) => {
  if (mapping?.product_name) return mapping.product_name;

  const product = findById(products, mapping?.product_id, [
    "id",
    "product_id",
  ]);

  return (
    product?.name ||
    product?.product_name ||
    product?.sku ||
    mapping?.product_id ||
    "Unknown product"
  );
};

const getShelfName = (mapping, shelves) => {
  if (mapping?.shelf_name) return mapping.shelf_name;

  const shelf = findById(shelves, mapping?.shelf_id, [
    "id",
    "shelf_id",
  ]);

  return shelf?.name || shelf?.shelf_name || mapping?.shelf_id || "Unknown shelf";
};

const getCameraName = (mapping, cameras) => {
  if (mapping?.camera_name) return mapping.camera_name;

  const camera = findById(cameras, mapping?.camera_id, ["id", "camera_id"]);

  return camera?.name || camera?.camera_name || mapping?.camera_id || "Unknown camera";
};

function Field({ label, children, required = false }) {
  return (
    <label className="product-field">
      <span>
        {label}
        {required && <em aria-hidden="true"> *</em>}
      </span>
      {children}
    </label>
  );
}

export default function ProductMapping() {
  const [products, setProducts] = useState([]);
  const [shelves, setShelves] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [mappings, setMappings] = useState([]);

  const [form, setForm] = useState(createEmptyForm);
  const [points, setPoints] = useState([]);
  const [editing, setEditing] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [productResponse, shelfResponse, cameraResponse, mappingResponse] =
        await Promise.all([
          mappingApi.listProducts(),
          mappingApi.listShelves(),
          mappingApi.listCameras(),
          mappingApi.listProductMappings(),
        ]);

      setProducts(asArray(productResponse));
      setShelves(asArray(shelfResponse));
      setCameras(asArray(cameraResponse));
      setMappings(asArray(mappingResponse));
    } catch (requestError) {
      console.error("Product mapping load failed:", requestError);
      setError(
        getErrorMessage(
          requestError,
          "Unable to load product mapping data."
        )
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const selectedShelf = useMemo(
    () => findById(shelves, form.shelf_id, ["id", "shelf_id"]),
    [shelves, form.shelf_id]
  );

  const selectedCamera = useMemo(
    () => findById(cameras, form.camera_id, ["id", "camera_id"]),
    [cameras, form.camera_id]
  );

  const effectiveStoreId = useMemo(
    () => form.store_id || selectedShelf?.store_id || "",
    [form.store_id, selectedShelf]
  );

  const availableProducts = useMemo(
    () =>
      effectiveStoreId
        ? products.filter(
            (product) => !product.store_id || getId(product.store_id) === getId(effectiveStoreId)
          )
        : products,
    [effectiveStoreId, products]
  );

  const availableCameras = useMemo(
    () =>
      selectedShelf?.store_id
        ? cameras.filter(
            (camera) =>
              !camera.store_id ||
              getId(camera.store_id) === getId(selectedShelf.store_id)
          )
        : cameras,
    [cameras, selectedShelf]
  );

  const updateField = useCallback((field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
    setError("");
  }, []);

  const resetForm = useCallback(() => {
    setEditing(null);
    setForm(createEmptyForm());
    setPoints([]);
    setError("");
  }, []);

  const handleShelfChange = useCallback(
    (shelfId) => {
      const shelf = findById(shelves, shelfId, ["id", "shelf_id"]);

      setForm((current) => ({
        ...current,
        shelf_id: shelfId,
        store_id: shelf?.store_id || current.store_id || "",
        camera_id:
          current.camera_id &&
          (!shelf?.store_id ||
            getId(findById(cameras, current.camera_id)?.store_id) ===
              getId(shelf.store_id))
            ? current.camera_id
            : "",
      }));
      setError("");
    },
    [cameras, shelves]
  );

  const startEditing = useCallback(
    (mapping) => {
      const shelf = findById(shelves, mapping?.shelf_id, ["id", "shelf_id"]);

      setEditing(mapping);
      setForm({
        product_id: mapping?.product_id || "",
        shelf_id: mapping?.shelf_id || "",
        camera_id: mapping?.camera_id || "",
        store_id: mapping?.store_id || shelf?.store_id || "",
        tier: Number(mapping?.tier) > 0 ? Number(mapping.tier) : 1,
      });
      setPoints(asArray(mapping?.roi_polygon));
      setError("");
    },
    [shelves]
  );

  const validateForm = useCallback(() => {
    if (!form.product_id) return "Please select a product.";
    if (!form.shelf_id) return "Please select a shelf.";
    if (!form.camera_id) return "Please select a camera.";
    if (!effectiveStoreId) return "The selected shelf does not have a store assigned.";

    const tier = Number(form.tier);
    if (!Number.isInteger(tier) || tier < 1 || tier > 20) {
      return "Tier must be an integer between 1 and 20.";
    }

    if (!Array.isArray(points) || points.length < MIN_ROI_POINTS) {
      return `Draw at least ${MIN_ROI_POINTS} ROI points before saving.`;
    }

    return "";
  }, [effectiveStoreId, form, points]);

  const buildPayload = useCallback(
    () => ({
      product_id: form.product_id,
      store_id: effectiveStoreId,
      shelf_id: form.shelf_id,
      camera_id: form.camera_id || null,
      tier: Number(form.tier),
      roi_polygon: points,
    }),
    [effectiveStoreId, form, points]
  );

  const handleSave = async (event) => {
    event.preventDefault();
    if (saving) return;

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setSaving(true);
    setError("");

    try {
      const payload = buildPayload();

      if (editing?.id) {
        await mappingApi.updateProductMapping(editing.id, payload);
      } else {
        await mappingApi.createProductMapping(payload);
      }

      resetForm();
      await loadData();
    } catch (requestError) {
      console.error("Product mapping save failed:", requestError);
      setError(
        getErrorMessage(requestError, "Unable to save product mapping.")
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (mapping) => {
    if (!mapping?.id || deletingId) return;

    const productName = getProductName(mapping, products);
    if (!window.confirm(`Delete the product mapping for "${productName}"?`)) {
      return;
    }

    setDeletingId(mapping.id);
    setError("");

    try {
      await mappingApi.deleteProductMapping(mapping.id);

      if (getId(editing?.id) === getId(mapping.id)) resetForm();
      await loadData();
    } catch (requestError) {
      console.error("Product mapping deletion failed:", requestError);
      setError(
        getErrorMessage(requestError, "Unable to delete product mapping.")
      );
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="product-mapping-page">
      <PageHeader
        title="Product mapping"
        description="Map each SKU to its camera-space ROI. A shelf can contain multiple product mappings across tiers and cameras."
        actions={
          <button
            type="button"
            className="product-new"
            onClick={resetForm}
            disabled={loading || saving || Boolean(deletingId)}
          >
            <Plus size={15} />
            New product mapping
          </button>
        }
      />

      {error && (
        <div className="product-mapping-error" role="alert">
          {error}
        </div>
      )}

      <section className="product-map-layout">
        <div className="product-map-canvas">
          <RoiMappingCanvas
            camera={selectedCamera}
            mode="rectangle"
            initialPoints={points}
            onChange={setPoints}
            title={
              selectedShelf
                ? `${selectedShelf.name || selectedShelf.shelf_name || "Shelf"} · product ROI`
                : "Select camera + shelf"
            }
          />
        </div>

        <form className="product-map-editor" onSubmit={handleSave}>
          <div className="product-editor-heading">
            <span>PRODUCT ENTITY</span>
            <h2>{editing ? "Update product ROI" : "Create product ROI"}</h2>
          </div>

          <Field label="Product" required>
            <select
              value={form.product_id}
              onChange={(event) => updateField("product_id", event.target.value)}
              disabled={saving}
            >
              <option value="">Select product</option>
              {availableProducts.map((product) => {
                const id = product.id || product.product_id;
                return (
                  <option key={id} value={id}>
                    {product.name || product.product_name || product.sku || "Unnamed product"}
                  </option>
                );
              })}
            </select>
          </Field>

          <Field label="Shelf" required>
            <select
              value={form.shelf_id}
              onChange={(event) => handleShelfChange(event.target.value)}
              disabled={saving}
            >
              <option value="">Select shelf</option>
              {shelves.map((shelf) => {
                const id = shelf.id || shelf.shelf_id;
                return (
                  <option key={id} value={id}>
                    {shelf.name || shelf.shelf_name || "Unnamed shelf"}
                  </option>
                );
              })}
            </select>
          </Field>

          <Field label="Camera" required>
            <select
              value={form.camera_id}
              onChange={(event) => updateField("camera_id", event.target.value)}
              disabled={saving || !form.shelf_id}
            >
              <option value="">
                {form.shelf_id ? "Select camera" : "Select shelf first"}
              </option>
              {availableCameras.map((camera) => (
                <option key={camera.id} value={camera.id}>
                  {camera.name || camera.camera_name || camera.id}
                </option>
              ))}
            </select>
          </Field>

          <div className="product-two">
            <Field label="Tier">
              <input
                type="number"
                min="1"
                max="20"
                step="1"
                value={form.tier}
                onChange={(event) => updateField("tier", event.target.value)}
                disabled={saving}
              />
            </Field>

            <Field label="Store">
              <input
                value={effectiveStoreId}
                readOnly
                aria-readonly="true"
                placeholder="Auto-detected from shelf"
              />
            </Field>
          </div>

          <div className="product-roi-status">
            <span>ROI points</span>
            <strong>{points.length}</strong>
            {points.length < MIN_ROI_POINTS && (
              <small>Draw a rectangle using two opposite corners.</small>
            )}
          </div>

          <div className="product-actions">
            <button type="button" onClick={resetForm} disabled={saving}>
              Clear
            </button>
            <button
              type="submit"
              disabled={loading || saving || Boolean(deletingId)}
            >
              {saving ? "Saving..." : editing ? "Save changes" : "Create mapping"}
            </button>
          </div>
        </form>
      </section>

      <ProductMappingList
        mappings={mappings}
        products={products}
        shelves={shelves}
        cameras={cameras}
        loading={loading}
        editingId={editing?.id}
        saving={saving}
        deletingId={deletingId}
        onEdit={startEditing}
        onDelete={handleDelete}
      />
    </div>
  );
}

function ProductMappingList({
  mappings,
  products,
  shelves,
  cameras,
  loading,
  editingId,
  saving,
  deletingId,
  onEdit,
  onDelete,
}) {
  return (
    <section className="product-map-list">
      <header>
        <div>
          <span>MULTI-PRODUCT SHELVES</span>
          <h2>Individual product coverage</h2>
        </div>
        <b>{mappings.length}</b>
      </header>

      {loading ? (
        <div className="product-map-empty">Loading product mappings...</div>
      ) : mappings.length === 0 ? (
        <div className="product-map-empty">
          No product mappings have been created yet.
        </div>
      ) : (
        mappings.map((mapping) => {
          const roi = asArray(mapping.roi_polygon);
          const productName = getProductName(mapping, products);

          return (
            <div
              className={`product-map-row ${
                getId(editingId) === getId(mapping.id) ? "selected" : ""
              }`}
              key={mapping.id}
            >
              <div>
                <strong>{productName}</strong>
                <small>
                  Tier {mapping.tier ?? 1} ·{" "}
                  {roi.length ? `${roi.length} pts` : "ROI not drawn"}
                </small>
              </div>

              <span>{getShelfName(mapping, shelves)}</span>
              <span>{getCameraName(mapping, cameras)}</span>

              <button
                type="button"
                onClick={() => onEdit(mapping)}
                disabled={saving || Boolean(deletingId)}
                aria-label={`Edit ${productName}`}
                title="Edit mapping"
              >
                <Pencil size={14} />
              </button>

              <button
                type="button"
                className="danger"
                onClick={() => onDelete(mapping)}
                disabled={saving || Boolean(deletingId)}
                aria-label={`Delete ${productName}`}
                title="Delete mapping"
              >
                <Trash2 size={14} />
              </button>
            </div>
          );
        })
      )}
    </section>
  );
}
