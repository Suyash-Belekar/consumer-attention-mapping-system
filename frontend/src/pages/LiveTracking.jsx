import { useCallback, useEffect, useMemo, useState } from "react";
import {
    Activity,
    Pause,
    Play,
    Radio,
    UserRound,
} from "lucide-react";

import PageHeader from "../components/PageHeader";
import { mappingApi } from "../api/mappingApi";
import {
    fetchLiveTracking,
    fetchTrackingPoints,
} from "../api/analyticsApi";
import { listResource } from "../api/resources";

import "./LiveTracking.css";

const REFRESH_INTERVAL = 5000;
const SNAPSHOT_INTERVAL = 3000;
const TRACKING_POINT_LIMIT = 500;
const RECENT_EVENT_LIMIT = 8;

const getErrorMessage = (
    error,
    fallback = "Something went wrong. Please try again."
) => {
    const detail = error?.response?.data?.detail;

    if (typeof detail === "string" && detail.trim()) {
        return detail;
    }

    if (Array.isArray(detail)) {
        const messages = detail
            .map((item) => item?.msg)
            .filter(Boolean);

        if (messages.length > 0) {
            return messages.join(", ");
        }
    }

    return fallback;
};

const normalizeId = (value) => String(value ?? "");

const getTimestamp = (value) => {
    const timestamp = new Date(value).getTime();
    return Number.isFinite(timestamp) ? timestamp : 0;
};

export default function LiveTracking() {
    const [stores, setStores] = useState([]);
    const [cameras, setCameras] = useState([]);
    const [storeId, setStoreId] = useState("");

    const [selectedCameraIds, setSelectedCameraIds] = useState([]);

    const [running, setRunning] = useState(true);
    const [live, setLive] = useState(null);
    const [points, setPoints] = useState([]);
    const [error, setError] = useState("");

    const loadSources = useCallback(async () => {
        try {
            const [storeList, cameraList] = await Promise.all([
                listResource("stores"),
                mappingApi.listCameras(),
            ]);

            const safeStores = Array.isArray(storeList)
                ? storeList
                : [];

            const safeCameras = Array.isArray(cameraList)
                ? cameraList
                : [];

            setStores(safeStores);
            setCameras(safeCameras);

            setStoreId((currentStoreId) => {
                if (currentStoreId) {
                    const exists = safeStores.some(
                        (store) =>
                            normalizeId(store.id) ===
                            normalizeId(currentStoreId)
                    );

                    if (exists) {
                        return currentStoreId;
                    }
                }

                return safeStores[0]?.id
                    ? String(safeStores[0].id)
                    : "";
            });

            setError("");
        } catch (requestError) {
            setError(
                getErrorMessage(
                    requestError,
                    "Unable to load camera sources."
                )
            );
        }
    }, []);

    const refreshTracking = useCallback(async () => {
        if (!storeId || !running) {
            return;
        }

        try {
            const [summary, trackingPoints] = await Promise.all([
                fetchLiveTracking(storeId),
                fetchTrackingPoints(storeId, {
                    limit: TRACKING_POINT_LIMIT,
                }),
            ]);

            setLive(summary ?? null);
            setPoints(
                Array.isArray(trackingPoints)
                    ? trackingPoints
                    : []
            );

            setError("");
        } catch (requestError) {
            setError(
                getErrorMessage(
                    requestError,
                    "Unable to load live tracking data."
                )
            );
        }
    }, [storeId, running]);

    useEffect(() => {
        loadSources();
    }, [loadSources]);

    const storeCameras = useMemo(() => {
        if (!storeId) {
            return [];
        }

        const normalizedStoreId = normalizeId(storeId);

        return cameras.filter(
            (camera) =>
                normalizeId(camera.store_id) ===
                normalizedStoreId
        );
    }, [cameras, storeId]);

    useEffect(() => {
        setSelectedCameraIds((currentSelection) => {
            const availableIds = new Set(
                storeCameras.map((camera) =>
                    normalizeId(camera.id)
                )
            );

            const validSelection = currentSelection.filter(
                (cameraId) =>
                    availableIds.has(normalizeId(cameraId))
            );

            if (validSelection.length > 0) {
                return validSelection;
            }

            return storeCameras.map((camera) => camera.id);
        });
    }, [storeCameras]);

    useEffect(() => {
        if (!storeId || !running) {
            return undefined;
        }

        refreshTracking();

        const timer = window.setInterval(
            refreshTracking,
            REFRESH_INTERVAL
        );

        return () => {
            window.clearInterval(timer);
        };
    }, [storeId, running, refreshTracking]);

    const activeCameras = useMemo(() => {
        const selectedIds = new Set(
            selectedCameraIds.map(normalizeId)
        );

        return storeCameras.filter((camera) =>
            selectedIds.has(normalizeId(camera.id))
        );
    }, [storeCameras, selectedCameraIds]);

    const latestPoint = useMemo(() => {
        if (!points.length) {
            return null;
        }

        return points.reduce((latest, current) => {
            if (!latest) {
                return current;
            }

            return getTimestamp(current.timestamp) >
                getTimestamp(latest.timestamp)
                ? current
                : latest;
        }, null);
    }, [points]);

    const trackerIds = useMemo(() => {
        return new Set(
            points
                .map((point) => point.tracker_id)
                .filter(
                    (trackerId) =>
                        trackerId !== null &&
                        trackerId !== undefined
                )
                .map(normalizeId)
        );
    }, [points]);

    const recentPoints = useMemo(() => {
        return [...points]
            .sort(
                (a, b) =>
                    getTimestamp(b.timestamp) -
                    getTimestamp(a.timestamp)
            )
            .slice(0, RECENT_EVENT_LIMIT);
    }, [points]);

    const toggleCamera = useCallback((cameraId) => {
        const normalizedId = normalizeId(cameraId);

        setSelectedCameraIds((currentSelection) => {
            const exists = currentSelection.some(
                (id) => normalizeId(id) === normalizedId
            );

            if (exists) {
                return currentSelection.filter(
                    (id) =>
                        normalizeId(id) !== normalizedId
                );
            }

            return [...currentSelection, cameraId];
        });
    }, []);

    const handleStoreChange = useCallback((event) => {
        setStoreId(event.target.value);
        setError("");
    }, []);

    const toggleRunning = useCallback(() => {
        setRunning((current) => !current);
    }, []);

    return (
        <main className="tracking-page-v2">
            <PageHeader
                title="Live Tracking"
                description="Monitor synchronized shopper trajectories using tracking data persisted by the CAMS backend."
                actions={
                    <div className="tracking-actions">
                        <button
                            type="button"
                            onClick={toggleRunning}
                            aria-label={
                                running
                                    ? "Pause live tracking"
                                    : "Resume live tracking"
                            }
                        >
                            {running ? (
                                <Pause size={14} />
                            ) : (
                                <Play size={14} />
                            )}

                            {running ? "Pause" : "Resume"}
                        </button>

                        <span
                            className={
                                running
                                    ? "tracking-live"
                                    : "tracking-paused"
                            }
                        >
                            <Radio size={13} />

                            {running ? "LIVE" : "PAUSED"}
                        </span>
                    </div>
                }
            />

            {error && (
                <div
                    className="tracking-note"
                    role="alert"
                >
                    {error}
                </div>
            )}

            <section
                className="tracking-controls"
                aria-label="Tracking filters"
            >
                <label htmlFor="tracking-store">
                    Store

                    <select
                        id="tracking-store"
                        value={storeId}
                        onChange={handleStoreChange}
                    >
                        <option value="">
                            Select store
                        </option>

                        {stores.map((store) => (
                            <option
                                key={store.id}
                                value={store.id}
                            >
                                {store.name}
                            </option>
                        ))}
                    </select>
                </label>

                <div
                    className="tracking-camera-filter"
                    aria-label="Camera filters"
                >
                    {storeCameras.map((camera) => {
                        const isSelected =
                            selectedCameraIds.some(
                                (id) =>
                                    normalizeId(id) ===
                                    normalizeId(camera.id)
                            );

                        return (
                            <button
                                key={camera.id}
                                type="button"
                                className={
                                    isSelected
                                        ? "active"
                                        : ""
                                }
                                aria-pressed={isSelected}
                                onClick={() =>
                                    toggleCamera(camera.id)
                                }
                            >
                                {camera.name || camera.id}
                            </button>
                        );
                    })}

                    {!storeCameras.length && storeId && (
                        <span className="tracking-empty">
                            No cameras configured for this store.
                        </span>
                    )}
                </div>
            </section>

            <section className="tracking-grid-v2">
                <div className="tracking-feed-grid">
                    {activeCameras.map((camera) => (
                        <CameraCard
                            key={camera.id}
                            camera={camera}
                        />
                    ))}

                    {!activeCameras.length && (
                        <div className="tracking-empty">
                            Select at least one camera to view
                            live tracking.
                        </div>
                    )}
                </div>

                <aside className="tracking-side">
                    <TrackingSummary
                        live={live}
                        points={points}
                        trackerCount={trackerIds.size}
                        latestPoint={latestPoint}
                    />

                    <TrackingEvents points={recentPoints} />
                </aside>
            </section>
        </main>
    );
}

function TrackingSummary({
    live,
    points,
    trackerCount,
    latestPoint,
}) {
    return (
        <div className="tracking-side-card">
            <span>LIVE TRACKING</span>

            <h2>
                <UserRound size={18} />

                {live?.active_visitors ?? 0}

                <span>active visitors</span>
            </h2>

            <Metric
                label="Tracking window"
                value={`${live?.window_seconds ?? 120}s`}
            />

            <Metric
                label="Recent points"
                value={points.length}
            />

            <Metric
                label="Unique trackers"
                value={trackerCount}
            />

            <Metric
                label="Latest tracker"
                value={latestPoint?.tracker_id ?? "—"}
            />
        </div>
    );
}

function TrackingEvents({ points }) {
    return (
        <div className="tracking-side-card">
            <div className="tracking-side-title">
                <span>RECENT TRACKING EVENTS</span>
                <Activity size={14} />
            </div>

            {points.map((point, index) => (
                <div
                    className="tracking-event"
                    key={
                        point.id ??
                        `${point.tracker_id}-${point.timestamp}-${index}`
                    }
                >
                    <b>
                        Tracker {point.tracker_id ?? "—"}
                    </b>

                    <span>
                        {point.camera_id || "camera"} · (
                        {Math.round(Number(point.x) || 0)},{" "}
                        {Math.round(Number(point.y) || 0)})
                    </span>

                    <small>
                        {formatTime(point.timestamp)}
                    </small>
                </div>
            ))}

            {!points.length && (
                <div className="tracking-empty">
                    No tracking points have been persisted
                    for this store yet.
                </div>
            )}
        </div>
    );
}

function CameraCard({ camera }) {
    const [src, setSrc] = useState("");
    const [loading, setLoading] = useState(true);

    const loadSnapshot = useCallback(async () => {
        try {
            setLoading(true);

            const blob = await mappingApi.snapshot(camera.id);

            if (!(blob instanceof Blob)) {
                throw new Error(
                    "Camera snapshot response is not a valid image."
                );
            }

            const nextUrl = URL.createObjectURL(blob);

            setSrc((previousUrl) => {
                if (previousUrl) {
                    URL.revokeObjectURL(previousUrl);
                }

                return nextUrl;
            });
        } catch {
            setSrc((previousUrl) => {
                if (previousUrl) {
                    URL.revokeObjectURL(previousUrl);
                }

                return "";
            });
        } finally {
            setLoading(false);
        }
    }, [camera.id]);

    useEffect(() => {
        loadSnapshot();

        const timer = window.setInterval(
            loadSnapshot,
            SNAPSHOT_INTERVAL
        );

        return () => {
            window.clearInterval(timer);
        };
    }, [loadSnapshot]);

    useEffect(() => {
        return () => {
            setSrc((currentUrl) => {
                if (currentUrl) {
                    URL.revokeObjectURL(currentUrl);
                }

                return "";
            });
        };
    }, []);

    const cameraName = camera.name || camera.id;
    const cameraStatus = camera.status || "offline";

    return (
        <article className="tracking-camera-card">
            <header>
                <strong>{cameraName}</strong>

                <span>{cameraStatus}</span>
            </header>

            {src ? (
                <img
                    src={src}
                    alt={`${cameraName} snapshot`}
                />
            ) : (
                <div className="tracking-camera-placeholder">
                    {loading
                        ? "Loading camera frame..."
                        : "No camera frame available"}
                </div>
            )}

            <footer>
                <span>{camera.id}</span>

                <small>
                    {camera.source_type || "camera"}
                </small>
            </footer>
        </article>
    );
}

function Metric({ label, value }) {
    return (
        <div className="tracking-metric">
            <span>{label}</span>
            <b>{value}</b>
        </div>
    );
}

function formatTime(timestamp) {
    if (!timestamp) {
        return "—";
    }

    const date = new Date(timestamp);

    if (Number.isNaN(date.getTime())) {
        return "—";
    }

    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
}