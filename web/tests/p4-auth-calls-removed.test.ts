import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

function source(relativePath: string): string {
  return readFileSync(path.resolve(process.cwd(), relativePath), "utf8");
}

test("the frontend cannot reactivate the removed account auth flow", () => {
  const proxy = source("proxy.ts");
  const api = source("lib/api.ts");
  const sessions = source("lib/session-api.ts");
  const nextConfig = source("next.config.js");
  const networkSettings = source("app/(utility)/settings/network/page.tsx");

  for (const text of [proxy, api, sessions, nextConfig, networkSettings]) {
    assert.doesNotMatch(text, /\/login|dt_token|DEEPTUTOR_AUTH_ENABLED/);
  }
  assert.doesNotMatch(proxy, /classifyToken|isAuthExempt|redirectToLogin/);
  assert.doesNotMatch(api, /setRuntimeAuthEnabled|skipAuthRedirect/);
  assert.doesNotMatch(api, /credentials\s*:\s*["']include["']/);
  assert.doesNotMatch(
    nextConfig,
    /AUTH_SETTINGS|AUTH_ENABLED|auth\.json|NEXT_PUBLIC_AUTH_ENABLED/,
  );
  assert.doesNotMatch(
    networkSettings,
    /payload\.auth|cookie_secure|cookie_samesite|cross_site_cookie_ready/,
  );
});

test("account, admin, grant, and capability-gate UI is absent", () => {
  const removed = [
    "app/(auth)/login/page.tsx",
    "app/(auth)/register/page.tsx",
    "app/(admin)/admin/users/page.tsx",
    "app/(utility)/profile/page.tsx",
    "components/auth/ProfileLink.tsx",
    "components/access/CapabilityGate.tsx",
    "features/multi-user/components/GrantEditor.tsx",
    "hooks/useAuthStatus.ts",
    "lib/auth.ts",
    "lib/admin-api.ts",
    "lib/profile-api.ts",
  ];
  for (const relativePath of removed) {
    assert.equal(existsSync(path.resolve(process.cwd(), relativePath)), false);
  }
});
