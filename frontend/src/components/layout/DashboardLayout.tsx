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
            <main className="flex-1 flex flex-col h-full overflow-hidden relative">
                {/* Mobile Header could go here */}

                <div className="flex-1 overflow-y-auto p-4 md:p-8">
                    <div className="max-w-6xl mx-auto h-full">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
}
