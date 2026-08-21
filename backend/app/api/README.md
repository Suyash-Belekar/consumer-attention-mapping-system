# API routing policy

The backend exposes one canonical router per domain.

- `stores.py` — store CRUD
- `users.py` / `auth.py` — identity
- `cameras.py` — camera source, upload, test, snapshot, stream
- `zones.py` — zone CRUD
- `shelves.py` — shelf CRUD
- `mapping.py` — camera→zone and camera→shelf ROI mappings
- `products.py` — product CRUD, product ROI mappings and scores
- `tracking.py` — tracking point ingestion/query
- `analytics.py` — dashboard analytics
- `behavior.py` — behavioral classification
- `heatmaps.py` — generated heatmap images
- `dashboard.py` — dashboard summary helpers
- `reports.py` — export/report endpoints
- `alerts.py` — optimization alerts

Older duplicate `resources`, `layout`, `camera`, and `compatibility` routers were removed from the runtime surface so the frontend cannot accidentally hit two different implementations of the same resource.
