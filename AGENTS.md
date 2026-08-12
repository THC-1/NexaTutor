# NexaTutor — 当前架构与施工约束

## Windows Shell

- Windows 上所有 PowerShell 命令使用 PowerShell 7（`pwsh`）。
- 禁止调用 `powershell.exe` 或依赖 Windows PowerShell 5.1。
- Shell 版本不明确时先确认 `$PSVersionTable.PSVersion.Major -ge 7`。

## 项目状态

NexaTutor 正在从 DeepTutor 渐进裁剪为单用户、本地优先的 AI 学习工作台。前端品牌已经切换，但 Python 分发名、内部 namespace、兼容 CLI、Docker / Compose 标识目前仍是 `deeptutor` / `DeepTutor`。

当前已经完成的 Remove 步骤只有：FastAPI 生命周期不再自动启动或停止 Partner / IM Runtime。Partner Router、CLI、Tools、UI、实现和依赖仍存在，不能在文档或代码中冒充已经完整删除。

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

Tool 共 43 个，Provider Spec 共 36 个，RAG Provider 共 6 个。完整清单见 `NEXATUTOR_RUNTIME_BASELINE.md`。这些是裁剪前基线，不是最终 NexaTutor 范围。

需要持续保护的 Core：

- Chat、Solve、Research、Quiz / Question Pipeline、Mastery Path。
- Mermaid、SVG、Chart.js、HTML 轻量可视化。
- 会话、文件上传、知识库、Notebook、Question Bank、Memory。
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

- `web/.next-deeptutor/` 有大量被 Git 跟踪的历史构建产物变化。
- 禁止执行 `git add -A`。
- 状态、Diff 和暂存必须显式排除 `web/.next-deeptutor/**`。
- 前端验证使用被忽略的 `web/.next`。
- 不恢复、覆盖或删除无法确认归属的已有修改。
- 不提交 `data/`、API Key、Token、日志、上传资料、索引和缓存。

## 常用命令

当前兼容 CLI 仍为 `deeptutor`：

```powershell
deeptutor init
deeptutor start
deeptutor start --dev
deeptutor serve --port 8001
deeptutor chat
deeptutor run chat "解释傅里叶变换"
deeptutor kb list
deeptutor memory show
```

`partner`、`plugin`、`provider`、`book` 等迁移期命令仍可能存在，但不属于最终 Core。

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

当前 `pyproject.toml` 仍包含 `cli`、`server`、`partners`、`matrix`、`matrix-e2e`、`math-animator`、`graphrag`、`rag-lightrag`、`dev` 和 `all` 等 extra。依赖只能在运行时、测试、构建、CLI、动态 import 和 optional extra 引用全部消失后删除。

默认开发安装使用 `pip install -e ".[dev]"`，不要使用会拉入全部待裁剪能力的 `.[all]`。
