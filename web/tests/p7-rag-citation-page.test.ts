import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

test("RAG trace sources display retrieved PDF page labels", () => {
  const source = fs.readFileSync(
    path.join(process.cwd(), "components", "chat", "home", "TracePanels.tsx"),
    "utf8",
  );

  assert.match(source, /source\.page/);
  assert.match(source, /t\("Page"\)/);
});
