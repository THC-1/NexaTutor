# NexaTutor 贡献指南

NexaTutor 正在从 DeepTutor 渐进裁剪为单用户、本地优先的 AI 学习工作台。当前阶段最重要的不是快速增加功能，而是让每一次改动都有明确边界、证据和回滚点。

## 贡献范围

优先接受：

- Chat、Solve、Research、Quiz、Mastery Path 与轻量 Visualize 的可靠性修复。
- 文件解析、知识库、FAISS / BM25 / Hybrid Retrieval 与引用链路修复。
- Notebook、Question Bank、Memory、会话和本地数据恢复修复。
- API Key 脱敏、路径边界、上传安全和 Code Execution 风险收敛。
- 按正式计划执行的单功能域裁剪。
- 简体中文文档与可重复 Smoke / E2E。

暂不接受：

- 新的 IM Channel、外部 Agent、MCP、CLI Apps 或插件市场能力。
- 新的复杂 RAG Engine、本地模型专用入口或高维护 Provider。
- 与当前批次无关的大规模重构。
- 将多个功能域、机械改名和依赖升级混在一个提交中。

## 开始前

1. 阅读 [NEXATUTOR_SLIMMING_PLAN_REVISED新版.md](NEXATUTOR_SLIMMING_PLAN_REVISED新版.md)。
2. 查看 [UPSTREAM_BASE.md](UPSTREAM_BASE.md) 和 [NEXATUTOR_RUNTIME_BASELINE.md](NEXATUTOR_RUNTIME_BASELINE.md)。
3. 记录 `git status --short`，确认没有混入别人的源码修改或生成物。
4. 为本次工作定义一个可命名、可回滚的小目标。
5. 先列出注册点、调用点、UI、后端实现、依赖和共享基础设施。

## 裁剪功能的固定顺序

每个 Remove 功能域必须按以下顺序执行：

```text
1. 取消注册
2. 取消调用
3. 删除 UI
4. 删除后端实现
5. 删除依赖
```

每完成一步就运行对应验证。验证失败时停在当前步骤，不继续删除后续层。

## 开发环境

Python 要求 `>=3.11,<3.14`。Windows 必须使用 PowerShell 7。

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"

cd web
npm ci --legacy-peer-deps
cd ..
```

不要使用 `.[all]` 作为默认开发安装；它会拉入正在计划移除的 Partners、Matrix、Manim 等大型或平台相关依赖。

## 基本验证

Python：

```powershell
ruff check .
ruff format --check .
python -m pytest -q tests deeptutor/learning/tests
```

前端：

```powershell
cd web
npm run i18n:parity
npm run test:node
npm run lint
npm run build
```

每个微步骤可以先跑相关测试；功能域完成时再跑完整测试和干净环境 E2E。不能把缺少依赖导致的失败直接解释为代码回归。

## 工作区规则

- 禁止执行 `git add -A`。
- 禁止把 `data/`、API Key、Token、上传资料、知识库索引或日志提交到仓库。
- `web/.next-deeptutor/` 有大量历史被跟踪构建产物；检查和暂存时必须显式排除。
- 前端本地验证使用被忽略的 `web/.next`。
- 不恢复、覆盖或删除无法确认归属的已有修改。
- 不自动删除旧 Partner、Book、Agent、OAuth 或 RAG 数据。

## 代码与文档

- Python 使用 Ruff 规则和现有类型约定。
- TypeScript / React 沿用现有组件、i18n 和设计 Token。
- 用户可见文案必须进入简体中文翻译体系；运行时英文 Prompt 不属于项目文档，不能为“只留中文文档”而删除。
- 文档必须区分“当前已实现”“正在施工”“最终目标”。
- 兼容命令、包名和环境变量在代码真正改名之前必须按真实名称书写。

## 提交建议

使用 Conventional Commits，并保持一个提交只表达一个目的：

```text
chore(remove-partners): unregister partner runtime
refactor(remove-partners): remove partner call sites
refactor(remove-partners): remove partner UI
refactor(remove-partners): delete partner backend
build(remove-partners): remove partner dependencies
docs: update NexaTutor runtime status
```

提交前检查：

- Diff 中没有 `.next-deeptutor`、数据或凭据。
- 新增测试能在修改前捕获问题、修改后通过。
- 删除功能不能由旧配置、环境变量或动态 Provider 重新启用。
- Core import、CLI 参数解析和相关用户流程仍通过。

## 上游修复

DeepTutor 作为上游来源保留。不要周期性全量 merge；先阅读改动，再选择性 cherry-pick 或手动移植以下内容：

- 安全修复
- 严重 Bug 修复
- RAG 与文档解析修复
- 模型兼容修复
- Core Runtime 修复

移植时必须排除已删除功能的重新注册、调用、UI 和依赖。

## 安全问题

不要在公开 Issue、日志、截图或测试 Fixture 中提交密钥与个人数据。涉及凭据泄露、路径穿越、任意代码执行或权限绕过的问题，应先在私下渠道报告给仓库维护者，再决定公开方式。
