import api from "../services/api";

const BASE = "/analytics";
const get = async (path, params = {}) => (await api.get(`${BASE}${path}`, { params })).data;

export const fetchSummary = (hours = 24, storeId) => get("/summary", { hours, ...(storeId ? { store_id: storeId } : {}) });
export const fetchProductRankings = (hours = 24, storeId) => get("/products", { hours, ...(storeId ? { store_id: storeId } : {}) });
export const fetchHeatmap = (hours = 24, storeId) => get("/heatmap", { hours, ...(storeId ? { store_id: storeId } : {}) });
export const fetchTraffic = (hours = 24, storeId) => get("/traffic", { hours, ...(storeId ? { store_id: storeId } : {}) });
export const fetchRecommendations = (hours = 24, storeId) => get("/recommendations", { hours, ...(storeId ? { store_id: storeId } : {}) });
export const fetchAttentionData = (hours = 24, storeId) => get("/attention", { hours, ...(storeId ? { store_id: storeId } : {}) });
export const fetchBehaviorSegments = (hours = 24, storeId) => get("/behavior", { hours, ...(storeId ? { store_id: storeId } : {}) });
export const fetchProductScores = (hours = 24, storeId) => get("/product-scores", { hours, ...(storeId ? { store_id: storeId } : {}) });

export const generateHeatmap = (payload) => api.post("/heatmaps/generate", payload).then(({ data }) => data);
export const fetchStoreHeatmap = (storeId, heatmapType = "traffic") => api.get(`/heatmaps/store/${storeId}`, { params: { heatmap_type: heatmapType }, responseType: "blob" }).then(({ data }) => data);

export const fetchLiveTracking = (storeId) => getTracking(`/tracking/live`, { store_id: storeId });
export const fetchTrackingPoints = (storeId, params = {}) => getTracking(`/tracking/points`, { store_id: storeId, ...params });
const getTracking = async (path, params) => (await api.get(path, { params })).data;

export const fetchReports = async (storeId, hours = 24) => {
  const [attention, products] = await Promise.all([
    api.get("/reports/attention", { params: { store_id: storeId, hours } }),
    api.get("/reports/products", { params: { store_id: storeId } }),
  ]);
  return { attention: attention.data, products: products.data };
};
export const reportDownloadUrl = (kind, storeId, hours = 24) => {
  const base = api.defaults.baseURL;
  const path = kind === "attention.csv" || kind === "attention.pdf" ? `/reports/${kind}` : "/reports/products.xlsx";
  const query = new URLSearchParams({ store_id: storeId, ...(kind !== "products.xlsx" ? { hours: String(hours) } : {}) });
  return `${base}${path}?${query.toString()}`;
};

export const fetchAlerts = (storeId, unreadOnly = false) => api.get("/alerts", { params: { ...(storeId ? { store_id: storeId } : {}), unread_only: unreadOnly } }).then(({ data }) => data);
export const markAlertRead = (id) => api.post(`/alerts/${id}/read`).then(({ data }) => data);
