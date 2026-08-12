# NexaTutor 上游基线

- 来源项目：`HKUDS/DeepTutor`
- 本地基线提交：`8865da7c6d51d579db66ad123fcf3f16a2eed0a4`
- 基线标签：等待基线文件审核并提交后创建
- 基线日期：`2026-08-12`
- 当前分支：`main`
- 建立基线前存在本地修改：是
- 上游远程地址：`https://github.com/HKUDS/DeepTutor.git`

## 工作区分类

裁剪前共发现 2,960 项工作区变化：

- `web/.next-deeptutor/` 下有 2,959 项前端构建产物变化，其中 2,798 个已跟踪文件被修改、161 个已跟踪文件被删除。
- 一份未跟踪的正式执行计划：`NEXATUTOR_SLIMMING_PLAN_REVISED新版.md`。
- 生成目录之外没有源码或配置修改。
- 没有已暂存文件。

`.gitignore` 已忽略 `web/.next-deeptutor/`，但 Git 历史中仍跟踪该目录的 4,322 个文件。现有生成物变化不得混入功能裁剪提交，也不得未经确认整体恢复或删除。若后续停止跟踪，必须作为独立的仓库卫生变更处理。

## 基线环境

- PowerShell：`7.6.4`
- Python：`3.13.0`
- Node.js：`24.12.0`
- npm：`11.6.2`

初始后端导入冒烟已通过，覆盖 Orchestrator、Tool Registry、Capability Registry、Runtime Settings 和统一 WebSocket Router。

## 安全改动边界

在生成物得到独立处理前：

- 禁止为 NexaTutor 改造执行 `git add -A`。
- 只暂存并检查明确指定的源码或文档路径。
- 裁剪 Diff 与状态检查必须排除 `web/.next-deeptutor/**`。
- 前端构建应使用被忽略的 `web/.next`，不得继续污染被跟踪的 `.next-deeptutor` 基线。
