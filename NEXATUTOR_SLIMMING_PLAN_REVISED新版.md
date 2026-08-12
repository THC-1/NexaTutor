# NexaTutor 项目精简与裁剪方案（执行版）

> 文档状态：正式执行基准
> 基础项目：DeepTutor
> 目标项目名：NexaTutor
> 目标场景：个人本地运行、接入云端 API、数据默认保存在本地
> 改造方式：以当前本地 DeepTutor 代码为基线，逐步裁剪并演化为独立项目
> 执行节奏：单功能、小提交、逐步验证、缓慢推进
> 最后修订：2026-08-12

本文件是 NexaTutor 裁剪工作的唯一执行基准。旧版方案仅作为历史参考；如果后续决策发生变化，应先更新本文件，再实施代码改动。

---

## 0. 当前执行状态（2026-08-12）

- P0 仓库级安全与发布收口已完成：`serve` 默认绑定 `127.0.0.1`，Auth off 不再接受任意 CORS Origin，原 PyPI / Docker Release workflows 已暂停，`web/.next-deeptutor` 已停止跟踪并忽略。
- Partners 已按“取消注册 → 取消调用 → 删除 UI → 删除后端实现 → 删除依赖”完整裁剪；Router、CLI、Tools、Partner Subagent backend、调用点、UI、实现、依赖和正向测试均已移除。
- P2 决策变更：**My Agents / Subagents 保留**。后续只移除 Partner、MCP、CLI Apps、在线 Hub、Auth / Multi-user 等对它们的外部注入和多用户耦合，保护 `/agents`、`/settings/agents`、`/api/v1/subagents`、`consult_subagent` 与本地 Agent backend。
- P3 已完成：MCP、CLI Apps 扩展系统、Deferred Tools / `load_tools`、在线 Skill Hub、Plugin Management Router / UI / CLI 和专用依赖均已删除；旧 grant 中的 `mcp_tools` / `cli_apps` 字段会被忽略，不能重新激活功能。
- P4 已完成：账号 Auth / Admin / Multi-user / Grants 的注册、调用、UI、实现与专属依赖均已删除，运行边界已收敛为 `LocalUserContext → LocalWorkspace → data/user`；OpenAI Codex OAuth 与 My Agents / Subagents 继续保留。
- P5 已完成：PocketBase / 外部集成 Sidecar 与公网部署能力已按五步裁剪；Session 固定使用本地 SQLite，公网配置收敛为 loopback，Next 同源代理、Sandbox Runner、Codex OAuth 与 My Agents / Subagents 继续保留。
- P6 已完成：Book / Living Book、Videogen、Math Animator / Manim、GeoGebra、Cron、Built-in GitHub / Brainstorm / Reason / Exec 已按单功能五步删除；受限 Code Execution 已完成 Python-only、显式启用、SYSTEM isolation、argv-only 安全收敛。
- P7 已完成：RAG Registry 只保留 `llamaindex`，知识库产品路径收敛为 Parse → Chunk → Embedding → FAISS + BM25 Hybrid → Citation；非标准引擎均按五步删除。下一步为 P8 Provider 收缩。
- P8 已完成：LLM 产品入口收敛为六类，Runtime Registry 为六类加独立 `openai_codex`；29 个非目标 Spec、GitHub Copilot / Azure 专用实现、Copilot CLI 与专属依赖已删除。Provider Key 改为普通响应不可读的 write-only 三态更新。下一步为 P9 Memory UI 精简。

---

## 1. 项目定位

NexaTutor 是面向个人用户的本地 AI 学习工作台。

应用前后端运行在用户自己的计算机上，通过云端 API 使用大语言模型、Embedding 和搜索服务；会话、资料、知识库、笔记、题库与学习记录默认保存在本地。

产品只围绕以下核心链路建设：

```text
本地启动
  → 配置云端 API
  → 对话 / 解题 / 研究 / 练习
  → 上传资料并建立知识库
  → 保存笔记、题目和学习进度
  → 重启后继续恢复原有学习状态
```

NexaTutor 不再定位为：

- 多用户平台
- IM 机器人平台
- 面向多用户或远程编排的 Agent 调度平台
- 插件市场
- 通用自动化平台
- 多 Provider 聚合平台
- 复杂 RAG 实验平台

后续任何新功能是否进入 Core，统一以以下问题判断：

1. 是否直接服务于个人学习？
2. 是否进入主要学习链路？
3. 长期维护成本是否值得？

至少两个问题明确为“是”，才应进入 Core；否则进入 Optional 或不做。

---

## 2. 新名称

### 2.1 推荐名称

- 产品名：**NexaTutor**
- 中文说明名：**NexaTutor 个人学习助手**
- 名称含义：`Nexa` 取自 nexus，表示连接模型、资料、知识库、笔记与学习路径；`Tutor` 保留学习助手定位。
- 推荐 Python 分发名：`nexatutor`
- 目标 Python 顶级包名：`nexatutor`（延后决策，第一阶段可继续使用内部 namespace `deeptutor`）
- 推荐 CLI：`nexatutor`
- 推荐默认数据目录：`data/user`
- 推荐默认本地用户 ID：`local`

正式公开发布前，应单独核验：

- GitHub 仓库名
- PyPI 包名
- npm 包名（如涉及）
- 域名
- 商标
- 社交媒体名称

### 2.2 改名时机

项目改名安排在功能裁剪和核心回归测试完成之后。

功能删除和机械重命名不得混在同一批提交中，以减少：

- Diff 噪声
- 回归定位难度
- Git blame 失真
- Merge / cherry-pick 冲突
- Import 问题

---

## 3. 本地基线策略

由于项目已经拉取到本地并准备直接修改，不要求回退或对齐某个特定官方 Release / Commit。

真正需要冻结的是：

> **NexaTutor 开始改造时的当前本地代码状态。**

### 3.1 建立基线

在改造开始前记录：

```bash
git status
git rev-parse HEAD
git branch --show-current
git remote -v
```

如果当前工作区无未提交改动：

```bash
git switch -c nexatutor
git tag nexatutor-baseline
```

如果当前已经有未提交修改，禁止直接执行 `git add -A`。先把修改分为：

- 源码与测试
- 方案和项目文档
- 用户数据与凭据
- 构建产物
- 缓存与临时文件
- 与本次改造无关的已有修改

基线建立时，`web/.next-deeptutor/` 曾存在大量被 Git 跟踪的构建产物。当前已经作为独立仓库卫生变更停止跟踪，并由 `.gitignore` 保持忽略；后续仍不能把本地生成物混入源码提交。

先记录：

```bash
git diff > before-nexatutor-baseline.patch
git status --short
git diff --stat
git diff --name-only
```

再仅暂存人工确认过的文件：

```bash
git add <confirmed-source-or-document-paths>
git commit -m "chore: establish NexaTutor baseline"
git tag nexatutor-baseline
```

不得把 API Key、运行数据、缓存、`node_modules`、`.next-deeptutor` 构建输出或其他无关改动提交到 baseline。

### 3.2 建议新增文件

```text
UPSTREAM_BASE.md
```

当前仓库的 `.gitignore` 忽略整个 `/docs/`，因此基线来源文件默认放在仓库根目录。只有在明确调整忽略规则后，才可改放到 `docs/`。

内容至少包括：

```text
Source Project: HKUDS/DeepTutor
Local Baseline Commit: <git rev-parse HEAD>
Baseline Tag: nexatutor-baseline
Baseline Date: <date>
Branch: <branch>
Local Changes Before Baseline: yes/no
Upstream Remote: <url>
```

### 3.3 目的

这个基线用于：

- 回滚
- Diff 对比
- 查找裁剪造成的回归
- 后续选择性同步上游修复
- 保留项目来源可追溯性

---

## 4. 裁剪总原则

### 4.1 强制执行顺序

每一个待删除功能域都必须严格执行：

```text
1. 取消注册
2. 取消调用
3. 删除 UI
4. 删除后端实现
5. 删除依赖
```

不得：

- 先删依赖
- 先删目录
- 在仍有运行时调用时删除实现
- 在同一个提交里顺手大规模重构
- 在裁剪阶段同时进行全项目改名

### 4.2 核心施工原则

> 先让功能消失，再让代码消失；
> 先让依赖没人用，再让依赖消失；
> 先完成裁剪，再做重构；
> 先完成重构，再改名字。

### 4.3 基本约束

1. 每完成一步，项目应保持可启动，或至少通过对应层的静态检查。
2. 一次只裁剪一个相对独立的功能域。
3. 不在裁剪提交中顺便重构核心业务。
4. 不自动删除用户已有数据。
5. 旧配置出现已删除字段时应忽略、迁移或给出明确提示，不能无理由阻止启动。
6. 依赖只能在所有引用与实现删除后清理。
7. 每个功能域的五个步骤原则上拆成独立提交。
8. 所有高风险删除必须有可回滚提交点。
9. 任何公共 Schema、类型、工具协议、路径服务都应先确认是否被保留功能复用。
10. 禁止把多个大功能域集中删除；一个功能域验收完成后，才能开始下一个。
11. 每个批次允许继续细分为更小子批次，宁可多提交，不做“大爆炸式”删除。
12. 如果某一步无法独立验证，应先补测试或观测点，而不是继续向后删除。

---

## 5. 功能范围

所有功能分为：

- Core
- Optional
- Remove

---

## 5.1 Core：默认保留

### 基础运行

- 本地 Web 应用
- FastAPI 后端
- WebSocket / 流式通信
- 单用户本地工作区
- 会话创建
- 会话恢复
- 会话重命名
- 会话删除
- 回答重新生成
- 本地配置
- API 使用量统计
- API 成本统计

### CLI

保留 NexaTutor CLI，并使其与单用户 Core 能力一致。保留的主要入口：

```text
nexatutor init
nexatutor start
nexatutor serve
nexatutor chat
nexatutor run
nexatutor kb
nexatutor session
nexatutor notebook
nexatutor memory
nexatutor config
```

CLI 仍可支持交互模式和结构化 NDJSON 输出，但不能继续暴露已删除功能。以下命令或子命令随对应功能删除：

```text
partner
在线 skill market / login / publish / update
MCP 管理
CLI Apps 管理
已删除 Provider 的专用 OAuth 登录
Book 管理
```

必须区分：

- **NexaTutor CLI**：Core，保留。
- **CLI Apps 扩展系统**：Remove，完整删除。

### 模型与服务

保留产品层入口：

- OpenAI
- Anthropic
- Gemini
- DeepSeek
- OpenAI-compatible
- Anthropic-compatible

保留能力：

- LLM 独立配置
- Embedding 独立配置
- Search 独立配置
- API Key
- Base URL
- 模型名称
- API 连接测试
- 模型切换
- 错误提示
- Key 脱敏与日志保护

### 学习能力

- Chat
- Deep Solve
- Deep Research
- Quiz
- Mastery Path
- Visualize
- Mermaid
- SVG
- Chart.js
- HTML 可视化

### 资料与知识

- 文件上传
- PDF
- DOCX
- PPTX
- XLSX
- Markdown
- 纯文本
- 文档解析
- LlamaIndex
- FAISS
- BM25
- Hybrid Retrieval
- 云端 Embedding
- 来源
- 页码
- 引用
- 知识库创建
- 添加文件
- 删除文件
- 重建索引
- 搜索
- 知识库完整生命周期

### 学习沉淀

- Notebook
- Question Bank
- 简化版 Memory UI
- 基础 Persona
- 学习目标
- 学习进度

### 核心工具

保留：

```text
rag
kb_files
read_source
read_memory
write_memory
web_search
web_fetch
paper_search
ask_user
list_notebook
write_note
受限 code_execution
必要的 mastery 内部工具
必要的 solve 内部工具
必要的 quiz / grading 内部工具
```

工具最终归属：

| 工具 | 归属 | 处理方式 |
| --- | --- | --- |
| `rag` | Core | 保留 |
| `kb_files` | Core | 保留 |
| `read_source` | Core | 保留 |
| `read_memory` | Core | 保留 |
| `write_memory` | Core | 保留 |
| `web_search` | Core | 保留，后期可随 Research Pack 降级 |
| `web_fetch` | Core | 保留，后期可随 Research Pack 降级 |
| `paper_search` | Core | 保留，后期可随 Research Pack 降级 |
| `ask_user` | Core | 保留 |
| `list_notebook` | Core | 保留 |
| `write_note` | Core | 保留 |
| `code_execution` | Core / 默认可关闭 | 安全收敛后保留 |
| `read_skill` | Optional | 仅本地 Skill 启用时挂载 |
| `imagegen` | Optional | 默认关闭 |
| `brainstorm` | Remove | 普通 Chat 可完成相同目标 |
| `reason` | Remove | 能力并入 Chat / Deep Solve，不再二次调用专用 LLM |
| `load_tools` | Remove | 随 MCP 与 CLI Apps 扩展系统删除 |
| `exec` | Remove | 完整删除 |
| `github` | Remove | 完整删除 |
| `cron` | Remove | 完整删除 |
| `geogebra_analysis` | Remove | 完整删除 |
| `videogen` | Remove | 完整删除 |
| `consult_subagent` / Subagent 工具 | Core | 保留 My Agents；仅允许用户显式配置的本地 Agent |
| Partner 工具 | Remove | 随 Partners 删除 |

Quiz / Grading 当前主要由 Question Pipeline、API 与 Quiz Judge WebSocket 实现，不应误当成普通 Built-in Tool 删除或迁移。

### Preserve 与 Build 的边界

Core 中的目标分为两类：

#### Core Preserve

当前已经存在，裁剪过程中需要持续保护：

- Chat、Solve、Research、Quiz、Mastery Path、Visualize
- 会话、本地配置、文件上传、知识库、Notebook、Question Bank、Memory
- CLI、WebSocket、模型配置、RAG 与引用

#### Core Build

目标需要，但当前项目尚未形成完整产品能力，必须作为裁剪后的独立建设任务：

- 通用数据导入
- 通用数据导出
- 数据与隐私设置页
- 统一的使用量与成本页面
- 收敛后的 Python-only Code Execution 安全策略
- DeepTutor 旧数据一次性迁移器

Core Build 不得混入 Remove 功能的五步删除提交。当前 `/imports/chat-history` 主要服务外部聊天历史导入，是否继续作为 My Agents 的会话导入能力保留，需要在批次 2 单独核对；不能直接视为通用数据导入能力。

---

## 5.2 Optional：默认关闭或后续评估

- Co-Writer
- Obsidian 接入
- 本地 Skill 文件
- 图片生成
- STT
- TTS
- 高级 Memory 管理
- Deep Research Pack（后续可根据实际使用频率从 Core 降为 Optional）

Optional 功能必须满足：

- 不成为 Core 启动依赖
- 默认安装不要求额外大型依赖
- 默认 UI 可隐藏
- 可独立关闭
- 不影响核心测试链

---

## 5.3 Remove：完整删除

### 平台化功能

删除：

- 注册
- 登录
- JWT
- Cookie Auth
- 管理员后台
- Multi-User
- Grants
- 多用户审计
- 用户管理 UI

但注意：

> 不彻底删除“用户上下文”抽象。

保留一个固定：

```text
LocalUserContext
```

推荐：

```text
user_id = "local"
workspace = data/user
role = owner
```

目的：

- 减少原有 `user_id` / workspace / owner 依赖的大面积改写
- 保留资源归属与路径上下文
- 为输出文件、知识库、Notebook、Memory 提供统一作用域
- 避免删除多用户系统时破坏大量共享基础设施

`LocalUserContext` 不是单独增加一个 Dataclass 就算完成。当前 Core 仍大量使用 `multi_user.paths`、`context`、`identity`、`knowledge_access`、`tool_access`、`skill_access` 与 `model_access`。删除 Multi-User 前必须完成以下替换：

| 现有模块职责 | NexaTutor 替代职责 |
| --- | --- |
| `multi_user.context` | `LocalUserContext` |
| `multi_user.paths` | `LocalWorkspacePaths` |
| `multi_user.identity` | 固定 Local Identity |
| `multi_user.knowledge_access` | `LocalKnowledgeAccess` |
| `multi_user.model_access` | `LocalModelAccess` |
| `multi_user.tool_access` | 固定本地 Tool Policy |
| `multi_user.skill_access` | `LocalSkillAccess`，仅本地 Skill 启用时保留 |
| `multi_user.personal_models` | 随个人 OAuth Provider 删除 |
| `multi_user.partner_access` | 随 Partners 删除 |
| `multi_user.grants` | 删除 |
| `multi_user.audit` | 删除 |

迁移顺序：

```text
引入 LocalUserContext 与本地 Access / Path Adapter
  → 逐个迁移 Core 调用点
  → 为每个 Adapter 增加测试
  → 确认 Core 不再 import 对应 multi_user 模块
  → 取消 Auth / Multi-User 注册与调用
  → 删除平台化实现
```

### Partners / IM

删除：

- Partners
- Partner Memory
- Partner Workspace
- 飞书
- Telegram
- Slack
- Discord
- 钉钉
- QQ
- 企业微信
- WhatsApp
- Matrix
- Teams
- 其他 IM Channel
- Partner 专用工具

### My Agents / Subagents：保留并收敛边界

保留：

- My Agents
- Subagents
- `consult_subagent`
- 用户显式配置的本地 Claude Code、Codex、Gemini CLI、Kimi、OpenCode、MiMo 等 Agent Provider
- 与 My Agents 直接相关的本地会话查看与导入能力（批次 2 逐项核对）

边界：

- 不作为多用户、远程托管或在线市场能力
- 不允许旧 Partner、MCP、CLI Apps 或在线 Hub 配置隐式新增 Agent Provider
- 不自动启动用户未启用的 Agent 进程
- Partner 专用 Subagent Backend 与 `/api/v1/subagents/partners` 旁路仍随 Partners 删除；不得误删通用 Subagent 能力
- Agent 依赖只有在确认不再被保留 Provider 使用后才可删除

### 扩展生态

删除：

- MCP 完整运行时
- MCP Manager / Provider / Deferred Tools
- MCP Store
- MCP Router / API
- MCP OAuth 与 Secret Storage
- MCP 用户配置与设置
- MCP 前端页面、管理 UI 与 API Client
- MCP 相关启动 / 关闭钩子
- MCP 相关依赖
- CLI Apps 完整扩展运行时
- CLI Apps Store
- CLI Apps Installer / Runner / Provider
- CLI Apps 前端页面、管理 UI 与 API Client
- CLI Apps 相关依赖
- EduHub
- ClawHub
- Skill 在线搜索
- Skill 在线登录
- Skill 发布
- Skill 在线更新
- 插件管理 UI

MCP 不进入 Optional，也不保留隐藏开发入口。删除完成后，旧配置不得重新启用 MCP，运行时不得再构建 MCP Provider，Chat 不得再通过 Deferred Tools 或 `load_tools` 加载 MCP 工具。

NexaTutor CLI 属于 Core；这里删除的是“允许模型安装和调用第三方命令行程序”的 CLI Apps 扩展系统，不是删除项目自身 CLI。

如保留本地 Skill，仅支持：

- 手动导入
- 查看
- 启用
- 禁用
- 删除
- Chat 按需读取

### 非核心内容生产与高维护功能

删除：

- Book / Living Book
- 视频生成
- Manim
- GeoGebra 图形重建
- Cron
- GitHub Tool
- 通用 Exec Tool

保留：

- Mermaid
- SVG
- Chart.js
- HTML 可视化
- 受限 Code Execution
- Optional Co-Writer

### 高维护知识库引擎

删除：

- GraphRAG
- LightRAG
- LightRAG Server
- RAG-Anything
- PageIndex
- Tencent IMA

### 非目标模型入口

删除独立产品逻辑：

- Ollama
- vLLM
- LM Studio
- llama.cpp
- Lemonade
- OVMS
- GitHub Copilot OAuth
- Coding Plan Provider

OpenAI Codex OAuth 是 Core 保留的独立 Provider 登录能力，不在非目标模型入口删除范围内。

其他兼容 API 如确有需要，统一通过：

```text
OpenAI-compatible
或
Anthropic-compatible
```

接入。

### 部署与外部集成

删除：

- PocketBase（若最终确认 Core 无依赖）
- PocketBase / 外部集成 Sidecar
- 公网部署配置 UI
- 远程 OAuth 桥接
- 面向多用户的 CORS 配置
- 多用户反向代理配置
- 凭据共享配置

注意：不得把外部集成 Sidecar 与 `Sandbox Runner Sidecar` 混为一谈。后者当前属于 Code Execution 的隔离后端，在 Code Execution 新方案落地前不能顺带删除。

---

## 6. 推荐裁剪顺序

### 批次 0：建立本地基线

完成：

- Git baseline
- 当前 Python 依赖清单
- 当前 Node 依赖清单
- FastAPI 路由清单
- Capability 清单
- Tool 清单
- Provider 清单
- RAG Engine 清单
- 核心用户流程冒烟测试
- 干净环境安装脚本
- 脱敏旧配置样例
- 旧数据样例
- Feature → Dependency Matrix
- 清理或隔离被跟踪的 `.next-deeptutor` 构建产物变化
- 确认 baseline 不包含 API Key、运行数据、缓存与无关修改
- 建立 LocalUserContext 迁移矩阵
- 建立 Tool / Capability 最终归属矩阵

批次 0 本身继续拆成：

```text
0A Git 与工作区卫生
0B Registry / Router / Dependency 快照
0C Core Smoke
0D 旧数据样例与迁移边界
0E Feature → Dependency Matrix
```

每个子批次单独验收，不集中一次完成。

---

### 批次 1：Partners / IM

删除：

- Partners
- IM Channels
- Partner Runtime
- Partner Memory
- Partner Workspace

完成标志：

- 后端不启动任何 IM Channel
- 前端无 Partner 页面
- Chat 不挂载 Partner Tool
- 默认安装不包含 IM SDK

---

### 批次 2：My Agents / Subagents 保留与边界固化

本批次不再执行 Remove，而是保护并收敛现有本地 Agent 能力：

- 保留 My Agents、Subagents 与 `consult_subagent`
- 逐个核对本地 Agent Provider 的注册、进程生命周期、工作目录和权限边界
- 将 Partner 专用 Subagent Backend、MCP / CLI Apps 注入点与通用 Subagent 能力拆开
- 核对 Agent 会话查看与导入是否只服务本地 My Agents
- 记录保留 Provider 的必要依赖，避免后续依赖清洗误删

完成标志：

- Chat 可按用户显式配置调用 Subagent
- 未启用的 Agent 不自动启动
- Partner、MCP、CLI Apps 与在线 Hub 的旧配置不能隐式激活或注入 Agent
- Agent 工作目录、进程生命周期和错误处理有定向测试
- 保留的 Agent Provider 及其依赖有明确清单

---

### 批次 3：扩展市场

删除：

- MCP 全部运行时、配置、API、UI、Provider、OAuth、Secret 与依赖
- CLI Apps 全部扩展运行时、Store、Installer、Runner、Provider、UI 与依赖
- EduHub
- ClawHub
- Skill 发布 / 搜索 / 更新
- Plugin Management UI

本地 Skill 若保留，只保留文件级能力。

批次 3 拆分为：

```text
3A MCP 取消注册
3B MCP 取消调用与 Deferred Tool / load_tools 清理
3C MCP UI 删除
3D MCP Backend 删除
3E MCP 依赖删除与旧配置失效验证
3F CLI Apps 取消注册
3G CLI Apps 取消调用
3H CLI Apps UI 删除
3I CLI Apps Backend 删除
3J CLI Apps 依赖删除
3K EduHub / ClawHub 与在线 Skill 能力
```

NexaTutor CLI 不在此批次删除。

---

### 批次 4：Auth / Admin / Multi-user / Grants

删除：

- 登录 UI
- 注册 UI
- JWT
- Cookie Auth
- Admin
- Multi-user
- Grants
- 审计
- 用户管理

先引入固定：

```text
LocalUserContext
```

并完成 `LocalWorkspacePaths`、本地 Knowledge / Model / Tool / Skill Access Adapter 的迁移。只有 Core 调用点完成迁移后，才开始取消 Auth / Multi-User 注册。

批次 4 拆分为：

```text
4A LocalUserContext 与 Local Identity                         ✅
4B LocalWorkspacePaths                                       ✅
4C LocalKnowledgeAccess                                      ✅
4D LocalModelAccess                                          ✅
4E LocalToolPolicy / LocalSkillAccess                        ✅
4F Core 调用点迁移验证                                       ✅
4G Auth / Admin 取消注册与调用                               ✅
4H Auth UI 删除                                              ✅
4I Multi-User / Grants / Audit 后端删除                      ✅
4J Auth 与 Multi-User 依赖删除                               ✅
```

#### 4I / 4J 施工计划（2026-08-12）

继续按可回滚边界执行，不把后端实现、旧配置兼容和依赖删除混成一次修改：

```text
4I-1 生产引用清零
     - 证明除待删 Auth 实现外，Core 不再 import deeptutor.multi_user
     - 移除 launcher / runtime settings / network status 中的 Auth 激活调用
     - 旧 auth.json、环境变量和 Docker 参数不能重新启用登录态

4I-2 Auth 实现删除
     - 删除未注册的 account Auth Router 与 Auth service
     - 删除 JWT、Cookie、密码、Profile、Avatar、用户管理实现
     - 独立保护 OpenAI Codex OAuth callback / service

4I-3 Multi-User 平台实现删除
     - 删除 context / identity / paths / grants / audit / router
     - 删除 knowledge/model/tool/skill/personal access 旧 Adapter
     - 保证 LocalUserContext → LocalWorkspace → data/user 是唯一运行路径

4I-4 测试与兼容面清理
     - 删除只验证账号隔离、Grant、Admin、JWT、Cookie 的测试
     - 将仍保护 Core 的测试改写为 LocalWorkspace 语义
     - 增加旧配置、动态 import、HTTP/WS 路由不能复活功能的负断言

4J-1 依赖归属证明
     - 检查运行时、测试、CLI、Docker、动态 import、optional extra
     - 区分账号 Auth 专属依赖与 Codex OAuth / Core 共享依赖

4J-2 删除专属依赖并锁文件验收
     - 删除 JWT / password hash / account Auth 专属包与配置
     - 不删除 Codex OAuth、My Agents 或其他 Core 仍需依赖
     - 干净 import、FastAPI startup、CLI、Python 与前端构建通过
```

完成证据（2026-08-12）：账号 Auth / Multi-user 实现与专属依赖已清零；旧配置无法激活；P4 后端集成 256 passed / 1 skipped；前端 Node 271 passed、i18n / lint / production build 通过。下一步进入批次 5，只先做 PocketBase 与外部集成 Sidecar 的 Core 依赖盘点。

并行施工约束：Agent 可并行做只读盘点或互不重叠的文件域；共享注册点、依赖文件、计划与交接文档只由主 Agent 修改，避免覆盖工作区已有变更。

完成标志：

- 启动后直接进入首页
- 不创建登录态
- 不发认证 Cookie
- 数据统一进入 `data/user`
- 所有原有 owner / user scope 能通过 LocalUserContext 正常工作
- 服务默认只监听 `127.0.0.1`

---

### 批次 5：PocketBase / 外部集成 Sidecar / 公网部署能力

检查其是否仍被：

- Chat
- Knowledge
- Notebook
- Question Bank
- Memory
- Mastery Path

依赖。

若无 Core 依赖，再删除。

不要仅因为“看起来属于旧平台”就直接删除。

此批次不得删除 Sandbox Runner Sidecar、Sandbox Service、资源限制、Artifact 收集或 Code Execution 仍在使用的隔离基础设施。

#### 5A 只读依赖盘点（2026-08-12）

PocketBase 当前不是 Core 的必需存储，但仍可被旧配置激活，不能跳过取消注册与取消调用直接删除实现：

| Core 域 | 当前实际依赖 | 本地替代 / 结论 |
| --- | --- | --- |
| Chat / Session | 盘点时 `get_session_store()` 会在 `integrations.pocketbase_url` 非空时选择 `PocketBaseSessionStore`；Turn Runtime、Session API、Dashboard 与 App Facade 使用该选择结果 | SQLite Session Store 是默认零配置路径；5B-1 已取消 PocketBase backend 选择 |
| Knowledge | `KnowledgeManager` 会镜像 KB metadata，上传 Router 会镜像附件；均为 best-effort PocketBase 调用 | 本地 `kb_config.json`、文件和索引明确是 source of truth；取消镜像调用不改变 Core 主路径 |
| Notebook | 无 PocketBase import 或调用 | `data/user/workspace/notebook/*.json` 本地持久化 |
| Question Bank | 无 PocketBase import；Router 显式使用 `get_sqlite_session_store()` | 本地 `chat_history.db` 持久化 |
| Memory | 无 PocketBase import；Memory 文档、trace、snapshot 均走 LocalWorkspace 文件，Chat / Quiz snapshot 显式读取本地 SQLite | 不依赖 PocketBase；带有 `sidecar` 名称的 `*.meta.json` 是本地伴随文件，不是外部服务 |
| Mastery Path | 学习进度由 `LearningStore` 保存为本地 JSON；取消 active turn 时会经 Turn Runtime 间接使用当前 Session Store | 先固定 Session Store 为 SQLite，即可解除这条传递依赖 |

注册、调用、UI、实现、依赖与共享基础设施盘点：

- 注册 / 激活：Session Store 条件选择、FastAPI lifespan health ping、Docker / Podman Compose `pocketbase` service 与 `depends_on`、runtime settings / env 导出。
- 调用：Knowledge metadata / attachment 镜像、PocketBase session CRUD / turn event persistence、Compose wrapper 端口渲染和初始化脚本。
- UI：没有 PocketBase 专属页面或前端 API client；`integrations.json` 当前仅由后端、脚本和 Compose wrapper 使用。
- 实现：`services/pocketbase_client.py`、`services/session/pocketbase_store.py`、`scripts/pb_setup.py` 及 PocketBase 专属测试。
- 依赖：`pocketbase>=0.12.0` 同时出现在主依赖、`server` extra 与 `requirements/server.txt`，只能在实现和动态 import 清零后删除。
- Sidecar 分类：当前 Compose 中唯一非沙箱外部 Sidecar 是 PocketBase。Research Note Agent、Memory / RAG `*.meta.json` 等只是内部代理或本地伴随文件；`sandbox-runner` 是 Code Execution 安全基础设施，明确保留。
- 公网部署边界：可删除的是 `next_public_api_base_external`、用户自定义远程 CORS Origin、远程 Docker / 反向代理 UI 与配置；本地端口、固定 loopback CORS、Next.js 到 FastAPI 的同源代理继续保留。
- Codex OAuth 边界：保留 callback Router、OAuth service、前端 callback rewrite 与临时本地 callback overlay；不得把它们当作公网部署或外部 Sidecar 删除。

#### 5B 小步施工顺序

严格按一个负断言对应一个微步骤推进：

```text
5B-1 取消 PocketBase Session Store 条件注册；旧 integrations 配置也只能得到 SQLite  ✅
5B-2 取消 FastAPI PocketBase startup health hook  ✅
5B-3 取消 Compose PocketBase service / depends_on 注册和 wrapper 端口注入  ✅
5C-1 取消 Knowledge metadata 镜像调用  ✅
5C-2 取消 Knowledge attachment 镜像调用  ✅
5C-3 取消 runtime settings / env 对 PocketBase 的读取、导出和旧配置激活  ✅
5D    UI 负断言（PocketBase 当前无专属 UI）  ✅
5E-1 删除 PocketBase client、Session Store、setup script 和专属测试  ✅
5E-2 删除 PocketBase Python 依赖并执行依赖验证  ✅
5F-1 单独取消公网 API base 与自定义远程 CORS 配置注册 / 调用  ✅
5F-2 将 Network UI 收敛为本地端口、localhost 状态与现有 Chat timeout  ✅
5F-3 删除公网部署专属后端兼容、Compose / 文档配置与专属依赖  ✅
```

PocketBase 完成五步前不开始公网部署域；任何步骤均不得修改或删除 `Dockerfile.runner`、`deeptutor/services/sandbox/**`、`sandbox-runner` service、Codex OAuth 或 My Agents / Subagents。

5B-1 验证证据（2026-08-12）：负断言在修改前准确选中 `PocketBaseSessionStore` 并失败；修改后该断言通过，相关 Turn Runtime / WebSocket / Notebook 组合回归 71 passed，FastAPI import 与 SQLite store smoke 通过。完整 Session 目录另有 1 个可独立复现的既有 SQLite 旧路径迁移失败，不属于本步骤修改范围。

P5 完成证据（2026-08-12）：PocketBase 五步门禁 12 passed，公网部署 / 配置 / launcher / Compose 与 Codex callback 定向回归 107 passed，Codex OAuth / Subagents 保护回归 127 passed；扩大 Python 定向回归 681 passed，仅有同一既有 SQLite 迁移失败。排除无法在 Windows 收集的 Linux runner 文件后，全量 Python 为 2612 passed / 13 skipped / 12 failed；失败均是既有 Windows 编码、路径分隔、POSIX `sleep` / `resource` 与 SQLite 旧路径迁移差异。前端 Node 271/271、i18n parity、lint 0 error（34 条既有 warning）及 production build 均通过；`pip check` 无破损依赖。Sandbox 实现未修改。

---

### 批次 6：Book / 多媒体 / 高权限工具

删除：

- Book
- Living Book
- 视频生成
- Manim
- GeoGebra
- Cron
- GitHub Tool
- 通用 Exec

保留：

- Mermaid
- SVG
- Chart.js
- HTML
- 受限 Code Execution

批次 6 必须按单功能拆分：

```text
6A Book / Living Book  ✅
6B Video / videogen  ✅
6C Math Animator / Manim  ✅
6D GeoGebra  ✅
6E Cron  ✅
6F GitHub Tool  ✅
6G Brainstorm Tool  ✅
6H Reason Tool  ✅
6I 通用 Exec  ✅
```

每个子批次分别执行“取消注册 → 取消调用 → 删除 UI → 删除后端 → 删除依赖”，不能把 Book、多媒体和工具集中删除。

### 批次 6J：Code Execution 安全收敛

这不是删除批次，而是 Core Build。只有在通用 Exec 清理完成、Sandbox 共享依赖明确后再实施。

目标：

- 默认关闭，由用户明确启用
- 第一版仅支持 Python
- 固定工作目录
- 禁止 Shell 入口
- 禁止直接提供任意命令字符串
- 明确网络、文件、时间、输出和进程限制
- Windows 本地运行时明确使用哪一种隔离后端
- 没有可靠隔离后端时保持不可用，而不是静默降级

6J 已完成：默认关闭并由用户显式启用，仅支持 Python；工具使用 argv 调用且不接受任意 Shell 命令；只有健康且声明 `argv-v1` 的 SYSTEM runner 才能激活，旧 runner 与 Windows 裸机 subprocess 均失败关闭。runner 仅挂载单用户 workspace，位于 internal network 且无宿主端口；资源限制、Quota 与 Artifact 收集继续保留。

P6 完成证据（2026-08-12）：各域负断言均在修改前准确失败，完成后 P6 总门禁 39 passed；Registry / Router / CLI / Core / Codex OAuth / My Agents / Subagents 整合回归 555 passed / 2 skipped。前端 i18n parity、Node 265/265、lint 0 error（27 条既有 warning）和 production build 均通过；`pip check` 无破损依赖。排除 Windows 无法收集的 Linux runner 文件后，全量 Python 为 2581 passed / 10 skipped / 9 failed，失败均是已知 Windows 路径分隔、POSIX `sleep` / `resource` 或既有 SQLite 迁移差异。`data/` 无 Git 状态变更。

---

### 批次 7：知识库引擎收缩

> 状态：✅ 已完成（2026-08-12）

保留唯一标准路径：

```text
Parse
  ↓
Chunk
  ↓
Embedding
  ↓
FAISS
+
BM25
  ↓
Hybrid Retrieval
  ↓
RAG Answer
  ↓
Citation
```

用户界面不再暴露：

```text
Choose RAG Engine
```

只展示：

```text
创建知识库
```

删除：

- GraphRAG
- LightRAG
- PageIndex
- Tencent IMA
- 其他已列 Remove 的 RAG Engine

完成标志：

- 创建知识库只有一条主流程
- 普通 PDF 可以上传
- 可以解析
- 可以索引
- 可以搜索
- 可以 RAG 问答
- 可以显示页码 / 引用
- 删除文件与重建索引正常

P7 完成证据（2026-08-12）：删除与标准路径门禁 26 passed；Knowledge / RAG / Chat / Question / Capabilities / Memory 扩大回归 481 passed / 1 skipped。标准写路径测试实际产出 FAISS index 与 BM25 sidecar，检索使用 reciprocal-rank fusion；普通 PDF 的页码 metadata 已贯通到 chunk source 与 Chat citation UI。前端 i18n parity、Node 266/266、lint 0 error（27 条既有 warning）及 production build 均通过；`pip check` 无破损依赖。排除 Windows 无法收集的 Linux runner 文件后，全量 Python 为 2444 passed / 9 skipped / 8 failed，失败均为已知 Windows 路径分隔、POSIX `sleep` / `resource` 或既有 SQLite 迁移差异。旧设置、索引和远程 pointer 未自动删除或改写，`data/` 无 Git 状态变更。

Visualize 不随 Manim 删除。保留 `visualize` Capability 及 Mermaid、SVG、Chart.js、HTML 路径，只移除 Manim 路由、Math Animator 调用与相关配置。

---

### 批次 8：Provider 收缩

> 状态：✅ 已完成（2026-08-12）

产品层只保留：

- OpenAI
- Anthropic
- Gemini
- DeepSeek
- OpenAI-compatible
- Anthropic-compatible

最终用户只需要理解：

```text
Provider
Model
API Key
Base URL
```

保留：

- LLM 独立配置
- Embedding 独立配置
- Search 独立配置
- Connection Test

安全要求：

- API Key 不进入普通接口响应
- API Key 不进入前端日志
- API Key 不进入后端普通日志
- 错误提示不得回显完整 Key

Provider 收缩分两阶段：

```text
8A 产品层收敛
   - UI 只展示六类入口
   - 统一 API Key / Base URL / Model 配置体验
   - 删除本地模型与专用 OAuth UI

8B Runtime Adapter 清理
   - 逐一确认兼容网关的参数转换是否仍被使用
   - 确认 Embedding / Search 不依赖待删 Adapter
   - 仅删除无 Core 引用的 Provider Spec 与专用实现
```

不能把“UI 不显示”直接等价为“立即删除全部内部兼容元数据”。

P8 实际完成边界：

- 产品下拉与 CLI 初始化只展示 OpenAI、Anthropic、Gemini、DeepSeek、OpenAI-compatible、Anthropic-compatible；OpenAI Codex 作为独立 OAuth Core 保留。
- LLM Runtime Spec 从 36 项减为 7 项；旧非目标 binding 不修改原始 `model_catalog.json`，运行时只归一到 `custom` 或 `custom_anthropic`，不能复活专用 Adapter。
- 删除 GitHub Copilot、Azure OpenAI 的专用 LLM Provider、动态 import、Agentic 分支与 Copilot CLI；删除仅由 Copilot 使用的 `oauth-cli-kit`。
- 共享 OpenAI-compatible / Anthropic-compatible、模型级 Qwen / DeepSeek 推理与视觉能力继续保留，避免兼容端点退化。
- Embedding、Search、My Agents / Subagents 分别为独立 Registry；Aliyun Embedding、Perplexity Search 和六个本地 Agent backend 不属于本批删除范围。
- Settings / Catalog 普通响应不再回显明文 API Key；前端通过 `api_key_set` 显示状态，空值保留、显式 clear、非空替换，Connection Test 在后端内存合并已存密钥。

P8 完成证据（2026-08-12）：定向与 LLM 组合回归 246 passed；Chat / Knowledge / Notebook / Question / Memory / Mastery / Codex OAuth / Subagents 扩大回归 762 passed / 2 skipped。前端 i18n parity、Node 269/269、lint 0 error（26 条既有 warning）及 production build 均通过；`pip check` 无破损依赖。排除 Windows 无法收集的 Linux runner 文件后，全量 Python 为 2211 passed / 9 skipped / 8 failed，失败均为 P7 已知 Windows 路径分隔、POSIX `sleep` / `resource` 或 SQLite 迁移差异。未自动删除或改写用户历史设置、索引和数据。

---

### 批次 9：Memory UI 与设置精简

完成证据（2026-08-12）：P9 保留 L1 / L2 / L3 技术层级展示，但将默认首页改为用户语义入口：用户偏好、学习目标/画像、当前知识水平、最近学习内容、主动保存的长期记忆。Memory Graph、手工 Consolidator Run、Budget / Audit / Chunking / Reference 参数不再出现在默认产品入口；旧 Graph 路由兼容重定向到 `/memory`。未修改 Memory Backend、Router、数据模型、Consolidation、历史 Markdown 或用户数据。新增前端契约测试，Memory 后端与 resolver 回归 124 passed。

第一阶段：

> 只简化 UI 与配置暴露，不重写底层 Memory 数据模型。

用户只看到：

```text
我的记忆
├── 用户偏好
├── 学习目标
├── 当前知识水平
├── 最近学习内容
└── 主动保存的长期记忆
```

默认隐藏：

- L1 / L2 / L3 技术结构
- Memory Graph
- Consolidator Budget
- 多 Surface 审计参数
- 内部调度细节

待 NexaTutor 稳定后，如确认原 Memory Backend 过重，再单独启动：

```text
refactor(memory)
```

不得与裁剪混在同一阶段。

---

### 批次 10：设置与导航收口

完成证据（2026-08-12）：主导航收敛为对话、知识库、学习空间、写作（Optional）、设置；Memory 与 My Agents 迁入学习空间个性化入口，原 `/memory`、`/agents` 路由继续保留。Settings Hub 隐藏 Network、image、stt、tts 独立入口，保留其兼容页面/API/运行时；`/settings/status` 与 `/settings/mineru` 继续重定向，Settings Hub 保留状态条。Models 仅默认展示 LLM、Embedding、Search；Chat 与工具保留 Tools、Capabilities、Attachments 与本地 Agents 配置。MinerU 保留为可选文档解析实现，不能因默认隐藏而删除。P10 契约、Node 275 passed、i18n parity、lint 0 error、production build、TypeScript、pip check、API/Memory/Settings/Config 定向回归 219 passed 均通过。

P11 边界：只在运行时、测试、CLI、动态 import、optional extra 与构建引用全部清零后清洗依赖；不得删除 Memory、MinerU、voice/image、Sandbox、My Agents/Subagents 或 Codex OAuth 的共享依赖。

最终主导航：

```text
NexaTutor
├── 对话
├── 知识库
├── 学习空间
│   ├── 笔记
│   ├── 题库
│   └── 学习路径
├── 写作（Optional）
└── 设置
```

设置页最终只保留：

- 模型 API
- Embedding
- 网络搜索
- 文档解析
- Chat 与工具
- Memory
- 外观
- 数据与隐私
- 使用量与成本

现有页面处理表：

| 当前页面 | 目标处理 |
| --- | --- |
| `/profile` | 随 Auth 删除 |
| `/playground` | Remove |
| `/settings/network` | 收敛为本地端口与 localhost 状态，复杂公网配置删除 |
| `/settings/attachments` | 合并到“数据与隐私”或“Chat 与工具” |
| `/settings/capabilities` | 合并到“Chat 与工具” |
| `/settings/status` | 合并为设置首页状态条 |
| `/settings/mineru` | 默认 Remove；如保留托管解析则改为 Optional 并单独评估 |
| `/settings/image` | Optional，默认隐藏 |
| `/settings/stt` | Optional，默认隐藏 |
| `/settings/tts` | Optional，默认隐藏 |
| `/settings/video` | Remove |
| `/memory/*` 高级页面 | 默认隐藏，底层数据暂保留 |
| Persona | 放入“学习空间 → 个性化” |
| 本地 Skill | Optional，放入“学习空间 → 个性化” |

“我的记忆”第一阶段继续保留独立入口或放入“学习空间 → 个性化”；正式删除现有 Memory 顶级入口前，必须先完成替代入口，不能让用户失去查看与编辑记忆的能力。

---

### 批次 11：依赖最终清洗

完成证据（2026-08-12）：Feature → Dependency Matrix 已记录于 `NEXATUTOR_HANDOFF.md`。独立 CLI wheel 删除零引用 `nest_asyncio`，补齐保留的本地 Agent 模型同步依赖 `pyte`；requirements 同步。其余声明均有 Core、Optional 或共享调用证据，未为追求数量误删。P11 定向 73 passed；扩大 Python 2298 passed / 9 skipped / 8 个既有 Windows/POSIX/SQLite 差异；前端 275 passed、i18n、lint 0 error、build、pip check、compileall 通过。

建立并维护：

```text
Feature → Dependency Matrix
```

例如：

```text
Partners
├── <IM SDK>
├── <channel SDK>
└── <shared packages>

My Agents（保留）
├── <terminal / PTY packages：按保留 Provider 保护>
├── <OAuth packages：逐项判断本地 Agent 是否需要>
└── <agent integration packages：记录为保留依赖>

Auth
├── <JWT package>
├── <hash package>
└── <auth storage package>

MCP
├── mcp client / transport packages
├── OAuth / secret helpers
├── deferred-tool provider wiring
└── MCP-only networking packages

CLI Apps
├── installer / catalog dependencies
├── executable discovery and runner wiring
└── CLI Apps-only sandbox integration
```

删除依赖前必须确认：

1. 无运行时引用
2. 无测试引用
3. 无构建引用
4. 无 CLI 引用
5. 无动态 import
6. 无 optional extra 间接引用

检查：

- `pyproject.toml`
- `requirements/*.txt`
- `Dockerfile*`
- Compose
- `web/package.json`
- Python Lock
- Node Lock
- CI
- 安装脚本
- Optional Extras

---

### 批次 12：项目改名

第一层完成证据（2026-08-12）：分发名与正式 CLI 为 `nexatutor`；旧 `deeptutor` CLI 是带迁移提示的单实现转发。前端 metadata、OpenAPI、Docker/Compose、Logger、User-Agent、文档和暂停的发布目标均切换到 NexaTutor。环境变量采用 `NEXATUTOR_*` 优先、仍活跃 `DEEPTUTOR_*` 单向 fallback；已删除 Auth 变量不建立新别名。数据根 `data/user` 不迁移。第二层 `deeptutor` → `nexatutor` Python 顶级 namespace 继续延后。

所有 Core 稳定后再进行：

```text
DeepTutor
↓
NexaTutor
```

改名范围：

- `pyproject.toml`
- Python 顶级包
- CLI
- 前端 package metadata
- 页面标题
- Logo
- favicon
- OpenAPI 标题
- 环境变量前缀
- Logger 名称
- Docker 镜像
- Compose 服务名
- README
- 文档
- CI
- 发布脚本
- 制品名
- User-Agent

改名分两层进行：

#### 第一层：必须完成

- 产品品牌
- Python 分发名
- CLI 命令
- 前端 metadata
- 页面标题、Logo、favicon
- 文档、制品、Docker 镜像和 User-Agent

#### 第二层：延后决策

- Python 顶级包 `deeptutor` → `nexatutor`

顶级包改名会产生大面积机械 Diff，并显著提高后续移植上游修复的成本。第一阶段允许产品、分发包和 CLI 已使用 NexaTutor，但内部 Python namespace 暂时保持 `deeptutor`。只有项目稳定、上游同步策略经过验证后，再单独决定是否执行顶级包改名。

迁移期可短暂保留：

```text
deeptutor → 显示迁移提示并转发到 nexatutor
nexatutor → 正式入口
```

旧入口只保留一个明确版本周期。

---

## 7. 每个功能域的标准裁剪流程

### 7.0 小步施工门禁

开始任一功能域前必须满足：

1. 上一个功能域已通过对应 Smoke。
2. 工作区状态已记录，未混入上一批残留修改。
3. 本批只处理一个可命名、可回滚的目标。
4. 已列出注册点、调用点、UI、后端模块和依赖。
5. 已明确哪些共享基础设施不能删除。

每完成五步中的一步就提交并验证。若验证失败，停在当前步骤修复或回滚，不继续删除后续层。

### 7.1 第一步：取消注册

检查：

- Capability Registry
- Tool Registry
- FastAPI Router
- CLI 命令
- Provider Registry
- RAG Registry
- Plugin Registry
- Background Task
- Startup Hook
- Shutdown Hook

验收：

- 后端可启动
- 功能 API 不再注册
- Chat 不再挂载相关 Tool
- CLI 不再展示相关命令
- 旧配置不会导致启动失败
- Registry 快照只减少预期条目

---

### 7.2 第二步：取消调用

检查：

- Orchestrator
- Tool 自动挂载
- Capability 间调用
- 生命周期钩子
- 配置加载器
- 数据初始化器
- 导入导出
- API Client
- 公共 Schema
- TypeScript Type
- 常量
- Fixture
- Mock
- 动态 import

验收：

- 全局搜索无有效调用点
- 临时重命名模块目录后 Core 仍可导入
- Chat 冒烟通过
- RAG 冒烟通过
- Solve 冒烟通过
- Research 冒烟通过
- Quiz 冒烟通过
- NexaTutor CLI 核心命令仍可解析和运行

---

### 7.3 第三步：删除 UI

顺序：

1. 主导航
2. 二级导航
3. 设置入口
4. Next.js Route
5. Layout
6. Component
7. Hook
8. Context
9. API Client
10. TypeScript Type
11. i18n
12. 图片 / 图标 / Demo
13. 前端测试

验收：

- 无死链接
- 无失效动态 import
- Next.js production build 通过
- TypeScript 通过
- ESLint 通过
- i18n parity 通过

---

### 7.4 第四步：删除后端实现

删除：

- Router
- Service
- Capability
- Tool
- Schema
- Data Model
- Storage
- Config Model
- Background Task
- Script
- Test
- Docs
- Demo

注意：

- 不自动删除旧数据
- 历史会话应尽量仍可读
- 公共 Schema 若被 Core 使用不得误删
- 共享 Path / User / Workspace 抽象不得因平台化功能删除而顺带破坏

---

### 7.5 第五步：删除依赖

确认全部引用消失后再删。

验收：

- 全新 venv 安装成功
- 全新 Node 环境安装成功
- production build 成功
- 无开发机残留依赖
- Core E2E 通过
- CLI 安装、帮助与核心命令 Smoke 通过

---

## 8. Code Execution 安全边界

删除：

```text
通用 Exec
```

保留：

```text
受限 Code Execution
```

第一版建议：

- 默认可关闭
- 仅支持 Python
- 固定工作目录
- import 白名单
- 文件访问限制
- 禁止 Shell
- 禁止 subprocess
- 默认禁止或限制网络访问
- 运行时间限制
- 内存限制（如可行）
- 输出大小限制
- 进程数量限制
- 明确异常终止机制

P6 完成后的实现边界：

- 第一版只支持 Python，C / C++ 已移除。
- 模型只提交 Python 源码；执行请求由服务端构造为 argv，不接受任意 Shell 命令。
- AST import 白名单与危险调用限制作为纵深防御，不作为强隔离替代品。
- Windows 裸机 restricted subprocess 默认关闭且不会激活 Code Execution。
- 只有健康且声明 `argv-v1` 的 SYSTEM Sandbox Runner 才能激活；旧 runner 失败关闭。
- runner 仅挂载单用户 workspace，位于无默认公网路由的 internal Compose network，且不发布宿主端口。

`import` 白名单、禁止 `subprocess` 等 AST 限制只是纵深防御；默认关闭与无可靠隔离后端时不可用仍是基础策略。

Sandbox 基础设施处置：

| 组件 | 处理 |
| --- | --- |
| 通用 `exec` Tool | Remove |
| `code_execution` Tool | 安全收敛后保留 |
| Sandbox Service / ResourceLimits / Quota | 保留 |
| Artifact 收集 | 保留 |
| 外部集成 Sidecar | Remove |
| Sandbox Runner Sidecar | 在替代隔离方案确认前保留 |
| Restricted Subprocess Backend | 默认禁用；仅开发者明确启用 |

文档必须明确：

> NexaTutor 的受限 Code Execution 是风险降低机制，不应宣称为可对抗恶意代码的强安全沙箱。

如未来面向不受信任用户，需另行实现：

- Docker / Podman 隔离
- 独立 Worker
- Namespace / Jail
- Seccomp
- 文件系统隔离
- 网络隔离

---

## 9. Memory 处理原则

### 第一阶段

保留原 Backend，减少产品暴露。

目标：

```text
技术结构复杂
用户体验简单
```

### 第二阶段

只有在确认以下问题后，才考虑重写 Memory：

- 内部复杂度确实造成大量维护成本
- 数据结构明显超出个人学习需求
- 性能 / 存储明显不合理
- 原 Consolidation 工作流难以维护

Memory 重构必须作为独立项目，不与 Remove 批次混合。

---

## 10. Deep Research 后期评估

当前保留为 Core。

后期通过真实使用情况判断：

```text
Chat       → 使用频率
Solve      → 使用频率
Quiz       → 使用频率
Research   → 使用频率
```

如果 Research 使用率很低，可以将以下整体降为 Optional：

```text
Deep Research
web_search
web_fetch
paper_search
```

形成：

```text
Optional Research Pack
```

不要在第一阶段为了追求最小体积而提前砍掉可能有价值的学习能力。

---

## 11. 旧数据兼容策略

由于 NexaTutor 目标是个人项目，不需要永久承担 DeepTutor 全历史格式兼容。

推荐：

```text
DeepTutor Data
      ↓
一次性 Import / Migration
      ↓
NexaTutor Data Schema
```

优先保证：

- Chat
- Notebook
- Question Bank
- Knowledge Base
- Memory

如当前没有重要 DeepTutor 历史数据，可进一步降低兼容工作优先级。

旧功能数据：

- Partner
- Book
- Agent Import
- 旧 RAG Engine 索引
- OAuth Token
- Multi-user Workspace

默认：

- 不自动删除
- 不自动迁移
- 停止使用
- 后续提供显式扫描 / 清理

可选命令：

```text
nexatutor cleanup scan
nexatutor cleanup apply --target <category>
```

执行 `apply` 前必须显示：

- 绝对路径
- 文件数量
- 预计释放空间
- 数据类型
- 明确确认提示

---

## 12. 提交策略

每个功能域建议至少拆成：

```text
chore(remove-<feature>): unregister runtime entries
refactor(remove-<feature>): remove call sites
refactor(remove-<feature>): remove UI
refactor(remove-<feature>): delete backend implementation
build(remove-<feature>): remove dependencies
```

示例：

```text
chore(remove-partners): unregister partner runtime
refactor(remove-partners): remove partner call sites
refactor(remove-partners): remove partner UI
refactor(remove-partners): delete partner backend
build(remove-partners): remove partner dependencies
```

如引入 LocalUserContext：

```text
refactor(local-user): introduce fixed local user context
refactor(local-user): migrate workspace resolution
refactor(local-user): remove multi-user branches
```

项目改名单独提交：

```text
refactor(brand): rename Python package
refactor(brand): rename CLI
refactor(brand): rename frontend branding
refactor(brand): rename environment variables
docs(brand): rename documentation
```

---

## 13. 每批次统一验收

### 13.1 静态与构建

- Python import smoke test
- Python 单元测试
- FastAPI startup test
- Runtime Registry test
- TypeScript check
- ESLint
- Next.js production build
- i18n parity
- 全局残留引用扫描
- 动态 import 检查

### 13.2 核心用户流程

每批裁剪后必须验证：

```text
启动应用
  → 配置云端模型
  → 创建会话
  → 上传文件
  → 建立知识库
  → 基于资料提问
  → Solve 或 Research
  → Quiz
  → 保存笔记或题目
  → 关闭应用
  → 重新启动
  → 恢复历史会话与本地数据
```

### 13.3 自动化 Smoke 建议

至少建立：

```text
Smoke 01  Backend import
Smoke 02  FastAPI startup
Smoke 03  Frontend build
Smoke 04  Create chat
Smoke 05  Knowledge base lifecycle
Smoke 06  RAG query
Smoke 07  Solve
Smoke 08  Quiz
Smoke 09  Notebook persistence
Smoke 10  Restart persistence
Smoke 11  CLI init / config / help
Smoke 12  CLI chat / run argument parsing
Smoke 13  Removed Registry / Router negative checks
Smoke 14  MCP cannot be re-enabled by legacy config
```

---

## 14. 安全检查

每批次检查：

- 后端默认监听 `127.0.0.1`
- API Key 不进入前端日志
- API Key 不进入普通 API 响应
- API Key 不进入普通后端日志
- 已删除 Exec 无法通过旧配置重新启用
- 已删除 Cron 无法通过旧配置重新启用
- 已删除 CLI Apps 无法通过旧配置重新启用
- 已删除 MCP 无法通过旧配置、环境变量或动态 Provider 重新启用
- 已删除 IM Channel 无法通过旧配置重新启用
- 上传路径有边界检查
- 解压路径有 Zip Slip / Path Traversal 检查
- 文档解析器无法任意越界访问文件
- Code Execution 有明确限制
- 输出文件路径有本地用户作用域
- 不把“受限执行”宣传为强安全沙箱

---

## 15. 全新环境验收

开发机容易残留旧依赖，因此最终必须在“干净环境”验证。

要求：

```text
新的 Python venv
+
新的 node_modules
+
新的 data 目录
+
没有旧配置
+
没有旧环境变量
+
没有旧依赖缓存影响
```

完整执行：

```text
安装
  → 启动
  → 配置 API
  → 上传 PDF
  → 建立知识库
  → RAG
  → Solve
  → Quiz
  → 保存 Notebook
  → 关闭
  → 重启
  → 恢复
  → CLI 核心命令验证
  → 确认 MCP / Partners / CLI Apps 无注册与入口
  → 确认 My Agents / Subagents 的本地保留流程可用
```

只有这条链完整通过，才算真正完成裁剪。

---

## 16. Upstream 后续维护策略

建议保留 DeepTutor 作为：

```text
upstream
```

自己的仓库作为：

```text
origin
```

示例：

```bash
git remote rename origin upstream
git remote add origin <NexaTutor Repository URL>
```

以后不要周期性：

```bash
git merge upstream/main
```

建议流程：

```text
DeepTutor 更新
      ↓
阅读 Release / Changelog
      ↓
判断是否涉及：
- 安全修复
- 严重 Bug
- RAG 改进
- 模型兼容
- 文档解析修复
- Core Runtime 修复
      ↓
查看具体 Commit
      ↓
cherry-pick
或
手动移植
```

NexaTutor 越精简，越不适合全量同步上游。

---

## 17. 防止后期重新膨胀

任何新增功能进入 Core 前必须回答：

```text
1. 是否直接服务个人学习？
2. 是否进入主要学习链？
3. 是否值得长期维护？
```

建议采用：

```text
Core
Optional
Experimental
Rejected
```

四级分类。

不要因为“功能看起来很酷”就重新引入：

- 面向多用户或远程托管的 Agent 平台
- MCP
- IM
- 大量 Provider
- 视频
- 图片
- GitHub
- 自动任务
- 插件市场

否则 NexaTutor 会逐渐重新长回 DeepTutor 的体积。

---

## 18. 最终目标架构

```text
NexaTutor
│
├── Core Runtime
│   ├── Orchestrator
│   ├── Context
│   ├── Stream
│   ├── Tool Registry
│   └── Capability Registry
│
├── Capabilities
│   ├── Chat
│   ├── Solve
│   ├── Research
│   ├── Quiz
│   ├── Mastery Path
│   └── Visualize
│
├── Knowledge
│   ├── Upload
│   ├── Parser
│   ├── Chunking
│   ├── Embedding
│   ├── FAISS
│   ├── BM25
│   ├── Hybrid Search
│   └── Citation
│
├── Learning
│   ├── Notebook
│   ├── Question Bank
│   └── Progress
│
├── Memory
│   └── Simplified User-facing UI
│
├── Agents
│   ├── My Agents
│   ├── Subagents
│   └── Local Agent Providers
│
├── User
│   ├── LocalUserContext
│   ├── LocalWorkspacePaths
│   ├── LocalKnowledgeAccess
│   ├── LocalModelAccess
│   └── LocalToolPolicy
│
├── Settings
│   ├── LLM
│   ├── Embedding
│   ├── Search
│   ├── Parser
│   ├── Memory
│   ├── Appearance
│   └── Data / Privacy
│
├── CLI
│   ├── Init / Start / Serve
│   ├── Chat / Run
│   ├── KB / Session / Notebook / Memory
│   └── Config
│
└── Web
```

最终架构不包含 MCP Runtime、CLI Apps 扩展运行时、Partners、插件市场或多用户权限系统；保留单用户、本地范围内的 My Agents / Subagents。

---

## 19. 完成定义

满足以下条件时，NexaTutor 精简改造才算完成：

1. Core 功能全部可用。
2. Remove 功能不再注册。
3. Remove 功能不再被调用。
4. Remove 功能不再显示。
5. Remove 功能不再安装相关依赖。
6. Optional 不影响默认启动。
7. LocalUserContext 稳定工作。
8. 全新环境可安装。
9. 全新环境可启动。
10. 核心用户流程 E2E 通过。
11. 重启后数据可恢复。
12. API Key 无明显泄露路径。
13. Code Execution 安全边界描述准确。
14. 旧数据有迁移、保留或清理策略。
15. 默认安装体积与依赖数量有可量化下降。
16. 项目统一使用 NexaTutor 品牌。
17. 仓库无仍然指向已删除功能的有效入口。
18. 上游更新采用选择性吸收，而不是全量 Merge。
19. 功能新增有明确 Core / Optional 边界。
20. NexaTutor CLI 核心命令可用，已删除功能的 CLI 命令不可用。
21. MCP 的 Registry、Router、Provider、Manager、配置、UI、动态工具和依赖全部删除。
22. Visualize 轻量路径可用，Manim / Math Animator 路径已删除。
23. Internal Python namespace 是否改名已有明确决策，不阻塞产品品牌发布。

---

## 20. 推荐执行顺序总览

```text
建立本地 baseline
  ↓
建立测试 / 路由 / Registry / 依赖基线
  ↓
清理或隔离当前被跟踪的前端构建产物变化
  ↓
Partners / IM（逐 Channel / Runtime 小步删除）
  ↓
My Agents / Subagents（保留并逐 Provider 固化本地边界）
  ↓
MCP 全运行时（按注册、调用、UI、Backend、依赖分步）
  ↓
CLI Apps 扩展系统（不删除 NexaTutor CLI）
  ↓
EduHub / ClawHub / 在线 Skill
  ↓
LocalUserContext / Paths / Access Adapters
  ↓
Auth / Admin / Multi-user / Grants
  ↓
PocketBase / Sidecar / 公网部署能力
  ↓
Book（单独完成五步）
  ↓
Video / Manim / GeoGebra（逐项完成五步）
  ↓
Cron / GitHub / Brainstorm / Reason / 通用 Exec（逐项完成五步）
  ↓
Code Execution 安全收敛
  ↓
RAG 收敛
  ↓
Provider UI 收缩
  ↓
Provider Runtime Adapter 清理
  ↓
Memory UI 精简
  ↓
Settings / Navigation 收口
  ↓
依赖树最终清洗
  ↓
全新环境 E2E
  ↓
DeepTutor → NexaTutor 改名
  ↓
再次全新环境 E2E
  ↓
单独决定是否重命名内部 Python namespace
  ↓
进入长期维护
```

---

## 21. 最终施工原则

> **NexaTutor 不是 DeepTutor 的“删功能版本”，而是以 DeepTutor Runtime 为技术底座，重新收敛出的单用户、本地优先 AI 学习工作台。**

后续所有工程决策都应围绕 NexaTutor 自己的产品目标，而不是围绕“DeepTutor 原来还有什么功能”展开。

施工过程中始终遵循：

> 一个功能域，一个小目标；
> 一个删除步骤，一个可回滚提交；
> 一次验证通过，再进入下一步；
> 不追求一次删完，优先保持项目持续可运行。
