"use client";

import { useState, useEffect } from "react";
import { useNotifications } from "@/hooks/useNotifications";
import { Bell } from "lucide-react";

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
                <div className="fixed bottom-4 right-4 z-50 max-w-sm bg-white dark:bg-sage-900 rounded-2xl shadow-xl border border-sage-200 dark:border-sage-700/50 p-5 opacity-0 animate-fade-in">
                    <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-sage-500 to-sage-600 flex items-center justify-center">
                            <Bell className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-sm font-semibold text-sage-900 dark:text-sage-50">
                                Enable Notifications
                            </h3>
                            <p className="mt-1 text-sm text-sage-500 dark:text-sage-400">
                                Get instant alerts for urgent tasks even when DeepFlow is in the background.
                            </p>
                            <div className="mt-4 flex gap-2">
                                <button
                                    onClick={handleRequestPermission}
                                    className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-sage-600 to-sage-500 rounded-xl hover:from-sage-500 hover:to-sage-400 transition-all shadow-md shadow-sage-500/20"
                                >
                                    Enable
                                </button>
                                <button
                                    onClick={handleDismiss}
                                    className="px-4 py-2 text-sm font-medium text-sage-600 dark:text-sage-300 hover:bg-sage-100 dark:hover:bg-sage-800 rounded-xl transition-colors"
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
                    <div className={`px-2 py-1 rounded-lg ${isConnected ? "bg-sage-100 text-sage-800 dark:bg-sage-900 dark:text-sage-300" : "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300"}`}>
                        SSE: {isConnected ? "Connected" : "Disconnected"}
                        {error && ` (${error})`}
                    </div>
                </div>
            )}
        </>
    );
}

