import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";

// Unit tests for the pure middleware routing policy (web/lib/proxy-policy.ts).
// The policy is deliberately decoupled from `next/server`, so it can be
// exercised here without booting the Next runtime. proxy.ts itself is a thin
// adapter that maps these decisions onto NextResponse.

import {
  CODEX_CALLBACK_API_PATH,
  CODEX_CALLBACK_PATH,
  isBackendPath,
  isCodexCallbackPath,
} from "../lib/proxy-policy";

test("isBackendPath matches /api and /ws paths only", () => {
  assert.equal(isBackendPath("/api/v1/knowledge/list"), true);
  assert.equal(isBackendPath("/ws/chat"), true);
  assert.equal(isBackendPath("/home"), false);
  assert.equal(isBackendPath("/apidocs"), false); // no trailing slash → not backend
  assert.equal(isBackendPath("/logo.png"), false);
});

test("isCodexCallbackPath matches only the exact public callback path", () => {
  assert.equal(CODEX_CALLBACK_PATH, "/auth/callback");
  assert.equal(CODEX_CALLBACK_API_PATH, "/api/v1/auth/openai-codex/callback");
  assert.equal(isCodexCallbackPath("/auth/callback"), true);
  assert.equal(isCodexCallbackPath("/auth/callback/"), false);
  assert.equal(isCodexCallbackPath("/auth/callback/extra"), false);
  assert.equal(isCodexCallbackPath("/auth/callback-near"), false);
  assert.equal(isCodexCallbackPath("/Auth/callback"), false);
});

test("proxy rewrites the exact callback before backend routing", () => {
  const source = readFileSync(path.resolve(process.cwd(), "proxy.ts"), "utf8");
  const callbackBranch = source.indexOf("if (isCodexCallbackPath(pathname))");
  const backendBranch = source.indexOf("if (isBackendPath(pathname))");

  assert.notEqual(callbackBranch, -1);
  assert.notEqual(backendBranch, -1);
  assert.ok(callbackBranch < backendBranch);
  assert.match(
    source,
    /NextResponse\.rewrite\(\s*new URL\(\s*CODEX_CALLBACK_API_PATH \+ search,\s*API_BASE_URL,?\s*\),?\s*\)/,
  );
});
