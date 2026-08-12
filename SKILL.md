# NexaTutor CLI 使用说明

本文供自动化 Agent 和终端用户调用 NexaTutor 当前兼容 CLI。迁移期命令名仍为 `deeptutor`；不要虚构尚未发布的 `nexatutor` 可执行文件。

## 适用场景

- 从终端启动本地 Web / API。
- 执行 Chat、Solve、Research、Question、Mastery 或 Visualize。
- 管理知识库、会话、Notebook 和 Memory。
- 以 NDJSON / JSON 形式接收结构化事件。

## 前置条件

```powershell
deeptutor init
```

运行设置位于当前 workspace 的 `data/user/settings/`。项目根 `.env` 不作为运行时配置来源。

## 核心命令

### 启动

```powershell
deeptutor start
deeptutor start --dev
deeptutor serve --port 8001
```

### Chat 与 Capability

```powershell
deeptutor chat
deeptutor run chat "解释傅里叶变换"
deeptutor run deep_solve "求解 x^2 = 4" --tool rag --kb calculus
deeptutor run deep_question "为线性代数生成练习题"
deeptutor run deep_research "整理量子计算研究脉络" --config mode=report --config depth=2
deeptutor run visualize "用 Mermaid 展示 TCP 握手"
deeptutor run mastery_path "制定微积分掌握路径"
```

当前 `run` 仍可能接受 `math_animator`，但该能力计划从 NexaTutor 删除，不应作为新的 Core 工作流依赖。

常用参数：

```text
--session <id>          继续已有会话
--tool / -t <name>      启用工具，可重复
--kb <name>             挂载知识库，可重复
--notebook-ref <ref>    引用 Notebook 记录
--history-ref <id>      引用历史会话
--language / -l <code>  回答语言
--config <key=value>    Capability 配置，可重复
--config-json <json>    JSON 配置
--format / -f <fmt>     rich 或 json
```

### 知识库

```powershell
deeptutor kb list
deeptutor kb create calculus --doc .\textbook.pdf
deeptutor kb info calculus
```

### 会话、Notebook 与 Memory

```powershell
deeptutor session list
deeptutor notebook list
deeptutor memory show
```

### 配置

```powershell
deeptutor config show
```

Provider 专用 OAuth / validation 仍是迁移期兼容入口，后续会随 Provider 收缩处理：

```powershell
deeptutor provider login openai-codex
deeptutor provider login github-copilot
```

`openai-codex` 执行 OAuth 登录；`github-copilot` 只校验已有 Copilot 认证，不执行新的 OAuth 登录。

## 结构化输出

Agent 调用时优先使用 JSON 格式：

```powershell
deeptutor run chat "总结这份资料" --format json
```

输出为逐行事件。每个事件包含会话或 Turn 相关字段；调用方应等待最终 `done` / result 事件，不要只读取第一行。

`ask_user` 可能暂停一轮等待用户输入。无交互环境必须明确处理空回答或超时，不能无限等待。

## REPL

```powershell
deeptutor chat
```

常用斜杠命令以当前 `deeptutor chat --help` 和 REPL 内 `/help` 为准。`/regenerate` 或 `/retry` 会重新执行上一条用户消息。

## 迁移期入口

当前 CLI 仍可能显示：

```text
partner, plugin, skill, skills, provider, book
```

这些入口并不属于 NexaTutor 最终 Core。只有相应代码真正完成取消注册后，文档与契约测试才能删除它们；在此之前不要声称命令已经不可用。

## Agent 使用约束

- 不使用 `exec` 作为通用 Shell 后门。
- 不自动开启 Code Execution；它目前不应被视为强安全沙箱。
- 不通过 CLI 自动删除历史数据。
- 不输出或记录 API Key、OAuth Token 和个人资料。
- 需要修改项目时先读取 `AGENTS.md` 和正式裁剪计划。
