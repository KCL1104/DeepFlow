"use client";

import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { FocusStateDisplay } from '@/components/dashboard/FocusStateDisplay';
import { TaskQueue } from '@/components/dashboard/TaskQueue';
import { QuickAddDialog } from '@/components/dashboard/QuickAddDialog';

export default function DashboardPage() {
    return (
        <DashboardLayout>
            <div className="space-y-8">

                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight text-sage-900 dark:text-sage-50">
                            Dashboard
                        </h1>
                        <p className="text-sage-500 dark:text-sage-400">
                            Monitor your cognitive load and task flow.
                        </p>
                    </div>
                    {/* Quick Actions */}
                    <div className="flex gap-2">
                        <QuickAddDialog />
                    </div>
                </div>

                {/* Focus State - Main Visualization */}
                <section>
                    <FocusStateDisplay initialState="IDLE" />
                </section>

                {/* Two Column Layout for Tasks & Stats */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left: Task Queue (2 cols) */}
                    <div className="lg:col-span-2 space-y-6">
                        <TaskQueue />

                        {/* Secondary Queue Placeholder (e.g. Next Up) */}
                        <div className="p-6 rounded-xl border border-dashed border-sage-300 dark:border-sage-700 flex items-center justify-center text-sage-400">
                            <span>Calendar / Schedule Integration Coming Soon</span>
                        </div>
                    </div>

                    {/* Right: Stats (1 col) */}
                    <div className="lg:col-span-1 space-y-6">
                        {/* Daily Stats Placeholder */}
                        <div className="bg-white dark:bg-sage-900/40 rounded-xl border border-sage-200 dark:border-sage-800 p-6">
                            <h3 className="font-semibold text-sage-900 dark:text-sage-50 mb-4">Daily Focus</h3>
                            <div className="space-y-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-sage-600 dark:text-sage-400">Deep Work</span>
                                    <span className="font-medium">2h 15m</span>
                                </div>
                                <div className="w-full h-2 bg-sage-100 rounded-full overflow-hidden">
                                    <div className="h-full bg-sage-500 w-[35%]" />
                                </div>

                                <div className="flex justify-between text-sm mt-4">
                                    <span className="text-sage-600 dark:text-sage-400">Context Switches</span>
                                    <span className="font-medium">12</span>
                                </div>
                                <div className="w-full h-2 bg-sage-100 rounded-full overflow-hidden">
                                    <div className="h-full bg-amber-400 w-[60%]" />
                                </div>
                            </div>
                        </div>

                        {/* Agent Status */}
                        <div className="bg-sage-900 text-sage-50 rounded-xl p-6 relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-sage-800 rounded-full translate-x-10 -translate-y-10" />
                            <h3 className="font-semibold mb-2 relative z-10">Agent Status</h3>
                            <p className="text-sm text-sage-300 mb-4 relative z-10">
                                DeepFlow Sentinel is active and processing signals.
                            </p>
                            <div className="flex items-center gap-2 text-xs font-mono bg-black/20 p-2 rounded relative z-10">
                                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                                Listening for Telegram updates...
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </DashboardLayout>
    );
}
