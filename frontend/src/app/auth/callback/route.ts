import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  const error = searchParams.get('error')
  const error_description = searchParams.get('error_description')
  const next = searchParams.get('next') ?? '/dashboard'

  // 使用環境變數來確保正確的 redirect URL
  // 這解決了反向代理環境中 request.url origin 可能返回 localhost 的問題
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || new URL(request.url).origin

  // 處理 Supabase 返回的錯誤
  if (error) {
    console.error('Auth callback error:', error, error_description)
    return NextResponse.redirect(
      `${siteUrl}/login?error=${encodeURIComponent(error)}&error_description=${encodeURIComponent(error_description || '')}`
    )
  }

  if (code) {
    const cookieStore = await cookies()
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll()
          },
          setAll(cookiesToSet) {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          },
        },
      }
    )

    const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code)

    if (!exchangeError) {
      return NextResponse.redirect(`${siteUrl}${next}`)
    }

    console.error('Code exchange error:', exchangeError)
    return NextResponse.redirect(
      `${siteUrl}/login?error=code_exchange_failed&error_description=${encodeURIComponent(exchangeError.message)}`
    )
  }

  return NextResponse.redirect(`${siteUrl}/login?error=missing_code`)
}

