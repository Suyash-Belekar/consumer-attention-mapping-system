import { useEffect, useState } from "react";
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

export default function ViewShelves() {
    const navigate = useNavigate();

    const [shelves, setShelves] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchShelves();
    }, []);

    async function fetchShelves() {
        try {
            setLoading(true);
            let data = [];
            try {
                const res = await api.get("/shelves");
                data = res.data;
            } catch (err1) {
                const res = await api.get("/shelves");
                data = res.data;
            }
            setShelves(data);
        } catch (err) {
            console.error(err);
            setError("Unable to load shelves from database.");
        } finally {
            setLoading(false);
        }
    }

    const renderRoiBadge = (shelf) => {
        const poly = shelf.roi_polygon || shelf.zone_coordinates;
        if (!poly) return <span className="text-slate-500 text-xs">No Polygon</span>;
        
        let ptsStr = "";
        if (Array.isArray(poly)) {
            ptsStr = `${poly.length} Vertices (${JSON.stringify(poly.slice(0, 2))}...)`;
        } else {
            ptsStr = String(poly);
        }
        return <span className="inline-flex rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300">{ptsStr}</span>;
    };

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 px-5 py-10">
            <div className="mx-auto max-w-7xl space-y-8">
                <header className="rounded-[32px] border border-slate-800 bg-slate-900/95 px-8 py-8 shadow-2xl shadow-slate-950/40 sm:flex sm:items-center sm:justify-between">
                    <div>
                        <h1 className="text-3xl font-semibold text-white">Registered Shelves & ROI Overview</h1>
                        <p className="mt-3 max-w-2xl text-slate-400">Active computer vision regions of interest and shelf tier mappings.</p>
                    </div>
                    <div className="mt-5 flex flex-wrap gap-3 sm:mt-0">
                        <Button variant="default" onClick={() => navigate("/shelves/add")}>+ Add / Map New Shelf</Button>
                        <Button variant="outline" onClick={() => navigate("/dashboard")}>Dashboard</Button>
                    </div>
                </header>

                <Card className="rounded-[32px] border border-slate-800 bg-slate-900/95 shadow-lg shadow-slate-950/20">
                    <CardHeader>
                        <CardTitle className="text-xl font-semibold text-white">Computer Vision Active Spatial Grids</CardTitle>
                        <CardDescription className="text-slate-400">All configured shelves assigned to YOLOv8 & ByteTrack inference pipelines.</CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-6 px-8 pb-8 pt-3">
                        {loading && (
                            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 text-slate-400">Loading active shelf spatial grids...</div>
                        )}

                        {!loading && error && (
                            <div className="rounded-3xl border border-red-500/20 bg-red-500/10 p-6 text-red-200">{error}</div>
                        )}

                        {!loading && !error && shelves.length === 0 && (
                            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-8 text-center text-slate-400">
                                <p>No active mapped shelves found in database.</p>
                                <Button variant="outline" className="mt-4" onClick={() => navigate("/shelves/add")}>Launch Shelf Visual Setup Hub</Button>
                            </div>
                        )}

                        {!loading && !error && shelves.length > 0 && (
                            <div className="grid gap-6 lg:grid-cols-2">
                                {shelves.map((shelf) => {
                                    const name = shelf.name || shelf.shelf_name || `Shelf #${shelf.id}`;
                                    const storeId = shelf.store_id;
                                    const category = shelf.category || "General Retail";
                                    const camera = shelf.camera_id || "CAM_02_AISLE3";
                                    const tiers = shelf.tier_count || 3;

                                    return (
                                        <div key={shelf.id} className="rounded-[28px] border border-slate-800 bg-slate-950/95 p-6 shadow-lg shadow-slate-950/10">
                                            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                                                <div>
                                                    <div className="text-lg font-semibold text-white">{name}</div>
                                                    <div className="mt-1 text-sm text-slate-400">Store ID: {storeId}</div>
                                                </div>
                                                <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300">📷 {camera}</span>
                                            </div>

                                            <div className="mt-6 grid gap-3 text-sm text-slate-400">
                                                <div className="flex justify-between">
                                                    <span>Category:</span>
                                                    <strong className="text-slate-200">{category}</strong>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Tier Structure:</span>
                                                    <strong className="text-slate-200">{tiers} Tiers</strong>
                                                </div>
                                            </div>

                                            <div className="mt-6 rounded-3xl border border-slate-800 bg-slate-900/80 p-4 text-sm text-slate-300">
                                                <div className="font-semibold text-slate-100 mb-2">ROI Geometry</div>
                                                {renderRoiBadge(shelf)}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
