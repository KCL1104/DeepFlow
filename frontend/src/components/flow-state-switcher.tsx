"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type FlowState = "FLOW" | "SHALLOW" | "IDLE";

interface FlowStateSwitcherProps {
    value?: FlowState;
    onChange?: (state: FlowState) => void;
    className?: string;
}

const stateConfig: Record<FlowState, { label: string; color: string; description: string }> = {
    FLOW: {
        label: "Flow",
        color: "bg-sage-500",
        description: "Deep focus, minimal interruptions",
    },
    SHALLOW: {
        label: "Shallow",
        color: "bg-amber-500",
        description: "Light work, allow some notifications",
    },
    IDLE: {
        label: "Idle",
        color: "bg-neutral-400",
        description: "Available, all notifications enabled",
    },
};

export function FlowStateSwitcher({
    value = "IDLE",
    onChange,
    className,
}: FlowStateSwitcherProps) {
    const states: FlowState[] = ["FLOW", "SHALLOW", "IDLE"];

    return (
        <div className={cn("flex items-center gap-2", className)}>
            {/* Status Indicator */}
            <div className="flex items-center gap-2 mr-2">
                <div
                    className={cn(
                        "w-2.5 h-2.5 rounded-full",
                        stateConfig[value].color,
                        value === "FLOW" && "animate-pulse"
                    )}
                />
                <span className="font-mono text-sm text-neutral-700 dark:text-neutral-300">
                    {value}
                </span>
            </div>

            {/* State Buttons */}
            <div className="flex rounded-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden">
                {states.map((state) => (
                    <button
                        key={state}
                        onClick={() => onChange?.(state)}
                        className={cn(
                            "px-3 py-1.5 text-xs font-medium transition-colors",
                            value === state
                                ? "bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100"
                                : "text-neutral-500 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/50"
                        )}
                        title={stateConfig[state].description}
                    >
                        {stateConfig[state].label}
                    </button>
                ))}
            </div>
        </div>
    );
}
