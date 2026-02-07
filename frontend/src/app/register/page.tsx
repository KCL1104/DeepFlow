'use client'

import { useState } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { Zap, Loader2, CheckCircle } from 'lucide-react'

export default function RegisterPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState(false)
    const { signUp } = useAuth()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (password !== confirmPassword) {
            setError('Passwords do not match')
            return
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters')
            return
        }

        setIsSubmitting(true)

        const result = await signUp(email, password)

        if (result.error) {
            setError(result.error.message || 'Failed to create account')
            setIsSubmitting(false)
        } else {
            setSuccess(true)
            setIsSubmitting(false)
        }
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-sage-50 dark:bg-sage-950 p-4 relative overflow-hidden">
            {/* Background decorations */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-gradient-radial from-sage-200/30 dark:from-sage-700/10 to-transparent rounded-full -translate-x-1/3 -translate-y-1/3" />
                <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-gradient-radial from-sage-300/20 dark:from-sage-600/10 to-transparent rounded-full translate-x-1/3 translate-y-1/3" />
            </div>

            <div className="w-full max-w-sm relative z-10 opacity-0 animate-fade-in">
                {/* Card */}
                <div className="bg-white dark:bg-sage-900/60 p-8 rounded-2xl shadow-xl shadow-sage-500/5 dark:shadow-black/20 border border-sage-200/50 dark:border-sage-700/30 backdrop-blur-sm">
                    {/* Logo & Title */}
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-sage-500 to-sage-600 mb-4 shadow-lg shadow-sage-500/20">
                            <Zap className="w-7 h-7 text-white" fill="currentColor" />
                        </div>
                        <h2 className="text-2xl font-bold text-sage-900 dark:text-sage-50">Create Account</h2>
                        <p className="mt-2 text-sm text-sage-500 dark:text-sage-400">Register for a DeepFlow account</p>
                    </div>

                    {success ? (
                        <div className="rounded-xl bg-sage-50 dark:bg-sage-800/30 p-6 text-center space-y-4 border border-sage-200 dark:border-sage-700">
                            <CheckCircle className="w-12 h-12 text-sage-500 mx-auto" />
                            <p className="font-semibold text-sage-800 dark:text-sage-200">Registration successful!</p>
                            <p className="text-sm text-sage-600 dark:text-sage-400">Please check your email to confirm your account.</p>

                            {/* Telegram Bot Connection Guide */}
                            <div className="mt-4 p-4 rounded-lg bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-800">
                                <div className="flex items-center justify-center gap-2 mb-2">
                                    <svg className="w-5 h-5 text-blue-500" viewBox="0 0 24 24" fill="currentColor">
                                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z" />
                                    </svg>
                                    <span className="font-semibold text-blue-700 dark:text-blue-300">Get Push Notifications</span>
                                </div>
                                <p className="text-sm text-blue-600 dark:text-blue-400 mb-3">
                                    Connect with our Telegram Bot to receive instant task updates and focus reminders!
                                </p>
                                <a
                                    href="https://t.me/DeepFlow_Notify_Bot"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors"
                                >
                                    Connect @DeepFlow_Notify_Bot
                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                    </svg>
                                </a>
                            </div>

                            <Link href="/login" className="inline-block mt-2 px-6 py-2.5 rounded-lg bg-sage-100 dark:bg-sage-700 text-sm font-semibold text-sage-700 dark:text-sage-200 hover:bg-sage-200 dark:hover:bg-sage-600 transition-colors">
                                Go to Login
                            </Link>
                        </div>
                    ) : (
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
                                        placeholder="Password (min 6 characters)"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                    />
                                </div>
                                <div>
                                    <label htmlFor="confirmPassword" className="sr-only">Confirm Password</label>
                                    <input
                                        id="confirmPassword"
                                        name="confirmPassword"
                                        type="password"
                                        required
                                        className="block w-full rounded-xl border border-sage-200 dark:border-sage-700 bg-sage-50/50 dark:bg-sage-800/30 px-4 py-3.5 text-sage-900 dark:text-sage-100 placeholder:text-sage-400 dark:placeholder:text-sage-500 focus:border-sage-500 dark:focus:border-sage-400 focus:outline-none focus:ring-2 focus:ring-sage-500/20 transition-all"
                                        placeholder="Confirm Password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
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
                                        Creating account...
                                    </>
                                ) : (
                                    'Create account'
                                )}
                            </button>
                        </form>
                    )}

                    {/* Login Link */}
                    <p className="text-center text-sm text-sage-500 dark:text-sage-400 mt-6">
                        Already have an account?{' '}
                        <Link href="/login" className="font-semibold text-sage-700 dark:text-sage-300 hover:text-sage-900 dark:hover:text-sage-100 transition-colors">
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    )
}

