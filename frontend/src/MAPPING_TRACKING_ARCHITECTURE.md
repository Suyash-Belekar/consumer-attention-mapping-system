# Multi-camera Mapping and Tracking

## Domain separation

Mapping is configuration/master data. Tracking is runtime CV observation. Tracking reads mappings but does not modify them.

Store is the parent context. Both domains operate on multiple cameras belonging to the selected store.

## Mapping
Store -> Cameras -> Camera coverage -> Shelf ROI -> Tiers -> Product mapping -> Camera-specific coordinates.

The same physical shelf/product may have mappings in multiple cameras.

## Tracking
Store -> selected cameras -> live feeds -> local tracking IDs -> cross-camera/global shopper identity -> gaze -> mapping lookup -> shelf/product -> dwell/attention.

## Analytics
Analytics consumes tracking outputs and produces traffic, attention, product scores, heatmaps and recommendations.

## Frontend page families
- MappingOverview
- CameraMapping
- ShelfMapping
- ProductMapping
- LiveTracking

Replace the sample UI data with the project's FastAPI contracts. The components are deliberately separated so API hooks can be added without coupling Mapping to Tracking.
