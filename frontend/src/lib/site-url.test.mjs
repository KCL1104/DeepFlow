import assert from "node:assert/strict";
import test from "node:test";
import { buildSitePath, resolveSiteUrl, sanitizeNextPath } from "./site-url.ts";

test("resolveSiteUrl keeps a valid absolute NEXT_PUBLIC_SITE_URL", () => {
  const resolved = resolveSiteUrl({ envSiteUrl: "https://deepflow.zeabur.app/" });
  assert.equal(resolved, "https://deepflow.zeabur.app");
});

test("resolveSiteUrl normalizes host-only-with-dot env values to https origin", () => {
  const resolved = resolveSiteUrl({ envSiteUrl: "deepflow.zeabur.app" });
  assert.equal(resolved, "https://deepflow.zeabur.app");
});

test("resolveSiteUrl falls back when env hostname is not resolvable", () => {
  const resolved = resolveSiteUrl({
    envSiteUrl: "deepflow",
    requestUrl: "https://deepflow.zeabur.app/login",
  });
  assert.equal(resolved, "https://deepflow.zeabur.app");
});

test("resolveSiteUrl falls back to request origin for malformed env URLs", () => {
  const resolved = resolveSiteUrl({
    envSiteUrl: "://not-a-url",
    requestUrl: "https://deepflow.zeabur.app/dashboard",
  });
  assert.equal(resolved, "https://deepflow.zeabur.app");
});

test("buildSitePath returns absolute paths with the resolved origin", () => {
  const loginUrl = buildSitePath("/login", { envSiteUrl: "deepflow.zeabur.app" });
  assert.equal(loginUrl, "https://deepflow.zeabur.app/login");

  const callbackUrl = buildSitePath("auth/callback", { envSiteUrl: "deepflow.zeabur.app" });
  assert.equal(callbackUrl, "https://deepflow.zeabur.app/auth/callback");
});

test("sanitizeNextPath accepts only internal relative paths", () => {
  assert.equal(sanitizeNextPath("/dashboard/tasks"), "/dashboard/tasks");
  assert.equal(sanitizeNextPath("https://evil.com"), "/dashboard");
  assert.equal(sanitizeNextPath("//evil.com"), "/dashboard");
  assert.equal(sanitizeNextPath("dashboard"), "/dashboard");
  assert.equal(sanitizeNextPath(undefined), "/dashboard");
});
