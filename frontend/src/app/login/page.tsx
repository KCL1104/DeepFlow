'use client'

import { useState } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import { cn } from '@/lib/utils'

export default function LoginPage() {
    const [email, setEmail] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [isSent, setIsSent] = useState(false)
    const [devUserId, setDevUserId] = useState('')
    const [error, setError] = useState('')
    const { signInWithEmail } = useAuth()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSubmitting(true)
        setError('')
        try {
            await signInWithEmail(email)
            setIsSent(true)
        } catch (err: any) {
            setError(err.message || 'Failed to send login link')
        } finally {
            setIsSubmitting(false)
        }
    }

    // Dev Auth Bypass for backwards compatibility testing
    const handleDevLogin = () => {
        if (!devUserId) return
        localStorage.setItem('deepflow_token', `dev-user-${devUserId}`)
        window.location.href = '/dashboard'
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-stone-50 p-4">
            <div className="w-full max-w-sm space-y-8 bg-white p-8 rounded-2xl shadow-sm border border-stone-100">
                <div className="text-center">
                    <h2 className="text-2xl font-semibold text-stone-900">DeepFlow Sentinel</h2>
                    <p className="mt-2 text-sm text-stone-500">Sign in to access your dashboard</p>
                </div>

                {isSent ? (
                    <div className="rounded-lg bg-green-50 p-4 text-green-800 text-center">
                        <p>Check your email for the login link!</p>
                    </div>
                ) : (
                    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
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
                            {isSubmitting ? 'Sending...' : 'Sign in with Magic Link'}
                        </button>
                    </form>
                )}

                {/* Dev Mode Section */}
                <div className="pt-6 border-t border-stone-100 mt-6">
                    <p className="text-xs text-center text-stone-400 mb-2 uppercase tracking-widest">Development Mode</p>
                    <div className="flex gap-2">
                        <input
                            type="text"
                            placeholder="user_id (e.g. 123)"
                            className="flex-1 rounded border border-stone-200 px-3 py-2 text-sm"
                            value={devUserId}
                            onChange={(e) => setDevUserId(e.target.value)}
                        />
                        <button
                            onClick={handleDevLogin}
                            className="bg-stone-200 hover:bg-stone-300 text-stone-700 px-3 py-2 rounded text-sm font-medium transition-colors"
                        >
                            Bypass
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
