"use client";

import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { HistoryList } from '@/components/dashboard/HistoryList';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function HistoryPage() {
    return (
        <DashboardLayout>
            <div className="space-y-8">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 opacity-0 animate-fade-in">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <Link
                                href="/dashboard"
                                className="p-2 rounded-lg hover:bg-sage-100 dark:hover:bg-sage-800/50 transition-colors"
                            >
                                <ArrowLeft className="w-5 h-5 text-sage-500" />
                            </Link>
                            <h1 className="text-3xl font-bold tracking-tight text-sage-900 dark:text-sage-50">
                                History
                            </h1>
                        </div>
                        <p className="text-sage-500 dark:text-sage-400 mt-1 ml-12">
                            View your completed tasks and past activities.
                        </p>
                    </div>
                </div>

                {/* History List */}
                <section className="opacity-0 animate-fade-in stagger-1">
                    <HistoryList />
                </section>
            </div>
        </DashboardLayout>
    );
}
