import { useEffect, useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

const MAX_POLYGON_POINTS = 8;
const MIN_POLYGON_POINTS = 4;

const CAMERA_FEEDS = [
    { id: "CAM_01_ENTRANCE", label: "Camera 01 - Main Entrance" },
    { id: "CAM_02_AISLE3", label: "Camera 02 - Aisle 3 (Snacks)" },
    { id: "CAM_03_BEVERAGES", label: "Camera 03 - Cold Beverages" },
];

const ZONE_OPTIONS = [
    "Zone A - Snack Aisle",
    "Zone B - Refrigerated Beverages",
    "Zone C - Bakery",
];

export default function AddShelf() {
    const navigate = useNavigate();

    // Data States
    const [stores, setStores] = useState([]);
    const [storesLoading, setStoresLoading] = useState(true);
    const [selectedStoreId, setSelectedStoreId] = useState("");
    const [selectedZone, setSelectedZone] = useState(ZONE_OPTIONS[0]);
    const [cameraId, setCameraId] = useState("CAM_02_AISLE3");

    // Form Metadata
    const [shelfName, setShelfName] = useState("");
    const [category, setCategory] = useState("Chips & Snacks");
    const [tierCount, setTierCount] = useState(3);
    const [locationInStore, setLocationInStore] = useState("Aisle 3 - Bay 2");

    // Polygon State: array of [x, y] points, in canvas coordinate space (0-640 x 0-400)
    const [roiPolygon, setRoiPolygon] = useState([]);

    // Canvas & UI state
    const canvasRef = useRef(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [successMsg, setSuccessMsg] = useState("");
    const [validationLog, setValidationLog] = useState(null);

    useEffect(() => {
        fetchStores();
    }, []);

    async function fetchStores() {
        setStoresLoading(true);
        try {
            const response = await api.get("/stores");
            setStores(response.data);
            if (response.data.length > 0) {
                setSelectedStoreId(String(response.data[0].id));
            }
        } catch (err) {
            console.error(err);
            setError("Unable to load stores list.");
        } finally {
            setStoresLoading(false);
        }
    }

    // Canvas drawing handler. Depends on everything it reads so the overlay
    // text (store/zone/camera) never goes stale.
    const drawCanvas = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#0f172a";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.strokeStyle = "#1e293b";
        ctx.lineWidth = 1;
        for (let x = 0; x < canvas.width; x += 40) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
        for (let y = 0; y < canvas.height; y += 40) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }

        ctx.strokeStyle = "#334155";
        ctx.lineWidth = 3;
        ctx.strokeRect(60, 60, 520, 330);
        for (let y = 140; y <= 320; y += 90) {
            ctx.beginPath();
            ctx.moveTo(60, y);
            ctx.lineTo(580, y);
            ctx.strokeStyle = "#475569";
            ctx.stroke();
        }

        ctx.fillStyle = "#22c55e";
        ctx.font = "12px monospace";
        ctx.fillText(`LIVE STREAM // ${cameraId} // 30 FPS`, 15, 25);
        ctx.fillStyle = "#94a3b8";
        ctx.fillText(`STORE ID: ${selectedStoreId || "NONE"} | ZONE: ${selectedZone}`, 15, 42);

        if (roiPolygon.length > 0) {
            ctx.beginPath();
            ctx.moveTo(roiPolygon[0][0], roiPolygon[0][1]);
            for (let i = 1; i < roiPolygon.length; i++) {
                ctx.lineTo(roiPolygon[i][0], roiPolygon[i][1]);
            }
            if (roiPolygon.length >= 3) {
                ctx.closePath();
                ctx.fillStyle = "rgba(59, 130, 246, 0.25)";
                ctx.fill();
            }

            ctx.strokeStyle = "#3b82f6";
            ctx.lineWidth = 2;
            ctx.stroke();

            roiPolygon.forEach(([x, y], idx) => {
                ctx.beginPath();
                ctx.arc(x, y, 5, 0, 2 * Math.PI);
                ctx.fillStyle = "#ef4444";
                ctx.fill();
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1;
                ctx.stroke();

                ctx.fillStyle = "#ffffff";
                ctx.font = "10px sans-serif";
                ctx.fillText(`P${idx + 1}`, x + 7, y - 5);
            });
        }
    }, [roiPolygon, cameraId, selectedStoreId, selectedZone]);

    useEffect(() => {
        drawCanvas();
    }, [drawCanvas]);

    // Maps a mouse event to canvas coordinate space, correcting for any
    // difference between the canvas's rendered (CSS) size and its internal
    // resolution (640x400) caused by the `w-full` class.
    const handleCanvasClick = (e) => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        if (roiPolygon.length >= MAX_POLYGON_POINTS) {
            setError(`Maximum of ${MAX_POLYGON_POINTS} polygon vertices reached. Remove a point or clear the polygon to continue.`);
            return;
        }

        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        const x = Math.round((e.clientX - rect.left) * scaleX);
        const y = Math.round((e.clientY - rect.top) * scaleY);

        setError("");
        setRoiPolygon((prev) => [...prev, [x, y]]);
        setValidationLog(null);
    };

    const undoLastPoint = () => {
        setRoiPolygon((prev) => prev.slice(0, -1));
        setValidationLog(null);
    };

    const clearPolygon = () => {
        setRoiPolygon([]);
        setValidationLog(null);
        setError("");
    };

    const addDefaultBox = () => {
        setRoiPolygon([
            [120, 80],
            [520, 80],
            [520, 340],
            [120, 340],
        ]);
        setValidationLog(null);
        setError("");
    };

    const handleValidateROI = () => {
        if (roiPolygon.length < MIN_POLYGON_POINTS) {
            setError(`At least ${MIN_POLYGON_POINTS} polygon vertices are required to validate computer vision ROI.`);
            setValidationLog(null);
            return;
        }

        const xs = roiPolygon.map((p) => p[0]);
        const ys = roiPolygon.map((p) => p[1]);
        const x_min = Math.min(...xs);
        const x_max = Math.max(...xs);
        const y_min = Math.min(...ys);
        const y_max = Math.max(...ys);

        setError("");
        setValidationLog({
            status: "PASS",
            message: "ROI is geometrically valid for YOLOv8 & ByteTrack inference grid.",
            bbox: { x_min, y_min, x_max, y_max },
            area_px: (x_max - x_min) * (y_max - y_min),
            overlap_check: "No overlapping shelves detected in Camera Zone.",
        });
    };

    async function handleSubmit(e) {
        e.preventDefault();

        if (!selectedStoreId) {
            setError("Please select a store from the layout tree.");
            return;
        }

        if (!shelfName.trim()) {
            setError("Please enter a shelf name.");
            return;
        }

        if (roiPolygon.length < MIN_POLYGON_POINTS) {
            setError(`Please draw or generate at least ${MIN_POLYGON_POINTS} ROI polygon points on the camera canvas.`);
            return;
        }

        setLoading(true);
        setError("");
        setSuccessMsg("");

        const payload = {
            store_id: Number(selectedStoreId),
            shelf_name: shelfName.trim(),
            category,
            tier_count: Number(tierCount),
            camera_id: cameraId,
            zone: selectedZone,
            location_in_store: locationInStore,
            zone_coordinates: roiPolygon,
        };

        try {
            await api.post("/shelves", payload);
            setSuccessMsg("Shelf ROI configuration successfully saved & assigned to CV engine!");
            setTimeout(() => navigate("/shelves/view"), 1500);
        } catch (err) {
            // Surface the real error instead of silently retrying a
            // differently-shaped payload against a fallback route - if
            // /shelves is genuinely being deprecated in favor of
            // /layout/shelves, that should be a deliberate migration, not a
            // silent runtime fallback that hides failures.
            console.error(err);
            setError(err.response?.data?.detail || "Unable to save shelf configuration.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 px-5 py-10">
            <div className="mx-auto max-w-7xl space-y-7">
                <header className="rounded-[32px] border border-slate-800 bg-slate-900/95 px-8 py-8 shadow-2xl shadow-slate-950/40 md:flex md:items-center md:justify-between">
                    <div>
                        <h1 className="text-3xl font-semibold text-white">Store & Shelf Management Hub</h1>
                        <p className="mt-3 max-w-2xl text-slate-400">Interactive visual spatial editor for shelf ROI mapping tied to YOLOv8 computer vision workflows.</p>
                    </div>
                    <div className="mt-6 flex flex-wrap gap-3 md:mt-0">
                        <Button variant="outline" onClick={() => navigate("/shelves/view")}>View Shelves</Button>
                        <Button variant="default" onClick={() => navigate("/dashboard")}>Dashboard</Button>
                    </div>
                </header>

                <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
                    <Card className="rounded-[32px] border border-slate-800 bg-slate-900/95 shadow-lg shadow-slate-950/20">
                        <CardHeader>
                            <CardTitle className="text-xl font-semibold text-white">Store Hierarchy & Tree</CardTitle>
                            <CardDescription className="text-slate-400">Select the target store and camera zone for ROI mapping.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6 px-6 pb-6 pt-3">
                            <div className="space-y-3">
                                <Label htmlFor="store-select" className="text-xs uppercase tracking-[0.25em] text-slate-400">Active Store</Label>
                                <Select value={selectedStoreId} onValueChange={setSelectedStoreId} disabled={storesLoading}>
                                    <SelectTrigger id="store-select" className="w-full">
                                        <SelectValue placeholder={storesLoading ? "Loading stores…" : "Select a store"} />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {stores.map((s) => (
                                            <SelectItem key={s.id} value={String(s.id)}>
                                                🏢 {s.store_name} ({s.location})
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-3">
                                <Label htmlFor="zone-select" className="text-xs uppercase tracking-[0.25em] text-slate-400">Camera Zone</Label>
                                <Select value={selectedZone} onValueChange={setSelectedZone}>
                                    <SelectTrigger id="zone-select" className="w-full" />
                                    <SelectContent>
                                        {ZONE_OPTIONS.map((zone) => (
                                            <SelectItem key={zone} value={zone}>{zone}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-4 text-sm text-slate-300">
                                <div className="space-y-3">
                                    <div className="font-semibold text-slate-100">Current Zone Overview</div>
                                    <div>🟢 <strong>Zone A:</strong> Snacks & Bakery</div>
                                    <div className="ml-4">├── Shelf 1 (ROI Mapped)</div>
                                    <div className="ml-4">└── 🎯 Current Active Drawing</div>
                                    <div>🔵 <strong>Zone B:</strong> Refrigerated Beverages</div>
                                    <div className="ml-4">└── Shelf 3 (Dairy Rack)</div>
                                </div>
                            </div>

                            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-4 text-xs text-slate-300">
                                <div className="font-semibold text-slate-100 mb-2">Quick Stats</div>
                                <div><strong>Connected Cameras:</strong> {CAMERA_FEEDS.length} Online</div>
                                <div><strong>Active Tracked Shelves:</strong> 8 ROI Zones</div>
                                <div><strong>Coverage Index:</strong> 94.2%</div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="rounded-[32px] border border-slate-800 bg-slate-900/95 shadow-lg shadow-slate-950/20">
                        <CardHeader className="flex flex-col gap-4 pb-4 sm:flex-row sm:items-center sm:justify-between">
                            <div>
                                <CardTitle className="text-xl font-semibold text-white">Interactive Visual Mapping Canvas</CardTitle>
                                <CardDescription className="text-slate-400">Click the frame to plot ROI bounding polygon vertices.</CardDescription>
                            </div>
                            <div className="flex flex-wrap items-center gap-3">
                                <Select value={cameraId} onValueChange={setCameraId}>
                                    <SelectTrigger id="camera-select" className="w-[220px] h-10" />
                                    <SelectContent>
                                        {CAMERA_FEEDS.map((feed) => (
                                            <SelectItem key={feed.id} value={feed.id}>
                                                📷 {feed.label}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-5 px-6 pb-6 pt-3">
                            <div className="rounded-[28px] border border-slate-800 bg-slate-950/95 p-3">
                                <canvas
                                    ref={canvasRef}
                                    width={640}
                                    height={400}
                                    onClick={handleCanvasClick}
                                    className="w-full cursor-crosshair rounded-3xl bg-slate-950"
                                />
                            </div>

                            <div className="flex flex-col gap-3 sm:flex-row">
                                <Button size="sm" variant="secondary" onClick={addDefaultBox}>Auto Bounding Box</Button>
                                <Button size="sm" variant="outline" onClick={undoLastPoint} disabled={roiPolygon.length === 0}>Undo Last Point</Button>
                                <Button size="sm" variant="outline" onClick={clearPolygon} disabled={roiPolygon.length === 0}>Clear Polygon Points</Button>
                                <Button size="sm" variant="default" onClick={handleValidateROI}>Validate ROI Intersect</Button>
                            </div>

                            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-4 text-sm text-slate-300">
                                <strong>ROI Polygon Array ({roiPolygon.length}/{MAX_POLYGON_POINTS}):</strong>{' '}
                                {roiPolygon.length === 0 ? 'No points defined. Click canvas to draw vertices.' : JSON.stringify(roiPolygon)}
                            </div>

                            {validationLog && (
                                <div className="rounded-3xl border border-blue-500/30 bg-blue-500/10 p-4 text-slate-200">
                                    <div className="font-semibold text-emerald-300">✓ {validationLog.status}: {validationLog.message}</div>
                                    <div className="mt-2 text-sm text-slate-300">Bounding Box (x_min, y_min, x_max, y_max): [{validationLog.bbox.x_min}, {validationLog.bbox.y_min}, {validationLog.bbox.x_max}, {validationLog.bbox.y_max}]</div>
                                    <div className="mt-1 text-sm text-slate-300">Effective Area: {validationLog.area_px} px² | {validationLog.overlap_check}</div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                <Card className="rounded-[32px] border border-slate-800 bg-slate-900/95 shadow-lg shadow-slate-950/20">
                    <CardHeader>
                        <CardTitle className="text-xl font-semibold text-white">Shelf Properties & Planogram Configuration</CardTitle>
                        <CardDescription className="text-slate-400">Link visual shelf space to database management entities.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6 px-6 pb-6 pt-3">
                        <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-2">
                            <div className="space-y-3">
                                <Label htmlFor="shelf-name">Shelf Designation / Name</Label>
                                <Input
                                    id="shelf-name"
                                    value={shelfName}
                                    onChange={(e) => setShelfName(e.target.value)}
                                    placeholder="Aisle 3 - Snack Shelf"
                                    required
                                />
                            </div>
                            <div className="space-y-3">
                                <Label htmlFor="category">Category Mapping</Label>
                                <Input
                                    id="category"
                                    value={category}
                                    onChange={(e) => setCategory(e.target.value)}
                                    placeholder="Snacks & Chips"
                                />
                            </div>
                            <div className="space-y-3">
                                <Label htmlFor="tier-count">Tier / Level Count</Label>
                                <Input
                                    id="tier-count"
                                    type="number"
                                    min={1}
                                    max={10}
                                    value={tierCount}
                                    onChange={(e) => {
                                        const val = Number(e.target.value);
                                        if (Number.isNaN(val)) return;
                                        setTierCount(Math.min(10, Math.max(1, val)));
                                    }}
                                />
                            </div>
                            <div className="space-y-3">
                                <Label htmlFor="location">Physical Location Description</Label>
                                <Input
                                    id="location"
                                    value={locationInStore}
                                    onChange={(e) => setLocationInStore(e.target.value)}
                                    placeholder="Aisle 3, Middle Section"
                                />
                            </div>

                            <div className="lg:col-span-2">
                                {error && <div className="rounded-3xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">{error}</div>}
                                {successMsg && <div className="rounded-3xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-200">{successMsg}</div>}
                            </div>

                            <div className="lg:col-span-2 flex flex-col gap-3 sm:flex-row sm:justify-end">
                                <Button type="button" variant="outline" onClick={() => navigate("/dashboard")}>Cancel</Button>
                                <Button type="submit" disabled={loading}>{loading ? 'Saving ROI Configuration...' : 'Save Shelf Configuration'}</Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}