'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'
import { useRouter } from 'next/navigation'

interface AuthContextType {
    user: User | null
    session: Session | null
    isLoading: boolean
    signInWithPassword: (email: string, password: string) => Promise<{ error?: Error }>
    signUp: (email: string, password: string) => Promise<{ error?: Error }>
    signInWithGitHub: () => Promise<void>
    signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [session, setSession] = useState<Session | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const router = useRouter()

    useEffect(() => {
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            (_event, session) => {
                setSession(session)
                setUser(session?.user ?? null)
                setIsLoading(false)

                if (session) {
                    // Refresh/Set cookie logic if needed, but for now client-side is fine
                }
            }
        )

        return () => subscription.unsubscribe()
    }, [])

    const signInWithPassword = async (email: string, password: string): Promise<{ error?: Error }> => {
        const { error } = await supabase.auth.signInWithPassword({
            email,
            password,
        })
        if (error) {
            return { error }
        }
        return {}
    }

    const signUp = async (email: string, password: string): Promise<{ error?: Error }> => {
        const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || window.location.origin
        const { error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                emailRedirectTo: `${siteUrl}/auth/callback`,
            },
        })
        if (error) {
            return { error }
        }
        return {}
    }

    const signInWithGitHub = async (): Promise<void> => {
        // 使用環境變數來確保正確的 redirect URL
        // 這解決了 SSR 環境中 window.location.origin 可能不正確的問題
        const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || window.location.origin
        const { error } = await supabase.auth.signInWithOAuth({
            provider: 'github',
            options: {
                redirectTo: `${siteUrl}/auth/callback`,
            },
        })
        if (error) throw error
    }

    const signOut = async () => {
        await supabase.auth.signOut()
        router.push('/login')
    }

    return (
        <AuthContext.Provider value={{ user, session, isLoading, signInWithPassword, signUp, signInWithGitHub, signOut }}>
            {!isLoading && children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
