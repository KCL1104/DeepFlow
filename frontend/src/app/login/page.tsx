"use client";

import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function LoginPage() {
    const [email, setEmail] = React.useState("");
    const [password, setPassword] = React.useState("");
    const [isLoading, setIsLoading] = React.useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        // TODO: Implement actual authentication
        setTimeout(() => {
            setIsLoading(false);
            window.location.href = "/dashboard";
        }, 1000);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-900 p-4">
            <div className="w-full max-w-sm">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-sage-100 dark:bg-sage-900/30 mb-4">
                        <svg
                            className="w-8 h-8 text-sage-600 dark:text-sage-400"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <path d="M2 12c0-3 2.5-6 6-6 4 0 5 4 8 4 3.5 0 6-3 6-6" />
                            <path d="M2 20c0-3 2.5-6 6-6 4 0 5 4 8 4 3.5 0 6-3 6-6" />
                        </svg>
                    </div>
                    <h1 className="font-mono text-2xl font-semibold text-neutral-800 dark:text-neutral-100">
                        DeepFlow
                    </h1>
                    <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">
                        Protect your focus
                    </p>
                </div>

                {/* Login Card */}
                <div className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 p-6 shadow-sm">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label
                                htmlFor="email"
                                className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1.5"
                            >
                                Email
                            </label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="Enter your email"
                                required
                                className={cn(
                                    "w-full px-3 py-2.5 rounded-lg",
                                    "border border-neutral-200 dark:border-neutral-600",
                                    "bg-white dark:bg-neutral-700",
                                    "text-neutral-800 dark:text-neutral-100",
                                    "placeholder:text-neutral-400 dark:placeholder:text-neutral-500",
                                    "focus:outline-none focus:ring-2 focus:ring-sage-500 focus:border-transparent",
                                    "transition-shadow"
                                )}
                            />
                        </div>

                        <div>
                            <label
                                htmlFor="password"
                                className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1.5"
                            >
                                Password
                            </label>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                                className={cn(
                                    "w-full px-3 py-2.5 rounded-lg",
                                    "border border-neutral-200 dark:border-neutral-600",
                                    "bg-white dark:bg-neutral-700",
                                    "text-neutral-800 dark:text-neutral-100",
                                    "placeholder:text-neutral-400 dark:placeholder:text-neutral-500",
                                    "focus:outline-none focus:ring-2 focus:ring-sage-500 focus:border-transparent",
                                    "transition-shadow"
                                )}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className={cn(
                                "w-full py-2.5 rounded-lg font-medium",
                                "bg-sage-600 hover:bg-sage-700",
                                "text-white",
                                "transition-colors",
                                "disabled:opacity-50 disabled:cursor-not-allowed"
                            )}
                        >
                            {isLoading ? "Signing in..." : "Sign In"}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="relative my-6">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-neutral-200 dark:border-neutral-700" />
                        </div>
                        <div className="relative flex justify-center text-xs">
                            <span className="px-2 bg-white dark:bg-neutral-800 text-neutral-500">
                                or
                            </span>
                        </div>
                    </div>

                    {/* Google Sign In */}
                    <button
                        type="button"
                        className={cn(
                            "w-full py-2.5 rounded-lg font-medium",
                            "border border-neutral-200 dark:border-neutral-600",
                            "bg-white dark:bg-neutral-700",
                            "text-neutral-700 dark:text-neutral-300",
                            "hover:bg-neutral-50 dark:hover:bg-neutral-600",
                            "transition-colors",
                            "flex items-center justify-center gap-2"
                        )}
                    >
                        <svg className="w-5 h-5" viewBox="0 0 24 24">
                            <path
                                fill="#4285F4"
                                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            />
                            <path
                                fill="#34A853"
                                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            />
                            <path
                                fill="#FBBC05"
                                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                            />
                            <path
                                fill="#EA4335"
                                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            />
                        </svg>
                        Continue with Google
                    </button>
                </div>

                {/* Sign Up Link */}
                <p className="text-center text-sm text-neutral-500 dark:text-neutral-400 mt-6">
                    Don&apos;t have an account?{" "}
                    <Link
                        href="/register"
                        className="text-sage-600 dark:text-sage-400 hover:underline"
                    >
                        Sign up
                    </Link>
                </p>
            </div>
        </div>
    );
}
