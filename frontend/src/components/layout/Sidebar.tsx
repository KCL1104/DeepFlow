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
        <div className={cn("flex flex-col h-full bg-sage-50 dark:bg-sage-900 border-r border-sage-200 dark:border-sage-800", className)}>
            <div className="p-6 flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-sage-600 flex items-center justify-center text-white">
                    <Zap size={20} fill="currentColor" />
                </div>
                <h1 className="font-bold text-xl text-sage-900 dark:text-sage-50 tracking-tight">
                    DeepFlow
                </h1>
            </div>

            <nav className="flex-1 px-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    const Icon = item.icon;

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                                isActive
                                    ? "bg-sage-200/50 dark:bg-sage-800/50 text-sage-800 dark:text-sage-100 shadow-sm"
                                    : "text-sage-600 dark:text-sage-400 hover:bg-sage-100 dark:hover:bg-sage-800/30 hover:text-sage-900 dark:hover:text-sage-200"
                            )}
                        >
                            <Icon size={18} />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-sage-200 dark:border-sage-800">
                <div className="flex items-center gap-3 px-3 py-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-xs font-medium text-sage-500 dark:text-sage-400">System Online</span>
                </div>
            </div>
        </div>
    );
}
