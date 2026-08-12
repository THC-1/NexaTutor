// API configuration and utility functions.
//
// The frontend bundle is now URL-agnostic: the browser issues requests against
// the frontend origin (`:3782/api/...` and `:3782/api/.../ws`), and
// `web/proxy.ts` rewrites `/api/*` and `/ws/*` to the configured backend on
// every request. This means there is no build-time or runtime URL substitution
// in the bundle, and no placeholder token to keep alive. `apiUrl` and `wsUrl`
// stay as one-liner pass-throughs so the dozens of existing call sites continue
// to compile and work without modification.

/**
 * Construct a full API URL from a path.
 *
 * Pass-through: returns the path unchanged. The actual backend URL is
 * determined at request time by `web/proxy.ts`, which reads
 * `DEEPTUTOR_API_BASE_URL` (exported by the container entrypoint from
 * `data/user/settings/system.json`).
 *
 * @param path - API path (e.g., '/api/v1/knowledge/list')
 * @returns The same path, unchanged
 */
export function apiUrl(path: string): string {
  return path;
}

/**
 * Construct a WebSocket URL from a path.
 *
 * Pass-through: returns the path unchanged. `proxy.ts` rewrites `/ws/*` to
 * the configured backend, and the runtime upgrades to `ws://` /
 * `wss://` based on the backend's scheme.
 *
 * @param path - WebSocket path (e.g., '/api/v1/solve')
 * @returns The same path, unchanged
 */
export function wsUrl(path: string): string {
  return path;
}

/** Fetch wrapper retained as the shared seam for local API requests. */
export async function apiFetch(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  return fetch(input, init);
}
