import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const read = (filePath: string) =>
  fs.readFileSync(path.join(process.cwd(), filePath), "utf8");

test("session-api exposes the folder CRUD and move surface", () => {
  const source = read("lib/session-api.ts");

  assert.match(source, /export interface SessionFolder/);
  assert.match(source, /status: "active" \| "archived"/);
  assert.match(source, /pinned\?: number/);
  assert.match(source, /listSessionFolders/);
  assert.match(source, /createSessionFolder/);
  assert.match(source, /renameSessionFolder/);
  assert.match(source, /archiveSessionFolder/);
  assert.match(source, /restoreSessionFolder/);
  assert.match(source, /deleteSessionFolder/);
  assert.match(source, /moveSessionsToFolder/);
  assert.match(source, /setSessionFolder/);
  assert.match(source, /pinSessionFolder/);
  assert.match(source, /unpinSessionFolder/);
  // listSessions must forward the folder filter into the request
  assert.match(source, /folderId\?: string \}/);
  assert.match(source, /qs\.set\("folder_id", options\.folderId\)/);
  // the folder filter is part of the cache key so filtered lists don't collide
  assert.match(
    source,
    /`sessions:\$\{limit\}:\$\{offset\}:\$\{options\?\.folderId \?\? "\*"\}`/,
  );
  // every folder mutation invalidates both cache families
  assert.match(source, /invalidateSessionFolderCache\(\)/);
  assert.match(source, /invalidateClientCache\("session-folders:"\)/);
});

test("SessionList renders folder groups, unassigned bucket and archived section", () => {
  const source = read("components/SessionList.tsx");

  // folder grouping is enabled whenever folders are provided
  assert.match(source, /folderUiEnabled = folders !== undefined/);
  assert.match(source, /groupByFolder\(sessions, folders\)/);
  // the unassigned bucket always exists as a landing spot and is collapsible
  assert.match(source, /t\("Unassigned"\)/);
  assert.match(
    source,
    /renderGroupHeader\(Inbox, t\("Unassigned"\), unassigned\.length, \{/,
  );
  assert.match(source, /unassignedCollapsed/);
  assert.match(source, /setUnassignedCollapsed\(\(prev\) => !prev\)/);
  // archived folders get their own collapsible section
  assert.match(source, /archivedGroups\.length > 0/);
  assert.match(source, /t\("Archived"\)/);
  // moving a session out of an archived folder is the individual recovery path
  assert.match(source, /inArchivedFolder && onMoveSession/);
  assert.match(source, /onMoveSession\(session\.session_id, ""\)/);
  // sessions inside active folders get a direct "remove from folder" action
  assert.match(source, /!inArchivedFolder && session\.folder_id && onMoveSession/);
  assert.match(source, /t\("Remove from folder"\)/);
  assert.match(source, /<FolderMinus size=\{10\} \/>/);
  // archived folders are never move targets in the picker
  assert.match(source, /folders\.filter\(\(folder\) => folder\.status === "active"\)/);
  // folder lifecycle actions are opt-in via props
  assert.match(source, /onCreateFolder\?: \(name: string\)/);
  assert.match(source, /onRenameFolder\?: \(folderId: string, name: string\)/);
  assert.match(source, /onArchiveFolder\?: \(folderId: string\)/);
  assert.match(source, /onRestoreFolder\?: \(folderId: string\)/);
  assert.match(source, /onDeleteFolder\?: \(folderId: string\)/);
});

test("SessionList supports drag & drop moves", () => {
  const source = read("components/SessionList.tsx");

  // rows are draggable (disabled in select mode) and carry a custom mime type
  assert.match(source, /draggable=\{!selectMode && !!onMoveSession\}/);
  assert.match(source, /setData\("application\/x-session-id", sessionId\)/);
  assert.match(source, /effectAllowed = "move"/);
  assert.match(source, /handleDragStart/);
  assert.match(source, /handleDragEnd/);
  // active folder headers and the unassigned header are drop targets
  assert.match(source, /const dropTarget = !archived && !!onMoveSession/);
  assert.match(source, /handleDropOnTarget\(event, folder\.id\)/);
  assert.match(source, /handleDropOnTarget\(event, ""\)/);
  // archived folders are never drop targets
  assert.match(source, /sessions cannot move into archives/);
  // visual feedback while hovering a target
  assert.match(source, /dragOverTarget === folder\.id/);
  assert.match(source, /bg-\[var\(--primary\)\]\/15 ring-1/);
});

test("SessionList supports multi-select batch moves", () => {
  const source = read("components/SessionList.tsx");

  assert.match(source, /onBatchMove\?:/);
  assert.match(source, /const \[selectMode, setSelectMode\]/);
  assert.match(source, /selectedIds/);
  assert.match(source, /enterSelectMode/);
  assert.match(source, /exitSelectMode/);
  assert.match(source, /t\("Batch select"\)/);
  assert.match(source, /ListChecks/);
  // rows toggle selection instead of navigating in select mode
  assert.match(source, /if \(selectMode\) \{\s*toggleSelected/);
  // action bar shows the selection count and reuses the folder picker
  assert.match(source, /t\("\{\{count\}\} selected", \{ count: selectedIds\.size \}\)/);
  assert.match(source, /onBatchMove\(ids, folderId\)/);
  // select mode disables drag and hides hover actions
  assert.match(source, /draggable=\{!selectMode && !!onMoveSession\}/);
  assert.match(source, /\{!selectMode \? \(\s*<div className="flex shrink-0/);
});

test("SessionList supports folder pinning", () => {
  const source = read("components/SessionList.tsx");

  assert.match(source, /onPinFolder\?:/);
  assert.match(source, /t\("Pin folder"\)/);
  assert.match(source, /t\("Unpin folder"\)/);
  assert.match(source, /<Pin size=\{10\} \/>/);
  assert.match(source, /<PinOff size=\{10\} \/>/);
  // pinned folders sort to the top of the active groups
  assert.match(
    source,
    /grouped\.activeGroups\.sort\(\s*\(a, b\) => \(b\.folder\.pinned \?\? 0\) - \(a\.folder\.pinned \?\? 0\)/,
  );
});

test("WorkspaceSidebar wires folder handlers into the shell", () => {
  const source = read("components/sidebar/WorkspaceSidebar.tsx");

  assert.match(source, /listSessionFolders\(/);
  assert.match(source, /createSessionFolder\(name\)/);
  assert.match(source, /renameSessionFolder\(folderId, name\)/);
  assert.match(source, /archiveSessionFolder\(folderId\)/);
  assert.match(source, /restoreSessionFolder\(folderId\)/);
  assert.match(source, /deleteSessionFolder\(folderId, true\)/);
  assert.match(source, /setSessionFolder\(sessionId, folderId\)/);
  assert.match(source, /pinSessionFolder\(folderId\)/);
  assert.match(source, /unpinSessionFolder\(folderId\)/);
  assert.match(source, /moveSessionsToFolder\(folderId, sessionIds\)/);
  // deleting an archived folder asks before cascading to its sessions
  assert.match(source, /t\("Delete folder with sessions", \{ count, name/);
  assert.match(source, /window\.confirm\(message\)/);
  // folder props forwarded to SidebarShell
  assert.match(source, /folders=\{folders\}/);
  assert.match(source, /onCreateFolder=\{handleCreateFolder\}/);
  assert.match(source, /onMoveSession=\{handleMoveSession\}/);
  assert.match(source, /onPinFolder=\{handlePinFolder\}/);
  assert.match(source, /onBatchMove=\{handleBatchMove\}/);
});

test("SidebarShell forwards folder props to SessionList", () => {
  const source = read("components/sidebar/SidebarShell.tsx");

  assert.match(source, /folders\?: SessionFolder\[\]/);
  assert.match(source, /folders=\{folders\}/);
  assert.match(source, /onCreateFolder=\{onCreateFolder\}/);
  assert.match(source, /onMoveSession=\{onMoveSession\}/);
  assert.match(source, /onPinFolder=\{onPinFolder\}/);
  assert.match(source, /onBatchMove=\{onBatchMove\}/);
});

test("ChatHistorySection offers a folder filter", () => {
  const source = read("components/space/ChatHistorySection.tsx");

  assert.match(source, /FILTER_ALL = "__all__"/);
  assert.match(source, /FILTER_UNASSIGNED = "__unassigned__"/);
  assert.match(source, /FILTER_ARCHIVED = "__archived__"/);
  assert.match(source, /listSessionFolders\(\{ force \}\)/);
  assert.match(source, /session\.folder_id === folderFilter/);
  assert.match(source, /folders=\{folders\}/);
});

test("backend registers the session-folders router", () => {
  const source = read("../deeptutor/api/main.py");

  assert.match(source, /session_folders,/);
  assert.match(
    source,
    /prefix="\/api\/v1\/session-folders",\s*tags=\["session-folders"\]/s,
  );
});
