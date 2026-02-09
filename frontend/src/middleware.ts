import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { buildSitePath } from '@/lib/site-url'

export async function middleware(request: NextRequest) {
    const siteUrlOptions = {
        envSiteUrl: process.env.NEXT_PUBLIC_SITE_URL,
        requestUrl: request.url,
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
                    cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
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
            return NextResponse.redirect(buildSitePath('/login', siteUrlOptions))
        }
    }

    // Redirect login to dashboard if already logged in
    if (request.nextUrl.pathname === '/login') {
        if (user) {
            return NextResponse.redirect(buildSitePath('/dashboard', siteUrlOptions))
        }
    }

    // Redirect register to dashboard if already logged in
    if (request.nextUrl.pathname === '/register') {
        if (user) {
            return NextResponse.redirect(buildSitePath('/dashboard', siteUrlOptions))
        }
    }

    return response
}

export const config = {
    matcher: ['/dashboard/:path*', '/login', '/register'],
}
