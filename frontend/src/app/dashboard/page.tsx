"use client";

import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { FocusStateDisplay } from '@/components/dashboard/FocusStateDisplay';
import { TaskQueue } from '@/components/dashboard/TaskQueue';
import { QuickAddDialog } from '@/components/dashboard/QuickAddDialog';
import { Calendar, TrendingUp, Activity } from 'lucide-react';

export default function DashboardPage() {
    return (
        <DashboardLayout>
            <div className="space-y-8">

                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 opacity-0 animate-fade-in">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight text-sage-900 dark:text-sage-50">
                            Dashboard
                        </h1>
                        <p className="text-sage-500 dark:text-sage-400 mt-1">
                            Monitor your cognitive load and task flow.
                        </p>
                    </div>
                    {/* Quick Actions */}
                    <div className="flex gap-2">
                        <QuickAddDialog />
                    </div>
                </div>

                {/* Focus State - Main Visualization */}
                <section className="opacity-0 animate-fade-in stagger-1">
                    <FocusStateDisplay initialState="IDLE" />
                </section>

                {/* Two Column Layout for Tasks & Stats */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left: Task Queue (2 cols) */}
                    <div className="lg:col-span-2 space-y-6 opacity-0 animate-fade-in stagger-2">
                        <TaskQueue />

                        {/* Calendar Placeholder */}
                        <div className="p-8 rounded-2xl border border-dashed border-sage-300/50 dark:border-sage-700/30 flex flex-col items-center justify-center text-center gap-3 bg-sage-50/30 dark:bg-sage-900/20">
                            <Calendar className="w-8 h-8 text-sage-400 dark:text-sage-600" />
                            <span className="text-sage-500 dark:text-sage-400 font-medium">Calendar / Schedule Integration Coming Soon</span>
                        </div>
                    </div>

                    {/* Right: Stats (1 col) */}
                    <div className="lg:col-span-1 space-y-6 opacity-0 animate-fade-in stagger-3">
                        {/* Daily Stats */}
                        <div className="bg-white dark:bg-sage-900/40 rounded-2xl border border-sage-200/50 dark:border-sage-700/30 p-6">
                            <div className="flex items-center gap-2 mb-5">
                                <TrendingUp className="w-5 h-5 text-sage-500 dark:text-sage-400" />
                                <h3 className="font-semibold text-sage-900 dark:text-sage-50">Daily Focus</h3>
                            </div>
                            <div className="space-y-5">
                                <div>
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-sage-600 dark:text-sage-400">Deep Work</span>
                                        <span className="font-semibold text-sage-800 dark:text-sage-200">2h 15m</span>
                                    </div>
                                    <div className="w-full h-2.5 bg-sage-100 dark:bg-sage-800/50 rounded-full overflow-hidden">
                                        <div className="h-full bg-gradient-to-r from-sage-500 to-sage-400 w-[35%] rounded-full" />
                                    </div>
                                </div>

                                <div>
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-sage-600 dark:text-sage-400">Context Switches</span>
                                        <span className="font-semibold text-sage-800 dark:text-sage-200">12</span>
                                    </div>
                                    <div className="w-full h-2.5 bg-sage-100 dark:bg-sage-800/50 rounded-full overflow-hidden">
                                        <div className="h-full bg-gradient-to-r from-amber-400 to-amber-300 w-[60%] rounded-full" />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Agent Status */}
                        <div className="bg-gradient-to-br from-sage-700 via-sage-600 to-sage-700 text-sage-50 rounded-2xl p-6 relative overflow-hidden shadow-lg shadow-sage-900/20">
                            {/* Decorative elements */}
                            <div className="absolute top-0 right-0 w-40 h-40 bg-sage-500/30 rounded-full translate-x-12 -translate-y-12 blur-2xl" />
                            <div className="absolute bottom-0 left-0 w-24 h-24 bg-amber-400/10 rounded-full -translate-x-6 translate-y-6 blur-xl" />

                            <div className="relative z-10">
                                <div className="flex items-center gap-2 mb-2">
                                    <Activity className="w-5 h-5 text-sage-200" />
                                    <h3 className="font-semibold">Agent Status</h3>
                                </div>
                                <p className="text-sm text-sage-200/80 mb-4 leading-relaxed">
                                    DeepFlow Sentinel is active and processing signals.
                                </p>
                                <div className="flex items-center gap-2 text-xs font-mono bg-black/20 px-3 py-2.5 rounded-lg">
                                    <span className="relative flex h-2 w-2">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-400"></span>
                                    </span>
                                    <span className="text-sage-100">Listening for Telegram updates...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </DashboardLayout>
    );
}

