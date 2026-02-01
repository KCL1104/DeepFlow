"use client";

import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import type { Task } from '@/lib/api';
import { Clock, CheckCircle2, Loader2, History } from 'lucide-react';

export function HistoryList() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await api.queue.history(20, 0);
                setTasks(response);
            } catch (error) {
                console.error('Failed to fetch history:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchHistory();
    }, []);

    if (isLoading) {
        return (
            <div className="p-12 flex items-center justify-center text-sage-400">
                <Loader2 className="animate-spin w-6 h-6" />
            </div>
        );
    }

    return (
        <div className="bg-white dark:bg-sage-900/40 rounded-2xl border border-sage-200/50 dark:border-sage-700/30 overflow-hidden">
            {/* Header */}
            <div className="p-5 border-b border-sage-100 dark:border-sage-800/50 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <History className="w-5 h-5 text-sage-500 dark:text-sage-400" />
                    <h3 className="font-semibold text-lg text-sage-900 dark:text-sage-50">Task History</h3>
                </div>
                <span className="px-3 py-1.5 rounded-lg bg-sage-100 dark:bg-sage-800/50 text-xs font-semibold text-sage-600 dark:text-sage-300">
                    {tasks.length} Completed
                </span>
            </div>

            {/* Task List */}
            <div className="divide-y divide-sage-100/50 dark:divide-sage-800/30">
                {tasks.length === 0 ? (
                    <div className="p-12 text-center">
                        <CheckCircle2 className="w-12 h-12 text-sage-300 dark:text-sage-600 mx-auto mb-3" />
                        <p className="text-sage-500 dark:text-sage-400 font-medium">No completed tasks yet.</p>
                    </div>
                ) : (
                    tasks.map((task, index) => (
                        <div
                            key={task.id}
                            className={cn(
                                "p-4 hover:bg-sage-50/50 dark:hover:bg-sage-800/20 transition-all duration-200 flex items-center gap-4",
                                "opacity-0 animate-fade-in",
                                index === 0 && "stagger-1",
                                index === 1 && "stagger-2",
                                index === 2 && "stagger-3",
                                index >= 3 && "stagger-4"
                            )}
                        >
                            {/* Completed Icon */}
                            <div className="flex-shrink-0">
                                <CheckCircle2 className="w-5 h-5 text-green-500 dark:text-green-400" />
                            </div>

                            {/* Task Content */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1.5">
                                    <span className={cn(
                                        "text-xs px-2 py-0.5 rounded-md font-semibold",
                                        task.urgency >= 7
                                            ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
                                            : task.urgency >= 4
                                                ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300"
                                                : "bg-sage-100 text-sage-600 dark:bg-sage-800/50 dark:text-sage-400"
                                    )}>
                                        {task.urgency >= 7 ? 'High' : task.urgency >= 4 ? 'Medium' : 'Low'}
                                    </span>
                                    <span className="text-xs text-sage-400 dark:text-sage-500 flex items-center gap-1">
                                        <Clock size={10} />
                                        {new Date(task.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                                <h4 className="text-sm font-medium text-sage-600 dark:text-sage-300 line-through truncate">
                                    {task.title}
                                </h4>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
