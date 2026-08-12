# NexaTutor — 当前架构与施工约束

## Windows Shell

- Windows 上所有 PowerShell 命令使用 PowerShell 7（`pwsh`）。
- 禁止调用 `powershell.exe` 或依赖 Windows PowerShell 5.1。
- Shell 版本不明确时先确认 `$PSVersionTable.PSVersion.Major -ge 7`。

## 项目状态

NexaTutor 已完成 P11/P12 第一层：分发名、正式 CLI、Docker / Compose 和公开品牌使用 `nexatutor` / `NexaTutor`。内部 Python namespace 与持久化兼容标识继续保留 `deeptutor`。

P0、Partners、P3、P4、P5、P6、P7 与 P8 已完成。Partner / IM、MCP、CLI Apps、在线 Skill Hub、账号 Auth / Admin / JWT / Cookie / Grants / Multi-user、PocketBase、公网部署、Book、Videogen、Math Animator / Manim、GeoGebra、Cron、Built-in GitHub / Brainstorm / Reason / Exec，以及非标准 RAG 和非目标 LLM Provider 的注册、调用、UI、后端实现和专属依赖均已删除，旧配置不能重新启用专用 Adapter。知识库只保留 LlamaIndex → FAISS + BM25 Hybrid → Citation 标准路径。LLM 产品入口只保留 OpenAI、Anthropic、Gemini、DeepSeek、OpenAI-compatible、Anthropic-compatible；OpenAI Codex OAuth 是独立 Core 登录能力，继续保留。Embedding、Search 与本地 Subagent Provider 是独立 Registry，不随 LLM 同名项删除。普通 Settings 响应不返回 Provider 明文 API Key，密钥使用 write-only 三态更新。运行边界已收敛为 `LocalUserContext → LocalWorkspace → data/user`，服务和容器端口只绑定 loopback；My Agents / Subagents 与 Sandbox Runner 明确保留。下一步从 P9 Memory UI 精简开始。

P9/P10、P11 与 P12 第一层已完成。Python 顶级 namespace 改名延后单独决策；不得机械替换内部 import 或自动迁移用户数据、浏览器持久化键。

所有施工以 `NEXATUTOR_SLIMMING_PLAN_REVISED新版.md` 为唯一执行基准。

## 核心架构

```text
CLI (Typer) | WebSocket /api/v1/ws | Python SDK
                         ↓
                  ChatOrchestrator
                         ↓
          ToolRegistry + CapabilityRegistry
                         ↓
                      StreamBus
```

- `ChatOrchestrator` 将 `UnifiedContext` 路由到选定 Capability，默认是 `chat`。
- Tool 是 LLM 单次选择调用的函数；Capability 是接管整轮的多阶段流程。
- Capability 通过共享 `StreamBus` 输出事件。
- 运行设置保存在 `data/user/settings/*.json`，项目根 `.env` 不作为运行时配置来源。

## 当前 Registry 基线

Capability 共 7 个：

```text
chat, deep_solve, deep_question, deep_research, visualize, math_animator,
mastery_path
```

裁剪前 Tool 共 43 个、LLM Provider Spec 共 36 个、RAG Provider 共 6 个；当前 LLM Provider Spec 为 7 个（六类产品入口加 `openai_codex`）。完整裁剪前清单见 `NEXATUTOR_RUNTIME_BASELINE.md`，不能把该历史基线当作当前运行时范围。

需要持续保护的 Core：

- Chat、Solve、Research、Quiz / Question Pipeline、Mastery Path。
- Mermaid、SVG、Chart.js、HTML 轻量可视化。
- 会话、文件上传、知识库、Notebook、Question Bank、Memory。
- My Agents / Subagents 与用户显式配置的本地 Agent Provider。
- CLI、WebSocket、模型配置、RAG、引用、使用量与成本统计。

## 固定裁剪流程

每个功能域必须严格按顺序执行：

```text
取消注册 → 取消调用 → 删除 UI → 删除后端实现 → 删除依赖
```

要求：

1. 一次只处理一个可命名、可回滚的小目标。
2. 先列出注册点、调用点、UI、实现、依赖和共享基础设施。
3. 每一步先补负断言或观测点，再修改代码。
4. 每一步验证通过后才进入下一步。
5. 不把机械改名、核心重构和多个 Remove 域混入同一批。
6. 不自动删除用户历史数据。

## 工作区边界

- `web/.next-deeptutor/` 已停止 Git 跟踪并由 `.gitignore` 忽略；本地历史生成物仍可能存在。
- 禁止执行 `git add -A`。
- 状态、Diff 和暂存必须显式排除 `web/.next-deeptutor/**`。
- 前端验证使用被忽略的 `web/.next`。
- 不恢复、覆盖或删除无法确认归属的已有修改。
- 不提交 `data/`、API Key、Token、日志、上传资料、索引和缓存。

## 常用命令

正式 CLI 为 `nexatutor`；`deeptutor` 是临时兼容转发：

```powershell
nexatutor init
nexatutor start
nexatutor start --dev
nexatutor serve --port 8001
nexatutor chat
nexatutor run chat "解释傅里叶变换"
nexatutor kb list
nexatutor memory show
```

`partner`、`plugin` 与 `book` 顶层命令已删除；`skill` / `skills` 只保留本地 `list`、`remove`。`provider` 等迁移期命令仍可能存在，但不属于最终 Core。

## 关键文件

| 路径 | 职责 |
| --- | --- |
| `deeptutor/runtime/orchestrator.py` | 统一编排入口 |
| `deeptutor/runtime/launcher.py` | 前后端生命周期与端口发现 |
| `deeptutor/runtime/registry/` | Tool / Capability Registry |
| `deeptutor/runtime/bootstrap/builtin_capabilities.py` | 内置 Capability 类路径 |
| `deeptutor/services/config/runtime_settings.py` | JSON Runtime Settings |
| `deeptutor/core/stream.py`、`stream_bus.py` | 流事件与 fan-out |
| `deeptutor/core/tool_protocol.py` | Tool 协议 |
| `deeptutor/core/capability_protocol.py` | Capability 协议 |
| `deeptutor/core/context.py` | `UnifiedContext` |
| `deeptutor/tools/builtin/__init__.py` | 内置 Tool 注册来源 |
| `deeptutor/api/main.py` | FastAPI App、Router 与 Lifespan |
| `deeptutor_cli/main.py` | Typer CLI 入口 |
| `web/` | Next.js 前端 |

## 验证层级

每个微步骤：

- Python import smoke。
- 相关 Registry / Router / CLI 精确断言。
- 相关单元测试。

涉及前端：

- `npm run i18n:parity`
- `npm run test:node`
- `npm run lint`
- `npm run build`

功能域完成：

- 完整 Python 测试。
- FastAPI startup、CLI、Core 用户流程。
- 干净 venv、干净 node_modules、干净 data 目录 E2E。
- 已删除功能不能被旧配置或动态 Provider 重新启用。

## 依赖层

当前 `pyproject.toml` 已移除 `partners`、`matrix`、`matrix-e2e`、`math-animator`、`graphrag`、`rag-lightrag` extra 与对应专用依赖，仍包含 `cli`、`server`、`dev` 和 `all` 等迁移期 extra。依赖只能在运行时、测试、构建、CLI、动态 import 和 optional extra 引用全部消失后删除。

默认开发安装使用 `pip install -e ".[dev]"`，不要使用会拉入全部待裁剪能力的 `.[all]`。
