'use client';

import React from 'react';
import { Sidebar } from './Sidebar';

interface DashboardLayoutProps {
    children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
    return (
        <div className="flex h-screen w-full bg-background text-foreground overflow-hidden">
            {/* Desktop Sidebar */}
            <aside className="hidden md:block w-64 h-full flex-shrink-0">
                <Sidebar />
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col h-full overflow-hidden relative bg-sage-50/30 dark:bg-sage-950">
                {/* Subtle background gradient */}
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-gradient-radial from-sage-200/20 dark:from-sage-700/5 to-transparent rounded-full translate-x-1/3 -translate-y-1/3" />
                    <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-gradient-radial from-sage-300/15 dark:from-sage-600/5 to-transparent rounded-full -translate-x-1/3 translate-y-1/3" />
                </div>

                {/* Content */}
                <div className="relative z-10 flex-1 overflow-y-auto p-4 md:p-8">
                    <div className="max-w-6xl mx-auto h-full">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
}

