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
                        <div className="rounded-xl bg-sage-50 dark:bg-sage-800/30 p-6 text-center space-y-3 border border-sage-200 dark:border-sage-700">
                            <CheckCircle className="w-12 h-12 text-sage-500 mx-auto" />
                            <p className="font-semibold text-sage-800 dark:text-sage-200">Registration successful!</p>
                            <p className="text-sm text-sage-600 dark:text-sage-400">Please check your email to confirm your account.</p>
                            <Link href="/login" className="inline-block mt-4 px-6 py-2.5 rounded-lg bg-sage-100 dark:bg-sage-700 text-sm font-semibold text-sage-700 dark:text-sage-200 hover:bg-sage-200 dark:hover:bg-sage-600 transition-colors">
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

