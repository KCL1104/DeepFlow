import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { api as backendApi } from '@/lib/api';
import { Shield, ShieldAlert, Waves, Loader2 } from 'lucide-react';

interface FocusStateDisplayProps {
    initialState?: 'FLOW' | 'IDLE'; // Optional now
}

export function FocusStateDisplay({ initialState = 'IDLE' }: FocusStateDisplayProps) {
    const [state, setState] = useState<'FLOW' | 'IDLE'>(initialState);
    const [isLoading, setIsLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState<string>('Just now');

    useEffect(() => {
        const fetchState = async () => {
            try {
                const response = await backendApi.state.get();
                // Map backend state to frontend (SHALLOW maps to IDLE for now visually)
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
        // Poll every 10 seconds for now (until we have SSE)
        const interval = setInterval(fetchState, 10000);
        return () => clearInterval(interval);
    }, []);

    const isFlow = state === 'FLOW';

    return (
        <div className={cn(
            "relative overflow-hidden rounded-2xl p-8 transition-all duration-500 ease-in-out border",
            isFlow
                ? "bg-sage-600 border-sage-500 shadow-xl shadow-sage-900/10"
                : "bg-white dark:bg-sage-900/40 border-sage-200 dark:border-sage-800"
        )}>
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-10 pointer-events-none overflow-hidden">
                <div className={cn(
                    "absolute -top-24 -right-24 w-64 h-64 rounded-full blur-3xl",
                    isFlow ? "bg-amber-400" : "bg-sage-300 dark:bg-sage-700"
                )} />
                <div className={cn(
                    "absolute -bottom-24 -left-24 w-64 h-64 rounded-full blur-3xl",
                    isFlow ? "bg-sage-400" : "bg-sage-200 dark:bg-sage-800"
                )} />
            </div>

            <div className="relative z-10 flex items-center justify-between">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <span className={cn(
                            "px-3 py-1 rounded-full text-xs font-semibold tracking-wider uppercase",
                            isFlow
                                ? "bg-amber-500/20 text-amber-100 border border-amber-500/30"
                                : "bg-sage-200 text-sage-600 dark:bg-sage-800 dark:text-sage-400"
                        )}>
                            Current State
                        </span>
                        <span className="text-xs text-sage-300 dark:text-sage-500">
                            Updated {lastUpdated}
                        </span>
                    </div>

                    <h2 className={cn(
                        "text-4xl md:text-5xl font-bold tracking-tight mb-4",
                        isFlow ? "text-white" : "text-sage-900 dark:text-sage-100"
                    )}>
                        {isFlow ? 'Deep Flow' : 'Ready & Idle'}
                    </h2>

                    <p className={cn(
                        "text-lg max-w-md",
                        isFlow ? "text-sage-100" : "text-sage-500 dark:text-sage-400"
                    )}>
                        {isFlow
                            ? "Sentinel is active. Distractions are being intercepted. Focus on your deep work."
                            : "Sentinel is monitoring. No active tasks detected. Begin a task to enter Flow."
                        }
                    </p>
                </div>

                {/* Visual Indicator */}
                <div className={cn(
                    "hidden md:flex items-center justify-center w-32 h-32 rounded-full border-4 transition-all duration-700",
                    isFlow
                        ? "border-amber-400/30 bg-sage-500 shadow-[0_0_40px_-10px_rgba(251,191,36,0.5)]"
                        : "border-sage-200 dark:border-sage-800 bg-sage-50 dark:bg-sage-800/50"
                )}>
                    {isFlow ? (
                        <Shield className="w-12 h-12 text-amber-300 animate-pulse-soft" />
                    ) : (
                        <Waves className="w-12 h-12 text-sage-400 dark:text-sage-600" />
                    )}
                </div>
            </div>

            {isFlow && (
                <div className="mt-8 pt-6 border-t border-sage-500/30 flex items-center gap-6">
                    <div className="flex flex-col">
                        <span className="text-xs text-sage-300 uppercase tracking-widest">Protection Level</span>
                        <span className="text-amber-200 font-medium flex items-center gap-2">
                            <ShieldAlert size={16} /> High Filtering
                        </span>
                    </div>
                    <div className="flex flex-col">
                        <span className="text-xs text-sage-300 uppercase tracking-widest">Next Break</span>
                        <span className="text-white font-medium">
                            25m remaining
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
}
