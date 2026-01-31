import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { api as backendApi } from '@/lib/api';
import { Shield, ShieldAlert, Waves, Loader2 } from 'lucide-react';

interface FocusStateDisplayProps {
    initialState?: 'FLOW' | 'IDLE';
}

export function FocusStateDisplay({ initialState = 'IDLE' }: FocusStateDisplayProps) {
    const [state, setState] = useState<'FLOW' | 'IDLE'>(initialState);
    const [isLoading, setIsLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState<string>('Just now');

    useEffect(() => {
        const fetchState = async () => {
            try {
                const response = await backendApi.state.get();
                const mappedState = response.state === 'FLOW' ? 'FLOW' : 'IDLE';
                setState(mappedState);
                setLastUpdated(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
            } catch (error) {
                console.error('Failed to fetch state:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchState();
        const interval = setInterval(fetchState, 10000);
        return () => clearInterval(interval);
    }, []);

    const isFlow = state === 'FLOW';

    return (
        <div className={cn(
            "relative overflow-hidden rounded-2xl p-8 transition-all duration-500 ease-out",
            isFlow
                ? "bg-gradient-to-br from-sage-600 via-sage-500 to-sage-600 shadow-2xl shadow-sage-500/20"
                : "bg-white dark:bg-sage-900/40 border border-sage-200/50 dark:border-sage-700/30"
        )}>
            {/* Background Effects */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                {/* Gradient orbs */}
                <div className={cn(
                    "absolute -top-32 -right-32 w-80 h-80 rounded-full blur-3xl transition-opacity duration-700",
                    isFlow
                        ? "bg-amber-400/30 opacity-100"
                        : "bg-sage-300/20 dark:bg-sage-600/10 opacity-50"
                )} />
                <div className={cn(
                    "absolute -bottom-32 -left-32 w-80 h-80 rounded-full blur-3xl transition-opacity duration-700",
                    isFlow
                        ? "bg-sage-400/40 opacity-100"
                        : "bg-sage-200/30 dark:bg-sage-700/10 opacity-50"
                )} />
            </div>

            <div className="relative z-10 flex items-center justify-between gap-8">
                <div className="flex-1">
                    {/* Status Badge */}
                    <div className="flex items-center gap-3 mb-4">
                        <span className={cn(
                            "px-3 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase transition-colors",
                            isFlow
                                ? "bg-amber-500/20 text-amber-100 border border-amber-400/30"
                                : "bg-sage-100 dark:bg-sage-800/50 text-sage-600 dark:text-sage-300 border border-sage-200 dark:border-sage-700/50"
                        )}>
                            Current State
                        </span>
                        <span className={cn(
                            "text-xs font-medium",
                            isFlow ? "text-sage-200" : "text-sage-400 dark:text-sage-500"
                        )}>
                            Updated {lastUpdated}
                        </span>
                    </div>

                    {/* Main Title */}
                    <h2 className={cn(
                        "text-4xl md:text-5xl font-bold tracking-tight mb-4 transition-colors",
                        isFlow ? "text-white" : "text-sage-900 dark:text-sage-50"
                    )}>
                        {isFlow ? 'Deep Flow' : 'Ready & Idle'}
                    </h2>

                    {/* Description */}
                    <p className={cn(
                        "text-lg max-w-lg leading-relaxed",
                        isFlow ? "text-sage-100/90" : "text-sage-500 dark:text-sage-400"
                    )}>
                        {isFlow
                            ? "Sentinel is active. Distractions are being intercepted. Focus on your deep work."
                            : "Sentinel is monitoring. No active tasks detected. Begin a task to enter Flow."
                        }
                    </p>
                </div>

                {/* Visual Indicator */}
                <div className={cn(
                    "hidden md:flex items-center justify-center w-36 h-36 rounded-full transition-all duration-700",
                    isFlow
                        ? "bg-sage-400/30 border-4 border-amber-400/40 animate-glow"
                        : "bg-sage-100 dark:bg-sage-800/30 border-4 border-sage-200/50 dark:border-sage-700/30"
                )}>
                    {isFlow ? (
                        <Shield className="w-14 h-14 text-amber-200 animate-pulse-soft" />
                    ) : (
                        <Waves className="w-14 h-14 text-sage-400 dark:text-sage-500" />
                    )}
                </div>
            </div>

            {/* Flow Mode Stats */}
            {isFlow && (
                <div className="relative z-10 mt-8 pt-6 border-t border-white/10 flex items-center gap-8">
                    <div className="flex flex-col gap-1">
                        <span className="text-xs text-sage-200/70 uppercase tracking-widest font-medium">Protection Level</span>
                        <span className="text-amber-200 font-semibold flex items-center gap-2">
                            <ShieldAlert size={16} />
                            High Filtering
                        </span>
                    </div>
                    <div className="flex flex-col gap-1">
                        <span className="text-xs text-sage-200/70 uppercase tracking-widest font-medium">Next Break</span>
                        <span className="text-white font-semibold">
                            25m remaining
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
}

