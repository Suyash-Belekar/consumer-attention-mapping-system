import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

import { Button } from "@/components/ui/button";

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";

export default function ViewStore() {
    const navigate = useNavigate();

    const [stores, setStores] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchStores();
    }, []);

    async function fetchStores() {
        try {
            setLoading(true);
            setError("");

            const response = await api.get("/stores");
            setStores(response.data);
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || "Unable to load stores.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 px-6 py-10">
            <div className="mx-auto max-w-6xl space-y-8">
                <div className="rounded-[32px] border border-slate-800 bg-slate-900/95 px-8 py-8 shadow-2xl shadow-slate-950/40 sm:flex sm:items-center sm:justify-between">
                    <div>
                        <h1 className="text-3xl font-semibold text-white">Store Management</h1>
                        <p className="mt-3 text-slate-400">View all registered retail stores.</p>
                    </div>
                    <div className="mt-6 flex flex-wrap gap-3 sm:mt-0">
                        <Button onClick={() => navigate("/stores/add")}>Add Store</Button>
                        <Button variant="outline" onClick={() => navigate("/dashboard")}>Dashboard</Button>
                    </div>
                </div>

                <Card className="rounded-[32px] border border-slate-800 bg-slate-900/95 shadow-lg shadow-slate-950/20">
                    <CardHeader>
                        <CardTitle className="text-2xl font-semibold text-white">Store Records</CardTitle>
                        <CardDescription className="text-slate-400">
                            {loading
                                ? "All stores currently registered in PostgreSQL."
                                : `${stores.length} store${stores.length === 1 ? "" : "s"} currently registered in PostgreSQL.`}
                        </CardDescription>
                    </CardHeader>

                    <CardContent>
                        {loading && (
                            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 text-slate-400">
                                Loading stores...
                            </div>
                        )}

                        {!loading && error && (
                            <div className="flex flex-col gap-4 rounded-3xl border border-red-500/20 bg-red-500/10 p-6 text-red-200 sm:flex-row sm:items-center sm:justify-between">
                                <span>{error}</span>
                                <Button size="sm" variant="outline" onClick={fetchStores}>
                                    Retry
                                </Button>
                            </div>
                        )}

                        {!loading && !error && stores.length === 0 && (
                            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 text-slate-400">
                                No stores found.
                            </div>
                        )}

                        {!loading && !error && stores.length > 0 && (
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>ID</TableHead>
                                        <TableHead>Store Name</TableHead>
                                        <TableHead>Location</TableHead>
                                    </TableRow>
                                </TableHeader>

                                <TableBody>
                                    {stores.map((store) => (
                                        <TableRow key={store.id}>
                                            <TableCell>{store.id}</TableCell>
                                            <TableCell>{store.store_name}</TableCell>
                                            <TableCell>{store.location}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}