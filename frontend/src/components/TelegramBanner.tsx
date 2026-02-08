"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { X } from "lucide-react";
import { supabase } from "@/lib/supabase";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface TelegramBindingResponse {
    is_linked: boolean;
    telegram_id: number | null;
}

/**
 * Telegram Bot Banner Component
 * 
 * Displays a banner prompting users to connect with the Telegram bot
 * for receiving push notifications.
 * Only shows if the user has NOT linked their Telegram account.
 */
export function TelegramBanner() {
    const [isLinked, setIsLinked] = useState<boolean | null>(null);
    const [isDismissed, setIsDismissed] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const checkTelegramBinding = async () => {
            try {
                // Get auth token
                const { data } = await supabase.auth.getSession();
                const token = data.session?.access_token;

                if (!token) {
                    setIsLinked(false);
                    setIsLoading(false);
                    return;
                }

                // Call API
                const response = await fetch(`${API_BASE_URL}/user/telegram-binding`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const result: TelegramBindingResponse = await response.json();
                    setIsLinked(result.is_linked);
                } else {
                    setIsLinked(false);
                }
            } catch (error) {
                console.error("Failed to check Telegram binding:", error);
                setIsLinked(false);
            } finally {
                setIsLoading(false);
            }
        };

        // Check if user has dismissed the banner this session
        const dismissed = sessionStorage.getItem("telegram_banner_dismissed");
        if (dismissed) {
            setIsDismissed(true);
            setIsLoading(false);
            return;
        }

        checkTelegramBinding();
    }, []);

    const handleDismiss = () => {
        setIsDismissed(true);
        sessionStorage.setItem("telegram_banner_dismissed", "true");
    };

    // Don't show if: loading, linked, or dismissed
    if (isLoading || isLinked || isDismissed) {
        return null;
    }

    return (
        <div className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-4 py-3">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <svg
                        className="w-6 h-6"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                    >
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z" />
                    </svg>
                    <span className="font-medium">
                        📱 Connect Telegram to receive push notifications
                    </span>
                </div>
                <div className="flex items-center gap-3">
                    <Link
                        href="https://t.me/DeepFlow_Notify_Bot"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-4 py-1.5 bg-white text-blue-600 rounded-full text-sm font-medium hover:bg-blue-50 transition-colors"
                    >
                        Connect @DeepFlow_Notify_Bot
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                    </Link>
                    <button
                        onClick={handleDismiss}
                        className="p-1.5 hover:bg-white/20 rounded-full transition-colors"
                        aria-label="Dismiss banner"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}
