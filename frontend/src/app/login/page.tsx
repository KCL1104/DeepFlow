'use client'

import { useState } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { cn } from '@/lib/utils'

export default function LoginPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [devUserId, setDevUserId] = useState('')
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

    // Dev Auth Bypass for backwards compatibility testing
    const handleDevLogin = () => {
        if (!devUserId) return
        document.cookie = `deepflow_dev_token=dev-user-${devUserId}; path=/; max-age=86400`
        localStorage.setItem('deepflow_token', `dev-user-${devUserId}`)
        window.location.href = '/dashboard'
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-stone-50 p-4">
            <div className="w-full max-w-sm space-y-8 bg-white p-8 rounded-2xl shadow-sm border border-stone-100">
                <div className="text-center">
                    <h2 className="text-2xl font-semibold text-stone-900">DeepFlow</h2>
                    <p className="mt-2 text-sm text-stone-500">Sign in to access your dashboard</p>
                </div>

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
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
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
                        {isSubmitting ? 'Signing in...' : 'Sign in'}
                    </button>
                </form>

                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-stone-200" />
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="bg-white px-2 text-stone-500">Or continue with</span>
                    </div>
                </div>

                <button
                    type="button"
                    onClick={handleGitHubLogin}
                    className="group relative flex w-full justify-center items-center gap-3 rounded-lg border border-stone-200 bg-white px-4 py-3 text-sm font-semibold text-stone-900 transition-all hover:bg-stone-50 focus:outline-none focus:ring-2 focus:ring-stone-500 focus:ring-offset-2"
                >
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                        <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                    </svg>
                    Sign in with GitHub
                </button>

                <p className="text-center text-sm text-stone-500">
                    Don&apos;t have an account?{' '}
                    <Link href="/register" className="font-semibold text-stone-900 hover:underline">
                        Register
                    </Link>
                </p>

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
