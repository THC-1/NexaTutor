import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const read = (filePath: string) =>
  fs.readFileSync(path.join(process.cwd(), filePath), "utf8");

test("chat composer keeps the connected-agent entry visible when the list is empty", () => {
  const source = read("components/chat/home/ChatComposer.tsx");

  assert.match(source, /\{onSelectAgent \? \(\s*<AgentSelector/);
  assert.doesNotMatch(
    source,
    /connectedAgents\.length\s*>\s*0\s*&&\s*onSelectAgent/,
  );
});

test("empty connected-agent picker links to agent management", () => {
  const source = read("components/chat/home/AgentSelector.tsx");

  assert.match(source, /agents\.length === 0/);
  assert.match(source, /href="\/agents"/);
  assert.match(source, /No connected agents — connect one in My Agents\./);
});
