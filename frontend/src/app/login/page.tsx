'use client'

import { useState } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { Zap, Loader2 } from 'lucide-react'

export default function LoginPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState('')
    const { signInWithPassword, signInWithGitHub } = useAuth()
    const router = useRouter()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSubmitting(true)
        setError('')

        const result = await signInWithPassword(email, password)

        if (result.error) {
            setError(result.error.message || 'Failed to sign in')
            setIsSubmitting(false)
        } else {
            router.push('/dashboard')
        }
    }

    const handleGitHubLogin = async () => {
        try {
            await signInWithGitHub()
        } catch (err: any) {
            setError(err.message || 'Failed to sign in with GitHub')
        }
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-sage-50 dark:bg-sage-950 p-4 relative overflow-hidden">
            {/* Background decorations */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-gradient-radial from-sage-200/30 dark:from-sage-700/10 to-transparent rounded-full translate-x-1/3 -translate-y-1/3" />
                <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-gradient-radial from-sage-300/20 dark:from-sage-600/10 to-transparent rounded-full -translate-x-1/3 translate-y-1/3" />
            </div>

            <div className="w-full max-w-sm relative z-10 opacity-0 animate-fade-in">
                {/* Card */}
                <div className="bg-white dark:bg-sage-900/60 p-8 rounded-2xl shadow-xl shadow-sage-500/5 dark:shadow-black/20 border border-sage-200/50 dark:border-sage-700/30 backdrop-blur-sm">
                    {/* Logo & Title */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-sage-500 to-sage-600 mb-4 shadow-lg shadow-sage-500/20">
                            <Zap className="w-7 h-7 text-white" fill="currentColor" />
                        </div>
                        <h2 className="text-2xl font-bold text-sage-900 dark:text-sage-50">Welcome back</h2>
                        <p className="mt-2 text-sm text-sage-500 dark:text-sage-400">Sign in to access your dashboard</p>
                    </div>

                    <form className="space-y-5" onSubmit={handleSubmit}>
                        <div className="space-y-4">
                            <div>
                                <label htmlFor="email" className="sr-only">Email address</label>
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    required
                                    className="block w-full rounded-xl border border-sage-200 dark:border-sage-700 bg-sage-50/50 dark:bg-sage-800/30 px-4 py-3.5 text-sage-900 dark:text-sage-100 placeholder:text-sage-400 dark:placeholder:text-sage-500 focus:border-sage-500 dark:focus:border-sage-400 focus:outline-none focus:ring-2 focus:ring-sage-500/20 transition-all"
                                    placeholder="name@company.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                            <div>
                                <label htmlFor="password" className="sr-only">Password</label>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    required
                                    className="block w-full rounded-xl border border-sage-200 dark:border-sage-700 bg-sage-50/50 dark:bg-sage-800/30 px-4 py-3.5 text-sage-900 dark:text-sage-100 placeholder:text-sage-400 dark:placeholder:text-sage-500 focus:border-sage-500 dark:focus:border-sage-400 focus:outline-none focus:ring-2 focus:ring-sage-500/20 transition-all"
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="text-red-500 dark:text-red-400 text-sm text-center bg-red-50 dark:bg-red-900/20 py-2 px-3 rounded-lg">{error}</div>
                        )}

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className={cn(
                                "group relative flex w-full justify-center items-center gap-2 rounded-xl bg-gradient-to-r from-sage-600 to-sage-500 px-4 py-3.5 text-sm font-semibold text-white transition-all hover:from-sage-500 hover:to-sage-400 focus:outline-none focus:ring-2 focus:ring-sage-500 focus:ring-offset-2 shadow-lg shadow-sage-500/25",
                                isSubmitting && "opacity-70 cursor-not-allowed"
                            )}
                        >
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                'Sign in'
                            )}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="relative my-6">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-sage-200 dark:border-sage-700" />
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="bg-white dark:bg-sage-900/60 px-3 text-sage-500 dark:text-sage-400">Or continue with</span>
                        </div>
                    </div>

                    {/* GitHub Button */}
                    <button
                        type="button"
                        onClick={handleGitHubLogin}
                        className="group relative flex w-full justify-center items-center gap-3 rounded-xl border border-sage-200 dark:border-sage-700 bg-white dark:bg-sage-800/30 px-4 py-3.5 text-sm font-semibold text-sage-900 dark:text-sage-100 transition-all hover:bg-sage-50 dark:hover:bg-sage-800/50 focus:outline-none focus:ring-2 focus:ring-sage-500/20"
                    >
                        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                            <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                        </svg>
                        Sign in with GitHub
                    </button>

                    {/* Register Link */}
                    <p className="text-center text-sm text-sage-500 dark:text-sage-400 mt-6">
                        Don&apos;t have an account?{' '}
                        <Link href="/register" className="font-semibold text-sage-700 dark:text-sage-300 hover:text-sage-900 dark:hover:text-sage-100 transition-colors">
                            Register
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    )
}

