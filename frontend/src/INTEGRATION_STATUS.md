# CAMS Frontend Integration Status

This source tree is aligned with `CAMS_backend_integrated_refactored`.

## Canonical API mapping

- Authentication: `/api/auth/*`
- Stores: `/api/stores`
- Zones: `/api/zones`
- Shelves: `/api/shelves`
- Cameras: `/api/cameras`
- Products: `/api/products`
- Product mappings: `/api/products/mappings`
- Camera-zone mappings: `/api/mappings/zones`
- Camera-shelf mappings: `/api/mappings/shelves`
- Tracking: `/api/tracking/*`
- Analytics: `/api/analytics/*`
- Heatmap generation: `/api/heatmaps/*`
- Reports: `/api/reports/*`
- Alerts: `/api/alerts/*`
- Users: `/api/users/*`

## Integration changes

- Removed legacy `/layout/zones` frontend calls.
- Removed legacy `/product-mappings` frontend calls.
- Behavior analytics now reads `/api/analytics/behavior`.
- Product intelligence now reads `/api/analytics/product-scores`.
- Heatmap generation now calls `/api/heatmaps/generate` and displays the generated image.
- Live tracking now reads `/api/tracking/live` and `/api/tracking/points`.
- Camera/ROI views use authenticated snapshot polling instead of trying to load RTSP URLs directly in the browser.
- Reports and alerts pages consume the backend report/alert APIs.
- Product mapping sends the required `store_id` and uses the canonical `/api/products/mappings` API.

## Runtime

Set `VITE_API_BASE=http://localhost:8000` in the frontend environment. The API client automatically appends `/api`.
