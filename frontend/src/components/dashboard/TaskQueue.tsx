import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';
import type { Task } from '@/lib/api';
import { Clock, Circle, Loader2 } from 'lucide-react';

export function TaskQueue() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchQueue = async () => {
            try {
                const response = await api.queue.get();
                setTasks(response.queue);
            } catch (error) {
                console.error('Failed to fetch queue:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchQueue();
        // Poll every 5s
        const interval = setInterval(fetchQueue, 5000);
        return () => clearInterval(interval);
    }, []);

    if (isLoading) {
        return (
            <div className="p-8 flex items-center justify-center text-sage-400">
                <Loader2 className="animate-spin w-6 h-6" />
            </div>
        );
    }

    return (
        <div className="bg-white dark:bg-sage-900/40 rounded-xl border border-sage-200 dark:border-sage-800 overflow-hidden">
            <div className="p-6 border-b border-sage-100 dark:border-sage-800 flex items-center justify-between">
                <h3 className="font-semibold text-lg text-sage-900 dark:text-sage-50">Task Queue</h3>
                <span className="px-2.5 py-1 rounded-md bg-sage-100 dark:bg-sage-800 text-xs font-medium text-sage-600 dark:text-sage-300">
                    {tasks.length} Pending
                </span>
            </div>

            <div className="divide-y divide-sage-100 dark:divide-sage-800/50">
                {tasks.length === 0 ? (
                    <div className="p-8 text-center text-sage-400 text-sm">
                        Queue is empty. Great job!
                    </div>
                ) : (
                    tasks.map((task) => (
                        <div key={task.id} className="p-4 hover:bg-sage-50/50 dark:hover:bg-sage-800/30 transition-colors flex items-center gap-4 group">
                            {/* Status Icon */}
                            <div className="flex-shrink-0">
                                {task.status === 'in_progress' ? (
                                    <div className="w-5 h-5 rounded-full border-2 border-amber-400 flex items-center justify-center">
                                        <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                                    </div>
                                ) : (
                                    <Circle className="w-5 h-5 text-sage-300 dark:text-sage-600" />
                                )}
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className={cn(
                                        "text-xs px-1.5 py-0.5 rounded font-medium",
                                        task.urgency >= 7 ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300" :
                                            task.urgency >= 4 ? "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300" :
                                                "bg-sage-100 text-sage-600 dark:bg-sage-800 dark:text-sage-400"
                                    )}>
                                        {task.urgency >= 7 ? 'High' : task.urgency >= 4 ? 'Medium' : 'Low'}
                                    </span>
                                    <span className="text-xs text-sage-400 flex items-center gap-1">
                                        <Clock size={10} /> {new Date(task.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                                <h4 className={cn(
                                    "text-sm font-medium truncate",
                                    task.status === 'completed' ? "text-sage-400 line-through" : "text-sage-800 dark:text-sage-200"
                                )}>
                                    {task.title}
                                </h4>
                            </div>

                            <div className="text-xs text-sage-400 font-mono">
                                System
                            </div>
                        </div>
                    ))
                )}
            </div>

            <div className="p-3 bg-sage-50 dark:bg-sage-900/20 text-center border-t border-sage-100 dark:border-sage-800">
                <button className="text-xs font-medium text-sage-500 hover:text-sage-800 dark:hover:text-sage-200 transition-colors">
                    View All Tasks
                </button>
            </div>
        </div>
    );
}
