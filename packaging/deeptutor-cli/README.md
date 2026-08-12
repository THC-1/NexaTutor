# NexaTutor CLI 兼容发行包

CLI-only Python 分发名为 `nexatutor-cli`，正式命令为 `nexatutor`。旧 `deeptutor` 命令仅作迁移提示与转发。

它包含终端工作流、RAG、文档解析和模型 Provider 所需的 Python 模块，不包含 Next.js Web 资源以及 `deeptutor start` 使用的完整 FastAPI / Uvicorn 服务依赖。

在仓库根目录执行：

```powershell
py -3.13 -m venv .venv-cli
.\.venv-cli\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .\packaging\deeptutor-cli
```

这是 editable install，使用期间需要保留源码 checkout。内部模块仍使用兼容 namespace `deeptutor`。
