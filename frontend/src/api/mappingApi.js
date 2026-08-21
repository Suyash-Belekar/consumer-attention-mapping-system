import api from "../services/api";

// Helper to normalize array vs paginated response objects
const unwrap = (data) => (Array.isArray(data) ? data : data?.items ?? []);

export const mappingApi = {
  // ==========================================
  // CAMERAS
  // ==========================================
  listCameras: async (storeId) => {
    const { data } = await api.get("/cameras", {
      params: storeId ? { store_id: storeId } : {},
    });
    return unwrap(data);
  },

  createCamera: async (payload) => {
    const { data } = await api.post("/cameras", payload);
    return data;
  },

  deleteCamera: async (id) => {
    const { data } = await api.delete(`/cameras/${id}`);
    return data;
  },

  startCamera: async (id) => {
    const { data } = await api.post(`/cameras/${id}/start`);
    return data;
  },

  stopCamera: async (id) => {
    const { data } = await api.post(`/cameras/${id}/stop`);
    return data;
  },

  testCamera: async (id) => {
    const { data } = await api.post(`/cameras/${id}/test`);
    return data;
  },

  uploadCamera: async (id, file) => {
    const form = new FormData();
    form.append("file", file);
    const { data } = await api.post(`/cameras/${id}/upload`, form);
    return data;
  },

  cameraMappingContext: async (id) => {
    const { data } = await api.get(`/cameras/${id}/mapping-context`);
    return data;
  },

  snapshot: async (id) => {
    const { data } = await api.get(`/cameras/${id}/snapshot`, {
      responseType: "blob",
    });
    return data;
  },

  // ==========================================
  // ZONES
  // ==========================================
  listZones: async (params = {}) => {
    const { data } = await api.get("/zones", { params });
    return unwrap(data);
  },

  createZone: async (payload) => {
    const { data } = await api.post("/zones", {
      store_id: payload.store_id,
      zone_name: payload.name ?? payload.zone_name,
      description: payload.description ?? null,
      roi_polygon: payload.roi_polygon ?? [],
    });
    return data;
  },

  updateZone: async (id, payload) => {
    const { data } = await api.put(`/zones/${id}`, {
      zone_name: payload.name ?? payload.zone_name,
      description: payload.description ?? null,
      roi_polygon: payload.roi_polygon ?? [],
      is_active: payload.is_active,
    });
    return data;
  },

  deleteZone: async (id) => {
    const { data } = await api.delete(`/zones/${id}`);
    return data;
  },

  // ==========================================
  // SHELVES
  // ==========================================
  listShelves: async (params = {}) => {
    const { data } = await api.get("/shelves", { params });
    return unwrap(data);
  },

  createShelf: async (payload) => {
    const { data } = await api.post("/shelves", payload);
    return data;
  },

  updateShelf: async (id, payload) => {
    const { data } = await api.put(`/shelves/${id}`, payload);
    return data;
  },

  deleteShelf: async (id) => {
    const { data } = await api.delete(`/shelves/${id}`);
    return data;
  },

  // ==========================================
  // ZONE MAPPINGS
  // ==========================================
  listZoneMappings: async (params = {}) => {
    const { data } = await api.get("/mappings/zones", { params });
    return unwrap(data);
  },

  createZoneMapping: async (payload) => {
    const { data } = await api.post("/mappings/zones", payload);
    return data;
  },

  updateZoneMapping: async (id, payload) => {
    const { data } = await api.put(`/mappings/zones/${id}`, payload);
    return data;
  },

  deleteZoneMapping: async (id) => {
    const { data } = await api.delete(`/mappings/zones/${id}`);
    return data;
  },

  // ==========================================
  // SHELF MAPPINGS
  // ==========================================
  listShelfMappings: async (params = {}) => {
    const { data } = await api.get("/mappings/shelves", { params });
    return unwrap(data);
  },

  createShelfMapping: async (payload) => {
    const { data } = await api.post("/mappings/shelves", payload);
    return data;
  },

  updateShelfMapping: async (id, payload) => {
    const { data } = await api.put(`/mappings/shelves/${id}`, payload);
    return data;
  },

  deleteShelfMapping: async (id) => {
    const { data } = await api.delete(`/mappings/shelves/${id}`);
    return data;
  },

  // ==========================================
  // PRODUCTS & PRODUCT MAPPINGS
  // ==========================================
  listProducts: async (params = {}) => {
    const { data } = await api.get("/products", { params });
    return unwrap(data);
  },

  listProductMappings: async (params = {}) => {
    const { data } = await api.get("/products/mappings", { params });
    return unwrap(data);
  },

  createProductMapping: async (payload) => {
    const { data } = await api.post("/products/mappings", payload);
    return data;
  },

  getProductMappingById: async (id) => {
    const rows = await mappingApi.listProductMappings();
    const row = rows.find((item) => String(item.id) === String(id));
    if (!row) throw new Error("Product mapping not found.");
    return row;
  },

  updateProductMapping: async (id, payload) => {
    const mapping = payload.product_id
      ? payload
      : await mappingApi.getProductMappingById(id);

    const { data } = await api.put(
      `/products/${mapping.product_id}/mapping`,
      mapping
    );
    return data;
  },

  deleteProductMapping: async (id, productId, cameraId) => {
    const mapping = productId
      ? { product_id: productId }
      : await mappingApi.getProductMappingById(id);

    const { data } = await api.delete(
      `/products/${mapping.product_id}/mapping`,
      {
        params: cameraId ? { camera_id: cameraId } : {},
      }
    );
    return data;
  },
};