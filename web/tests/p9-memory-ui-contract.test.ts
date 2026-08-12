import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const read = (filePath: string) =>
  fs.readFileSync(path.join(process.cwd(), filePath), "utf8");

test("memory hub is user-facing while preserving the L1/L2/L3 model", () => {
  const hub = read("components/memory/MemoryHub.tsx");

  for (const label of [
    "User preferences",
    "Learning goals",
    "Current knowledge level",
    "Recent learning",
    "Saved long-term memories",
    "L1",
    "L2",
    "L3",
  ]) {
    assert.match(hub, new RegExp(label));
  }

  assert.doesNotMatch(hub, /href="\/memory\/graph"/);
});

test("preferences have a visible editing route and workbench hides consolidator controls", () => {
  const workbench = read("components/memory/MemoryWorkbench.tsx");

  assert.match(workbench, /key: "preferences"/);
  assert.match(workbench, /method: "PUT"/);
  assert.doesNotMatch(workbench, /<MemoryRunPanel/);
});

test("advanced memory routes and settings no longer expose technical controls", () => {
  const graphPage = read("app/(utility)/memory/graph/page.tsx");
  const settingsPage = read("app/(utility)/settings/memory/page.tsx");

  assert.match(graphPage, /redirect\("\/memory"\)/);
  for (const term of ["l2_budget", "l3_budget", "Audit mode", "Chunking"]) {
    assert.doesNotMatch(settingsPage, new RegExp(term));
  }
});
