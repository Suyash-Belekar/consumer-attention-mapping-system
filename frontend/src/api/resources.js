import api from "../services/api";

// Canonical routes exposed by CAMS_backend_integrated_refactored.
export const resources = {
  stores: "/stores",
  zones: "/zones",
  shelves: "/shelves",
  cameras: "/cameras",
  products: "/products",
  mappings: "/products/mappings",
};

const unwrap = (data) => Array.isArray(data) ? data : data?.items ?? [];

export async function listResource(key, params = {}) {
  const { data } = await api.get(resources[key], { params });
  return unwrap(data);
}

export async function createResource(key, payload) {
  const { data } = await api.post(resources[key], payload);
  return data;
}

export async function updateResource(key, id, payload) {
  const { data } = await api.put(`${resources[key]}/${id}`, payload);
  return data;
}

export async function deleteResource(key, id) {
  await api.delete(`${resources[key]}/${id}`);
}
