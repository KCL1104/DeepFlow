"use client";

import { useState, useEffect } from "react";
import { useNotifications } from "@/hooks/useNotifications";

interface NotificationProviderProps {
    userId: string;
    children: React.ReactNode;
}

/**
 * Notification Provider Component
 * 
 * Wraps the app to handle notification permissions and SSE connection.
 * Automatically prompts for permission when user enters the dashboard.
 */
export function NotificationProvider({ userId, children }: NotificationProviderProps) {
    const [showPermissionPrompt, setShowPermissionPrompt] = useState(false);
    const [isEnabled, setIsEnabled] = useState(false);

    const { isConnected, hasPermission, requestPermission, error } = useNotifications({
        userId,
        enabled: isEnabled,
        onNotification: (notification) => {
            console.log("[App] Notification received:", notification.title);
        },
    });

    // Enable SSE connection when permission is granted
    useEffect(() => {
        if (hasPermission) {
            setIsEnabled(true);
        }
    }, [hasPermission]);

    // Check if we should prompt for permission
    useEffect(() => {
        if (typeof window !== "undefined" && "Notification" in window) {
            if (Notification.permission === "default") {
                // Show prompt after a short delay
                const timer = setTimeout(() => setShowPermissionPrompt(true), 2000);
                return () => clearTimeout(timer);
            }
        }
    }, []);

    const handleRequestPermission = async () => {
        await requestPermission();
        setShowPermissionPrompt(false);
    };

    const handleDismiss = () => {
        setShowPermissionPrompt(false);
    };

    return (
        <>
            {children}

            {/* Permission Prompt Modal */}
            {showPermissionPrompt && (
                <div className="fixed bottom-4 right-4 z-50 max-w-sm bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4">
                    <div className="flex items-start gap-3">
                        <div className="flex-shrink-0">
                            <svg className="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                            </svg>
                        </div>
                        <div className="flex-1">
                            <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                                Enable Notifications
                            </h3>
                            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                                Get instant alerts for urgent tasks even when DeepFlow is in the background.
                            </p>
                            <div className="mt-3 flex gap-2">
                                <button
                                    onClick={handleRequestPermission}
                                    className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    Enable
                                </button>
                                <button
                                    onClick={handleDismiss}
                                    className="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md"
                                >
                                    Not now
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Connection Status Indicator (for debugging) */}
            {process.env.NODE_ENV === "development" && (
                <div className="fixed bottom-4 left-4 z-50 text-xs">
                    <div className={`px-2 py-1 rounded ${isConnected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                        SSE: {isConnected ? "Connected" : "Disconnected"}
                        {error && ` (${error})`}
                    </div>
                </div>
            )}
        </>
    );
}
