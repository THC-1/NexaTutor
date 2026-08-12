# NexaTutor 运行时基线

本文冻结提交 `8865da7c6d51d579db66ad123fcf3f16a2eed0a4` 开始裁剪时的运行时表面，用于为“取消注册 → 取消调用 → 删除 UI → 删除实现 → 删除依赖”提供对照证据。这里记录的是裁剪前事实，不是最终目标。

## Registry 快照

### Capability（7）

`chat`、`deep_question`、`deep_research`、`deep_solve`、`mastery_path`、`math_animator`、`visualize`。

### Tool（43）

```text
ask_user, brainstorm, code_execution, consult_subagent, cron, exec,
geogebra_analysis, github, imagegen, kb_files, list_notebook, load_tools,
mastery_assess, mastery_build, mastery_grade, mastery_quiz, mastery_status,
obsidian_append, obsidian_backlinks, obsidian_create_note, obsidian_links,
obsidian_list, obsidian_read, obsidian_search, obsidian_set_property,
obsidian_tags, paper_search, partner_memorize, partner_read, partner_search,
rag, read_memory, read_skill, read_source, reason, solve_finish_step,
solve_plan, solve_replan, videogen, web_fetch, web_search, write_memory,
write_note
```

- Core 候选：`ask_user`、`code_execution`、`kb_files`、`list_notebook`、`paper_search`、`rag`、Memory / Source / Web / Note 工具，以及 Mastery、Solve、Quiz / Grading 内部工具。
- Optional 候选：`imagegen`、本地 Obsidian 工具、`read_skill`。
- Core：`consult_subagent`（按 2026-08-12 修订决定保留 My Agents / Subagents）。
- Remove 候选：`brainstorm`、`cron`、`exec`、`geogebra_analysis`、`github`、`load_tools`、三个 Partner Tool、`reason`、`videogen`。

### LLM Provider Spec（36）

```text
custom, custom_anthropic, azure_openai, openrouter, edenai, aihubmix,
siliconflow, novita, atlascloud, volcengine, volcengine_coding_plan, byteplus,
byteplus_coding_plan, anthropic, openai, openai_codex, github_copilot,
deepseek, gemini, zhipu, dashscope, moonshot, minimax, minimax_anthropic,
mistral, stepfun, xiaomi_mimo, vllm, ollama, lm_studio, llama_cpp, lemonade,
ovms, nvidia_nim, groq, qianfan
```

### RAG Provider（6）

`graphrag`、`ima`、`lightrag`、`lightrag-server`、`llamaindex`、`pageindex`。

## FastAPI Route 快照

- Route object 总数：327。
- `/api/v1/partners` Route object：32。
- Partner 旁路：`/api/v1/subagents/partners`。
- 路径含 `partner` 的 Route object：33。

这里按 Route object 而不是唯一路径计数，因为同一路径可能为不同 HTTP 方法分别注册。后续负断言必须在对应步骤确认主前缀和旁路均已消失。

## CLI 快照

裁剪前注册的 12 个 Typer 顶层组：`book`、`chat`、`config`、`kb`、`memory`、`notebook`、`partner`、`plugin`、`provider`、`session`、`skill`、`skills`。

项目 CLI 属于 Core；只随对应功能域删除功能专用命令组。

## 依赖数量

- Python 直接项目依赖：44。
- Python `partners` extra：19。
- Node 运行依赖：23。
- Node 开发依赖：12。

这些数字只用于对比，不代表可以立即删除依赖。只有运行时、测试、构建、CLI、动态 import 和 optional extra 引用全部消失后，才能删除对应包。

## 首个 Partner / IM 施工边界

已经确认的最小目标是 `deeptutor/api/main.py` 中 Partner 生命周期钩子：启动时曾调用 `auto_start_partners()`，关闭时曾调用 `stop_all(preserve_auto_start=True)`。

这两个调用已移除，并有 `tests/api/test_main_partner_lifecycle.py` 防回归测试。随后主应用的 Partner API Router 注册也已移除，并由 `tests/api/test_main_partner_router_registration.py` 证明 `/api/v1/partners` 不存在而 `/api/v1/subagents/partners` 暂时保留。Partner Router 实现、CLI、Tools、Plugin 转发、Subagent 旁路、UI、依赖、Memory 迁移和用户数据尚未删除。

后续取消注册继续拆成独立小步：

1. Partner API Router（已完成）。
2. Partner CLI Group（已完成）。
3. 三个 Partner Built-in Tool（已完成；Registry 从基线 43 减为 40）。
4. Partner Subagent Backend（下一步）。
5. 在确认共享所有权后处理 Partner 旁路和 Plugin 转发。

## 基线验证

每个小步都应关闭字节码写入并执行后端 import smoke，再为正在变化的 Registry 或 Router 运行精确断言。项目开发环境应安装 `pytest-asyncio` 后再解释异步测试结果。

`web/.next-deeptutor/` 已停止 Git 跟踪并由 `.gitignore` 忽略；前端生产构建仍必须使用被忽略的 `web/.next`，不得重新引入历史构建目录。
