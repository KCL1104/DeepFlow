import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const HOP_BY_HOP_HEADERS = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
  "host",
  "content-length",
]);

type RouteContext = {
  params: Promise<{ path: string[] }> | { path: string[] };
};

function resolveBackendBaseUrl(): string {
  const backendUrl = process.env.BACKEND_URL?.trim();
  if (backendUrl) {
    return backendUrl.replace(/\/+$/, "");
  }

  const publicApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (publicApiUrl && /^https?:\/\//i.test(publicApiUrl)) {
    return publicApiUrl.replace(/\/api\/v1\/?$/, "").replace(/\/+$/, "");
  }

  return "http://localhost:8000";
}

async function getPathSegments(context: RouteContext): Promise<string[]> {
  const { path } = await context.params;
  return Array.isArray(path) ? path : [];
}

function buildTargetUrl(pathSegments: string[], search: string): string {
  const backendBaseUrl = resolveBackendBaseUrl();
  const encodedPath = pathSegments.map((segment) => encodeURIComponent(segment)).join("/");
  return `${backendBaseUrl}/api/v1/${encodedPath}${search}`;
}

function buildForwardHeaders(request: NextRequest): Headers {
  const headers = new Headers();

  for (const [key, value] of request.headers.entries()) {
    if (HOP_BY_HOP_HEADERS.has(key.toLowerCase())) {
      continue;
    }
    headers.set(key, value);
  }

  return headers;
}

function buildResponseHeaders(upstreamHeaders: Headers): Headers {
  const headers = new Headers();

  for (const [key, value] of upstreamHeaders.entries()) {
    if (HOP_BY_HOP_HEADERS.has(key.toLowerCase())) {
      continue;
    }
    headers.set(key, value);
  }

  return headers;
}

async function proxyRequest(request: NextRequest, context: RouteContext): Promise<Response> {
  try {
    const pathSegments = await getPathSegments(context);
    const targetUrl = buildTargetUrl(pathSegments, request.nextUrl.search);
    const hasBody = request.method !== "GET" && request.method !== "HEAD";

    const init: RequestInit = {
      method: request.method,
      headers: buildForwardHeaders(request),
      redirect: "manual",
    };

    if (hasBody) {
      const bodyBuffer = await request.arrayBuffer();
      if (bodyBuffer.byteLength > 0) {
        init.body = bodyBuffer;
      }
    }

    const upstreamResponse = await fetch(targetUrl, init);
    return new Response(upstreamResponse.body, {
      status: upstreamResponse.status,
      statusText: upstreamResponse.statusText,
      headers: buildResponseHeaders(upstreamResponse.headers),
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unknown proxy error";
    return Response.json({ error: "Proxy request failed", detail }, { status: 502 });
  }
}

export async function GET(request: NextRequest, context: RouteContext): Promise<Response> {
  return proxyRequest(request, context);
}

export async function POST(request: NextRequest, context: RouteContext): Promise<Response> {
  return proxyRequest(request, context);
}

export async function PUT(request: NextRequest, context: RouteContext): Promise<Response> {
  return proxyRequest(request, context);
}

export async function PATCH(request: NextRequest, context: RouteContext): Promise<Response> {
  return proxyRequest(request, context);
}

export async function DELETE(request: NextRequest, context: RouteContext): Promise<Response> {
  return proxyRequest(request, context);
}

export async function OPTIONS(request: NextRequest, context: RouteContext): Promise<Response> {
  return proxyRequest(request, context);
}

export async function HEAD(request: NextRequest, context: RouteContext): Promise<Response> {
  return proxyRequest(request, context);
}
