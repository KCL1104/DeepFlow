import { createBrowserClient } from '@supabase/ssr'

// 移除 fallback，確保建置時必須有正確的環境變數
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase environment variables. Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.'
  )
}

// 使用 @supabase/ssr 的 createBrowserClient
// 這確保 PKCE code verifier 儲存在 cookies 中，而非 localStorage
// 讓 server-side (middleware, auth callback) 可以正確讀取
export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey)
