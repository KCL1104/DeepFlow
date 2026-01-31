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
    return "border-l-sage-300 dark:border-l-sage-600";
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
                "w-64 p-4 border-r border-sage-200 dark:border-sage-800",
                "bg-sage-50 dark:bg-sage-900/50",
                className
            )}
        >
            <h3 className="text-xs font-semibold uppercase tracking-wider text-sage-500 dark:text-sage-400 mb-4">
                Upcoming
            </h3>

            {queuedTasks.length === 0 ? (
                <p className="text-sm text-sage-400 dark:text-sage-500">
                    Queue is empty
                </p>
            ) : (
                <ul className="space-y-2">
                    {queuedTasks.slice(0, 5).map((task) => (
                        <li key={task.id}>
                            <button
                                onClick={() => onSelectTask?.(task.id)}
                                className={cn(
                                    "w-full text-left p-3 rounded-xl",
                                    "border-l-2",
                                    urgencyColor(task.urgency),
                                    "bg-white dark:bg-sage-800/50",
                                    "hover:bg-sage-100 dark:hover:bg-sage-700/50",
                                    "transition-colors",
                                    "group"
                                )}
                            >
                                <div className="font-medium text-sm text-sage-800 dark:text-sage-200 line-clamp-2">
                                    {task.title}
                                </div>
                                {task.estimatedMinutes && (
                                    <div className="text-xs text-sage-400 dark:text-sage-500 mt-1">
                                        ~{task.estimatedMinutes} min
                                    </div>
                                )}
                            </button>
                        </li>
                    ))}
                </ul>
            )}

            {queuedTasks.length > 5 && (
                <p className="text-xs text-sage-400 dark:text-sage-500 mt-3 text-center">
                    +{queuedTasks.length - 5} more tasks
                </p>
            )}
        </aside>
    );
}

