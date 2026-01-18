"use client";

import * as React from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { cn } from "@/lib/utils";

export function ThemeToggle() {
    const { resolvedTheme, setTheme } = useTheme();
    const [mounted, setMounted] = React.useState(false);

    React.useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return (
            <button className="w-9 h-9 rounded-lg border border-neutral-200 dark:border-neutral-700" />
        );
    }

    return (
        <button
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            className={cn(
                "w-9 h-9 rounded-lg flex items-center justify-center",
                "border border-neutral-200 dark:border-neutral-700",
                "hover:bg-neutral-100 dark:hover:bg-neutral-800",
                "transition-colors duration-200"
            )}
            aria-label="Toggle theme"
        >
            {resolvedTheme === "dark" ? (
                <Sun className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />
            ) : (
                <Moon className="w-4 h-4 text-neutral-600 dark:text-neutral-400" />
            )}
        </button>
    );
}
