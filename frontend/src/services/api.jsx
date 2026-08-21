import axios from "axios";

const rawBaseUrl = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const normalizedBaseUrl = rawBaseUrl.replace(/\/+$/u, "");
const baseURL = normalizedBaseUrl.endsWith("/api")
  ? normalizedBaseUrl
  : `${normalizedBaseUrl}/api`;

const api = axios.create({
    baseURL,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            const isAuthRoute = window.location.pathname === "/" || window.location.pathname === "/register";
            if (!isAuthRoute) {
                localStorage.removeItem("token");
                window.location.href = "/";
            }
        }
        return Promise.reject(error);
    }
);

export default api;