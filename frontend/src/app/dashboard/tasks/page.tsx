"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ListTodo } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { QuickAddDialog } from "@/components/dashboard/QuickAddDialog";
import { TaskQueue } from "@/components/dashboard/TaskQueue";

export default function TaskQueuePage() {
    const [queueRefreshNonce, setQueueRefreshNonce] = useState(0);

    return (
        <DashboardLayout>
            <div className="space-y-8">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 opacity-0 animate-fade-in">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <Link
                                href="/dashboard"
                                className="p-2 rounded-lg hover:bg-sage-100 dark:hover:bg-sage-800/50 transition-colors"
                            >
                                <ArrowLeft className="w-5 h-5 text-sage-500" />
                            </Link>
                            <h1 className="text-3xl font-bold tracking-tight text-sage-900 dark:text-sage-50 flex items-center gap-2">
                                <ListTodo className="w-7 h-7" />
                                Task Queue
                            </h1>
                        </div>
                        <p className="text-sage-500 dark:text-sage-400 mt-1 ml-12">
                            Review and manage active tasks in your queue.
                        </p>
                    </div>
                    <div className="flex gap-2">
                        <QuickAddDialog onTaskAdded={() => setQueueRefreshNonce((prev) => prev + 1)} />
                    </div>
                </div>

                <section className="opacity-0 animate-fade-in stagger-1">
                    <TaskQueue refreshNonce={queueRefreshNonce} />
                </section>
            </div>
        </DashboardLayout>
    );
}
