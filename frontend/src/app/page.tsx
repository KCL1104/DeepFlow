import Link from "next/link";
import { Zap, ArrowRight, Shield, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-sage-50 dark:bg-sage-950 p-8 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-gradient-radial from-sage-300/30 dark:from-sage-600/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 -right-32 w-[500px] h-[500px] bg-gradient-radial from-sage-200/40 dark:from-sage-700/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-amber-300/5 dark:from-amber-400/5 to-transparent rounded-full" />
      </div>

      <div className="text-center relative z-10 max-w-2xl opacity-0 animate-fade-in">
        {/* Logo */}
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-sage-500 to-sage-600 mb-8 shadow-xl shadow-sage-500/20">
          <Zap className="w-10 h-10 text-white" fill="currentColor" />
        </div>

        <h1 className="text-5xl md:text-6xl font-bold text-sage-900 dark:text-sage-50 mb-6 tracking-tight">
          DeepFlow
        </h1>

        <p className="text-xl text-sage-600 dark:text-sage-400 mb-10 leading-relaxed">
          Protect your focus with intelligent task scheduling and AI-powered priority management.
        </p>

        {/* Feature badges */}
        <div className="flex flex-wrap justify-center gap-3 mb-10">
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-sage-100 dark:bg-sage-800/40 text-sage-700 dark:text-sage-300 text-sm font-medium">
            <Shield size={16} />
            Focus Protection
          </span>
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-sage-100 dark:bg-sage-800/40 text-sage-700 dark:text-sage-300 text-sm font-medium">
            <Sparkles size={16} />
            AI-Powered
          </span>
        </div>

        {/* CTA Buttons */}
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="group inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-sage-600 to-sage-500 hover:from-sage-500 hover:to-sage-400 text-white font-semibold transition-all shadow-lg shadow-sage-500/25 hover:shadow-sage-500/40"
          >
            Get Started
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link
            href="/dashboard"
            className="px-8 py-4 rounded-xl border border-sage-200 dark:border-sage-700 text-sage-700 dark:text-sage-300 hover:bg-sage-100 dark:hover:bg-sage-800/50 font-semibold transition-colors"
          >
            Demo Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}

