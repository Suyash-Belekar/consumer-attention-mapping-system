# Refactor manifest

Existing project code is retained unless explicitly replaced above.

Replaced/refactored:
- App.jsx
- components/Sidebar.jsx
- api/analyticsApi.js
- api/resources.js
- pages/AnalyticsDashboard.jsx + CSS
- pages/MappingOverview.jsx + CSS
- pages/ShelfMapping.jsx + CSS
- pages/ProductMapping.jsx + CSS
- pages/LiveTracking.jsx + CSS

Added:
- api/mappingApi.js
- pages/BehaviorAnalytics.jsx + CSS
- pages/HeatmapAnalytics.jsx + CSS
- pages/ProductIntelligence.jsx + CSS
- ARCHITECTURE.md

The result intentionally separates mapping from tracking and treats multiple cameras as a first-class store-level concern.
