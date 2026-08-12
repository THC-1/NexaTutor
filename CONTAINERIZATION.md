# NexaTutor 容器运行指南

> Compose service 为 `nexatutor`，目标镜像为 `ghcr.io/thc-1/nexatutor`。发布 workflow 仍暂停，因此预构建镜像可用性需以仓库 Packages 页面为准。

返回 [项目说明](README.md)。

## 当前定位

NexaTutor 的目标是个人、本地优先运行。当前仓库仍保留以下上游容器能力：

- 源码构建 Docker 镜像。
- 上游 GHCR 预构建镜像。
- Docker Compose。
- Rootless Podman / read-only rootfs。
- Sandbox Runner 隔离后端。

所有应用端口只发布到宿主机 loopback。Sandbox Runner 仍被 Code Execution 使用，在替代隔离方案确认前不能删除。

## 推荐方式：本机源码运行

个人开发与当前裁剪验证优先使用本机 Python + Node.js，参见根 README。容器方式主要用于验证干净环境、Linux 隔离与发布制品，不是当前开发的最快路径。

## Docker 源码构建

```powershell
docker compose -f docker-compose.yml up -d --build
docker compose -f docker-compose.yml ps
docker compose -f docker-compose.yml logs -f nexatutor
```

默认访问地址通常为：

- 前端：`http://127.0.0.1:3782`
- 后端：`http://127.0.0.1:8001`

停止并保留数据：

```powershell
docker compose -f docker-compose.yml down
```

不要在未检查 volume 与绝对路径前执行 `down -v`。该操作可能删除知识库、会话、Memory、Token 和其他本地数据。

## GHCR 镜像目标

发布配置的目标镜像为：

```powershell
python scripts/docker_compose.py -f docker-compose.ghcr.yml up -d
python scripts/docker_compose.py -f docker-compose.ghcr.yml ps
```

镜像：

```text
ghcr.io/thc-1/nexatutor:latest
```

此方式会包含尚未裁剪完成的上游能力。做 NexaTutor 功能验收时，应优先构建当前源码，而不是用 GHCR 镜像判断裁剪结果。

## Rootless Podman

`compose.yaml` 是当前 rootless / read-only rootfs 方案：

```bash
podman compose -f compose.yaml up -d
podman compose -f compose.yaml ps
podman compose -f compose.yaml logs -f nexatutor
```

默认端口只绑定到 `127.0.0.1`。

停止并保留数据：

```bash
podman compose -f compose.yaml down
```

## 数据与设置

容器内主要数据根目录为：

```text
/app/data
```

当前 Compose 文件将宿主机 `./data` 挂载到 `/app/data`。运行设置位于：

```text
data/user/settings/*.json
```

修改设置后重启兼容 service：

```powershell
docker compose -f docker-compose.yml restart nexatutor
```

不要依赖项目根 `.env` 配置模型、Embedding、搜索或 Auth。`.env` 只用于 Compose 自身需要的宿主机变量；应用运行时以 JSON Settings 为准。

## 一次性数据迁移提醒

较旧的 `docker-compose.ghcr.yml` 只挂载部分目录，可能把 `data/system`、`data/users`、`data/partners` 或 `data/cli-apps` 留在容器可写层。当前文件挂载整个 `./data:/app/data`。

升级旧容器前应：

1. 停止写入。
2. 使用 `docker cp` 将旧容器 `/app/data` 复制到明确的临时目录。
3. 检查文件数量、权限和凭据目录。
4. 备份现有宿主机 `data/`。
5. 合并后再强制重建容器。

不要用空宿主机目录直接覆盖仍含数据的旧容器层。

### 临时本地 Codex OAuth 桥接

OpenAI Codex OAuth 仍是迁移期兼容能力。浏览器回调端口需要临时映射到前端 `3782`：

```text
127.0.0.1:1455:3782
127.0.0.1:1457:3782
```

源码 Docker Compose：

```powershell
docker compose -f docker-compose.yml -f compose.codex-oauth.yaml up -d --force-recreate nexatutor
```

GHCR Compose：

```powershell
docker compose -f docker-compose.ghcr.yml -f compose.codex-oauth.yaml up -d --force-recreate nexatutor
```

Podman：

```bash
podman compose -f compose.yaml -f compose.codex-oauth.yaml up -d --force-recreate nexatutor
```

完成登录后立即撤销临时端口映射，使用原基础文件重新创建：

```powershell
docker compose -f docker-compose.yml up -d --force-recreate nexatutor
```

远程 SSH 隧道、反向代理和共享 OAuth 凭据不属于 NexaTutor 支持范围。

## Sandbox Runner

不要把 Sandbox Runner Sidecar 与外部集成 Sidecar 混为一谈。前者可能仍是 `code_execution` 的隔离后端。当前 Windows restricted subprocess 不是强安全沙箱，容器运行也不会自动让任意代码执行安全。

当前 Code Execution 安全边界：

- 默认关闭，只能由用户明确启用，第一版仅支持 Python argv。
- Runner 位于无公网默认路由的内部网络，仅挂载 `data/user/workspace`。
- 旧 Runner 若不声明 `argv-v1` 会失败关闭，不降级为 Shell。
- AST allowlist、资源限制和容器隔离属于风险降低；不宣称可对抗恶意代码。
- 不删除 ResourceLimits、Quota、Artifact 收集或仍被使用的 Sandbox Runner。

## 本地服务地址

容器内的 `localhost` 指向容器本身。若需要访问宿主机服务：

- Docker Desktop 通常使用 `host.docker.internal`。
- Podman 通常使用 `host.containers.internal`。

本地模型入口最终计划从 NexaTutor 产品层删除，因此不要围绕 Ollama、LM Studio、vLLM 或 llama.cpp 新增长期文档与 UI。

## 故障检查

```powershell
docker compose -f docker-compose.yml ps
docker compose -f docker-compose.yml logs --tail 200 nexatutor
docker inspect nexatutor
```

检查顺序：

1. `./data` 是否可写且没有被空目录覆盖。
2. `data/user/settings/system.json` 中端口是否与 Compose 渲染结果一致。
3. 前端是否能通过 runtime proxy 到达后端。
4. 8001 / 3782 / 1455 / 1457 是否被其他程序占用。
5. API Key 是否只存在于受控设置或 Secret Storage 中。

## 安全要求

- 默认只绑定 `127.0.0.1`。
- 不把 API Key 写进 Compose、镜像层、前端 Bundle 或普通日志。
- 不将应用端口暴露到公网或局域网。
- 上传、解压和输出路径必须防止 Path Traversal / Zip Slip。
- 清理 volume 前显示绝对路径、文件数量和预计影响。
