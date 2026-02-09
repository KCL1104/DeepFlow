import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'
import { buildSitePath, sanitizeNextPath } from '@/lib/site-url'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  const error = searchParams.get('error')
  const error_description = searchParams.get('error_description')
  const next = sanitizeNextPath(searchParams.get('next'))
  const siteUrlOptions = {
    envSiteUrl: process.env.NEXT_PUBLIC_SITE_URL,
    requestUrl: request.url,
  }

  // 處理 Supabase 返回的錯誤
  if (error) {
    console.error('Auth callback error:', error, error_description)
    const params = new URLSearchParams({
      error,
      error_description: error_description || '',
    })
    return NextResponse.redirect(
      buildSitePath(`/login?${params.toString()}`, siteUrlOptions)
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
      return NextResponse.redirect(buildSitePath(next, siteUrlOptions))
    }

    console.error('Code exchange error:', exchangeError)
    const params = new URLSearchParams({
      error: 'code_exchange_failed',
      error_description: exchangeError.message,
    })
    return NextResponse.redirect(
      buildSitePath(`/login?${params.toString()}`, siteUrlOptions)
    )
  }

  return NextResponse.redirect(buildSitePath('/login?error=missing_code', siteUrlOptions))
}
