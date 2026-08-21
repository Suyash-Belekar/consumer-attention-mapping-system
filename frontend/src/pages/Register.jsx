import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AlertCircle, Loader2 } from "lucide-react";

import api from "../services/api";
import "./Register.css";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";

const ROLES = [
    { value: "1", label: "SuperAdmin" },
    { value: "2", label: "StoreManager" },
    { value: "3", label: "Analyst" },
];

const INITIAL_FORM = {
    email: "",
    password: "",
    roleId: "1",
};

const getErrorMessage = (error) => {
    const detail = error?.response?.data?.detail;

    if (typeof detail === "string") {
        return detail;
    }

    if (Array.isArray(detail)) {
        const messages = detail
            .map((item) => item?.msg)
            .filter(Boolean);

        return messages.length > 0
            ? messages.join(", ")
            : "Registration failed.";
    }

    return "Registration failed. Please try again.";
};

const validateForm = ({ email, password, roleId }) => {
    const normalizedEmail = email.trim();

    if (!normalizedEmail) {
        return "Email address is required.";
    }

    if (!normalizedEmail.includes("@")) {
        return "Please enter a valid email address.";
    }

    if (!password) {
        return "Password is required.";
    }

    if (password.length < 8) {
        return "Password must be at least 8 characters.";
    }

    if (!roleId) {
        return "Please select a role.";
    }

    return null;
};

function Register() {
    const navigate = useNavigate();

    const [form, setForm] = useState(INITIAL_FORM);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const updateField = (field, value) => {
        setForm((currentForm) => ({
            ...currentForm,
            [field]: value,
        }));

        if (error) {
            setError("");
        }
    };

    const handleRegister = async (event) => {
        event.preventDefault();

        const validationError = validateForm(form);

        if (validationError) {
            setError(validationError);
            return;
        }

        setLoading(true);
        setError("");

        try {
            await api.post("/auth/register", {
                email: form.email.trim(),
                password: form.password,
                role_id: Number(form.roleId),
            });

            navigate("/", { replace: true });
        } catch (requestError) {
            setError(getErrorMessage(requestError));
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="register-page">
            <Card className="register-card">
                <CardHeader className="register-header">
                    <p className="register-brand">
                        Consumer Attention Mapping
                    </p>

                    <CardTitle className="register-title">
                        Create your account
                    </CardTitle>

                    <CardDescription className="register-description">
                        Register a new user account to manage stores,
                        shelves and analytics.
                    </CardDescription>
                </CardHeader>

                <CardContent className="register-content">
                    {error && (
                        <Alert
                            variant="destructive"
                            className="register-alert"
                        >
                            <AlertCircle className="register-alert-icon" />

                            <div>
                                <AlertTitle>
                                    Registration Error
                                </AlertTitle>

                                <AlertDescription>
                                    {error}
                                </AlertDescription>
                            </div>
                        </Alert>
                    )}

                    <form
                        className="register-form"
                        onSubmit={handleRegister}
                        noValidate
                    >
                        <div className="register-fields">
                            <div className="register-field">
                                <Label htmlFor="email">
                                    Email Address
                                </Label>

                                <Input
                                    id="email"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    placeholder="name@example.com"
                                    value={form.email}
                                    disabled={loading}
                                    onChange={(event) =>
                                        updateField(
                                            "email",
                                            event.target.value
                                        )
                                    }
                                    required
                                />
                            </div>

                            <div className="register-field">
                                <Label htmlFor="password">
                                    Password
                                </Label>

                                <Input
                                    id="password"
                                    name="password"
                                    type="password"
                                    autoComplete="new-password"
                                    placeholder="Enter your password"
                                    value={form.password}
                                    disabled={loading}
                                    minLength={8}
                                    onChange={(event) =>
                                        updateField(
                                            "password",
                                            event.target.value
                                        )
                                    }
                                    required
                                />
                            </div>
                        </div>

                        <div className="register-field">
                            <Label htmlFor="role">
                                Role
                            </Label>

                            <Select
                                value={form.roleId}
                                disabled={loading}
                                onValueChange={(value) =>
                                    updateField("roleId", value)
                                }
                            >
                                <SelectTrigger
                                    id="role"
                                    className="register-select"
                                >
                                    <SelectValue placeholder="Select a role" />
                                </SelectTrigger>

                                <SelectContent className="register-select-content">
                                    {ROLES.map(({ value, label }) => (
                                        <SelectItem
                                            key={value}
                                            value={value}
                                        >
                                            {label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <Button
                            type="submit"
                            className="register-submit"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Creating...
                                </>
                            ) : (
                                "Create Account"
                            )}
                        </Button>
                    </form>
                </CardContent>

                <CardFooter className="register-footer">
                    <span>Already have an account?</span>

                    <Link
                        to="/"
                        className="register-login-link"
                    >
                        Login
                    </Link>
                </CardFooter>
            </Card>
        </main>
    );
}

export default Register;