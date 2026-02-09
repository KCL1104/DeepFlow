"use client";

import React from "react";
import Link from "next/link";
import { ArrowLeft, SlidersHorizontal, ShieldCheck, Bell, Bot } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";

const SETTINGS_ITEMS = [
    {
        title: "Focus Preferences",
        description: "Tune focus states, scheduling windows, and interruption thresholds.",
        icon: SlidersHorizontal,
    },
    {
        title: "Notification Rules",
        description: "Configure delivery channels and urgent alert behavior.",
        icon: Bell,
    },
    {
        title: "Automation Guardrails",
        description: "Define what the agent can auto-prioritize or defer.",
        icon: Bot,
    },
];

export default function SettingsPage() {
    return (
        <DashboardLayout>
            <div className="space-y-8">
                <div className="opacity-0 animate-fade-in">
                    <div className="flex items-center gap-3 mb-2">
                        <Link
                            href="/dashboard"
                            className="p-2 rounded-lg hover:bg-sage-100 dark:hover:bg-sage-800/50 transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5 text-sage-500" />
                        </Link>
                        <h1 className="text-3xl font-bold tracking-tight text-sage-900 dark:text-sage-50">
                            Settings
                        </h1>
                    </div>
                    <p className="text-sage-500 dark:text-sage-400 mt-1 ml-12">
                        Configuration options are being finalized. Preview available controls below.
                    </p>
                </div>

                <section className="opacity-0 animate-fade-in stagger-1">
                    <div className="rounded-2xl border border-sage-200/60 dark:border-sage-700/40 bg-white dark:bg-sage-900/40 overflow-hidden">
                        <div className="p-5 border-b border-sage-100 dark:border-sage-800/60 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <ShieldCheck className="w-5 h-5 text-sage-500" />
                                <h2 className="font-semibold text-sage-900 dark:text-sage-50">Configuration Preview</h2>
                            </div>
                            <span className="text-xs font-semibold px-2 py-1 rounded-md bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300">
                                Coming Soon
                            </span>
                        </div>
                        <div className="divide-y divide-sage-100/60 dark:divide-sage-800/40">
                            {SETTINGS_ITEMS.map((item) => {
                                const Icon = item.icon;
                                return (
                                    <div key={item.title} className="p-5 flex items-start gap-4">
                                        <div className="w-10 h-10 rounded-lg bg-sage-100 dark:bg-sage-800/50 flex items-center justify-center">
                                            <Icon className="w-5 h-5 text-sage-600 dark:text-sage-300" />
                                        </div>
                                        <div className="space-y-1">
                                            <h3 className="font-medium text-sage-900 dark:text-sage-50">{item.title}</h3>
                                            <p className="text-sm text-sage-500 dark:text-sage-400">{item.description}</p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </section>
            </div>
        </DashboardLayout>
    );
}
