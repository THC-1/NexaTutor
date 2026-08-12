import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import test from "node:test";

const editor = readFileSync(
  path.resolve(process.cwd(), "components/settings/ServiceConfigEditor.tsx"),
  "utf8",
);
const context = readFileSync(
  path.resolve(process.cwd(), "components/settings/SettingsContext.tsx"),
  "utf8",
);
const reasoning = readFileSync(
  path.resolve(process.cwd(), "lib/reasoning-effort.ts"),
  "utf8",
);

test("provider credentials are write-only in the settings editor", () => {
  assert.match(context, /api_key_set\?: boolean/);
  assert.match(context, /api_key_clear\?: boolean/);
  assert.match(editor, /profile\.api_key_set \? t\("API key configured"\)/);
  assert.match(editor, /updateProfileField\(service, "api_key_clear", true\)/);
  assert.doesNotMatch(context, /console\.(?:log|debug)\([^\n]*api_key/);
});

test("Codex OAuth remains a separate managed provider path", () => {
  assert.match(editor, /<CodexOAuthCard \/>/);
  assert.match(editor, /isCodexOAuthProfile/);
});

test("removed LLM providers do not retain frontend behavior branches", () => {
  for (const provider of [
    "github_copilot",
    "azure_openai",
    "volcengine_coding_plan",
    "byteplus_coding_plan",
    "dashscope",
    "minimax",
  ]) {
    assert.doesNotMatch(reasoning, new RegExp(`\\b${provider}\\b`));
  }
});
