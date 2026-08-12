# NexaTutor CLI 兼容发行包

这是当前迁移期的 CLI-only Python 分发配置。分发名仍为 `deeptutor-cli`，安装后命令仍为 `deeptutor`。

它包含终端工作流、RAG、文档解析和模型 Provider 所需的 Python 模块，不包含 Next.js Web 资源以及 `deeptutor start` 使用的完整 FastAPI / Uvicorn 服务依赖。

在仓库根目录执行：

```powershell
py -3.13 -m venv .venv-cli
.\.venv-cli\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .\packaging\deeptutor-cli
```

这是 editable install，使用期间需要保留源码 checkout。正式 `nexatutor` 分发名和命令将在核心裁剪稳定后单独迁移。
