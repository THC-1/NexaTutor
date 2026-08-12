import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const read = (filePath: string) =>
  fs.readFileSync(path.join(process.cwd(), filePath), "utf8");

test("primary navigation follows the NexaTutor core information architecture", () => {
  const source = read("components/sidebar/SidebarShell.tsx");
  for (const href of ["/home", "/knowledge", "/space", "/co-writer", "/settings"]) {
    assert.match(source, new RegExp(`href: "${href.replace("/", "\\/")}"`));
  }
  assert.doesNotMatch(source, /href: "\/memory"/);
  assert.doesNotMatch(source, /href: "\/agents"/);
});

test("settings hub exposes only the retained product categories", () => {
  const source = read("lib/settings-nav.ts");
  for (const key of ["appearance", "models", "knowledge", "chat", "memory"]) {
    assert.match(source, new RegExp(`key: "${key}"`));
  }
  assert.doesNotMatch(source, /key: "network"/);
  assert.doesNotMatch(source, /href: "\/settings\/tts"/);
  assert.doesNotMatch(source, /href: "\/settings\/stt"/);
  assert.doesNotMatch(source, /href: "\/settings\/image"/);
});

test("optional settings routes remain available as compatibility pages", () => {
  for (const route of ["image", "stt", "tts", "mineru"]) {
    assert.ok(fs.existsSync(path.join(process.cwd(), "app", "(utility)", "settings", route, "page.tsx")));
  }
  assert.match(read("app/(utility)/settings/status/page.tsx"), /redirect\("\/settings"\)/);
});
