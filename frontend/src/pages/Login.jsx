import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    ArrowRight,
    BarChart3,
    Camera,
    Eye,
    Loader2,
    ShieldCheck,
} from "lucide-react";

import api from "../services/api";
import "./Login.css";

const CAPABILITIES = [
    {
        icon: Camera,
        title: "Multi-camera operations",
        text: "Connect feeds and map store spaces from one workspace.",
    },
    {
        icon: Eye,
        title: "Attention intelligence",
        text: "Turn shopper movement and dwell into actionable insight.",
    },
    {
        icon: BarChart3,
        title: "Product performance",
        text: "Measure product attention, attractiveness and recommendations.",
    },
];

const INITIAL_FORM = {
    email: "",
    password: "",
};

function getLoginError(error) {
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

    if (!error?.response) {
        return "Unable to connect to the server. Please try again.";
    }

    if (error.response.status === 401) {
        return "Invalid email or password.";
    }

    return "Unable to sign in. Please try again.";
}

function validateForm(form) {
    const email = form.email.trim();

    if (!email) {
        return "Email address is required.";
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return "Please enter a valid email address.";
    }

    if (!form.password) {
        return "Password is required.";
    }

    return null;
}

function Brand({ mobile = false }) {
    return (
        <div
            className={
                mobile
                    ? "login-mobile-brand"
                    : "login-brand"
            }
        >
            <span className="login-brand-mark">CAM</span>

            <div>
                <strong>Attention Mapping</strong>
                <span>Enterprise console</span>
            </div>
        </div>
    );
}

function CapabilityList() {
    return (
        <div className="login-capabilities">
            {CAPABILITIES.map(
                ({ icon: Icon, title, text }) => (
                    <div
                        className="login-capability"
                        key={title}
                    >
                        <span className="login-capability-icon">
                            <Icon size={17} aria-hidden="true" />
                        </span>

                        <div>
                            <strong>{title}</strong>
                            <span>{text}</span>
                        </div>
                    </div>
                )
            )}
        </div>
    );
}

function LoginField({
    id,
    label,
    type,
    value,
    placeholder,
    autoComplete,
    disabled,
    onChange,
}) {
    return (
        <label
            className="login-field"
            htmlFor={id}
        >
            <span>{label}</span>

            <input
                id={id}
                name={id}
                type={type}
                value={value}
                placeholder={placeholder}
                autoComplete={autoComplete}
                disabled={disabled}
                onChange={onChange}
                required
            />
        </label>
    );
}

export default function Login() {
    const navigate = useNavigate();

    const [form, setForm] = useState(INITIAL_FORM);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const updateField = (field, value) => {
        setForm((current) => ({
            ...current,
            [field]: value,
        }));

        if (error) {
            setError("");
        }
    };

    const handleLogin = async (event) => {
        event.preventDefault();

        if (loading) {
            return;
        }

        const validationError = validateForm(form);

        if (validationError) {
            setError(validationError);
            return;
        }

        setLoading(true);
        setError("");

        try {
            const response = await api.post("/auth/login", {
                email: form.email.trim(),
                password: form.password,
            });

            const accessToken =
                response?.data?.access_token;

            if (!accessToken) {
                throw new Error(
                    "Authentication token was not returned."
                );
            }

            localStorage.setItem(
                "token",
                accessToken
            );

            navigate("/dashboard", {
                replace: true,
            });
        } catch (requestError) {
            setError(getLoginError(requestError));
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="login-page">
            <section
                className="login-shell"
                aria-label="Consumer Attention Mapping sign in"
            >
                {/* Brand / Product information */}
                <aside className="login-brand-panel">
                    <Brand />

                    <div className="login-brand-copy">
                        <span className="login-eyebrow">
                            Consumer intelligence platform
                        </span>

                        <h1>
                            See what shoppers notice.
                            <br />
                            Understand why.
                        </h1>

                        <p>
                            A unified workspace for camera
                            operations, spatial mapping,
                            shopper behavior, attention
                            heatmaps and product intelligence.
                        </p>
                    </div>

                    <CapabilityList />

                    <div className="login-status">
                        <ShieldCheck
                            size={16}
                            aria-hidden="true"
                        />

                        <span>
                            Secure enterprise workspace
                        </span>
                    </div>
                </aside>

                {/* Authentication */}
                <section className="login-form-panel">
                    <div className="login-form-wrap">
                        <Brand mobile />

                        <header className="login-heading">
                            <span className="login-section-label">
                                Welcome back
                            </span>

                            <h2>
                                Sign in to your workspace
                            </h2>

                            <p>
                                Access your stores, cameras,
                                mappings and analytics.
                            </p>
                        </header>

                        {error && (
                            <div
                                className="login-error"
                                role="alert"
                                aria-live="polite"
                            >
                                {error}
                            </div>
                        )}

                        <form
                            className="login-form"
                            onSubmit={handleLogin}
                            noValidate
                        >
                            <LoginField
                                id="email"
                                label="Email address"
                                type="email"
                                placeholder="name@example.com"
                                autoComplete="email"
                                value={form.email}
                                disabled={loading}
                                onChange={(event) =>
                                    updateField(
                                        "email",
                                        event.target.value
                                    )
                                }
                            />

                            <LoginField
                                id="password"
                                label="Password"
                                type="password"
                                placeholder="Enter your password"
                                autoComplete="current-password"
                                value={form.password}
                                disabled={loading}
                                onChange={(event) =>
                                    updateField(
                                        "password",
                                        event.target.value
                                    )
                                }
                            />

                            <button
                                className="login-submit"
                                type="submit"
                                disabled={loading}
                                aria-busy={loading}
                            >
                                {loading ? (
                                    <>
                                        <Loader2
                                            size={17}
                                            className="login-spinner"
                                            aria-hidden="true"
                                        />

                                        <span>
                                            Signing in...
                                        </span>
                                    </>
                                ) : (
                                    <>
                                        <span>
                                            Sign in
                                        </span>

                                        <ArrowRight
                                            size={17}
                                            aria-hidden="true"
                                        />
                                    </>
                                )}
                            </button>
                        </form>

                        <div className="login-register">
                            <span>
                                Don't have an account?
                            </span>

                            <Link to="/register">
                                Create account
                            </Link>
                        </div>

                        <p className="login-footer">
                            Consumer Attention Mapping System
                            {" · "}
                            Retail operations intelligence
                        </p>
                    </div>
                </section>
            </section>
        </main>
    );
}