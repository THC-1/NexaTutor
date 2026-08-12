// Pure request-routing policy for the Next.js middleware (web/proxy.ts).
//
// This module deliberately carries NO dependency on `next/server`: it answers
// "what should happen to this request?" as plain, side-effect-free functions,
// while proxy.ts stays a thin adapter that turns those answers into
// NextResponse objects. Keeping the policy pure means the routing/auth rules
// can be unit-tested in the node harness without booting the Next runtime.

export const CODEX_CALLBACK_PATH = "/auth/callback";
export const CODEX_CALLBACK_API_PATH = "/api/v1/auth/openai-codex/callback";

export function isCodexCallbackPath(pathname: string): boolean {
  return pathname === CODEX_CALLBACK_PATH;
}

// Paths whose responses come from the backend, not the Next app. The middleware
// rewrites these to DEEPTUTOR_API_BASE_URL so the browser can use frontend-
// relative URLs (e.g. `:3782/api/v1/...` or `.../ws`) and let the rewrite
// bridge the origin gap.
export function isBackendPath(pathname: string): boolean {
  return pathname.startsWith("/api/") || pathname.startsWith("/ws/");
}
