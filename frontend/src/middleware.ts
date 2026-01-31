import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
    // 使用環境變數來確保正確的 redirect URL
    // 這解決了反向代理環境中 request.url 可能返回 localhost 的問題
    const siteUrl = process.env.NEXT_PUBLIC_SITE_URL

    // Dev bypass 檢查 (在 Supabase 認證之前)
    const devToken = request.cookies.get('deepflow_dev_token')?.value
    if (devToken && devToken.startsWith('dev-user-')) {
        return NextResponse.next({
            request: {
                headers: request.headers,
            },
        })
    }

    let response = NextResponse.next({
        request: {
            headers: request.headers,
        },
    })

    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return request.cookies.getAll()
                },
                setAll(cookiesToSet) {
                    cookiesToSet.forEach(({ name, value, options }) => request.cookies.set(name, value))
                    response = NextResponse.next({
                        request,
                    })
                    cookiesToSet.forEach(({ name, value, options }) =>
                        response.cookies.set(name, value, options)
                    )
                },
            },
        }
    )

    const {
        data: { user },
    } = await supabase.auth.getUser()

    // Protected routes
    if (request.nextUrl.pathname.startsWith('/dashboard')) {
        if (!user) {
            const loginUrl = siteUrl ? `${siteUrl}/login` : new URL('/login', request.url)
            return NextResponse.redirect(loginUrl)
        }
    }

    // Redirect login to dashboard if already logged in
    if (request.nextUrl.pathname === '/login') {
        if (user) {
            const dashboardUrl = siteUrl ? `${siteUrl}/dashboard` : new URL('/dashboard', request.url)
            return NextResponse.redirect(dashboardUrl)
        }
    }

    // Redirect register to dashboard if already logged in
    if (request.nextUrl.pathname === '/register') {
        if (user) {
            const dashboardUrl = siteUrl ? `${siteUrl}/dashboard` : new URL('/dashboard', request.url)
            return NextResponse.redirect(dashboardUrl)
        }
    }

    return response
}

export const config = {
    matcher: ['/dashboard/:path*', '/login', '/register'],
}

