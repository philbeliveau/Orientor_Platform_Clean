import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)',
  '/onboarding',
  '/career',
  '/tree',
  '/hexaco-test',
  '/holland-test'
])

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default clerkMiddleware(async (auth, req) => {
  // Handle API requests
  if (req.nextUrl.pathname.startsWith('/api')) {
    // Clone the request headers
    const headers = new Headers(req.headers)
    
    // Add auth token if available
    const session = await auth()
    if (session.sessionClaims) {
      headers.set('Authorization', `Bearer ${session.sessionClaims.__raw}`)
    }

    // Rewrite to backend URL
    const url = new URL(req.nextUrl.pathname.replace('/api', ''), BACKEND_URL)
    return NextResponse.rewrite(url, {
      request: {
        headers
      }
    })
  }

  // Protect all routes except public ones
  if (!isPublicRoute(req)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}
