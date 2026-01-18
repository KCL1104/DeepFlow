"use client";

import * as React from "react";
import { Play, Pause, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";

interface PomodoroTimerProps {
    workMinutes?: number;
    breakMinutes?: number;
    className?: string;
}

type TimerState = "work" | "break" | "idle";

export function PomodoroTimer({
    workMinutes = 30,
    breakMinutes = 5,
    className,
}: PomodoroTimerProps) {
    const [timeLeft, setTimeLeft] = React.useState(workMinutes * 60);
    const [isRunning, setIsRunning] = React.useState(false);
    const [timerState, setTimerState] = React.useState<TimerState>("idle");

    const totalSeconds = timerState === "break" ? breakMinutes * 60 : workMinutes * 60;
    const progress = ((totalSeconds - timeLeft) / totalSeconds) * 100;

    React.useEffect(() => {
        let interval: NodeJS.Timeout;

        if (isRunning && timeLeft > 0) {
            interval = setInterval(() => {
                setTimeLeft((prev) => prev - 1);
            }, 1000);
        } else if (timeLeft === 0 && isRunning) {
            // Switch between work and break
            if (timerState === "work") {
                setTimerState("break");
                setTimeLeft(breakMinutes * 60);
            } else {
                setTimerState("work");
                setTimeLeft(workMinutes * 60);
            }
        }

        return () => clearInterval(interval);
    }, [isRunning, timeLeft, timerState, workMinutes, breakMinutes]);

    const handleStart = () => {
        if (timerState === "idle") {
            setTimerState("work");
        }
        setIsRunning(true);
    };

    const handlePause = () => {
        setIsRunning(false);
    };

    const handleReset = () => {
        setIsRunning(false);
        setTimerState("idle");
        setTimeLeft(workMinutes * 60);
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    };

    const strokeDasharray = 2 * Math.PI * 90;
    const strokeDashoffset = strokeDasharray * (1 - progress / 100);

    return (
        <div className={cn("flex flex-col items-center", className)}>
            {/* Timer Status */}
            <div className="mb-4 text-sm font-mono text-neutral-500 dark:text-neutral-400">
                {timerState === "idle" && "Ready to focus"}
                {timerState === "work" && `Work: ${formatTime(timeLeft)} / ${workMinutes}:00`}
                {timerState === "break" && `Break: ${formatTime(timeLeft)} / ${breakMinutes}:00`}
            </div>

            {/* Circular Timer */}
            <div className="relative w-52 h-52">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
                    {/* Background circle */}
                    <circle
                        cx="100"
                        cy="100"
                        r="90"
                        fill="none"
                        strokeWidth="4"
                        className="stroke-neutral-200 dark:stroke-neutral-700"
                    />
                    {/* Progress circle */}
                    <circle
                        cx="100"
                        cy="100"
                        r="90"
                        fill="none"
                        strokeWidth="4"
                        strokeLinecap="round"
                        className={cn(
                            "transition-all duration-1000",
                            timerState === "break"
                                ? "stroke-amber-500 dark:stroke-amber-400"
                                : "stroke-sage-600 dark:stroke-sage-400"
                        )}
                        style={{
                            strokeDasharray,
                            strokeDashoffset,
                        }}
                    />
                </svg>

                {/* Timer Display */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="font-mono text-4xl font-light text-neutral-800 dark:text-neutral-200">
                        {formatTime(timeLeft)}
                    </span>
                </div>
            </div>

            {/* Controls */}
            <div className="flex gap-3 mt-6">
                {!isRunning ? (
                    <button
                        onClick={handleStart}
                        className={cn(
                            "w-10 h-10 rounded-full flex items-center justify-center",
                            "bg-sage-600 hover:bg-sage-700 dark:bg-sage-500 dark:hover:bg-sage-600",
                            "text-white transition-colors"
                        )}
                        aria-label="Start timer"
                    >
                        <Play className="w-4 h-4 ml-0.5" />
                    </button>
                ) : (
                    <button
                        onClick={handlePause}
                        className={cn(
                            "w-10 h-10 rounded-full flex items-center justify-center",
                            "bg-neutral-200 hover:bg-neutral-300 dark:bg-neutral-700 dark:hover:bg-neutral-600",
                            "text-neutral-700 dark:text-neutral-300 transition-colors"
                        )}
                        aria-label="Pause timer"
                    >
                        <Pause className="w-4 h-4" />
                    </button>
                )}
                <button
                    onClick={handleReset}
                    className={cn(
                        "w-10 h-10 rounded-full flex items-center justify-center",
                        "border border-neutral-200 dark:border-neutral-700",
                        "hover:bg-neutral-100 dark:hover:bg-neutral-800",
                        "text-neutral-600 dark:text-neutral-400 transition-colors"
                    )}
                    aria-label="Reset timer"
                >
                    <RotateCcw className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}
