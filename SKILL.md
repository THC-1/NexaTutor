# NexaTutor CLI 使用说明

本文供自动化 Agent 和终端用户调用 NexaTutor CLI。正式命令为 `nexatutor`；旧 `deeptutor` 仅作带迁移提示的兼容转发，新脚本不应继续依赖旧命令。

## 前置条件

```powershell
nexatutor init
```

运行设置位于当前 workspace 的 `data/user/settings/`，项目根 `.env` 不作为应用运行时配置来源。

## 启动

```powershell
nexatutor start
nexatutor start --dev
nexatutor serve --port 8001
```

## Capability

当前内置 Capability：

```text
chat, deep_solve, deep_question, deep_research, visualize, mastery_path
```

示例：

```powershell
nexatutor chat
nexatutor run chat "解释傅里叶变换"
nexatutor run deep_solve "求解 x^2 = 4" --tool rag --kb calculus
nexatutor run deep_question "为线性代数生成练习题"
nexatutor run deep_research "整理量子计算研究脉络" --config mode=report --config depth=2
nexatutor run visualize "用 Mermaid 展示 TCP 握手"
nexatutor run mastery_path "制定微积分掌握路径"
```

`math_animator` 已删除，不是可用 Capability。

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

## 数据命令

```powershell
nexatutor kb list
nexatutor kb create calculus --doc .\textbook.pdf
nexatutor kb info calculus
nexatutor session list
nexatutor notebook list
nexatutor memory show
nexatutor config show
```

## Provider 登录

Provider CLI 只保留 OpenAI Codex OAuth：

```powershell
nexatutor provider login openai-codex
```

GitHub Copilot 和其他专用 Provider 登录已删除。

## 结构化输出

Agent 调用优先使用 JSON：

```powershell
nexatutor run chat "总结这份资料" --format json
```

输出为逐行事件。调用方应等待最终 `done` / result 事件，不能只读取第一行。`ask_user` 可能暂停一轮等待输入；无交互环境必须处理空回答或超时。

## 当前顶层入口

```text
init, run, start, serve, chat, kb, skill, skills,
memory, config, session, notebook, provider
```

`skill` / `skills` 仅管理本地 Skill；`provider` 不是通用 Provider 管理器。`partner`、`plugin`、`book` 已删除。

## Agent 约束

- 不使用已删除的 `exec` 作为 Shell 后门。
- 不自动开启 Code Execution；它是风险降低机制，不是强安全沙箱。
- 不自动删除或迁移历史数据。
- 不输出或记录 API Key、OAuth Token 和个人资料。
- 修改项目之前读取 `AGENTS.md` 和正式裁剪计划。
