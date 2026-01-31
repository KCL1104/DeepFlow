'use client'

import { useState } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import Link from 'next/link'
import { cn } from '@/lib/utils'

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
        <div className="flex min-h-screen items-center justify-center bg-stone-50 p-4">
            <div className="w-full max-w-sm space-y-8 bg-white p-8 rounded-2xl shadow-sm border border-stone-100">
                <div className="text-center">
                    <h2 className="text-2xl font-semibold text-stone-900">Create Account</h2>
                    <p className="mt-2 text-sm text-stone-500">Register for a DeepFlow account</p>
                </div>

                {success ? (
                    <div className="rounded-lg bg-green-50 p-4 text-green-800 text-center space-y-2">
                        <p className="font-medium">Registration successful!</p>
                        <p className="text-sm">Please check your email to confirm your account.</p>
                        <Link href="/login" className="inline-block mt-4 text-sm font-semibold text-green-700 hover:underline">
                            Go to Login
                        </Link>
                    </div>
                ) : (
                    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                        <div className="space-y-4">
                            <div>
                                <label htmlFor="email" className="sr-only">Email address</label>
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    required
                                    className="block w-full rounded-lg border border-stone-200 px-4 py-3 text-stone-900 placeholder:text-stone-400 focus:border-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-500"
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
                                    className="block w-full rounded-lg border border-stone-200 px-4 py-3 text-stone-900 placeholder:text-stone-400 focus:border-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-500"
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
                                    className="block w-full rounded-lg border border-stone-200 px-4 py-3 text-stone-900 placeholder:text-stone-400 focus:border-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-500"
                                    placeholder="Confirm Password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="text-red-500 text-sm text-center">{error}</div>
                        )}

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className={cn(
                                "group relative flex w-full justify-center rounded-lg bg-stone-900 px-4 py-3 text-sm font-semibold text-white transition-all hover:bg-stone-800 focus:outline-none focus:ring-2 focus:ring-stone-500 focus:ring-offset-2",
                                isSubmitting && "opacity-70 cursor-not-allowed"
                            )}
                        >
                            {isSubmitting ? 'Creating account...' : 'Create account'}
                        </button>
                    </form>
                )}

                <p className="text-center text-sm text-stone-500">
                    Already have an account?{' '}
                    <Link href="/login" className="font-semibold text-stone-900 hover:underline">
                        Sign in
                    </Link>
                </p>
            </div>
        </div>
    )
}
