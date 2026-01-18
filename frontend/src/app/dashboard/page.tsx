"use client";

import * as React from "react";
import { User, LogOut, Settings } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { FlowStateSwitcher } from "@/components/flow-state-switcher";
import { PomodoroTimer } from "@/components/pomodoro-timer";
import { FocusPlayer, type Task } from "@/components/focus-player";
import { QueueSidebar } from "@/components/queue-sidebar";
import { cn } from "@/lib/utils";

// Mock data for demonstration
const mockTasks: Task[] = [
    {
        id: "1",
        title: "Refactor authentication module",
        summary: "The authentication module needs to be updated to support OAuth 2.0",
        suggestedAction: "Review the current implementation and create a migration plan",
        urgency: 7,
        estimatedMinutes: 45,
        status: "in_progress",
    },
    {
        id: "2",
        title: "Write unit tests for API",
        urgency: 5,
        estimatedMinutes: 30,
        status: "pending",
    },
    {
        id: "3",
        title: "Update documentation",
        urgency: 3,
        estimatedMinutes: 20,
        status: "pending",
    },
    {
        id: "4",
        title: "Prepare weekly report",
        urgency: 4,
        estimatedMinutes: 15,
        status: "pending",
    },
];

type FlowState = "FLOW" | "SHALLOW" | "IDLE";

export default function DashboardPage() {
    const [flowState, setFlowState] = React.useState<FlowState>("IDLE");
    const [tasks, setTasks] = React.useState<Task[]>(mockTasks);
    const [isMenuOpen, setIsMenuOpen] = React.useState(false);

    const currentTask = tasks.find((t) => t.status === "in_progress") || null;

    const handleComplete = (taskId: string) => {
        setTasks((prev) =>
            prev.map((t) =>
                t.id === taskId
                    ? { ...t, status: "completed" as const }
                    : t.status === "pending" && prev.findIndex((x) => x.id === t.id) === prev.findIndex((x) => x.status === "pending")
                        ? { ...t, status: "in_progress" as const }
                        : t
            )
        );
    };

    const handleBlocked = (taskId: string) => {
        setTasks((prev) =>
            prev.map((t) =>
                t.id === taskId ? { ...t, status: "blocked" as const } : t
            )
        );
    };

    const handleDefer = (taskId: string) => {
        setTasks((prev) =>
            prev.map((t) =>
                t.id === taskId ? { ...t, status: "deferred" as const } : t
            )
        );
    };

    return (
        <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900 flex">
            {/* Sidebar */}
            <QueueSidebar tasks={tasks} currentTaskId={currentTask?.id} />

            {/* Main Content */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <header className="h-14 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between px-6">
                    {/* Logo */}
                    <div className="flex items-center gap-2">
                        <svg
                            className="w-6 h-6 text-sage-600 dark:text-sage-400"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <path d="M2 12c0-3 2.5-6 6-6 4 0 5 4 8 4 3.5 0 6-3 6-6" />
                            <path d="M2 20c0-3 2.5-6 6-6 4 0 5 4 8 4 3.5 0 6-3 6-6" />
                        </svg>
                        <span className="font-mono font-semibold text-neutral-800 dark:text-neutral-200">
                            DeepFlow
                        </span>
                    </div>

                    {/* Center: Flow State */}
                    <FlowStateSwitcher value={flowState} onChange={setFlowState} />

                    {/* Right: User Menu */}
                    <div className="flex items-center gap-3">
                        <ThemeToggle />

                        {/* User Dropdown */}
                        <div className="relative">
                            <button
                                onClick={() => setIsMenuOpen(!isMenuOpen)}
                                className={cn(
                                    "w-9 h-9 rounded-full flex items-center justify-center",
                                    "bg-sage-100 dark:bg-sage-900/30",
                                    "hover:bg-sage-200 dark:hover:bg-sage-900/50",
                                    "transition-colors"
                                )}
                            >
                                <User className="w-4 h-4 text-sage-700 dark:text-sage-400" />
                            </button>

                            {isMenuOpen && (
                                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 shadow-lg py-1 z-50">
                                    <button className="w-full px-4 py-2 text-left text-sm text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 flex items-center gap-2">
                                        <Settings className="w-4 h-4" />
                                        Settings
                                    </button>
                                    <button className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 flex items-center gap-2">
                                        <LogOut className="w-4 h-4" />
                                        Sign out
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </header>

                {/* Main Area */}
                <main className="flex-1 flex flex-col items-center justify-center p-8">
                    {/* Pomodoro Timer */}
                    <PomodoroTimer workMinutes={30} breakMinutes={5} className="mb-8" />

                    {/* Current Task */}
                    <FocusPlayer
                        task={currentTask}
                        onComplete={handleComplete}
                        onBlocked={handleBlocked}
                        onDefer={handleDefer}
                        className="w-full max-w-lg"
                    />
                </main>
            </div>
        </div>
    );
}
