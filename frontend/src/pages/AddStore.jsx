import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../services/api";

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function AddStore() {
    const navigate = useNavigate();

    const [storeName, setStoreName] = useState("");
    const [location, setLocation] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(e) {
        e.preventDefault();

        const trimmedStoreName = storeName.trim();
        const trimmedLocation = location.trim();

        if (!trimmedStoreName) {
            setError("Please enter a store name.");
            return;
        }

        if (!trimmedLocation) {
            setError("Please enter a store location.");
            return;
        }

        setLoading(true);
        setError("");

        try {
            await api.post("/stores", {
                store_name: trimmedStoreName,
                location: trimmedLocation,
            });

            alert("Store added successfully!");

            navigate("/stores/view");
        } catch (err) {
            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Unable to save store."
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 px-5 py-10">

            <div className="rounded-[32px] border border-slate-800 bg-slate-900/95 px-8 py-8 shadow-2xl shadow-slate-950/40 sm:flex sm:items-center sm:justify-between">

                <div>
                    <h1 className="text-3xl font-semibold text-white">
                        Add Store
                    </h1>

                    <p className="mt-3 max-w-2xl text-slate-400">
                        Register a new retail store.
                    </p>
                </div>

                <Button
                    variant="outline"
                    className="mt-6 sm:mt-0"
                    onClick={() => navigate("/dashboard")}
                >
                    Dashboard
                </Button>

            </div>

            <Card className="rounded-[32px] border border-slate-800 bg-slate-900/95 shadow-lg shadow-slate-950/20">

                <CardHeader>

                    <CardTitle>
                        Store Information
                    </CardTitle>

                    <CardDescription>
                        Enter the details of the retail store.
                    </CardDescription>

                </CardHeader>

                <CardContent>

                    <form
                        className="space-y-6"
                        onSubmit={handleSubmit}
                    >

                        <div className="space-y-2">

                            <Label>
                                Store Name
                            </Label>

                            <Input
                                value={storeName}
                                placeholder="Reliance Smart"
                                onChange={(e) =>
                                    setStoreName(e.target.value)
                                }
                                required
                            />

                        </div>

                        <div className="space-y-2">

                            <Label>
                                Location
                            </Label>

                            <Input
                                value={location}
                                placeholder="Pune"
                                onChange={(e) =>
                                    setLocation(e.target.value)
                                }
                                required
                            />

                        </div>

                        {error && <div className="rounded-3xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>}

                        <CardFooter className="px-0">
                            <Button type="submit" className="w-full rounded-3xl py-3" disabled={loading}>
                                {loading ? "Saving..." : "Save Store"}
                            </Button>
                        </CardFooter>

                    </form>

                </CardContent>

            </Card>

        </div>
    );
}