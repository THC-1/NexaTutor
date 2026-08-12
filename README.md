# NexaTutor

NexaTutor 是面向个人用户的本地 AI 学习工作台。应用前后端运行在用户自己的计算机上，通过云端 API 使用大语言模型、Embedding 和搜索服务；会话、资料、知识库、笔记、题库与学习记录默认保存在本地。

> 当前状态：项目正在从 DeepTutor 渐进裁剪为 NexaTutor。前端品牌已经切换为 NexaTutor，但 Python 分发名、内部包名和兼容 CLI 目前仍为 `deeptutor`。本文只描述当前可以验证的状态，不把规划中的目标写成已经完成的功能。

## 当前进度

截至 2026-08-12：

- 前端页面标题、侧栏、登录注册、状态文案和中英文界面文案已统一为 NexaTutor。
- FastAPI 生命周期不再自动启动或停止 Partner / IM Runtime。
- Partner API、CLI、Tools、UI、后端实现和依赖目前仍在仓库中，后续按“取消注册 → 取消调用 → 删除 UI → 删除实现 → 删除依赖”逐步处理。
- Python 顶级包仍为 `deeptutor`，兼容命令仍为 `deeptutor`；正式改名安排在核心裁剪与回归验证完成后。
- `web/.next-deeptutor/` 仍有历史上被 Git 跟踪的构建产物，任何改动不得将其混入源码提交。

详细施工顺序以 [NEXATUTOR_SLIMMING_PLAN_REVISED新版.md](NEXATUTOR_SLIMMING_PLAN_REVISED新版.md) 为唯一执行基准；基线信息见 [UPSTREAM_BASE.md](UPSTREAM_BASE.md) 和 [NEXATUTOR_RUNTIME_BASELINE.md](NEXATUTOR_RUNTIME_BASELINE.md)。

## 产品边界

NexaTutor 的核心链路是：

```text
本地启动
  → 配置云端模型、Embedding 与搜索 API
  → 对话 / 解题 / 研究 / 练习
  → 上传资料并建立知识库
  → 保存笔记、题目、记忆和学习进度
  → 重启后继续原有学习状态
```

默认保留的核心能力：

- Chat、Deep Solve、Deep Research、Quiz、Mastery Path。
- Mermaid、SVG、Chart.js、HTML 等轻量可视化。
- PDF、DOCX、PPTX、XLSX、Markdown 和纯文本资料处理。
- LlamaIndex、FAISS、BM25 与 Hybrid Retrieval 主知识库路径。
- 会话、知识库、Notebook、Question Bank、Memory 和学习进度。
- 本地 Web、FastAPI、WebSocket、Python SDK 与项目 CLI。

以下能力正在按批次移除，当前不能仅凭本表判断代码已经删除：

- Partners / IM Channels。
- My Agents / Subagents 与外部 CLI Agent 调用。
- MCP、CLI Apps、在线 Skill 市场与插件管理 UI。
- Auth / Admin / Multi-user / Grants。
- Book、视频、Manim、GeoGebra、Cron、GitHub Tool 与通用 Exec。
- GraphRAG、LightRAG、PageIndex、Tencent IMA 等非标准 RAG 路径。
- 本地模型入口、专用 OAuth Provider 与复杂公网部署能力。

## 环境要求

- Python `>=3.11,<3.14`
- Node.js `>=20`；CI 使用 Node.js 22
- npm
- Windows 开发建议使用 PowerShell 7

大型或平台相关的可选依赖不会成为 NexaTutor 最终默认安装要求。当前依赖仍处于迁移期，请以 `pyproject.toml` 和 `web/package.json` 为准。

## 从源码运行

```powershell
git clone https://github.com/THC-1/NexaTutor.git
cd NexaTutor

py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"

cd web
npm install --legacy-peer-deps
cd ..

deeptutor init
deeptutor start
```

当前兼容 CLI 仍叫 `deeptutor`。启动器会自动寻找可用端口；默认后端端口通常为 `8001`，前端端口通常为 `3782`，端口被占用时可能自动变化。

前端开发模式：

```powershell
deeptutor start --dev
```

只启动 API：

```powershell
deeptutor serve --port 8001
```

容器运行仍使用 DeepTutor 兼容镜像与 service 名，详见[容器运行指南](CONTAINERIZATION.md#临时本地-codex-oauth-桥接)。公网部署、PocketBase 与 Sidecar 属于迁移期遗留能力，不是 NexaTutor 最终目标。

## 配置与本地数据

项目根目录 `.env` 不作为运行时配置来源。设置保存在：

```text
data/user/settings/
```

主要配置包括：

- LLM Provider、Model、API Key、Base URL。
- Embedding Provider、Model、API Key、Base URL。
- 搜索 Provider 与凭据。
- 文档解析、Chat、Tools、Memory、外观和本地端口。

请勿提交 `data/`、API Key、OAuth Token、运行日志、上传资料、知识库索引或前端构建缓存。

## 当前 CLI

当前可解析的顶层命令包括：

```text
deeptutor init
deeptutor start
deeptutor serve
deeptutor chat
deeptutor run
deeptutor kb
deeptutor session
deeptutor notebook
deeptutor memory
deeptutor config
```

迁移期仍可能显示 `partner`、`plugin`、`skill`、`provider`、`book` 等待裁剪命令。文档不再将这些入口描述为 NexaTutor Core。

常用示例：

```powershell
deeptutor run chat "解释傅里叶变换"
deeptutor run deep_solve "求解 x^2 = 4"
deeptutor run deep_research "整理一个主题的研究脉络" --config mode=report --config depth=2
deeptutor kb list
deeptutor session list
deeptutor notebook list
deeptutor memory show
```

Provider 认证兼容入口：`openai-codex` 执行 OAuth 登录，`github-copilot` 只校验已有 Copilot 认证。该入口将在 Provider 收缩阶段单独处理。

## 开发验证

Python 快速检查：

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -B -c "from deeptutor.runtime.orchestrator import ChatOrchestrator; from deeptutor.api.main import app; print(len(app.routes))"
python -m pytest -p no:cacheprovider -q tests/runtime/registry tests/core/test_capabilities_runtime.py
```

前端检查：

```powershell
cd web
npm run i18n:parity
npm run test:node
npm run lint
npm run build
```

完整测试和干净环境 E2E 应在功能域完成时执行，不能只依赖开发机上已有的依赖与缓存。

## 安全边界

- 默认面向个人、本地运行，服务最终应只监听 `127.0.0.1`。
- API Key 不应进入前端日志、普通 API 响应或普通后端日志。
- 通用 `exec` 将被删除；`code_execution` 只有在形成可靠限制后才作为可关闭的 Core 能力保留。
- 当前 Windows 受限 subprocess 不是强安全沙箱。没有可靠隔离后端时，不应向不受信任用户开放代码执行。
- 不自动删除历史 Partner、Book、Agent、OAuth 或旧 RAG Engine 数据。

## 文档说明

- 项目文档只维护简体中文版本。
- `deeptutor/**/prompts/{en,zh}` 属于运行时语言资源，不是项目文档翻译，必须按功能需要保留。
- `assets/releases/` 保存 DeepTutor 上游历史发布记录，只用于来源追溯，不代表 NexaTutor 当前功能。
- 第三方许可证与声明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 上游与许可证

NexaTutor 以 HKUDS/DeepTutor 为技术底座，采用选择性移植安全修复、严重 Bug 修复、RAG 改进、模型兼容和文档解析修复的维护策略，不再周期性全量合并上游。

上游来源、基线提交和本地改造边界记录在 [UPSTREAM_BASE.md](UPSTREAM_BASE.md)。许可证与引用信息保留原仓库声明；裁剪过程不得删除第三方通知或掩盖项目来源。
