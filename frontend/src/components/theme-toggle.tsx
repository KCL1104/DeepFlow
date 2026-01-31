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
            <button className="w-9 h-9 rounded-xl border border-sage-200 dark:border-sage-700" />
        );
    }

    return (
        <button
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            className={cn(
                "w-9 h-9 rounded-xl flex items-center justify-center",
                "border border-sage-200 dark:border-sage-700",
                "hover:bg-sage-100 dark:hover:bg-sage-800",
                "transition-colors duration-200"
            )}
            aria-label="Toggle theme"
        >
            {resolvedTheme === "dark" ? (
                <Sun className="w-4 h-4 text-sage-600 dark:text-sage-400" />
            ) : (
                <Moon className="w-4 h-4 text-sage-600 dark:text-sage-400" />
            )}
        </button>
    );
}

