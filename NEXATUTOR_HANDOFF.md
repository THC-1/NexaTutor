# NexaTutor 项目交接说明

> 更新日期：2026-08-13
> 当前阶段：P0-P11 与 P12 第一层已完成，项目从裁剪阶段转入改造阶段
> 工作目录：`D:\games\DeepTutor`

本文只记录当前有效事实、兼容边界和下一阶段入口。裁剪前的注册表与数量快照见 `NEXATUTOR_RUNTIME_BASELINE.md`，完整决策和删除方法见 `NEXATUTOR_SLIMMING_PLAN_REVISED新版.md`；不要再从旧施工步骤推断当前代码状态。

## 1. 当前产品边界

NexaTutor 是单用户、本地优先的 AI 学习工作台。前后端在本机运行，通过云端 API 使用 LLM、Embedding 和搜索服务；会话、资料、知识库、Notebook、Question Bank、Memory 与学习记录默认保存在 `data/user`。

当前内置 Capability 共 6 个：

```text
chat, deep_solve, deep_question, deep_research, visualize, mastery_path
```

必须持续保护的 Core：

- Chat、Solve、Research、Question Pipeline、Mastery Path。
- Mermaid、SVG、Chart.js、HTML 轻量可视化。
- 会话、文件上传、知识库、Notebook、Question Bank、Memory。
- Memory L1 / L2 / L3 主导航、响应式工作台及手动 Refresh / Update / Audit / Dedup。
- My Agents / Subagents、`consult_subagent` 与用户显式配置的本地 Agent Provider。
- OpenAI Codex OAuth、Sandbox Runner 与受限 `code_execution`。
- CLI、WebSocket、Python SDK、模型配置、引用、使用量与成本统计。

## 2. 已完成的裁剪

以下功能的注册、调用、UI、后端实现和专属依赖均已删除，旧配置不得重新启用：

- Partners / IM、Partner Memory / Workspace / Subagent backend。
- MCP、CLI Apps、Deferred Tools、在线 Skill Hub、Plugin Management。
- 账号 Auth、Admin、JWT / Cookie / Grants、Multi-user。
- PocketBase、外部集成 Sidecar、公网部署入口。
- Book / Living Book、Videogen、Math Animator / Manim、GeoGebra、Cron。
- Built-in GitHub、Brainstorm、Reason、通用 Exec。
- GraphRAG、LightRAG、LightRAG Server、PageIndex、Tencent IMA。
- 非目标专用 LLM Provider、GitHub Copilot、Azure OpenAI 专用实现及本地模型专用入口。

保留但已经收敛的边界：

- RAG 只有 `llamaindex` 注册项，标准链路为 Parse → Chunk → Embedding → FAISS + BM25 Hybrid → Citation。
- LLM Registry 只有 `openai`、`anthropic`、`gemini`、`deepseek`、`custom`、`custom_anthropic`、`openai_codex`。
- 普通 Settings / Catalog 不返回明文 API Key；密钥采用 write-only 三态更新。
- `code_execution` 默认关闭、Python-only、argv-only，只向声明 `argv-v1` 的健康 SYSTEM Runner 提交任务。
- 服务与容器端口只绑定 loopback；Next 同源代理和临时 Codex OAuth 回调映射继续保留。

## 3. 命名与数据兼容

- Python 分发名和正式 CLI 是 `nexatutor` / `NexaTutor`。
- `deeptutor` CLI 仅作带迁移提示的兼容转发。
- 内部 Python namespace `deeptutor`、`deeptutor_cli`、`deeptutor_web` 暂不机械改名。
- `NEXATUTOR_*` 优先；仍活跃的 `DEEPTUTOR_*` 只作单向读取 fallback。已删除功能的旧变量只丢弃，不创建新别名。
- 浏览器 localStorage / IndexedDB 旧键、容器内部 Unix 用户、`data/user` 路径和用户历史数据不自动迁移或删除。
- 项目根 `.env` 不是应用运行设置来源；设置位于 `data/user/settings/*.json`。

## 4. 当前 CLI

正式入口为 `nexatutor`。当前顶层命令：

```text
init, run, start, serve, chat, kb, skill, skills,
memory, config, session, notebook, provider
```

`skill` / `skills` 仅管理本地 Skill；`provider` 仅保留 `openai-codex` OAuth 登录。`partner`、`plugin`、`book` 已不存在。

## 5. 改造阶段约束

后续工作不再以继续删除功能为默认目标。开始任何改造前，应先判断它属于 Core 修复、体验改造、架构演进还是新的产品能力，并明确以下事项：

1. 是否改变当前产品边界或恢复已删除域；若是，先修订正式计划并单独决策。
2. 是否影响 `LocalUserContext → LocalWorkspace → data/user`、持久化键或历史数据兼容。
3. 是否影响 Capability / Tool / Provider Registry、WebSocket 事件或 CLI 契约。
4. 是否影响 Memory、My Agents / Subagents、Codex OAuth、Sandbox Runner 或标准 RAG 路径。
5. 是否需要迁移；默认只做向后兼容读取，不自动删除用户数据。

若未来仍需删除某个功能域，继续严格采用：

```text
取消注册 → 取消调用 → 删除 UI → 删除后端实现 → 删除依赖
```

## 6. 工作区与验证

- 禁止 `git add -A`，状态、Diff 和暂存显式排除 `web/.next-deeptutor/**`。
- 前端构建使用被忽略的 `web/.next`。
- 不提交 `data/`、API Key、Token、日志、上传资料、索引或缓存。
- 不恢复、覆盖或删除无法确认归属的已有修改。
- Windows 使用 PowerShell 7。

后端最小冒烟：

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -B -c "from deeptutor.runtime.orchestrator import ChatOrchestrator; from deeptutor.api.main import app; print(len(app.routes))"
python -m pytest -p no:cacheprovider -q tests/runtime/registry tests/core/test_capabilities_runtime.py
```

前端基线：

```powershell
cd web
npm run i18n:parity
npm run test:node
npm run lint
npm run build
```

改造必须补与风险匹配的定向测试；触及共享契约、持久化或核心用户流程时，再扩大回归和干净环境 E2E。

## 7. 文档阅读顺序

1. `README.md`：产品和使用者视角的当前事实。
2. `NEXATUTOR_HANDOFF.md`：改造阶段的工程交接。
3. `AGENTS.md`：仓库施工约束。
4. `NEXATUTOR_SLIMMING_PLAN_REVISED新版.md`：产品边界、删除决策与历史执行基准。
5. `NEXATUTOR_RUNTIME_BASELINE.md`：裁剪前历史快照，不代表当前运行时。
6. `UPSTREAM_BASE.md`：上游来源与固定基线。

## 8. 当前工作区提示

本文更新时，工作区已有与本次文档整理无关的前端修改：`web/locales/en/app.json`、`web/locales/zh/app.json`、`web/next-env.d.ts`、`web/tests/appearance-settings-page.test.ts`。这些文件未被本次文档工作修改、恢复或暂存。
