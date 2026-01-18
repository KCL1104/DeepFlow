"use client";

import { useEffect, useRef, useCallback, useState } from "react";

interface NotificationData {
    id: string;
    type: string;
    title: string;
    body: string;
    urgency: "normal" | "urgent" | "critical";
    data?: {
        url?: string;
        notification_id?: string;
    };
    options?: NotificationOptions;
}

interface UseNotificationsOptions {
    userId: string;
    backendUrl?: string;
    onNotification?: (notification: NotificationData) => void;
    enabled?: boolean;
}

interface UseNotificationsReturn {
    isConnected: boolean;
    hasPermission: boolean;
    requestPermission: () => Promise<boolean>;
    error: string | null;
}

/**
 * Hook for receiving browser notifications via SSE from the backend.
 * 
 * Usage:
 * ```tsx
 * const { isConnected, hasPermission, requestPermission } = useNotifications({
 *   userId: "user-123",
 *   onNotification: (n) => console.log("Got notification:", n),
 * });
 * ```
 */
export function useNotifications({
    userId,
    backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000",
    onNotification,
    enabled = true,
}: UseNotificationsOptions): UseNotificationsReturn {
    const [isConnected, setIsConnected] = useState(false);
    const [hasPermission, setHasPermission] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    // Check initial permission state
    useEffect(() => {
        if (typeof window !== "undefined" && "Notification" in window) {
            setHasPermission(Notification.permission === "granted");
        }
    }, []);

    // Request notification permission
    const requestPermission = useCallback(async (): Promise<boolean> => {
        if (typeof window === "undefined" || !("Notification" in window)) {
            console.warn("This browser does not support notifications");
            return false;
        }

        if (Notification.permission === "granted") {
            setHasPermission(true);
            return true;
        }

        if (Notification.permission === "denied") {
            console.warn("Notification permission was denied");
            return false;
        }

        const permission = await Notification.requestPermission();
        const granted = permission === "granted";
        setHasPermission(granted);
        return granted;
    }, []);

    // Show browser notification
    const showNotification = useCallback((data: NotificationData) => {
        if (!hasPermission) return;

        const notification = new Notification(data.title, {
            body: data.body,
            icon: data.options?.icon || "/icons/deepflow-icon.png",
            badge: data.options?.badge || "/icons/deepflow-badge.png",
            tag: data.options?.tag || `deepflow-${data.id}`,
            requireInteraction: data.urgency !== "normal",
            silent: data.urgency === "normal",
            ...data.options,
        });

        notification.onclick = () => {
            window.focus();
            if (data.data?.url) {
                window.location.href = data.data.url;
            }
            notification.close();
        };

        // Auto-close after 10 seconds for non-critical
        if (data.urgency !== "critical") {
            setTimeout(() => notification.close(), 10000);
        }
    }, [hasPermission]);

    // Connect to SSE endpoint
    useEffect(() => {
        if (!enabled || !userId) return;

        const sseUrl = `${backendUrl}/api/v1/notifications/stream/${userId}`;

        const connect = () => {
            try {
                const eventSource = new EventSource(sseUrl);
                eventSourceRef.current = eventSource;

                eventSource.addEventListener("connected", (e) => {
                    console.log("[Notifications] SSE connected:", JSON.parse(e.data));
                    setIsConnected(true);
                    setError(null);
                });

                eventSource.addEventListener("notification", (e) => {
                    const data: NotificationData = JSON.parse(e.data);
                    console.log("[Notifications] Received:", data);

                    // Show browser notification
                    showNotification(data);

                    // Call callback if provided
                    onNotification?.(data);
                });

                eventSource.addEventListener("ping", () => {
                    // Keepalive, do nothing
                });

                eventSource.addEventListener("error", (e) => {
                    console.error("[Notifications] SSE error:", e);
                    setIsConnected(false);
                    setError("Connection lost");

                    // Reconnect after 5 seconds
                    setTimeout(connect, 5000);
                });

                eventSource.onerror = () => {
                    setIsConnected(false);
                };

            } catch (err) {
                console.error("[Notifications] Failed to connect:", err);
                setError(err instanceof Error ? err.message : "Failed to connect");
            }
        };

        connect();

        return () => {
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
        };
    }, [enabled, userId, backendUrl, showNotification, onNotification]);

    return {
        isConnected,
        hasPermission,
        requestPermission,
        error,
    };
}
