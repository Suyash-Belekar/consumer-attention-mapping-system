# Consumer Attention Mapping System

## Overview

The Consumer Attention Mapping System is an AI-powered retail analytics platform that leverages computer vision and machine learning to analyze shopper behavior inside retail stores. It tracks customer movement, gaze direction, dwell time, and product interactions to generate actionable insights that help retailers optimize store layouts, improve product visibility, and increase sales.




## Features

- Secure Authentication & Role-Based Access
- Store, Shelf, and Camera Management
- Real-Time Consumer Detection & Tracking
- Gaze and Attention Analysis
- Product Interaction Monitoring
- Consumer Behavior Analytics
- Attention Heatmap Generation
- Product Attractiveness Scoring
- AI-Based Recommendation Engine
- Interactive Dashboards & Reports
- PDF and Excel Report Export
- Dockerized Deployment

# ConsumerAnalytics AI: Computer Vision & Retail Intelligence Platform

Welcome to **ConsumerAnalytics AI**, an enterprise-grade Computer Vision (CV) and Retail Intelligence engine designed to turn raw video feeds into real-time operational metrics, spatial heatmaps, customer dwell analysis, and gaze/attention tracking.

---

## 🌟 Overview & System Architecture

ConsumerAnalytics AI combines high-performance Python deep learning pipelines (FastAPI, OpenCV, MediaPipe, PyTorch/YOLO) with a reactive, component-driven React dashboard (Vite, TailwindCSS, Recharts).

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 SYSTEM OVERVIEW                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────┐               RTSP Stream / Video Feed
│ Retail IP Cameras  │ ─────────► [ Multi-Camera Stream Engine ]
└────────────────────┘                         │
                                               ▼
                                            ┌──────────────────────────────┐
                                            │  AI Vision Engine (Python)   │
                                            │  • Face Detection & Mesh     │
                                            │  • Head Pose & Gaze Vector   │
                                            │  • Person Detection/Tracking │
                                            └──────────────┬───────────────┘
                                                           │
                                                           ▼
                                            ┌──────────────────────────────┐
                                            │  Analytics & Domain Engine   │
                                            │  • Dwell Time Calculation    │
                                            │  • Attention Score & Heatmap │
                                            │  • Shelf & Zone Mapping      │
                                            └──────────────┬───────────────┘
                                                           │
                                                           ▼
                                            ┌──────────────────────────────┐
                                            │   FastAPI Backend Server     │
                                            │   • RESTful APIs & Auth      │
                                            │   • Analytics Repositories   │
                                            └──────────────┬───────────────┘
                                                           │
                                                           ▼ JSON / WebSockets
                                            ┌──────────────────────────────┐
                                            │ React / Vite Web Frontend    │
                                            │  • Live ROI Mapping Canvas   │
                                            │  • Spatial Traffic & Heatmap │
                                            │  • Attention & Dwell Dash    │
                                            └──────────────────────────────┘
---

## 🚀 Key Features 

# Real-time Object Detection & Tracking:YOLO-based person and item tracking with multi-camera trajectory mapping .
# Biometric Attention & Gaze Projection: 3D Head pose estimation, MediaPipe Face Mesh landmark extraction, and spatial gaze vector projection .
# Dwell Time & Engagement Metrics: Granular dwell measurement per shelf, endcap, or custom ROI (Region of Interest) .
# Interactive ROI Mapping Canvas: Drag-and-drop shelf, product, and camera mapping interface built for retail store layouts .
# Heatmap & Traffic Analytics: Spatial visitor density mapping and pathing analytics .
# Enterprise Modular Architecture: DDD (Domain-Driven Design) structure separating core CV algorithms, analytics domain, and API layers .

---

## 📂 Project Directory Structure 

```text
.
├── app/                              # Backend AI Engine & FastAPI Core
│   ├── ai/                           # AI Vision Models & Pipeline
│   │   ├── detector.py               # Object & Face Detection Modules
│   │   ├── frame_processor.py        # Frame Extraction & Preprocessing
│   │   ├── models.py                 # PyTorch / OpenCV Model Containers
│   │   └── tracker.py                # Multi-Object Trajectory Tracker
│   ├── analytics/                    # Domain Analytics Calculation Engine
│   │   ├── domain/
│   │   │   ├── attention/            # Gaze Projection & Attention Scoring
│   │   │   │   ├── cv/               # Head Pose, Face Mesh, Face Detection
│   │   │   │   └── services/         # Attention Session & Stats Calculation
│   │   │   └── dwell/                # Dwell Time & Zone Interaction Logic
│   │   └── analytics_engine.py       # Main Analytics Integration Pipeline
│   ├── api/                          # REST API Endpoints (FastAPI)
│   │   ├── analytics.py, behavior.py, heatmaps.py, mapping.py ...
│   ├── core/                         # Database, Config, Security & Auth
│   ├── models/                       # SQLAlchemy Database Models & SQL Schemas
│   ├── repositories/                 # Data Access & Aggregation Repositories
│   └── services/                     # Camera Runtimes & Analytics Sync Services
│
└── src/                              # Frontend Web Application (React + Vite)
    ├── api/                          # Axios API Clients & Endpoints
    ├── components/
    │   ├── analytics/                # HeatMap, TrafficChart, Dwell Charts
    │   ├── mapping/                  # RoiMappingCanvas, CameraGrid, EntityPanel
    │   └── tracking/                 # Live Camera Feeds & Tracking Details
    ├── pages/                        # Analytics Dashboard, Product Mapping, Stores
    └── services/                     # Web Services & Helper Utilities
``` 

---

## 🛠️ Technology Stack 

# Backend & Vision Engine: Python 3.10+, FastAPI, Pydantic, SQLAlchemy, OpenCV, MediaPipe, PyTorch, PostgreSQL / SQLite .
# Frontend Dashboard:** React 18, Vite, TailwindCSS, Lucide React, Recharts, HTML5 Canvas API .

---

## 🏁 Quick Start & Local Setup 

### 1. Backend Setup (`app`) 
```bash
cd app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.core.migrations
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
``` 
*API documentation will be available at:* `http://localhost:8000/docs` 

### 2. Frontend Setup (`src`) 
```bash
npm install
npm run dev
``` 
*Frontend UI will be running at:* `http://localhost:5173` 

---

## 📡 API Endpoints Overview 

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/analytics/dwell` | `GET` | Fetches aggregated dwell times across stores and shelves |
| `/api/analytics/attention` | `GET` | Retrieves gaze and head-pose attention scores |
| `/api/heatmaps` | `GET` | Generates 2D spatial visitor traffic heatmaps |
| `/api/mapping/roi` | `POST` | Updates camera region-of-interest bounding polygons |
| `/api/cameras/stream` | `GET` | Streams active RTSP / WebRTC camera feeds | 

---

## 🛡️ License & Engineering Guidelines 

Designed and maintained for enterprise computer vision deployments. Follow Domain-Driven Design (DDD) patterns when extending `app/analytics/domain/` or adding frontend mapping tools in `src/components/mapping/`.