"use client";

import * as React from "react";
import { Check, AlertCircle, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

export interface Task {
    id: string;
    title: string;
    summary?: string;
    suggestedAction?: string;
    urgency: number;
    estimatedMinutes?: number;
    status: "pending" | "in_progress" | "completed" | "blocked" | "deferred";
}

interface FocusPlayerProps {
    task: Task | null;
    onComplete?: (taskId: string) => void;
    onBlocked?: (taskId: string) => void;
    onDefer?: (taskId: string) => void;
    className?: string;
}

export function FocusPlayer({
    task,
    onComplete,
    onBlocked,
    onDefer,
    className,
}: FocusPlayerProps) {
    if (!task) {
        return (
            <div
                className={cn(
                    "flex flex-col items-center justify-center p-12",
                    "border border-dashed border-neutral-300 dark:border-neutral-700",
                    "rounded-2xl bg-neutral-50 dark:bg-neutral-900",
                    className
                )}
            >
                <div className="text-neutral-400 dark:text-neutral-500 text-lg font-mono">
                    No tasks in queue
                </div>
                <p className="text-sm text-neutral-400 dark:text-neutral-600 mt-2">
                    Enjoy your focus time ✨
                </p>
            </div>
        );
    }

    return (
        <div
            className={cn(
                "flex flex-col p-8",
                "border border-neutral-200 dark:border-neutral-800",
                "rounded-2xl bg-white dark:bg-neutral-900",
                className
            )}
        >
            {/* Task Title */}
            <h2 className="font-mono text-2xl font-medium text-neutral-800 dark:text-neutral-100 text-center">
                {task.title}
            </h2>

            {/* Summary */}
            {task.summary && (
                <p className="mt-4 text-neutral-600 dark:text-neutral-400 text-center max-w-md mx-auto">
                    {task.summary}
                </p>
            )}

            {/* Suggested Action */}
            {task.suggestedAction && (
                <div className="mt-4 p-3 rounded-lg bg-sage-50 dark:bg-sage-900/20 border border-sage-200 dark:border-sage-800">
                    <p className="text-sm text-sage-700 dark:text-sage-300 text-center">
                        💡 {task.suggestedAction}
                    </p>
                </div>
            )}

            {/* Meta Info */}
            {task.estimatedMinutes && (
                <div className="mt-4 flex items-center justify-center gap-1 text-sm text-neutral-500 dark:text-neutral-400">
                    <Clock className="w-4 h-4" />
                    <span>~{task.estimatedMinutes} min</span>
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 mt-8 justify-center">
                <button
                    onClick={() => onComplete?.(task.id)}
                    className={cn(
                        "flex items-center gap-2 px-5 py-2.5 rounded-lg",
                        "bg-sage-600 hover:bg-sage-700 dark:bg-sage-600 dark:hover:bg-sage-700",
                        "text-white font-medium text-sm",
                        "transition-colors"
                    )}
                >
                    <Check className="w-4 h-4" />
                    Complete
                </button>

                <button
                    onClick={() => onBlocked?.(task.id)}
                    className={cn(
                        "flex items-center gap-2 px-5 py-2.5 rounded-lg",
                        "bg-amber-500 hover:bg-amber-600 dark:bg-amber-600 dark:hover:bg-amber-700",
                        "text-white font-medium text-sm",
                        "transition-colors"
                    )}
                >
                    <AlertCircle className="w-4 h-4" />
                    Blocked
                </button>

                <button
                    onClick={() => onDefer?.(task.id)}
                    className={cn(
                        "flex items-center gap-2 px-5 py-2.5 rounded-lg",
                        "border border-neutral-300 dark:border-neutral-700",
                        "hover:bg-neutral-100 dark:hover:bg-neutral-800",
                        "text-neutral-700 dark:text-neutral-300 font-medium text-sm",
                        "transition-colors"
                    )}
                >
                    <Clock className="w-4 h-4" />
                    Defer
                </button>
            </div>
        </div>
    );
}
