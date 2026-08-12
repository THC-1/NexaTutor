# NexaTutor CLI

正式命令为 `nexatutor`，实现仍位于兼容 Python 包 `deeptutor_cli`。旧 `deeptutor` 命令仅打印迁移提示并转发到同一实现。

## 安装

完整源码开发环境：

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
```

CLI-only editable install：

```powershell
py -3.13 -m venv .venv-cli
.\.venv-cli\Scripts\Activate.ps1
python -m pip install -e .\packaging\deeptutor-cli
```

默认开发安装不要使用 `.[all]`，请按需选择项目提供的 optional extra。

## 初始化与启动

```powershell
nexatutor init
nexatutor start
nexatutor start --dev
nexatutor serve --port 8001
```

设置保存在当前 workspace 的 `data/user/settings/`。

## `run`：执行 Capability

当前可用 Capability 包括 `chat`、`deep_solve`、`deep_question`、`deep_research`、`visualize` 和 `mastery_path`。轻量 `visualize` 保留 Mermaid、SVG、Chart.js 和 HTML。

```powershell
nexatutor run chat "解释傅里叶变换"
nexatutor run deep_solve "求解 x^2 = 4" --tool rag --kb calculus
nexatutor run deep_question "生成一组概率论练习"
nexatutor run deep_research "整理主题研究脉络" --config mode=report --config depth=2
nexatutor run visualize "用 Mermaid 展示请求链路"
nexatutor run mastery_path "制定微积分学习路径"
nexatutor run chat "总结资料" --format json
```

常用选项：

```text
--session <id>          恢复会话
--tool / -t <name>      启用工具，可重复
--kb <name>             挂载知识库，可重复
--notebook-ref <ref>    引用 Notebook 记录
--history-ref <id>      引用历史会话
--language / -l <code>  回答语言
--config <key=value>    Capability 配置，可重复
--config-json <json>    JSON 配置
--format / -f <fmt>     rich 或 json
```

## `chat`：交互式 REPL

```powershell
nexatutor chat
```

使用 `/help` 查看当前 REPL 命令。`/regenerate` 或 `/retry` 会重新执行上一条用户消息。

## 资源管理

```powershell
nexatutor kb list
nexatutor kb create calculus --doc .\textbook.pdf
nexatutor kb info calculus
nexatutor session list
nexatutor notebook list
nexatutor memory show
nexatutor config show
```

## Provider 认证入口

```powershell
nexatutor provider login openai-codex
```

- `openai-codex`：执行浏览器 OAuth 登录。

Provider 专用 OAuth 属于待收缩能力，后续会随 Provider 产品层与 Runtime Adapter 清理逐步处理。

## 迁移期非 Core 命令

`partner` 与 `plugin` 已删除；`skill` / `skills` 仅保留本地 `list`、`remove`。当前帮助中仍可能显示 `provider`、`book`，它们不属于 NexaTutor 最终 Core，文档不再推荐以这些命令建立新的工作流。

## 自动化调用

- 使用 `--format json` 获取逐行结构化事件。
- 等待最终 result / `done` 事件。
- 处理 `ask_user` 暂停，不要在无 TTY 环境无限等待。
- 不记录 API Key、OAuth Token 或包含个人数据的完整响应。
- `code_execution` 当前不应视为可对抗恶意代码的强安全沙箱。
