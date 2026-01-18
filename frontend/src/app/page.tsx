import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-neutral-50 dark:bg-neutral-900 p-8">
      <div className="text-center">
        {/* Logo */}
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-sage-100 dark:bg-sage-900/30 mb-6">
          <svg
            className="w-10 h-10 text-sage-600 dark:text-sage-400"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M2 12c0-3 2.5-6 6-6 4 0 5 4 8 4 3.5 0 6-3 6-6" />
            <path d="M2 20c0-3 2.5-6 6-6 4 0 5 4 8 4 3.5 0 6-3 6-6" />
          </svg>
        </div>

        <h1 className="font-mono text-4xl font-bold text-neutral-800 dark:text-neutral-100 mb-4">
          DeepFlow
        </h1>

        <p className="text-lg text-neutral-600 dark:text-neutral-400 mb-8 max-w-md">
          Protect your focus with intelligent task scheduling and AI-powered priority management.
        </p>

        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="px-6 py-3 rounded-lg bg-sage-600 hover:bg-sage-700 text-white font-medium transition-colors"
          >
            Get Started
          </Link>
          <Link
            href="/dashboard"
            className="px-6 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 font-medium transition-colors"
          >
            Demo Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
