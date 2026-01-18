"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import type { Task } from "./focus-player";

interface QueueSidebarProps {
    tasks: Task[];
    currentTaskId?: string;
    onSelectTask?: (taskId: string) => void;
    className?: string;
}

const urgencyColor = (urgency: number): string => {
    if (urgency >= 8) return "border-l-red-500";
    if (urgency >= 5) return "border-l-amber-500";
    return "border-l-neutral-300 dark:border-l-neutral-600";
};

export function QueueSidebar({
    tasks,
    currentTaskId,
    onSelectTask,
    className,
}: QueueSidebarProps) {
    const queuedTasks = tasks.filter(
        (t) => t.id !== currentTaskId && t.status === "pending"
    );

    return (
        <aside
            className={cn(
                "w-64 p-4 border-r border-neutral-200 dark:border-neutral-800",
                "bg-neutral-50 dark:bg-neutral-900/50",
                className
            )}
        >
            <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-500 dark:text-neutral-400 mb-4">
                Upcoming
            </h3>

            {queuedTasks.length === 0 ? (
                <p className="text-sm text-neutral-400 dark:text-neutral-500">
                    Queue is empty
                </p>
            ) : (
                <ul className="space-y-2">
                    {queuedTasks.slice(0, 5).map((task) => (
                        <li key={task.id}>
                            <button
                                onClick={() => onSelectTask?.(task.id)}
                                className={cn(
                                    "w-full text-left p-3 rounded-lg",
                                    "border-l-2",
                                    urgencyColor(task.urgency),
                                    "bg-white dark:bg-neutral-800",
                                    "hover:bg-neutral-100 dark:hover:bg-neutral-700",
                                    "transition-colors",
                                    "group"
                                )}
                            >
                                <div className="font-mono text-sm text-neutral-800 dark:text-neutral-200 line-clamp-2">
                                    {task.title}
                                </div>
                                {task.estimatedMinutes && (
                                    <div className="text-xs text-neutral-400 dark:text-neutral-500 mt-1">
                                        ~{task.estimatedMinutes} min
                                    </div>
                                )}
                            </button>
                        </li>
                    ))}
                </ul>
            )}

            {queuedTasks.length > 5 && (
                <p className="text-xs text-neutral-400 dark:text-neutral-500 mt-3 text-center">
                    +{queuedTasks.length - 5} more tasks
                </p>
            )}
        </aside>
    );
}
