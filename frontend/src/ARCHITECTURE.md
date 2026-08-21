# Consumer Attention Mapping System — Frontend Architecture

This refactor is based on the uploaded frontend source and the Milestone 3 requirements supplied for the project.

## Product surfaces

### 1. Store operations
- Stores
- Zones
- Shelves
- Cameras

### 2. Mapping
Mapping is deliberately separated from tracking.
- `/mapping`
- `/mapping/shelves`
- `/mapping/products`

The mapping workflow supports multiple camera views in one store and keeps shelf ROI and SKU placement as explicit entities.

### 3. Tracking
- `/tracking`

Tracking is an operational monitoring surface. It consumes synchronized camera feeds and displays shopper tracker state, dwell, shelf attention and events.

### 4. Milestone 3 analytics
- `/analytics`
- `/analytics/behavior`
- `/analytics/heatmaps`
- `/analytics/products`
- `/recommendations`

## Milestone 3 mapping

### Task 1 — Behavior intelligence
The UI is prepared for:
- Explorer
- Quick Buyer
- Comparison Shopper

The backend should return persisted segment tags based on trajectory length, total dwell, product-location dwell and attention/gaze shifts.

### Task 2 — Heatmaps
`HeatmapAnalytics` accepts either:
- generated image URL from `/api/heatmaps/store`, or
- coordinate points from `/api/analytics/heatmap`

This lets the backend move from point visualization to OpenCV-generated store/camera heatmap images without changing the page contract.

### Task 3 — Product attractiveness
`ProductIntelligence` exposes the required weighted model:
- Attention Duration: 35%
- Interaction Frequency: 25%
- Pickup Rate: 20%
- Conversion Rate: 15%
- Repeat Engagement: 5%

The backend remains authoritative for normalization and scoring.

### Task 4 — Recommendations
`Recommendations` consumes the backend rule engine and displays priority plus an actionable message.

## Important backend contracts

The frontend adds optional Milestone 3 calls:
- `GET /api/analytics/behavior`
- `GET /api/analytics/product-scores`
- `GET /api/analytics/heatmap/image`
- `GET /api/analytics/heatmaps/store`

If these endpoints are not implemented yet, the pages fail gracefully or use milestone-safe fallback presentation rather than breaking the application.

## CSS policy

Every new/changed page has its own CSS file under `pages/`:
- `MappingOverview.css`
- `ShelfMapping.css`
- `ProductMapping.css`
- `LiveTracking.css`
- `BehaviorAnalytics.css`
- `HeatmapAnalytics.css`
- `ProductIntelligence.css`
- `Recommendations.css`
- `AnalyticsDashboard.css`

The existing component library and shared components remain reusable.
