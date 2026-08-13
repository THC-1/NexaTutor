# NexaTutor 项目交接说明

## 0. P11 / P12 完成状态（2026-08-12）

- P11 已完成依赖最终清洗。删除独立 CLI 分发中无静态、动态、测试、构建、CLI 或 extra 引用的 `nest_asyncio`；补齐 My Agents 的 Claude Code 模型同步所需 `pyte`，并同步 `requirements/cli.txt`。
- P12 第一层已完成：Python 分发名 `nexatutor`、正式 CLI `nexatutor`、前端 package metadata、OpenAPI、Docker / Compose、环境变量、Logger、User-Agent 与公开文档均使用 NexaTutor。
- 旧 `deeptutor` CLI 仅由 `deeptutor_cli.compat:main` 打印迁移提示并转发到正式实现。`NEXATUTOR_*` 优先，仍活跃的 `DEEPTUTOR_*` 仅作单向读取 fallback；已删除 Auth 变量只丢弃，不提供新别名。
- Python 顶级 namespace `deeptutor`、`deeptutor_cli`、`deeptutor_web`、浏览器 localStorage / IndexedDB 旧键、容器内部 Unix 用户和 `data/user` 路径保留，不自动迁移。

### Feature → Dependency Matrix

| Feature | 直接/共享依赖 | 结论 |
| --- | --- | --- |
| Chat / Solve / Research / Quiz / Mastery | `pydantic`, `PyYAML`, `jinja2`, `openai`, `anthropic`, `tiktoken`, `tenacity` | Core 保留 |
| Knowledge / Citation | `llama-index`, BM25 retriever, FAISS vector store, `faiss-cpu`, `numpy`, `PyMuPDF` | LlamaIndex → FAISS + BM25 Hybrid → Citation 保留 |
| Notebook / Question Bank | `pydantic`, `aiosqlite`, office/PDF 读取包 | Core 保留 |
| Memory L1/L2/L3 | `PyYAML`, `aiosqlite`, FastAPI；前端 Memory workbench | Core 保留；三层视图、手动触发入口、Backend 和历史数据均保留 |
| My Agents / Subagents | `httpx`, `prompt_toolkit`, `pyte`, 本地 CLI/PTY 进程能力 | Core 保留；`pyte` 必须进入 CLI wheel |
| OpenAI Codex OAuth | `httpx`, Codex provider / callback router | 独立 Core 保留 |
| LLM / Embedding / Search | `openai`, `anthropic`, `dashscope`, `perplexityai`, `aiohttp`, `httpx`, `requests`, `ddgs` | Registry 独立，均有真实调用，保留 |
| Parsing | Core office/PDF 包；optional `markitdown`, `docling`, `pymupdf4llm`; MinerU 外部 CLI/API | 懒加载 Optional 边界保留 |
| imagegen / STT / TTS | `httpx`, FastAPI multipart，共享 Provider 配置 | Optional 实现保留 |
| Sandbox / Code Execution | stdlib runner、`httpx`; runner 镜像 office/data 工具栈 | Core 隔离基础设施保留 |
| CLI / WS / FastAPI / Next.js | Typer/Rich, FastAPI/Uvicorn/WebSockets, React/Next | Core 保留 |
| Visualize | Mermaid, Chart.js, React bindings, HTML/SVG 运行代码 | Core 保留 |
| Removed domains | Partner SDK、MCP、JWT/bcrypt、PocketBase、Manim、GeoGebra、Videogen、旧 RAG/LLM 专属包 | 声明与实现已清零，不恢复 |

`requests` / `aiohttp` / `httpx` 虽功能重叠，但分别被 Search、LLM 探测和 async Provider/OAuth/Sandbox 使用；office/PDF 依赖同时服务附件、RAG 与 Sandbox skills；无法证明专属归属的共享包未删除。

> 交接日期：2026-08-12
> 工作目录：`D:\games\DeepTutor`
> 当前阶段：P0-P11 与 P12 第一层已完成；Memory 手动触发入口已恢复
> 本文用途：供新会话快速恢复事实、约束、验证证据和下一步施工边界

## 1. 新会话先读什么

按以下顺序读取，不要只根据文件名推断项目状态：

1. `NEXATUTOR_HANDOFF.md`：当前交接事实和下一步。
2. `NEXATUTOR_SLIMMING_PLAN_REVISED新版.md`：唯一裁剪执行基准。
3. `NEXATUTOR_RUNTIME_BASELINE.md`：裁剪开始时的 Registry、Route、CLI 与依赖快照。
4. `UPSTREAM_BASE.md`：上游来源、许可证和基线说明。
5. `README.md`：当前面向使用者的项目介绍。
6. `AGENTS.md`：项目内执行约束。

所有裁剪继续遵循：

```text
取消注册 → 取消调用 → 删除 UI → 删除后端实现 → 删除依赖
```

一个步骤只处理一个可证明的边界。不得把整个功能域一次性删除。

## 1.1 2026-08-12 最新施工状态（优先于下方早期快照）

- P0 已完成：`serve` 默认监听 `127.0.0.1`；Auth off 时 CORS 不再接受任意 Origin；原 PyPI / Docker Release workflow 已暂停；`web/.next-deeptutor/**` 已停止跟踪。
- Partners 已按注册、调用、UI、实现、依赖顺序完整裁剪；Partner Router、CLI、Tools、Subagent backend、调用点、UI、依赖和对应测试均已清理。
- MCP / CLI Apps / Markets 已完整裁剪，并有旧配置不能重新激活的负断言。
- My Agents / Subagents 改为 Core 保留能力，不执行原 P2 删除计划。
- P4 已引入 `LocalUserContext` / `LocalWorkspace` / 本地 Knowledge Access，并将生产 Core 调用迁出 `deeptutor.multi_user.*`。
- Auth / Admin HTTP Router 与 WebSocket Auth 调用已取消；只保留独立的 OpenAI Codex OAuth callback 和本地 Codex OAuth 服务。
- 登录、注册、Profile、Admin Users、Grant Editor、Capability Gate、Cookie 前端门禁和 401 登录跳转 UI 已删除。
- P4 4I / 4J 已完成：账号 Auth Router / service 与整个 `deeptutor/multi_user` 包已删除；`bcrypt`、`python-jose` 已从项目和 server 依赖删除。
- 旧 `auth.json`、`AUTH_*`、`NEXT_PUBLIC_AUTH_ENABLED`、`DEEPTUTOR_AUTH_ENABLED` 不再被读取或导出；launcher、Docker 与 Compose wrapper 会显式丢弃遗留变量，但不删除用户已有配置或数据。
- P4 最终后端组合验证：256 passed / 1 skipped；删除模块不可发现，生产 import 与专属依赖引用均为 0。
- P4 最终前端验证：Node 271/271、i18n parity 通过、lint 0 error（34 条既有 warning）、Next 生产构建成功；构建路由中不存在账号 Auth / Admin 页面。
- P4 阶段的扩大 Python 回归曾为 2368 passed / 13 skipped；另有 12 个已确认的 Windows 编码、POSIX 路径和 sandbox 平台差异失败，与 P4 修改无关。
- P5 施工前的只读盘点已证明 PocketBase 不是 Core 必需存储；随后才按五步执行删除。Sandbox Runner Sidecar 不属于外部集成 Sidecar，继续保护。
- P5 已完成：PocketBase 的 Session backend 选择、startup hook、Compose service、Knowledge 镜像、runtime settings、实现、脚本与 Python SDK 依赖已按五步删除；旧 `integrations.json` 保留原样但不再读取、创建或改写。
- 公网部署能力已收口：external API base、自定义远程 CORS、LAN dev origin 与非 loopback 宿主端口映射已删除；Network UI 只保留本地端口与 Chat timeout。
- Next.js 同源 HTTP/WS proxy、内部 `next_public_api_base`、Codex OAuth callback/临时 loopback overlay、Sandbox Runner、My Agents / Subagents 均继续保留。
- P5 定向后端回归 107 passed；PocketBase 门禁 12 passed；Codex OAuth / Subagents 保护回归 127 passed；扩大定向回归 681 passed，仅有 1 个可独立复现的既有 SQLite 旧路径迁移失败。排除无法在 Windows 收集的 Linux runner 文件后，全量 Python 为 2612 passed / 13 skipped / 12 个已知平台或既有失败。前端 Node 271 passed、i18n parity、lint 0 error（34 warning）和 production build 均通过。
- 测试曾在被忽略的 `data/user/private` 生成少量占位凭据文件；未读取内容、未提交，也未自动删除。后续不得把它们作为代码产物处理，是否清理由用户决定。
- P6 已完成：Book / Living Book、Videogen、Math Animator / Manim、GeoGebra、Cron、Built-in GitHub Tool、Brainstorm、专用 Reason 与通用 Exec 均按五步删除；Notebook、Question Bank、Imagegen 与 Visualize 的 SVG / Chart.js / Mermaid / HTML 路径保留。
- 受限 `code_execution` 已收敛为显式 opt-in、Python-only、argv-only，并只接受声明 `argv-v1` 的健康 SYSTEM runner；Windows 裸机 restricted subprocess 不会激活。runner 仅挂单用户 workspace、位于 internal network 且无宿主端口。该机制是风险降低措施，不是对抗恶意代码的强安全沙箱。
- P6 总门禁 39 passed；后端整合与保护回归 555 passed / 2 skipped；前端 Node 265/265、i18n parity、lint 0 error（27 warning）与 production build 通过；`pip check` 通过。排除 Windows 无法收集的 Linux runner 文件后，全量 Python 为 2581 passed / 10 skipped / 9 个已知 Windows 路径、POSIX sandbox 或既有 SQLite 迁移失败。
- P7 已完成：RAG Registry 只保留 `llamaindex`，GraphRAG、LightRAG / RAG-Anything、LightRAG Server、PageIndex、Tencent IMA 均按五步删除；Knowledge 创建/上传不再接受引擎选择，UI 只保留单一创建知识库流程。
- 标准路径已验证为 Parse → Chunk → Embedding → FAISS + BM25 → Reciprocal-rank Hybrid Retrieval → RAG source / Citation；普通 PDF 页码可贯通到 chunk source，并在 Chat Sources 中显示。旧 SimpleVectorStore 仅保留只读兼容。
- 旧非标准 provider 配置会归一为 `llamaindex` 并标记 `needs_reindex`；旧远程 pointer 由 inactive legacy sentinel 保留原始数据但不可连接、检索或误删外部资源。所有历史索引和设置文件均未自动删除。
- P7 删除与标准路径门禁 26 passed；扩大 Knowledge / RAG / Core 回归 481 passed / 1 skipped；前端 Node 266/266、i18n parity、lint 0 error（27 warning）与 production build 通过；`pip check` 通过。排除 Windows 无法收集的 Linux runner 文件后，全量 Python 为 2444 passed / 9 skipped / 8 个已知 Windows 路径、POSIX sandbox 或既有 SQLite 迁移失败。
- P8 已完成：LLM Provider Registry 从 36 项收敛为 `openai`、`anthropic`、`gemini`、`deepseek`、`custom`、`custom_anthropic` 与独立 Core `openai_codex`。其余 29 项不能由旧 binding、模型名、Key 前缀、Base URL 或本地 URL 重新选择专用 Adapter；旧 catalog 文件本身未自动删除或改写，遗留 binding 只在内存中归入 OpenAI-compatible / Anthropic-compatible。
- GitHub Copilot 与 Azure OpenAI 的专用 LLM 实现、动态工厂分支、Agentic Adapter、CLI Copilot 验证入口及 `oauth-cli-kit` 已删除；CLI `provider login` 只保留 OpenAI Codex。Codex OAuth Router、服务、受管模型目录、前端卡片与 callback proxy 均继续保留。
- 普通 Settings / Catalog 响应现在只返回 `api_key=""` 与 `api_key_set`，不返回明文 Provider Key；保存、Apply、Connection Test 使用 write-only 三态合并，未触碰的空字段保留旧 Key，显式 clear 才清空。前端不记录 Key。
- Embedding、Search 与 My Agents / Subagents 是独立 Registry：Aliyun Embedding 仍需 `dashscope`，Perplexity Search 仍需 `perplexityai`，本地 Claude Code / Codex / Gemini / Kimi / OpenCode / MiMo Agent backend 均保留，未因同名 LLM Provider 收缩而删除。
- P8 定向与 LLM 组合回归 246 passed；Core 扩大回归 762 passed / 2 skipped；前端 Node 269/269、i18n parity、lint 0 error（26 warning）与 production build 通过；`pip check` 通过。排除 Windows 无法收集的 Linux runner 文件后，全量 Python 为 2211 passed / 9 skipped / 8 failed，失败与 P7 相同，均为既有 Windows 路径、POSIX sandbox/resource 或 SQLite 迁移差异。`data/` 与 `web/data` 无 Git 状态变化。

下方“Partner 第一小步”和“尚未完成”等段落是初始交接快照；与本节冲突时，以本节和实际代码负断言为准。

## 1.2 P9 / P10 状态

- Memory L1 / L2 / L3、可发现入口和手动触发能力均为 Core。L1 按 Surface 提供手动 Refresh；L2 / L3 按文档提供 Update / Audit / Dedup，并展示必要运行状态。Graph、Budget、Chunking、Reference 和内部调度细节可默认隐藏。
- Memory Router、Store、Consolidator、数据模型、运行 API、`MemoryRunPanel` 和用户历史数据均保留；`/memory`、`/memory/l1`、`/memory/l2`、`/memory/l3` 路由可用。Memory 已恢复主导航入口，L2 / L3 工作台已重新挂载运行面板；L3 默认进入可运行 Consolidator 的 Recent summary，Preferences 继续保留显式编辑入口。
- P10 Settings / Navigation 保持收口，但 Memory 必须使用独立导航或学习空间中的明确入口，不能只保留不可发现的路由。Settings Hub 隐藏 Network、image、stt、tts 独立入口，保留兼容页/API/旧配置；status 与 mineru 页面继续重定向，Hub 保留状态条。Attachments、Capabilities、Tools 和本地 Agents 归入 Chat 与工具信息架构。MinerU 仍是可选文档解析路径，不能删除。
- Memory 正向契约断言 L1 / L2 / L3 导航、L1 Refresh、L2 / L3 Update / Audit / Dedup 及运行状态；响应式工作台必须在桌面保持三栏，在中小屏按自然文档流排列且不得重叠或横向溢出。
- P11 只允许最终依赖清洗：先证明运行时、测试、CLI、动态 import、optional extra 和构建引用为零，再删除专属依赖；不删除 Memory、MinerU、voice/image、Sandbox、My Agents/Subagents 或 Codex OAuth 共享依赖。

## 2. Git 与 GitHub 当前状态

- GitHub 仓库：`https://github.com/THC-1/NexaTutor`
- 可见性：公开。
- 默认分支：`main`。
- `origin`：`https://github.com/THC-1/NexaTutor.git`
- `upstream`：`https://github.com/HKUDS/DeepTutor.git`
- 当前公开根提交：`ae95fe545a378401cc5559bc2d943609a9fcd9e5`。
- 当前公开历史只有一个根提交，不包含 DeepTutor 的上游提交历史。
- 上游来源和许可信息通过 `LICENSE`、`THIRD_PARTY_NOTICES.md` 与
  `UPSTREAM_BASE.md` 保留。
- 仓库级 Git 作者邮箱已配置为 GitHub noreply 地址，不要改回私人邮箱。

交接文档创建前，工作区除被忽略的运行/构建产物外是干净的。本文是本次新建文件，
是否提交和推送由后续会话按用户指令决定。

## 3. 当前可验证的产品状态

### 3.1 已经完成

#### 独立公开基线

- 已建立 NexaTutor 独立 Git 根提交并公开上传。
- `data/` 保持忽略，本地设置、会话、资料、知识库和凭据没有进入公开提交。
- `web/.next-deeptutor/` 已从 Git 跟踪中移除，但本地生成文件仍可存在。
- 当前提交中没有被跟踪的 `web/.next-deeptutor/**` 文件。
- 发布前对本次新增/修改文件执行密钥扫描，结果为 0 个候选。
- 全量扫描的候选来自上游已有的测试夹具、占位键名、固定提交哈希或协议常量；
  不得因此取消后续提交前的增量密钥检查。

#### 前端品牌

- 页面标题、登录注册、侧栏、状态文案和主要界面文案已从 DeepTutor 切换为
  NexaTutor。
- 已移除侧栏/AppShell 中旧品牌横幅和指向旧项目发布页的可见链接。
- 浏览器实测页面标题为 NexaTutor，可访问界面中未发现 DeepTutor 字样，控制台无错误。
- Python 包名、模块导入、发行名和兼容 CLI 仍为 `deeptutor`，这是有意保留的迁移边界，
  现在不要做全仓机械改名。
- `assets/` 中仍有旧截图、旧架构图和旧 Logo，它们不是当前可见前端品牌清理的完成证据，
  后续应随对应功能域或文档归档单独处理。

#### Partner / IM 第一小步

- `deeptutor/api/main.py` 的 FastAPI 生命周期不再调用
  `auto_start_partners()`。
- 应用关闭时不再调用 `stop_all(preserve_auto_start=True)`。
- 新增 `tests/api/test_main_partner_lifecycle.py` 作为防回归测试。
- 这只证明启动和关闭应用不会自动启停 IM Channel。
- Partner API、CLI、Tools、UI、后端实现、依赖、数据迁移和兼容代码均未删除。

#### 文档整理

- 根 README 已改为简体中文并准确声明迁移期边界。
- `AGENTS.md`、`CONTRIBUTING.md`、`SKILL.md`、`CONTAINERIZATION.md`、
  `THIRD_PARTY_NOTICES.md` 和 CLI README 已按当前项目状态更新。
- 已删除根目录 `Communication.md`。
- 已删除 `assets/README/` 下 10 份多语言 README，仅保留简体中文主 README 作为入口。
- 新增 `UPSTREAM_BASE.md`、`NEXATUTOR_RUNTIME_BASELINE.md` 和
  `assets/releases/README.md`。

### 3.2 明确尚未完成

- Partner 主 API Router 仍注册在 `deeptutor/api/main.py`。
- Partner Router 实现在 `deeptutor/api/routers/partners.py`，仍完整存在。
- `deeptutor/api/routers/plugins_api.py` 仍直接导入 Partner 的运行和流式聊天辅助函数。
- `deeptutor/api/routers/subagents.py` 仍保留 Partner 列表、连接和访问控制旁路。
- Partner CLI、三个 Partner Built-in Tool、服务层、Channel SDK 和测试仍存在。
- My Agents / Subagents、MCP、CLI Apps、Skill 市场、Auth/Admin、Book、视频、
  Manim、GeoGebra、高权限工具、多种 RAG 引擎和大量 Provider 均未开始正式删除。
- 内部 `deeptutor` 命名尚未迁移。
- 归档发布说明和部分历史图片仍反映 DeepTutor 时代，不代表 NexaTutor 当前功能。
- `README.md` 与 `NEXATUTOR_RUNTIME_BASELINE.md` 中仍有“构建目录被 Git 跟踪”的旧描述；
  实际状态已经变为 0 个跟踪文件，后续文档小提交应修正这两处。

## 4. 当前运行状态

交接时开发服务仍在运行：

- 前端：`http://127.0.0.1:3782`
- 后端：`http://127.0.0.1:8001`
- 前端进程为 Next.js 开发服务。
- 后端进程为 `uvicorn deeptutor.api.main:app`。

这些是交接瞬间的临时状态。新会话开始时必须重新检查端口，不能假定进程仍存活。
不要处理占用 `3000` 端口的其他项目。

推荐检查命令：

```powershell
Get-NetTCPConnection -State Listen |
  Where-Object LocalPort -in @(3782, 8001) |
  Select-Object LocalAddress, LocalPort, OwningProcess
```

## 5. 已通过的验证

### 后端与文档定向测试

```powershell
python -m pytest -p no:cacheprovider -q `
  tests/api/test_main_partner_lifecycle.py `
  tests/cli/test_docs_contract.py `
  tests/cli/test_provider_cli.py `
  tests/scripts/test_docker_compose.py
```

结果：`20 passed`，另有 1 个非阻断 warning。

### 前端 Node 测试

```powershell
cd web
npm run test:node
```

结果：`386 passed, 0 failed`。

### 国际化键一致性

```powershell
cd web
npm run i18n:parity
```

结果：通过。

### 其他已完成验证

- 前端生产构建成功，构建目录使用被忽略的 `web/.next`。
- ESLint 为 0 error；仍有既有 warning。
- Markdown 本地链接扫描为 0 个缺失链接。
- `git diff --check` 通过。
- 本地 HEAD 与 GitHub `origin/main` 在交接前一致。

注意：不要用 `node --test tests/*.test.ts` 直接运行前端测试。该命令会跳过项目的
TypeScript 路径解析配置并产生大量假失败；正式入口是 `npm run test:node`。

## 6. 下一会话推荐的第一个施工步骤

### 目标

只取消 Partner 主 API Router 的注册，不删除 Router 实现、服务层、前端、CLI、Tools
或依赖。

### 修改边界

重点检查 `deeptutor/api/main.py`：

- Router import 列表中的 `partners`。
- `partners.router` 对 `/api/v1/partners` 的 `include_router()` 调用。

当前基线中 `/api/v1/partners` 有 32 个 Route object；路径包含 `partner` 的 Route
object 共 33 个，另外一个是 `/api/v1/subagents/partners`。取消主 Router 注册后：

- `/api/v1/partners` 主前缀应完全消失。
- `/api/v1/subagents/partners` 在这个小步中可以继续存在，因为它属于后续
  Subagent/Partner 旁路处理。
- `plugins_api.py` 对 Partner helper 的引用也先保留；否则本步骤会扩大为取消调用或
  删除实现。

### 必须先补的证据

新增精确测试，至少断言：

1. 应用 Route 中不存在以 `/api/v1/partners` 开头的路径。
2. 应用仍能 import。
3. 不把 `/api/v1/subagents/partners` 的存在误判为本步骤失败。
4. 核心 `/api/v1`、WebSocket 和健康检查路由仍存在。

修改后先运行新测试和相关 API 测试，再运行最小 import smoke。不要因为旧
`tests/api/test_partners_router.py` 失败就立即删除整套 Partner 测试；先区分“Router
仍可独立测试”和“主应用不再注册 Router”这两个事实。

## 7. 下一批次顺序

Partner / IM 建议继续拆成以下独立提交：

1. 取消 Partner 主 API Router 注册。
2. 取消 Partner CLI Group 注册。
3. 取消三个 Partner Built-in Tool 注册。
4. 取消 Partner Subagent Backend 和 `/api/v1/subagents/partners` 旁路。
5. 解除 Plugin API 对 Partner helper 的转发。
6. 清理前端导航、页面、组件和 API client。
7. 在引用、动态 import、测试和兼容迁移均清零后删除实现。
8. 最后删除 Channel SDK、optional extra 和直接依赖。

每一步都必须重新搜索静态引用、动态 import、Registry、CLI、Route、测试和配置迁移。

## 8. 强制保护项

- 不提交 `data/`、`.env`、API Key、OAuth Token、上传资料、知识库索引或日志。
- 不把 `web/.next`、`web/.next-deeptutor`、`node_modules` 或其他生成目录重新加入 Git。
- 不删除用户本地数据，也不自动迁移 `data/partners`。
- 不在没有负断言和引用证据时删除整个目录。
- 不把“UI 隐藏”当成“功能已删除”。
- 不提前删除依赖；必须先证明运行时、构建、测试、CLI、动态 import 和 optional extra
  均不再使用。
- 不提前全仓替换 `deeptutor`；包名和 CLI 改名属于后期独立批次。
- 不因旧名称出现在许可证、上游说明、兼容标识符或历史归档中而机械删除。
- PowerShell 使用版本 7；先确认 `$PSVersionTable.PSVersion.Major -ge 7`。
- 发现与当前步骤无关的脏文件时保留它们，不重置、不覆盖。

## 9. 每次小提交的最低检查

```powershell
git status --short
git diff --check
git diff --name-only
```

随后按改动范围执行：

- 精确 pytest。
- FastAPI import/Route 负断言。
- `npm run test:node`。
- `npm run i18n:parity`。
- 涉及前端构建时使用 `web/.next`。
- 涉及公开推送时，对新增/修改文件重新执行密钥和个人路径扫描。

提交前明确列出：改了什么、没有改什么、验证结果、下一步边界。

## 10. 可直接交给新会话的开场指令

```text
请先完整阅读 D:\games\DeepTutor\NEXATUTOR_HANDOFF.md、
NEXATUTOR_SLIMMING_PLAN_REVISED新版.md、NEXATUTOR_RUNTIME_BASELINE.md 和 AGENTS.md。
继续按小步裁剪原则推进。第一步只取消 Partner 主 API Router 在 FastAPI 主应用中的
注册，先补 Route 负断言，再修改注册，不删除 Router 实现、前端、CLI、Tools、依赖、
Plugin 转发或 Subagent 旁路。修改前后都要给出可复核证据，并运行交接文档指定的测试。
```
