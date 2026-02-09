type ResolveSiteUrlOptions = {
  envSiteUrl?: string | null;
  requestUrl?: string | URL | null;
  windowOrigin?: string | null;
};

const DEFAULT_SITE_URL = "http://localhost:3000";
const URL_SCHEME_PATTERN = /^[a-zA-Z][a-zA-Z\d+\-.]*:\/\//;
const IPV4_PATTERN =
  /^(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}$/;

let hasWarnedInvalidSiteUrl = false;

function toOrigin(value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }

  const maybeAbsolute = URL_SCHEME_PATTERN.test(trimmed)
    ? trimmed
    : `https://${trimmed}`;

  try {
    const parsed = new URL(maybeAbsolute);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      return null;
    }
    if (!isResolvableHostname(parsed.hostname)) {
      return null;
    }
    return parsed.origin.replace(/\/+$/, "");
  } catch {
    return null;
  }
}

function isResolvableHostname(hostname: string): boolean {
  if (!hostname) {
    return false;
  }
  if (hostname === "localhost") {
    return true;
  }
  if (hostname.includes(".")) {
    return true;
  }
  if (hostname.includes(":")) {
    return true;
  }
  return IPV4_PATTERN.test(hostname);
}

function getRequestOrigin(requestUrl?: string | URL | null): string | null {
  if (!requestUrl) {
    return null;
  }

  try {
    const parsed = requestUrl instanceof URL ? requestUrl : new URL(requestUrl);
    return parsed.origin.replace(/\/+$/, "");
  } catch {
    return null;
  }
}

function getBrowserOrigin(explicitWindowOrigin?: string | null): string | null {
  if (explicitWindowOrigin) {
    return toOrigin(explicitWindowOrigin);
  }
  if (typeof window === "undefined") {
    return null;
  }
  return toOrigin(window.location.origin);
}

function warnInvalidSiteUrl(value: string, fallback: string): void {
  if (hasWarnedInvalidSiteUrl) {
    return;
  }
  hasWarnedInvalidSiteUrl = true;
  console.warn(
    `[site-url] Ignoring invalid NEXT_PUBLIC_SITE_URL="${value}". Falling back to "${fallback}".`
  );
}

export function resolveSiteUrl(options: ResolveSiteUrlOptions = {}): string {
  const { envSiteUrl, requestUrl, windowOrigin } = options;

  const normalizedEnvSiteUrl =
    typeof envSiteUrl === "string" ? toOrigin(envSiteUrl) : null;
  if (normalizedEnvSiteUrl) {
    return normalizedEnvSiteUrl;
  }

  const requestOrigin = getRequestOrigin(requestUrl);
  if (requestOrigin) {
    if (envSiteUrl && envSiteUrl.trim()) {
      warnInvalidSiteUrl(envSiteUrl, requestOrigin);
    }
    return requestOrigin;
  }

  const browserOrigin = getBrowserOrigin(windowOrigin);
  if (browserOrigin) {
    if (envSiteUrl && envSiteUrl.trim()) {
      warnInvalidSiteUrl(envSiteUrl, browserOrigin);
    }
    return browserOrigin;
  }

  if (envSiteUrl && envSiteUrl.trim()) {
    warnInvalidSiteUrl(envSiteUrl, DEFAULT_SITE_URL);
  }
  return DEFAULT_SITE_URL;
}

export function buildSitePath(
  path: string,
  options: ResolveSiteUrlOptions = {}
): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${resolveSiteUrl(options)}${normalizedPath}`;
}

export function sanitizeNextPath(
  nextPath: string | null | undefined,
  fallback = "/dashboard"
): string {
  if (!nextPath) {
    return fallback;
  }

  const normalized = nextPath.trim();
  if (!normalized.startsWith("/")) {
    return fallback;
  }
  if (normalized.startsWith("//")) {
    return fallback;
  }
  if (normalized.includes("\\") || normalized.includes("\r") || normalized.includes("\n")) {
    return fallback;
  }

  return normalized;
}
