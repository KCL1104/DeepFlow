'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, ListTodo, History, Settings, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
    className?: string;
}

const navItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Task Queue', href: '/dashboard/tasks', icon: ListTodo },
    { name: 'History', href: '/dashboard/history', icon: History },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export function Sidebar({ className }: SidebarProps) {
    const pathname = usePathname();

    return (
        <div className={cn(
            "flex flex-col h-full",
            "bg-sage-50 dark:bg-sage-950/80",
            "border-r border-sage-200/50 dark:border-sage-800/30",
            className
        )}>
            {/* Logo */}
            <div className="p-6 flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sage-500 to-sage-600 flex items-center justify-center text-white shadow-lg shadow-sage-500/20">
                    <Zap size={18} fill="currentColor" />
                </div>
                <h1 className="font-bold text-xl text-sage-900 dark:text-sage-50 tracking-tight">
                    DeepFlow
                </h1>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-3 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200",
                                isActive
                                    ? "bg-sage-500/10 dark:bg-sage-400/10 text-sage-700 dark:text-sage-200 shadow-sm"
                                    : "text-sage-600 dark:text-sage-400 hover:bg-sage-100 dark:hover:bg-sage-800/40 hover:text-sage-800 dark:hover:text-sage-200"
                            )}
                        >
                            <Icon size={18} className={cn(
                                isActive && "text-sage-600 dark:text-sage-300"
                            )} />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            {/* Status Footer */}
            <div className="p-4 border-t border-sage-200/50 dark:border-sage-800/30">
                <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-sage-100/50 dark:bg-sage-900/50">
                    <span className="relative flex h-2.5 w-2.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                    </span>
                    <span className="text-xs font-medium text-sage-600 dark:text-sage-400">System Online</span>
                </div>
            </div>
        </div>
    );
}

